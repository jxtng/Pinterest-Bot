from py3pin.Pinterest import Pinterest, BOARDS_RESOURCE, CREATE_BOARD_RESOURCE
from webdriver_manager.chrome import ChromeDriverManager
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as WebDriverOptions
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

from time import localtime, sleep, perf_counter
from random import randint, random, shuffle
from math import trunc
import re
import sys
import subprocess as cli
import os

from settings import *
from store import ShopifyStore
from quillbot import QuillBot

class Bot(Pinterest):
    def __init__(self):
        super().__init__(email=email, password=password, username=username)
        os.chdir(os.path.dirname(__file__))
        try:
            self.website = website

            self.existing_boards = []
            self.no_of_pins = no_of_pin_per_day
            self.successful_pins = 0
            self.failed_pins = 0
            self.failed_delta = 0

            self.morning_start = daytime_range['morning'][0]
            self.morning_end = daytime_range['morning'][1]
            self.afternoon_start = daytime_range['afternoon'][0]
            self.afternoon_end = daytime_range['afternoon'][1]
            self.evening_start = daytime_range['evening'][0]
            self.evening_end = daytime_range['evening'][1]
            self.frequency = pinning_frequency
            self.redirect_to_waiter = False

            self.pinned_history_file = 'data/pinned_history__'+self.email

            self.color_codes = {'e':'\033[0m', 'r':'\033[91m', 'b':'\033[94m', 'g':'\033[92m', 'y':'\033[93m', 'o':'\033[93m'}
        except NameError as err:
            self.p(f'@o;Settings Error - {err}. Check your settings.py and try again.')
            sys.exit('Exiting...')

    def start(self):
        self.p(f'@g;{"_-$-"*7} Initializing Bot {"-$-_"*7}@e;\n\n', effect=True)

        # Get Product Infomations
        store = ShopifyStore(self.website, title_selector, description_selector, image_area_selector, min_image_res)
        products = store.products()

        # Filter out already pinned pinterest products
        try:
            print('Filtering pinned products from unpinned ones...')
            with open(self.pinned_history_file, 'r') as file:
                pinned_products = file.read().split('\n')
            products = [p for p in products if f'Title: {p["title"]}, Image: {p["image"]}, Category: {p["category"]}' not in pinned_products]
        except: pass
        finally: self.p(f'Filtering Done. @b;{len(products)} Products@e; left.\n')

        # Apply product settings
        shuffle(products)
        products = products[:self.no_of_pins] if self.no_of_pins > 0 else products

        # Login Handling
        self.handle_login()

        # Paraphrasing and pinning
        qb = QuillBot()
        print('\nSetting up QuillBot Paraphraser...')
        self.p(qb.init())

        self.p(f'@g;Creating @b;{self.no_of_pins} @g;pins...\n@e;')
        start_time = perf_counter()
        try: 
            for product in products:
                if perf_counter()-start_time > 86400:
                    # Take a break
                    print('24hr has passed, taking a break. Redirecting to Waiter...')
                    self.redirect_to_waiter = True
                    break

                shuffled_desc = qb.paraphrase(product['description'], manual_description_shuffle)
                product['description'] = shuffled_desc['description']
                self.p(shuffled_desc['msg']+'\n')

                if self.failed_delta == 3: self.flush_dns()
                if self.failed_delta == 4: self.handle_login()

                if self.handle_pin(product) and self.successful_pins+self.failed_pins < len(products):
                    time_to_sleep = self.get_pinning_frequency()
                    self.p(f'Waiting/Sleeping for @b;{round(time_to_sleep/60, 3)} min(s) ==> {time_to_sleep} sec(s)@e;... Countdown: @b;@update; seconds@e;', countdown=time_to_sleep)
                    print('\n')
                else: sleep(3)

        except Exception as err: 
            self.p(f'\n@y;{"_-"*10} Bot Suspended {"-_"*10}\n@e;', effect=True)
            print(err)

        self.tried_pins = self.successful_pins + self.failed_pins
        self.p(f'@b;{self.tried_pins}@e; out of @b;{self.no_of_pins} {"@o;" if self.no_of_pins/2 > self.tried_pins else "@y;" if self.no_of_pins > self.tried_pins else "@g;"}requested pins gone through@e;')
        self.p(f'@b;{self.successful_pins} Pin(s) @g;Successfully done. @b;{self.failed_pins} Pin(s){"@r;" if self.failed_pins >= (self.tried_pins)/2 else "@o;" if self.failed_pins > (self.tried_pins)/2.75 else "@g;"} Unsuccessful@e;')
        
        runtime = int(perf_counter() - start_time)
        remaining_time = 86400 - runtime
        
        if remaining_time > 0 or self.redirect_to_waiter:
            try: 
                self.p(f'\nCleaning up stuff and Waiting for day to pass. \nRemaining time: @b;{trunc(remaining_time/3600)}hrs: {round(remaining_time/60%60)}mins@e;. Use ^C(Ctrl+C) to stop timer and resume pinning.')
                qb.done()
                self.p(f'Countdown in secs: @b;@update;@e;', countdown=remaining_time)
                self.__init__()
                self.start()
            except KeyboardInterrupt as err: 
                print('\nResuming Bot...')
                self.__init__()
                self.start()
            except: print('Key not pressed. Exiting...')

    def flush_dns(self):
        if os.name == 'nt': dns_flush = cli.run('ipconfig /flushdns', capture_output=True)
        print('Flushed DNS Successfully') if dns_flush.stdout else print('Unable to flush DNS')

    def handle_login(self):
        self.p('Logging in to Pinterest...\033[47m')
        chrome_options = WebDriverOptions()
        chrome_options.add_argument("--lang=en")
        chrome_options.add_argument("--headless")
        chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])

        try:
            driver = webdriver.Chrome(ChromeDriverManager().install(), options=chrome_options)
            driver.get("https://pinterest.com/login")

            try:
                WebDriverWait(driver, timeout=15).until( EC.element_to_be_clickable((By.ID, "email")) )
                driver.find_element(by=By.ID, value="email").send_keys(self.email)
                driver.find_element(by=By.ID, value="password").send_keys(self.password)

                logins = driver.find_elements(by=By.XPATH, value="//*[contains(text(), 'Log in')]")
                for login in logins:
                    login.click()

                WebDriverWait(driver, timeout=15).until( EC.invisibility_of_element((By.ID, "email")) )

                cookies = driver.get_cookies()
                self.http.cookies.clear()
                for cookie in cookies:
                    self.http.cookies.set(cookie["name"], cookie["value"])

                self.registry.update_all(self.http.cookies.get_dict())
            except Exception as err:
                driver.close()
                return self.p(f'\033[0m@r;Failed to login - {err}. Continuing@e;')
        except ConnectionError:
            return self.p(f'\033[0m@r;Failed to login - {err}. Check your internet connection@e;')
        
        self.p(f"\033[0m@g;Successfully logged in to account {self.email}@e;")
        driver.close()

    def handle_board(self, board, runtime=1):
        if not board: return ''
        if not self.existing_boards or not runtime:
            options = {
                "privacy_filter": "all",
                "sort": "custom",
                "username": self.username,
                "isPrefetch": False,
                "include_archived": True,
                "field_set_key": "profile_grid_item",
                "group_by": "visibility",
                "redux_normalize_feed": True,
            }
            try:
                url = self.req_builder.buildGet(url=BOARDS_RESOURCE, options=options, source_url=f"/{self.username}/boards/")
                boards_info = self.get(url=url).json()
                self.existing_boards = {board.get('name').lower():board.get('id') for board in boards_info["resource_response"]["data"]}
            except Exception as err: self.p(f'@o;Couldn\'t get exisiting boards - {err}@e;')
        
        board = board.replace('-', ' ').lower()
        if board in self.existing_boards: return self.existing_boards.get(board)
        else:
            self.p(f'Creating Board: @b;{board.title()}@e;')
            options = {
            "name": board.title(),
            "description": '',
            "category": 'other',
            "privacy": 'public',
            "layout": 'default',
            "collab_board_email": "true",
            "collaborator_invites_enabled": "true",
            }
            data = self.req_builder.buildPost(options=options, source_url=f"/{self.email}/boards/")
            try:
                created_board = self.post(url=CREATE_BOARD_RESOURCE, data=data)
                self.p(f'@g;Created board @b;{board.title()}@g; Successfully@e;\n')
                return created_board.json()['resource_response']['data']['id']
            except Exception as err: 
                if runtime: return self.handle_board(board, runtime-1)
                self.p(f'@r;Error creating board @b;{board.title()}@r; - {err} @e;\n')
    
    def handle_pin(self, info):
        board_id = self.handle_board(info.get('category'))

        if not info.get('title'): return self.p('@y;Couldn\'t find Product TITLE. skipping...@e;')
        if not info.get('description'): return self.p('@y;Couldn\'t find Product DESCRIPTION. skipping...@e;')
        if not info.get('image'): return self.p('@y;Couldn\'t find Product IMAGE. skipping...@e;')
        if not info.get('link'): return self.p('@y;Couldn\'t find Product LINK. skipping...@e;')

        try: 
            print(f"Creating Pin Title: {info['title']}, Image: @b;{info['image'][:10]}... to Board: {info.get('category').replace('-', ' ').title() if info.get('category') else 'None'}")
            created_pin = self.pin(board_id, image_url=info['image'], description=info['description'], link=info['link'], title=info['title'])            
            board_name = created_pin.json()['resource_response']['data']['board']['name']

            self.p(f"@g;Created pin Title: @b;{info['title']}@g;, Image: @b;{info['image'][:15]}...@g; to Board: @b;{board_name}@e;\n")
            self.successful_pins += 1
            self.failed_delta = 0
            return True
        except Exception as err: 
            self.p(f"@r;Failed to pin product Title: {info.get('title')} to Board: {info.get('category')} - {err}@e;\n") 
            self.failed_pins += 1
            self.failed_delta += 1
            print(err)
    
        # Store to file
        with open(self.pinned_history_file, 'a') as file:
            file.write(f'\nTitle: {info["title"]}, Image: {info["image"]}, Category: {info["category"]}')
    
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


if __name__ == '__main__':
    try:
        bot = Bot()
        bot.start()
    except:
        bot.p(f'\n\n@y;{"-^-"*3} Terminating {"-^-"*3}', effect=True)