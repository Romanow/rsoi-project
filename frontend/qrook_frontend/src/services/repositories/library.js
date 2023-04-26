import {HTTP} from '@/services/http'
import {HttpResponse} from './common'

class Author extends HttpResponse {
  constructor(ok, data) {
    super(ok);
    if (!data) return;

    this.id = data.id;
    this.description = data.description;
    this.name = data.name;
    this.photo = data.photo;
    this.birthdate = data.birthdate;
    this.country = data.country;
    this.sex = data.sex;
  }
}

class Series extends HttpResponse {
  constructor(ok, data) {
    super(ok);
    if (!data) return;

    this.id = data.id;
    this.description = data.description;
    this.title = data.title;
    this.skin_image = data.skin_image;
    this.is_finished = data.is_finished;
    this.books_count = data.books_count;
    this.authors = data.authors;
  }
}

class Book extends HttpResponse {
  constructor(ok, data) {
    super(ok);
    if (!data) return;

    this.id = data.id;
    this.description = data.description;
    this.title = data.title;
    this.skin_image = data.skin_image;
    this.genres = data.is_finished;
    this.series = data.series;
    this.authors = data.authors;
    this.publications = data.publications;
    this.book_order = data.book_order;
  }
}

class BookFile extends HttpResponse {
  constructor(ok, status, data) {
    super(ok);
    this.status = status;
    if (!data) return;

    this.data = data;
  }
}

class LibraryCollection extends HttpResponse {
  constructor(ok, data) {
    super(ok);
    if (!data) return;

    this.items = data;
  }
}


class Library {
    book(id, callback) {
      let http_callback = (response) => {
          callback(new Book(true, response.data))
        };
      let http_err_callback = (error) => {
          console.log(error.message);
          callback(new Book(false, null))
        }
      HTTP.get('books/' + id, {params: {}}).then(http_callback).catch(http_err_callback);
    }

    author(id, callback) {
      let http_callback = (response) => {
          callback(new Author(true, response.data))
        };
      let http_err_callback = (error) => {
          console.log(error.message);
          callback(new Author(false, null))
        }
      HTTP.get('authors/' + id, {params: {}}).then(http_callback).catch(http_err_callback);
    }

    series(id, callback) {
      let http_callback = (response) => {
          callback(new Series(true, response.data))
        };
      let http_err_callback = (error) => {
          console.log(error.message);
          callback(new Series(false, null))
        }
      HTTP.get('series/' + id, {params: {}}).then(http_callback).catch(http_err_callback);
    }

    book_file(file, callback) {
      let http_callback = (response) => {
          callback(new BookFile(true, response.status, response.data))
      };
      let http_err_callback = (error) => {
          console.log(error.message);
          callback(new BookFile(false, error.response.status, null))
      }

      let path = 'books/files/' + file.file_path
      HTTP.get(path, {responseType: "blob"}).then(http_callback).catch(http_err_callback);
    }

    recent_viewed(params, callback) {
      let http_callback = (response) => {
          callback(new LibraryCollection(true, response.data))
      };
      let http_err_callback = (error) => {
          console.log(error.message);
          callback(new LibraryCollection(false, null))
      }

      HTTP.get('users/recent_viewed', {params: params}).then(http_callback).catch(http_err_callback);
    }

    library(params, callback) {
      let http_callback = (response) => {
          callback(new LibraryCollection(true, response.data))
      };
      let http_err_callback = (error) => {
          console.log(error.message);
          callback(new LibraryCollection(false, null))
      }

      HTTP.get('library', {params: params}).then(http_callback).catch(http_err_callback);
    }
}

export let library = new Library()
