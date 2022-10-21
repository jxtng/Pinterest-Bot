from functools import reduce
from bs4 import BeautifulSoup
import requests
import re
import os
import json

class ShopifyStore:
    def __init__(self, hostname, title_sel = None, desc_sel = None, ia_sel = None,
    min_image_res = 600,):
        self.hostname = f'{"" if re.match("http[s]?://", hostname) else "https://"}{hostname}{"" if hostname[-1] == "/" else "/"}'
        self.categories = set()
        self.css_t = title_sel or 'h1, .title'
        self.css_d = desc_sel or '*[id*=escription], *[class*=escription]'
        self.css_ia = ia_sel or 'main > *:first-child'
        self.min_image_res = min_image_res or 600
        self.storage_file = 'data/products__' + re.sub('(http[s]?:\/\/)?(.+?)\/*', '\\2', hostname)

    def collection_pages(self, query=''):
        result, max_page_count, page = set(), 15, 2
        soup = BeautifulSoup(requests.get(f'{self.hostname}/collections?{query}').text, 'html.parser')
        links = soup.find_all('a', href=re.compile('/collections'))

        result.update([link.get('href') for link in links if '?' not in str(link.get('href'))])

        while max_page_count and not query:
            old_length = len(result)
            result.update(self.collection_pages(f'page={page}'))
            if old_length == len(result): break
            max_page_count, page = max_page_count-1, page+1

        return list(result)

    def product_pages(self, collection, query=''):
        result, max_page_count, page = set(), 15, 2
        soup = BeautifulSoup(requests.get(self.hostname+collection).text, 'html.parser')
        links = soup.find_all('a', href=re.compile(f'{collection}.+'))

        result.update([link.get('href') for link in links if '?' not in str(link.get('href'))])

        while max_page_count and not query:
            old_length = len(result)
            result.update(self.product_pages(collection, f'page={page}'))
            if old_length == len(result): break
            max_page_count, page = max_page_count-1, page+1

        return result

    def process_infos(self, product):
        result = []
        soup = BeautifulSoup(requests.get(self.hostname+product).text, 'html.parser')
        categories = product.split('collections/')[-1].split('/')[:-1]
        categories = [cat for cat in categories if cat != 'products']
        
        title = soup.select_one(self.css_t)
        if title: title = title.text.replace('\n', ' ')
        else: raise Exception('TITLE NOT FOUND - Check your settings')

        description = soup.select_one(self.css_d)
        if description:
            description = ' '.join(description.stripped_strings).split('. ')
            description = reduce(lambda a,b: a+'. '+b if len(a) < 497 else a+'', description) + '...'
        else: raise Exception('DESCRIPTION NOT FOUND - Check your settings')

        image_area = BeautifulSoup(str(soup.select_one(self.css_ia if self.css_ia else 'body')), 'html.parser')
        images = [image['src'] for image in image_area.select('img') if image.get('src') and 'product' in image['src'] and re.search('_(\d+?)x', image['src']) and int(re.search('_(\d+?)x', image['src']).group(1)) >= self.min_image_res]
        
        if not images: raise Exception('IMAGES NOT FOUND - Check your settings')
        [result.append({'category': category, 'title': title, 'description': description, 'image': image, 'link': self.hostname+product}) for image in images for category in categories
        
        if {'category': category, 'title': title, 'description': description, 'image': image, 'link': self.hostname+product} not in result
        ]
        return result
        

    def process_products(self):
        print('Getting Products and Infomations (will take some seconds)...')
        try: collections = self.collection_pages()
        except: raise Exception(f'@r;Failed to Get Categories from Site: @b;{self.hostname}@e;')

        print(f'{len(collections)} Categor(ies) found. Getting products from categories...')

        products = set()
        for col in collections:
            try: products.update(self.product_pages(col)), print(f'\rProducts gotten == {len(products)}', end='')
            except Exception as err: print(f'\nCouldn\'t extract products from {col} - {err}')

        print(f'\n{len(products)} Products(s) grabbed from Categories. Expanding products and images...')

        infos = []
        for product in products:
            try: infos.extend(self.process_infos(product)), print(f'\rProducts Info gotten == {len(infos)}', end='')
            except Exception as err: print(f'\nCouldn\'t extract information from {product} - {err}')

        if not products: raise Exception('\n@o;No Products Gotten, Check your configuration and settings@e;')
        return infos

    def products(self):
        if os.path.exists(self.storage_file):
            print('Getting information from stored products file...')
            with open(self.storage_file, 'r') as file:
                try: return json.load(file)
                except: print('Couldn\'t read/parse stored files, fetching products from from store')
        
        else: print('No stored files found..., fetching products from store')

        try: 
            products = self.process_products()
            print(f'\n{len(products)} Product(s) Information gotten✅')
        except Exception as err: raise Exception(err) 
        
        with open(self.storage_file, 'w') as file:
            try:
                json.dump(products, file)
                print('Stored Products To File Successfully✅\n')
            except Exception as err: print('Minimal Error storing products from store: {self.hostname} - {str(err)}❌\n')
            return products