import requests
from bs4 import BeautifulSoup
import datetime
from urllib.parse import unquote

months_samples = '. январ февр март апрел ма июн июл август сентябр октябр ноябр декабр'

author_selectors = {
    'name': '.infobox > tbody:nth-child(1) > tr:nth-child(4) > td:nth-child(2) > span:nth-child(1)',
    'description': '.mw-parser-output > p:nth-child(3)',
    'photo1': '.infobox-image > span:nth-child(1) > span:nth-child(1) > a:nth-child(1) > img:nth-child(1)',
    'photo2': '.infobox-image > span:nth-child(1) > a:nth-child(1) > img:nth-child(1)'
}

author_clear_type = {
    'name': 'tag',
    'description': 'text',
    'photo1': 'image',
    'photo2': 'image',
}


def clear_data(s, type):
    if type == 'tag':
        return s.string
    elif type == 'text':
        return s.text
    elif type == 'image':
        return s['src'][2:]
    else:
        return s



def find_google_url(search):
    text = search + ' серия книг википедия'
    url = 'https://google.com/search?q=' + text
    contents = requests.get(url).text
    l = contents.find('wikipedia')
    r = contents[l:].find('&')
    new_url = contents[l - 11: l + r]
    new_url = unquote(new_url)
    return new_url


def parse_series(name):
    original_name = name
    url = find_google_url(name)
    if url is None:
        print('google url not found')
        return {'name': original_name}


    contents = requests.get(url).text
    soup = BeautifulSoup(contents, 'lxml')
    data = {}
    for name, selector in author_selectors.items():
        x = soup.select(selector)
        if len(x) == 0: continue
        data[name] = clear_data(x[0], author_clear_type[name])


    data['name'] = original_name
    if data.get('photo1'):
        data['skin_image'] = data['photo1']
        data.pop('photo1')
    if data.get('photo2'):
        data['skin_image'] = data['photo2']
        data.pop('photo2')

    print(original_name, ':success, extracted', len(data), 'fields:', list(data.keys()))
    return data


if __name__ == '__main__':
    data = parse_author('Гюго Виктор')
    for k, v in data.items():
        print(k, '=', v)
