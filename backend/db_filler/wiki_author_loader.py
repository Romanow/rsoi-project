import requests
from bs4 import BeautifulSoup
import datetime
from urllib.parse import unquote

months_samples = '. январ февр март апрел ма июн июл август сентябр октябр ноябр декабр'

author_selectors = {
    'name': '.infobox > tbody:nth-child(1) > tr:nth-child(4) > td:nth-child(2) > span:nth-child(1)',
    'year': '.infobox > tbody:nth-child(1) > tr:nth-child(5) > td:nth-child(2) > span:nth-child(1) > span:nth-child(1) > span:nth-child(1) > a:nth-child(2)',
    'day_month': '.infobox > tbody:nth-child(1) > tr:nth-child(5) > td:nth-child(2) > span:nth-child(1) > span:nth-child(1) > span:nth-child(1) > a:nth-child(1)',
    'description': '.mw-parser-output > p:nth-child(3)',
    'country': '.country-name > span:nth-child(1) > a:nth-child(1)',
    'photo1': '.infobox-image > span:nth-child(1) > span:nth-child(1) > a:nth-child(1) > img:nth-child(1)',
    'photo2': '.infobox-image > span:nth-child(1) > a:nth-child(1) > img:nth-child(1)'
}

author_clear_type = {
    'name': 'tag',
    'year': 'tag',
    'day_month': 'tag',
    'description': 'text',
    'country': 'text',
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

def parse_date(year, day_month):
    try:
        day, month = day_month.split(' ')
        month_num = -1
        for i in range(len(months_samples)):
            if months_samples[i] in month:
                month_num = i
                break
        return datetime.date(int(year), month_num, int(day))
    except:
        return None


def find_google_url(search):
    text = search + ' википедия'
    url = 'https://google.com/search?q=' + text
    contents = requests.get(url).text
    l = contents.find('wikipedia')
    r = contents[l:].find('&')
    new_url = contents[l-11: l+r]
    new_url = unquote(new_url)
    return new_url

    '''
    url = 'https://yandex.ru/search/?text=%s' % (search + ' википедия')
    contents = requests.get(url).text
    soup = BeautifulSoup(contents, 'lxml')
    selector = 'li.serp-item:nth-child(3)'
    x = soup.findAll('h2')
    try:
        return x[0].find('a')['href']
    except:
        return None'''

def parse_author(name):
    original_name = name
    name = name.split(' ')
    if len(name) < 2:
        return {'name': original_name}

    url = find_google_url(name[0] + ' ' + name[1])
    if url is None:
        url = 'https://ru.wikipedia.org/wiki/%s,_%s' % (name[0], name[1])
        print('google url not found')

    contents = requests.get(url).text
    soup = BeautifulSoup(contents, 'lxml')
    data = {}
    for name, selector in author_selectors.items():
        x = soup.select(selector)
        if len(x) == 0: continue
        data[name] = clear_data(x[0], author_clear_type[name])

    if data.get('year') and data.get('day_month'):
        data['bdate'] = parse_date(data['year'], data['day_month'])
    data['name'] = original_name

    if data.get('year'): data.pop('year')
    if data.get('day_month'): data.pop('day_month')
    if data.get('photo1'):
        data['photo'] = data['photo1']
        data.pop('photo1')
    if data.get('photo2'):
        data['photo'] = data['photo2']
        data.pop('photo2')

    print(original_name, ':success, extracted', len(data), 'fields:', list(data.keys()))
    return data


if __name__ == '__main__':
    data = parse_author('Гюго Виктор')
    for k, v in data.items():
        print(k, '=', v)
