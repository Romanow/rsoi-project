<template>
  <div>
    <b-card
      border-variant="primary"
      no-body
      style="height:300px; width:200px; border-width: 3px"
    >
      <div class="card-header">
        <div v-if="!book_image"><img :src="require('@/assets/default_book.png')"
                                     width="110px" height="165px"></div>
        <div v-if="book_image"><img :src="book_image" width="110px" height="165px"></div>
        <div>
          <router-link :to="'/book/' + book_id" class="bookLink">{{ title }}</router-link>
        </div>
      </div>
      <b-card-text>
        <div v-for="(author, i) of authors">
          <img src="@/assets/pen_icon.png" width="22px">
          <router-link :to="'/author/' + author.id" class="bookLink">{{ author.name }}</router-link>
        </div>
      </b-card-text>
    </b-card>
  </div>
</template>

<script>
import {format_preview_authors} from "../services/formatting";

export default {
  name: "BookPreview",
  data() {
    return {
      id: 0,
    }
  },

  computed: {
    book_order() {
      return this.info['book_order']
    },

    book_image() {
      return this.info['skin_image']
    },

    title() {
      let t = this.info['title']
      if (!t) return null

      if (t.length > 41) {
        t = t.slice(0, 38) + '...'
      }
      return t
    },

    title_lines_busy() {
      if (!this.title) return 0
      return Math.ceil(this.title.length / 17)
    },

    authors() {
      if (!this.info['authors']) return []
      let free = 4 - this.title_lines_busy
      return format_preview_authors(this.info['authors'], free)
    },

    book_id() {
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
