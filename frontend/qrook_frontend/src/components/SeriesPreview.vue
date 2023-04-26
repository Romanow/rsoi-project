<template>
  <div>
    <b-card
      border-variant="success"
      no-body
      style="height:300px; width:200px; border-width: 3px"
    >
      <div class="card-header">
        <div v-if="!series_image"><img :src="require('@/assets/default_series.png')"
                                       width="110px" height="165px"></div>
        <div v-if="series_image"><img :src="series_image" width="110px" height="165px"></div>
        <div>
          <router-link :to="'/series/' + series_id" class="bookLink">{{ title }}</router-link>
        </div>
        <div>
          <span class="text-muted">Число книг:</span>
          <span>{{ books_cnt }}</span>
        </div>
      </div>
      <b-card-text>
        <div v-for="(author, i) of authors">
          <img src="@/assets/pen_icon.png" width="25px">
          <router-link :to="'/author/' + author.id" class="bookLink">{{ author.name }}</router-link>
        </div>
      </b-card-text>
    </b-card>
  </div>
</template>

<script>
import {format_preview_authors} from "../services/formatting";

export default {
  name: "SeriesPreview",
  data() {
    return {
      id: 0,
      authors_limit: 1
    }
  },

  computed: {
    series_image() {
      return this.info['skin_image']
    },

    title() {
      let t = this.info['title']
      if (!t) return null

      if (t.length > 25)
        t = t.slice(0, 21) + '...'

      return t
    },

    books_cnt() {
      return this.info['books_count']
    },

    title_lines_busy() {
      if (!this.title) return 0
      return Math.ceil(this.title.length / 17)
    },

    authors() {
      if (!this.info['authors']) return []
      let free = Math.min(this.authors_limit, 4 - this.title_lines_busy)
      return format_preview_authors(this.info['authors'], free)
    },

    series_id() {
      return this.info['id']
    }
  },

  methods: {
    getWidth() {
      return this.$refs.app.clientWidth
    },
    getHeight() {
      return this.$refs.app.clientHeight
    },
  },

  props: ['info']
}
</script>
