<template>
  <div>
    <b-sidebar id="filter-sidebar" ref="dropdown" title="Параметры поиска"
               shadow v-on:hidden="my_hide">
      <button pill v-on:click="bookToggle = !bookToggle"
              v-bind:class="{'btn-primary': bookToggle, 'btn-outline-primary': !bookToggle}"
              class="toggleFilterButton btn">Книги
      </button>

      <button v-on:click="seriesToggle = !seriesToggle"
              v-bind:class="{'btn-primary': seriesToggle, 'btn-outline-primary': !seriesToggle}"
              class="toggleFilterButton btn">Серии
      </button>

      <button v-on:click="authorToggle = !authorToggle"
              v-bind:class="{'btn-primary': authorToggle, 'btn-outline-primary': !authorToggle}"
              class="toggleFilterButton btn">Авторы
      </button>

      <b-form-input v-model="search" placeholder="Поиск" v-on:input="search_update" @keyup.enter="enterClicked"
                    style="max-width:280px; margin-left: 20px; margin-bottom: 20px"></b-form-input>

      <div class="px-3 py-2" style="text-align: left">
        <div class="filter_tag"><b>Язык:</b></div>
        <b-form-select v-model="language.selected" :options="language.options" class="filter_form"></b-form-select>

        <div class="filter_tag"><b>Формат файла:</b></div>
        <b-form-select v-model="file_format.selected" :options="file_format.options"
                       class="filter_form"></b-form-select>

        <div class="filter_tag"><b>Сортировать по:</b></div>
        <b-form-select v-model="sort.selected" :options="sort.options"
                       class="filter_form"></b-form-select>

        <div>
          <label class="filter_tag"><b>Жанры</b></label>
          <multiselect v-model="genres.selected" placeholder="Выберите жанры книг"
                       :options="genres.options" :multiple="true" :taggable="true"
                       @tag="addTag" class="filter_form"
                       selectLabel="добавить" deselectLabel="удалить" selectedLabel=""></multiselect>


        </div>

        <b-button v-on:click="searchCall" v-b-toggle.filter-sidebar ref="filters_search_btn">Найти</b-button>
        <div>
          <a v-on:click="clearFilters" style="color:black; cursor: pointer;">очистить фильтры</a>
        </div>
      </div>
    </b-sidebar>
  </div>
</template>

<script>
import Multiselect from 'vue-multiselect';
import { log_event } from '@/services/scouting';

export default {
  name: 'FilterSidebar',

  data() {
    return {
      toggler: 0,
      search: '',
      bookToggle: true,
      seriesToggle: true,
      authorToggle: true,
      language: {
        selected: null,
        options: [
          { value: null, text: 'Любой' },
          { value: 'ru', text: 'Русский' },
          { value: 'en', text: 'Английский' },
          // {value: 'other', text: 'Другое'},
        ],
      },
      file_format: {
        selected: null,
        options: [
          { value: null, text: 'Любой' },
          { value: 'fb2', text: 'fb2' },
          { value: 'zip', text: 'zip' },
          { value: 'epub', text: 'epub' },
          // todo manage other filters {value: 'other', text: 'Другое'},
        ],
      },
      sort: {
        selected: 'date_desc',
        options: [
          { value: 'date_desc', text: 'По дате добавления - сначала новые' },
          { value: 'name_acc', text: 'По названию (имени) - а..я' },
          { value: 'name_desc', text: 'По названию (имени) - я..а' },
          { value: 'date_acc', text: 'По дате добавления - сначала старые' },
        ],
      },

      genres: {
        selected: null,
        options: [
          'приключения',
          'фэнтези', 'фантастика',
          'юмор', 'романы',
          'детектив', 'поэзия', 'наука',
        ],
      },
    };
  },


  created() {
    this.$parent.$on('clear_filters', this.clearFilters);
    this.$parent.$on('receive_search', (s) => {
      this.search = s;
    });
    document.addEventListener('click', this.clicked);
    this.applyFilters();
  },

  destroyed() {
    document.removeEventListener('click', this.clicked);
  },

  components: {
    Multiselect,
  },

  methods: {
    searchCall() {
      const filters = this.applyFilters();
      log_event('using_filters', { filters });

      setTimeout(() => {
        this.$refs.dropdown.hide(true);
        this.my_hide();
      }, 100);
      this.$router.push('/main').catch(()=>{})
    },
    enterClicked() {
      this.$refs.filters_search_btn.click();
    },

    search_update(s) {
      this.$emit('set_search', s);
    },
    my_hide(e) {
      this.toggler = 0;
    },

    clicked(e) {
      if (!this.$refs.dropdown.isOpen) return;
      this.toggler += 1;
      if (this.toggler === 1) return;

      const el = document.getElementById('filter-sidebar');
      const target = e.target;

      if (el !== target && !el.contains(target)) {
        this.$refs.dropdown.hide(true);
        this.my_hide();
      }
    },

    addTag(newTag) {
      const tag = newTag;
      this.genres.options.push(tag);
      this.genres.selected.push(tag);
    },

    clearFilters() {
      this.bookToggle = true;
      this.seriesToggle = true;
      this.authorToggle = true;
      this.language.selected = null;
      this.file_format.selected = null;
      this.sort.selected = 'date_desc';
      this.genres.selected = null;
      this.search = '';
      this.applyFilters();
    },

    applyFilters() {
      let gen_list = null;
      if (this.genres.selected) {
        gen_list = this.genres.selected.join(';');
      }

      const filters = {
        find_book: this.bookToggle,
        find_series: this.seriesToggle,
        find_author: this.authorToggle,
        language: this.language.selected,
        format: this.file_format.selected,
        sort: this.sort.selected,
        genres: gen_list,
        search: this.search,
      };

      for (const key in filters) {
        if (filters[key] === null) { delete filters[key]; }
      }

      this.$store.dispatch('filters/set_filters', filters)
      return filters;
    },
  },
};
</script>

<style src="vue-multiselect/dist/vue-multiselect.min.css"></style>
<style scoped>
.filter_tag {
  margin-bottom: 5px
}

.filter_form {
  margin-bottom: 20px
}

.toggleFilterButton {
  margin: 10px;
}
</style>
