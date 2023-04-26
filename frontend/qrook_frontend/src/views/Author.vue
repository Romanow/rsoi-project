<template>
  <div>
    <b-card class="mb-3" style="width: 600px; margin-left: 10px; margin-top: 10px;" img-left>
      <b-row>
        <b-col>
          <img v-if="!photo" :src="require('@/assets/author_default.png')"
               width="200px" height="300px"></img>
          <img v-if="photo" :src="photo" width="200px" height="300px"></img>
        </b-col>
        <b-col>
          <b-card-body :title="name">
            <b-card-text>
              <b-row v-if="sex">
                <span class="text-muted">Пол:&nbsp</span>
                <span>{{ sex }}</span>
              </b-row>
              <b-row v-if="bdate">
                <span class="text-muted">Дата рождения:&nbsp</span>
                <span>{{ bdate }}</span>
              </b-row>
            </b-card-text>
          </b-card-body>
        </b-col>
      </b-row>
    </b-card>

    <b-card style=" margin-left: 10px; max-width: 95%">
      <b-row>
        <b-card-body title="Об авторе">
          <b-card-text>
            <pre align="left">{{ description }}</pre>
          </b-card-text>
        </b-card-body>
      </b-row>
    </b-card>
    <div style="margin-top: 10px">
      <h4 align="center">Написанные книги:</h4>
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

export default {
  name: "Author",
  data() {
    return {
      id: null,
      info: {},
      filters: {author_id: this.id, find_book: true, find_series: true}
    }
  },

  watch: {
    '$route.params.id': {
      handler: function (id) {
        this.load_data();
        this.filters = {author_id: id, find_book: true, find_series: true}
      },
      deep: true,
      immediate: true
    }
  },

  computed: {
    sex() {
      return this.info.sex
    },
    photo() {
      return this.info.photo
    },
    name() {
      return this.info.name
    },

    bdate() {
      let bd = this.info.birthdate
      if (!bd) return null
      return (new Date(bd)).toLocaleDateString()
    },

    description() {
      let info = this.info.description
      if (!info) return 'Информации об авторе нет'
      return info
    }
  },

  components: {
    PreviewCollection
  },

  methods: {
    load_data() {
      this.id = this.$route.params.id

      let callback = (author) => {
        this.info = author
        log_event('view_author', {author_id: Number(this.id)})
      }

      library.author(this.id, callback);
    }
  },
}
</script>
