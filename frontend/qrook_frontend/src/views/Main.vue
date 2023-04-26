<template>
  <div>
    <PreviewCollection
      v-bind:filters="search_filters"></PreviewCollection>
  </div>
</template>


<script>
import PreviewCollection from "@/components/PreviewCollection.vue";

export default {
  components: {
    PreviewCollection
  },

  created() {
    this.set_route_query(true)
  },

  updated() {
    this.set_route_query(false)
  },

  computed: {
    search_filters() {
      return this.$store.state.filters.filters
    }
  },

  methods: {
    set_route_query(created) {
      let query = this.$route.query
      if (Object.keys(query).length === 0 || !created) {
        this.$router.replace({name: "Main", query: this.search_filters})
      }
      else {
        this.$store.dispatch('filters/set_filters', query)
      }
    }
  }

}
</script>
