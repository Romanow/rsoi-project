<template>
  <div>
    <b-card
      border-variant="warning"
      no-body
      style="height:300px; width:200px; border-width: 3px"
    >
      <div class="card-header" style="height: 300px">
        <div v-if="!photo"><img :src="require('@/assets/author_default.png')"
                                     width="150px" height="225px"></div>
        <div v-if="photo"><img :src="photo" width="150px" height="225px"></div>
        <div>
          <router-link :to="'/author/' + author_id" class="bookLink">{{ author_name }}</router-link>
        </div>
      </div>
    </b-card>
  </div>
</template>

<script>
export default {
  name: "AuthorPreview",
  data() {
    return {
      id: 0,
    }
  },

  computed: {
    photo() {
      return this.info['photo']
    },

    author_name() {
      let t = this.info['name']
      if (!t) return null

      if (t.length > 51)
        t = t.slice(0, 48) + '...'
      return t
    },

    author_id() {
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
