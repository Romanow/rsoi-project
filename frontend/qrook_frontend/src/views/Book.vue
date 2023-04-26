<template>
  <div>
    <div class="row" style="max-width: 100%">
      <b-card class="mb-3" style="width: 600px; margin-left: 30px; margin-top: 10px;" img-left>
        <b-row>
          <b-col>
            <img v-if="!skin_image" :src="require('@/assets/default_book.png')"
                 width="200px" height="300px"></img>
            <img v-if="skin_image" :src="skin_image" width="200px" height="300px"></img>
          </b-col>
          <b-col>
            <b-card-body :title="title">
              <b-card-text>

                <b-row v-if="book_order">
                  <span class="text-muted">номер книги в серии:&nbsp</span>
                  <span>{{ book_order }}</span>
                </b-row>
                <b-row v-if="series">
                  <img src="@/assets/series_link.png" width="25px" height="25px">
                  <router-link :to="'/series/' + series.id" class="bookLink">{{ series.title }}</router-link>
                </b-row>

                <b-row>
                  <div v-for="(author, i) of authors" style="clear: both;">
                    <div style="margin-right: 20px">
                      <img src="@/assets/pen_icon.png" width="25px">
                     <router-link :to="'/author/' + author.id" class="bookLink">{{ author.name  }}</router-link>
                    </div>
                  </div>
                </b-row>
              </b-card-text>
            </b-card-body>
          </b-col>
        </b-row>
      </b-card>

      <b-card class="mb-3" style="width: 600px; margin-left: 10px; margin-top: 10px;" img-left>
        <b-row>
          <b-col>
            <b-card-body title="Публикации">
              <b-dropdown text="Left align" variant="outline-primary" style="margin-bottom: 10px">
                <template #button-content>
                  {{ publ_dropdown_title }}
                  <country-flag :country=publ_dropdown_lang size='normal'/>
                </template>

                <div v-for="(pub, i) of publications">
                  <b-dropdown-item href="#" v-on:click=change_publication(i)>
                    {{ publ_repr(pub) }}
                    <country-flag :country=publ_lang(pub) size='normal'/>
                  </b-dropdown-item>
                </div>
              </b-dropdown>

              <div v-for="(info, i) of publ_info">
                <b-row>
                  <span class="text-muted">{{ i }}:&nbsp</span>
                  <span>{{ info }}</span>
                </b-row>
              </div>

              <div style="margin-bottom: 10px; margin-top: 20px">
                Скачать книгу:
              </div>
              <b-button-group>
                <div v-for="(file, i) of publ_files" style="margin-left: 10px">
                  <b-button
                    v-on:click=download(i)
                    variant="outline-primary">{{ file.file_type }}
                  </b-button>
                </div>
              </b-button-group>
              <div v-if="download_error" style="margin-bottom: 10px; margin-top: 20px; color: firebrick">
                {{ download_error }}
              </div>

            </b-card-body>
          </b-col>
        </b-row>
      </b-card>
    </div>


    <b-card style=" margin-left: 10px; max-width: 95%">
      <b-row>
        <b-card-body title="О книге">
          <b-card-text>
            <pre>{{ description }}</pre>
          </b-card-text>
        </b-card-body>
      </b-row>
    </b-card>
  </div>
</template>

<script>
import {log_event} from '@/services/scouting'
import CountryFlag from 'vue-country-flag'
import {library} from "@/services/repositories/library"
import {format_authors, language_to_country_code} from "@/services/formatting";

// todo нет публикаций, пустое описание, нет файлов
export default {
  name: "Book",
  data() {
    return {
      id: null,
      info: {},
      filters: {},
      publication: undefined,
      download_error: undefined
    }
  },

  components: {
    CountryFlag,
  },
  watch: {
    '$route.params.id': {
      handler: function (id) {
        this.load_data();
        this.download_error = undefined
      },
      deep: true,
      immediate: true
    }
  },

  computed: {
    book_order() {
      return this.info['book_order']
    },

    series() {
      let s = this.info['series']
      if (!s) return null

      if (s.title.length > 25)
        s.title = s.title.slice(0, 22) + '...';
      return s
    },

    publ_files() {
      if (!this.publication) return undefined
      return this.publication.files
    },

    publ_info() {
      if (!this.publication) return undefined
      let info = this.publication.info
      if (this.publication.isbn)
        info['ISBN'] = this.publication.isbn

      if (this.publication.isbn13)
        info['ISBN-13'] = this.publication.isbn13

      if (this.publication.publication_year)
        info['год публикации'] = this.publication.publication_year
      return info
    },

    publ_dropdown_title() {
      return this.publ_repr(this.publication)
    },

    publ_dropdown_lang() {
      return this.publ_lang(this.publication)
    },

    publications() {
      return this.info['publications']
    },

    authors() {
      return format_authors(this.info['authors'])
    },

    skin_image() {
      return this.info['skin_image']
    },

    title() {
      return this.info['title']
    },

    description() {
      let description = this.info['description']
      if (!description) return 'Информации о книге нет'
      return description
    }
  },

  methods: {
    change_publication(publ_num) {
      this.publication = this.publications[publ_num]
    },

    download(file_num) {
      let file = this.publication.files[file_num]

      let callback = (bookFile) => {
        if (!bookFile.ok) {
          console.log(bookFile)
          if (bookFile.status === 401)
            this.download_error = 'чтобы скачать книгу, необходимо авторизоваться'
          else
            this.download_error = 'файл недоступен'
          return
        }

        this.download_error = undefined
        const url = window.URL.createObjectURL(new Blob([bookFile.data]));
        const link = document.createElement("a");
        link.href = url;
        link.setAttribute("download", file.file_path); //or any other extension
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link)

        log_event('download_book', {book_id: this.id, file: file})
      }

      library.book_file(file, callback);
    },

    load_data() {
      this.id = this.$route.params.id

      let callback = (book) => {
        this.info = book
        this.publication = book.publications[0]
        log_event('view_book', {book_id: Number(this.id)})
      }

      library.book(this.id, callback);
    },

    publ_repr(publ) {
      if (!publ) return
      let s = this.title
      if (s.length > 25) {
        s = this.title.slice(0, 22) + '...'
      }
      return s + ' ' + publ['language_code']
    },

    publ_lang(publ) {
      if (!publ) return
      return language_to_country_code(publ['language_code'])
    },

  },
}
</script>
