<template>
  <div>
    <VirtualCollection
      id="virt-coll"
      v-if="have_data"
      :cellSizeAndPositionGetter="cellSizeAndPositionGetter"
      :collection="items"
      :height="height"
      :width="width"
      v-on:scrolled-to-bottom-range="upload_data"
      :scrollToBottomRange="1000"
      >
      <div slot="cell" slot-scope="props">
        <ItemPreview
          v-bind:info=props.data>
        </ItemPreview>
      </div>
    </VirtualCollection>
    <div v-if="!have_data" style="margin-top: 50px">
      Информация по запросу не найдена
    </div>
  </div>
</template>


<script>
import ItemPreview from "@/components/ItemPreview.vue";
import {HTTP} from '@/services/http'
import {log_event} from '@/services/scouting'
import {library} from "@/services/repositories/library";

export default {
  data() {
    return {
      offset: 0,
      limit: 100,
      all_read: false,

      width: window.innerWidth,
      height: document.documentElement.clientHeight - 76,
      items: [],
      failed: false,

      place_data: {
        per_row: null,
        item_width: null,
        item_height: null,
        x_first: null,
        x_space: null,
        y_first: null,
        y_space: null
      }
    }
  },

  created() {
    window.addEventListener('resize', this.updateMainSize);
    this.upload_data()
    setTimeout(() => {  this.updateMainSize() }, 300);
  },

    watch: {
    filters: {
      handler: function (id) {
        this.offset = 0
        this.all_read = false
        this.items = []
        this.upload_data()
      },
      deep: true,
      immediate: true
    }
  },

  computed: {
    have_data() {
      return this.items.length > 0
    }
  },

  methods: {
    upload_data() {
      if (this.all_read) {
        return
      }

      let params = {offset: this.offset, limit: this.limit}

      let callback = (collection) => {
        this.failed = !collection.ok
        if (this.failed)
          return

        let items = collection.items
        for (let i = 0; i < items.length; ++i) {
          items[i] = {data: items[i]}
        }

        this.all_read = items.length === 0
        this.items.push.apply(this.items, items)
        this.$forceUpdate();
      }

      if (this.filters['ready'] === true) {
        callback(this.filters['collection'])
      }
      else if (this.filters['recent_viewed'] === true) {
        library.recent_viewed(params, callback);
      } else {
        params = Object.assign({}, params, this.filters);
        library.library(params, callback);
      }
      this.offset += this.limit
      this.$forceUpdate();
    },

    define_place_params(item) {
      this.place_data.item_height = 300
      this.place_data.item_width = 200

      let width = this.place_data.item_width
      this.place_data.per_row = Math.floor(this.width / (width * 1.1))
      this.place_data.x_first = 10
      this.place_data.x_space = (this.width * 0.98 - 2 * this.place_data.x_first - this.place_data.per_row * width) / (this.place_data.per_row - 1)
      this.place_data.y_first = 10
      this.place_data.y_space = 10
    },

    cellSizeAndPositionGetter(item, index) {
      if (this.place_data.per_row === null) {
        this.define_place_params(item)
      }
      let width = this.place_data.item_width
      let height = this.place_data.item_height
      let per_row = this.place_data.per_row
      let x_first = this.place_data.x_first
      let y_first = this.place_data.y_first
      let x_space = this.place_data.x_space
      let y_space = this.place_data.y_space
      return {
        width: width,
        height: height,
        x: x_first + (index % per_row) * (width + x_space),
        y: y_first + Math.floor(index / per_row) * (height + y_space)
      }
    },

    updateMainSize() {
      let el = document.getElementById("virt-coll")
      if (!el) {
        return
      }

      this.width = window.innerWidth
      this.height = document.documentElement.clientHeight - 76
      this.place_data.per_row = null
      this.$forceUpdate();
    }
  },

  components: {
    ItemPreview
  },

  props: ['filters']
}
</script>
