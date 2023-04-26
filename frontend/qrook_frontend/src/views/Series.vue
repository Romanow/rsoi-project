<template>
  <div>
    <b-card class="mb-3" style="width: 600px; margin-left: 10px; margin-top: 10px;" img-left>
      <b-row>
        <b-col>
          <img v-if="!skin_image" :src="require('@/assets/default_series.png')"
               width="200px" height="300px"></img>
          <img v-if="skin_image" :src="skin_image" width="200px" height="300px"></img>
        </b-col>
        <b-col>
          <b-card-body :title="name">
            <b-card-text>
              <b-row v-if="finished">
                <span class="text-muted">Закончена:&nbsp</span>
                <span>{{ finished }}</span>
              </b-row>
              <b-row v-if="books_cnt">
                <span class="text-muted">Количество книг:&nbsp</span>
                <span>{{ books_cnt }}</span>
              </b-row>

              <b-row>
                <div v-for="(author, i) of authors">
                  <div style="margin-right: 20px">
                    <img src="@/assets/pen_icon.png" width="25px">
                    <router-link :to="'/author/' + author.id" class="bookLink">{{ author.name }}</router-link>
                  </div>
                </div>
              </b-row>
            </b-card-text>
          </b-card-body>
        </b-col>
      </b-row>
    </b-card>

    <b-card style=" margin-left: 10px; max-width: 95%">
      <b-row>
        <b-card-body title="О серии">
          <b-card-text>
            <pre>{{ description }}</pre>
          </b-card-text>
        </b-card-body>
      </b-row>
    </b-card>
    <div style="margin-top: 10px">
      <h4 align="center">Книги серии:</h4>
      <div>
        <PreviewCollection
          v-bind:filters="filters">
        </PreviewCollection>
      </div>
    </div>
  </div>
</template>

<script>
import {log_event} from '@/services/scouting'
import PreviewCollection from "@/components/PreviewCollection.vue";
import {library} from "@/services/repositories/library"
import {format_authors} from "@/services/formatting";

export default {
  name: "Series",
  data() {
    return {
      id: null,
      info: {},
      filters: {series_id: this.id, find_book: true, sort: 'series_order'}
    }
  },

  watch: {
    '$route.params.id': {
      handler: function (id) {
        this.load_data();
        this.filters = {series_id: id, find_book: true, sort: 'series_order'}
      },
      deep: true,
      immediate: true
    }
  },

  computed: {
    authors() {
      return format_authors(this.info.authors)
    },

    skin_image() {
      return this.info.skin_image
    },

    name() {
      return this.info.title
    },

    books_cnt() {
      return this.info.books_count
    },

    finished() {
      let finished = this.info.is_finished
      if (finished === true)
        return 'да'
      else if (finished === false)
        return 'нет'
      else
        return 'неизвестно'
    },

    description() {
      let description = this.info.description
      if (!description) return 'Информации о серии книг нет'
      return description
    }
  },

  components: {
    PreviewCollection
  },

  methods: {
    load_data() {
      this.id = this.$route.params.id

      let callback = (series) => {
        this.info = series
        log_event('view_series', {series_id: Number(this.id)})
      }

      library.series(this.id, callback);
    },
  },

}
</script>
