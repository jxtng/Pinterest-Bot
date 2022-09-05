def get_all_products_v2(collection_page='https://wowu.shop/search?q=*'):
    params, all_links = {'page': 1, 'q': '*'}, []
    while True:
        soup = BeautifulSoup(requests.get(collection_page, params=params).text, 'html.parser')
        links = ['https://wowu.shop'+a['href'].split('?')[0] for a in soup.find_all('a', class_='grid-product__link')]
        all_links.extend(links)
        if len(links) <= 0: break
        params['page'] += 1