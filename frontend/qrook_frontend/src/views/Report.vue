<template>
  <div>
    <b-card class="mb-3" style="width: 600px; margin-left: 10px; margin-top: 10px;" img-left>
      <b-row>
        <span class="before"></span>
        <div
          class="d-flex align-items-center justify-content-center"
          style="width: 100%; height: 100%; display: inline-block; vertical-align: middle;">
          <b-form @submit="on_submit">

            <b-form-group id="input-group-1" label="Время начала:" label-for="input-1"
                          label-align="right" content-cols="16">
              <date-pick v-model="date_from"></date-pick>
            </b-form-group>

            <b-form-group id="input-group-2" label="Время конца:" label-for="input-2"
                          label-align="right" content-cols="16">
              <date-pick v-model="date_to"></date-pick>
            </b-form-group>

            <p class="error_logging" v-if="failed"> Недостаточно прав </p>

            <b-button type="submit" value="update" block variant="primary">Создать отчет</b-button>
            <div>
              <a v-on:click="$router.go(-1)" style="color:black; cursor: pointer;">назад</a>
            </div>
          </b-form>
        </div>
      </b-row>
    </b-card>

    <div style="margin-top: 60px">
      <div v-if="this.report">
        <div>
          <p align="left">Количество скачиваний книг: {{ this.report.downloads_cnt }}</p>
        </div>
        <div align="left">
          <p>Поисковые запросы:</p>
          <ul>
            <li>Количество запросов: {{ this.report.search_cnt }}</li>
            <li>Самый популярный запрос: {{ this.report.most_frequent_search }}</li>
          </ul>
        </div>
        <div align="left">
          <p>Количество просмотров:</p>
          <ul>
            <li>Всего: {{ this.report.views_cnt.total }}</li>
            <li>Книг: {{ this.report.views_cnt.books }}</li>
            <li>Авторов: {{ this.report.views_cnt.authors }}</li>
            <li>Серий книг: {{ this.report.views_cnt.series }}</li>
          </ul>
        </div>
      </div>

      <div v-if="this.filters.collection.items.length > 0">
        <p align="left">Самое популярное за период:</p>
        <div>
          <PreviewCollection
            v-bind:filters="filters">
          </PreviewCollection>
        </div>
      </div>
    </div>

  </div>

</template>


<script>
import PreviewCollection from "@/components/PreviewCollection.vue";
import {user_repo} from "@/services/repositories/user";
import DatePick from 'vue-date-pick';
import 'vue-date-pick/dist/vueDatePick.css';

export default {
  data() {
    let d = new Date()
    d.setDate(d.getDate() - 7);
    return {
      failed: false,
      date_to: new Date().toISOString().slice(0, 10),
      date_from: d.toISOString().slice(0, 10),
      report: undefined,
      filters: {
        ready: true,
        collection: {   // this is LibraryCollection
          ok: 'true',
          items: []
        }
      }
    }
  },

  computed: {
    from_timestamp() {
      let d = this.date_from.split("-");
      var ts = new Date(d[0], d[1] - 1, d[2]);
      return Math.floor(ts.getTime() / 1000)  // число секунд
    },

    to_timestamp() {
      let d = this.date_to.split("-");
      var ts = new Date(d[0], d[1] - 1, d[2]);
      return Math.floor(ts.getTime() / 1000) + 3600*24  // прибавим сутки, чтобы день учитывался целиком
    }
  },


  methods: {
    on_submit: function (event) {
      event.preventDefault()
      this.report = undefined
      this.filters.collection.items = []

      let callback = (reportData) => {
        this.failed = !reportData.ok;
        if (this.failed) return;
        this.filters.collection.items = reportData.most_frequent_entities
        this.report = reportData
      }

      user_repo.generate_report(this.from_timestamp, this.to_timestamp, callback);
    },
  },

  components: {
    PreviewCollection,
    DatePick
  },
};
</script>
