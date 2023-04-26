<template>
  <div>
    <BookPreview
      v-if="item_type === 'book'"
      v-bind:info=info>
    </BookPreview>
    <AuthorPreview
      v-if="item_type === 'author'"
      v-bind:info=info>
    </AuthorPreview>
    <SeriesPreview
      v-if="item_type === 'series'"
      v-bind:info=info>
    </SeriesPreview>
  </div>
</template>

<script>
import BookPreview from "@/components/BookPreview.vue";
import AuthorPreview from "@/components/AuthorPreview.vue";
import SeriesPreview from "@/components/SeriesPreview.vue";

export default {
  name: "ItemPreview",
  props: ['info'],

  computed: {
    item_type() {
      return this.info['type']
    }
  },

  components: {
    BookPreview,
    AuthorPreview,
    SeriesPreview
  },
}
</script>

