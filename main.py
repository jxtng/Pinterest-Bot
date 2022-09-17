from py3pin.Pinterest import Pinterest
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor
from time import sleep, localtime
from functools import reduce
from random import random, shuffle, randint
import requests
import re
import json
import sys

from settings import *
from quillbot import QuillBot


class PinBoterest:
    def __init__(self, email, password, username):
        try:
            self.email = email
            self.password = password
            self.username  = username

            self.profile = Pinterest(email=self.email, password=self.password, username=self.username)

            self.domain = domain or 'http://wowu.shop'
            self.collection_link = all_collections_link or 'https://wowu.shop/collections/'
            self.domain_for_naming = self.domain.split('/')[-1]

            self.default_product_info= product_info
            self.default_product_link = product_link

            self.collections_selector = collections_link_selector or 'a[href*=collection]'
            self.products_selector = products_link_selector or 'a.grid-product__link'
            self.image_link_container_selector = product_image_link_container_selector or 'product__thumb-item'
            self.title_selector = product_title_selector or 'product-single__title'
            self.description_selector = product_description_selector or '[id*=content-description]'
            self.board_url_pos = board_name_position_in_url or -3

            self.no_of_pins = no_of_product_to_pin
            self.successful_pins = 0
            self.failed_pins = 0

            self.product_infos_file = f'data/product_infos_{self.domain_for_naming}'
            self.pinned_products_file = f'data/pinned_products_{self.domain_for_naming}'

            self.morning_start = daytime_range['morning'][0]
            self.morning_end = daytime_range['morning'][1]
            self.afternoon_start = daytime_range['afternoon'][0]
            self.afternoon_end = daytime_range['afternoon'][1]
            self.evening_start = daytime_range['evening'][0]
            self.evening_end = daytime_range['evening'][1]
            self.frequency = pinning_frequency

            # self.color_codes = {'e':'\033[0m', 'r':'\033[38;5;196m', 'b':'\033[38;5;27m', 'g':'\033[38;5;82m', 'y':'\033[38;5;221m', 'o':'\033[38;5;208m'}
            self.color_codes = {'e':'\033[0m', 'r':'\033[91m', 'b':'\033[94m', 'g':'\033[92m', 'y':'\033[93m', 'o':'\033[93m'}
        except:
            self.p('@o;Settings Error. Check your settings and try again...')

    def init(self):
        # Cool Effect
        self.p(f'@g;{"_-$-"*7} Initializing PinBoterest {"-$-_"*7}@e;\n\n', effect=True)

        # Get Product Infomations
        try:
            products = self.handle_products()
            self.p(f'@b;{len(products)} Products @g;and Infomations @b;Grabbed@g; Successfully.\n@e;')
        except:
            self.p('@r;Error Getting Product infos online. Might be your internet connection. Exiting...\n@e;')
            sleep(5), sys.exit()

        # Filter out already pinned pinterest products
        try:
            print('Filtering pinned products from unpinned ones...')
            with open(self.pinned_products_file, 'r') as file:
                pinned_products = file.read().split('\n')
            products = [p for p in products if f'Title: {p["title"]}, Image: {p["image"]}' not in pinned_products]
        except: pass
        finally: self.p(f'Filtering Done. @b;{len(products)} Products@e; left.\n')

        # Apply settings
        shuffle(products)
        products = products[:self.no_of_pins] if self.no_of_pins > 0 else products

        # Login Handling
        try:
            self.p('logging in to pinterest... \n\033[37m\033[47m')
            self.profile.login(suppress=True)
            self.p(f'@e;\n@g;Logged In Successfully to Username: @b;{self.username}@g; Email: @b;{self.email}@e;\n')
        except:
            self.p('@e;@r;Login Failed... Might be related to your Internet Connection. Exiting...@e;\n')
            sleep(5), sys.exit()

        # Paraphrasing and pinning
        qb = QuillBot()
        print('Setting up QuillBot Paraphraser')
        self.p(qb.init())

        self.p(f'@g;Creating @b;{self.no_of_pins} @g;pins...\n@e;')

        try:
            for i, product in enumerate(products):
                shuffled_desc = qb.handle_phrasing(product['description'], manual_description_shuffle)
                product['description'] = shuffled_desc['description']
                self.p(shuffled_desc['msg'])

                if self.handle_pin(product) and i < len(products)-1:
                    time_to_sleep = self.get_pinning_frequency()
                    self.p(f'Waiting/Sleeping for @b;{round(time_to_sleep/60, 3)} min(s) ==> {time_to_sleep} sec(s)@e;... Countdown: @b;@update; seconds@e;', countdown=time_to_sleep)
                    print('\n')
                else: sleep(3)
        except:
            self.p(f'\n@g;{"_-"*10} PinBoterest Suspended {"-_"*10}\n@e;', effect=True)

        # Done and dusted
        self.tried_pins = self.successful_pins + self.failed_pins
        self.p(f'@b;{self.tried_pins}@e; out of @b;{self.no_of_pins} {"@o;" if self.no_of_pins/2 > self.tried_pins else "@y;" if self.no_of_pins > self.tried_pins else "@g;"}requested pins gone through@e;')
        self.p(f'@b;{self.successful_pins} Pin(s) @g;Successfully done. @b;{self.failed_pins} Pin(s){"@r;" if self.failed_pins >= (self.tried_pins)/2 else "@o;" if self.failed_pins > (self.tried_pins)/2.75 else "@g;"} Unsuccessful@e;')
        try: self.p('Cleaning up stuff and Exiting...\n'), qb.done()
        except: pass

    def get_categories_from_site(self):
        soup = BeautifulSoup(requests.get(self.collection_link).text, 'html.parser')
        return [a['href'] for a in soup.select(self.collections_selector)]

    def get_products_from_category(self, cat_link):
        soup = BeautifulSoup(requests.get(self.domain + cat_link).text, 'html.parser')
        return [self.domain + a['href'] for a in soup.select(self.products_selector)]

    def get_infos_from_product(self, pro_link):
        soup = BeautifulSoup(requests.get(pro_link).text, 'html.parser')
        board = pro_link.split('/')[self.board_url_pos]
        images = ['https:' + img.a['href'] for img in soup.select(self.image_link_container_selector)]
        title = soup.select_one(self.title_selector).string.strip()
        description = reduce(lambda a,b: a+' '+b if len(a)<500 else a+'', soup.select_one(self.description_selector).stripped_strings)+'.'

        return [{'board': board, 'image': image, 'title': title, 'description': description, 'link': pro_link} for image in images]

    def produce_products(self):
        print('Grabbing Products and Infomations (will take some seconds)...')
        products = []
        try: cats = self.get_categories_from_site()
        except: raise Exception('@r;Failed to Categories from Site@e;')

        self.p(f'@b;{len(cats)} Categor(ies) @e;found. Grabbing products from categories...')
        try:
            with ThreadPoolExecutor(max_workers=50) as ex:
                products = ex.map(self.get_products_from_category, cats)
                products = [p for pros in products for p in pros]
        except:
            self.p('@y;Using loops to grab Products from Categories@e;')
            try: products = [product_link for cat in cats for product_link in self.get_products_from_category(cat)]
            except: raise Exception('@r;Failed to grab Products from Categories@e;')

        self.p(f'@b;{len(products)} Products(s) @e;grabbed from Categories. Expanding products and images...')
        try:
            with ThreadPoolExecutor(max_workers=50) as ex:
                products = ex.map(self.get_infos_from_product, products)
                products = [p for pros in products for p in pros]
        except:
            self.p('@y;Using loops to grab infomations from Products@e;')
            try: products = [info for product in products for info in self.get_infos_from_product(product)]
            except: raise Exception('@r;Failed to grab Products from Categories@e;')

        self.p(f'Products expanded to @b;{len(products)} Pinaable items@e;')
        return products

    def handle_products(self, count=3):
        with open(self.product_infos_file, 'a+') as file:
            try:
                file.seek(0)
                products = json.load(file)
                if not products: raise Exception('Empty Products found')
                print('Found stored products history. Grabbing Products and Infomation from file...')
            except:
                try: products = self.produce_products()
                except Exception as err:
                    self.p(err)
                    if count: print('Retrying...'), self.handle_products(count-1)
                    else: sys.exit('Retried 3 times. Exiting...')

                try:
                    file.seek(0), file.truncate()
                    json.dump(products, file)
                except: self.p('@y;Couldn\'t write products to history file. Continuing...')

        return products

    def handle_board(self, name):
        try:
            soup = BeautifulSoup(requests.get(f'http://pinterest.com/{self.username}/{name.strip().replace(" ", "-")}').text, 'html.parser')
            dict_data = json.loads(soup.body.find(id='__PWS_DATA__').string)
            return list(dict_data.get('props').get('initialReduxState').get('feeds').keys())[0].split(':')[-1]
        except:
            try:
                self.p(f'\nCreating board: @b;{name}...@e;')
                created_board = self.profile.create_board(name=name.replace('-', ' ').title())
                self.p(f'@g;Created board: @b;{created_board["resource_response"]["data"]["name"]} @g;successfully\n@e;')
                return created_board['resource_response']['data']['id']
            except:
                self.p(f'@r;Failed to create board @b;{name.title()}\n@e;')
                return False

    def handle_pin(self, product_info):
        try:
            board_id = self.handle_board(product_info['board'])
            self.p(f'Creating pin with Title: @b;{product_info["title"]} @e;to Board: @b;{product_info["board"]}@e;')
            created_pin = self.profile.pin(
            board_id=board_id,
            image_url=product_info['image'],
            title=product_info['title'],
            description=product_info['description'],
            link=product_info['link'])
            self.p(f'@g;Pin with Title: @b;{product_info["title"]} @g;in Board: @b;{product_info["board"]} \n@g;and Image: @b;{product_info["image"][:30]}... @g;Created Successfully\n@e;')
            self.successful_pins += 1
        except:
            try: self.p(f'@r;Failed to create Pin with Title: @b;{product_info["title"]} @r;to Board: @b;{product_info["board"]} \n@r;Image: @b;{product_info["image"][:30]}...\n@e;')
            except: self.p(f'@r;Failed to create Pin. Couldn\'t get right product info: @bProduct - {product_info}\n@e;')
            self.failed_pins += 1
            return False

        try:
            with open(self.pinned_products_file, 'a') as file:
                file.write(f'\nTitle: {product_info["title"]}, Image: {product_info["image"]}')
        except: self.p('@y;Problem writing pinned image to history file@e;')
        return created_pin

    def get_pinning_frequency(self):
        curr_hr = localtime().tm_hour

        if curr_hr >= self.morning_start and curr_hr <= self.morning_end:
            current_part_of_day = 'morning'

        elif curr_hr >= self.afternoon_start and curr_hr <= self.afternoon_end:
            current_part_of_day = 'afternoon'

        elif curr_hr >= self.afternoon_start and curr_hr <= self.evening_end:
            current_part_of_day = 'evening'

        else: current_part_of_day = 'night'

        return randint(*self.frequency[current_part_of_day])

    def p(self, value, sep=' ', end='\n', flush=False, effect=False, update=False, countdown=False):
        try: value = re.sub('@(.);', lambda match: self.color_codes.get(match.group(1)) or '@'+match.group(1)+';', value)
        except: pass

        if effect:
            for s in value:
                print(s, end='', flush=True)
                sleep(random()*.01+.02)
            return

        if update or countdown:
            count = countdown if countdown else len(value)
            while count:
                print('\r\033[K'+value.replace('@update;', str(count) if countdown else str(value[count-1])), end='')
                sleep(1)
                count -= 1
            return

        print(value, sep=sep, end=end, flush=flush)

if not __name__ == '__main__':
    pinterest = PinBoterest(email, password, username)
    try: pinterest.init()
    except: pinterest.p(f'@y;{"_^-^_-_"*3} Quiting {"_-_^-^_"*3}@e;', effect=True)