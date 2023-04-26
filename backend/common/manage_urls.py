def parse_url(url: str, build_with: str):
    if not url: return url
    if url.startswith('http'): return url
    return build_with + url


def manage_urls(data: dict, file_service_url):
    for k in data.keys():
        if isinstance(data[k], dict):
            manage_urls(data[k], file_service_url)
        if data.get('type') == 'book':
            if data.get('skin_image') and not data['skin_image'].startswith('http'):
                data['skin_image'] = parse_url(data['skin_image'], file_service_url + 'api/v2/images/books/')
        if data.get('type') == 'series':
            if data.get('skin_image') and not data['skin_image'].startswith('http'):
                data['skin_image'] = parse_url(data['skin_image'], file_service_url + 'api/v2/images/series/')
        if data.get('type') == 'author':
            if data.get('photo') and not data['photo'].startswith('http'):
                data['photo'] = parse_url(data['photo'], file_service_url + 'api/v2/images/authors/')
