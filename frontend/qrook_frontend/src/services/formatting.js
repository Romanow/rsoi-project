export function language_to_country_code(code) {
    switch (code) {
      case 'ru':
        return 'ru'
      case 'en':
        return 'gb'
      case 'de':
        return 'de'
    }
}

export function format_authors(authors) {
    // todo add '...' if there are more authors than possible to show
    let data = []
    if (!authors) {
      return []
    }
    for (let a of authors) {
      a = {id: a.id, name: format_author_name(a['name'])}
      if (a.name.length > 25) {
        a.name = a.name.slice(0, 22) + '...'
      }
      data.push(a)
    }
    return data
}

export function format_author_name(a) {
    if (a.length > 20) {
      a = a.split(' ')
      for (let x of a.slice(1)) {
        if (x === '') continue
        a[0] += ' ' + x[0] + '.'
      }
      a = a[0]
    }
    return a
}

export function format_preview_authors(authors, max_cnt) {
    let data = []
    for (let a of authors.slice(0, max_cnt)) {
      a = {id: a.id, name: format_author_name(a['name'])}
      data.push(a)
    }
    return data
}
