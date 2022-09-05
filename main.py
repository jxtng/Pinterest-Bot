from helium import *

from bs4 import BeautifulSoup
from time import sleep

from random import randint, shuffle
from functools import reduce

import re, requests, infos


def get_product_info(page=infos.default_product):
    soup = BeautifulSoup(requests.get(page).text, 'html.parser')
    title = list(soup.find(class_=re.compile('product-single__title')).stripped_strings)[0]
    images = ['https:' + i.a['href'] for i in soup.find_all(class_='product__thumb-item')]
    description = list(soup.find(id=re.compile('[Pp]roduct-content-description')).stripped_strings)
    desc = re.split('(?<=[!?.])\s+', re.sub('\s+(?=[!?.])', '', ' '.join(description)))
    description = ''
    for i in desc:
        if len(description) + len(i) > 500:
            break
        description += f'{i} '
    return {'title': title, 'images': images, 'description': description, 'link': page}


def login_to_pinterest(email=infos.email, password=infos.password):
    go_to('http://pinterest.com')
    wait_until(Button('Log in').exists, 300)
    click(Button('Log in'))
    wait_until(TextField('Email').exists, 300)
    write(email, into=TextField('Email'))
    write(password, into=TextField('Password'))
    press(ENTER)


def create_pins(pin_data=infos.default_product_info, board_name=infos.board_name_to_pin_post):
    sleep(5), go_to('http://pinterest.com/pin-builder')

    # Image
    click('Save from site')
    write(pin_data['link']), click(S('[data-test-id="website-link-submit-button"]')), sleep(3)
    try:
        image = S(f'//img[@src="{pin_data["images"][randint(0, len(pin_data["images"]))]}"]')
        click(image)
        image = image.web_element.get_attribute('src')
    except:
        images =  find_all(S(f'div[data-group-id="pin-builder-pin-draft"] img'))
        image = images[randint(0, len(images)-1)]
        click(image)
        image = image.web_element.get_attribute('src')
    click('Add')

    # Board
    wait_until(S('button[data-test-id="board-dropdown-select-button"]').exists)
    click(S('button[data-test-id="board-dropdown-select-button"]')), click(Text(board_name))

    # Title
    write(pin_data['title'], into=TextField('Add your title'))

    # Description
    click(S('.DraftEditor-root')), write(pin_data['description'])

    # Alt Text
    click(Button('Add Alt Text')), write(pin_data['title'])

    # Link
    # try: write(pin_data['link'], into=TextField('Add a destination link'))
    # except: pass

    # Publish
    sleep(1)
    try: click(Button('Save')) if Button('Save').exists() else click(Button('Publish'))
    except: click(S('//button[@data-test-id="board-dropdown-save-button"]'))

    return {'title': pin_data['title'].upper(), 'image': image}


def get_all_products(collection_page=infos.everything_link):
    soup = BeautifulSoup(requests.get(collection_page).text, 'html.parser')
    return ['https://wowu.shop' + a['href'] for a in soup.find_all('a', class_='grid-product__link')]


def init():

    print('Grabbing all products from https://wowu.shop...')
    products = [*get_all_products(), *infos.extra_links_to_pin]
    products = [get_product_info(product) for product in products]

    print(f'{len(products)} Product(s) with {reduce(lambda x,y: x + len(y["images"]), products, 0)} Image(s) grabbed successfully\n\n', 'Initializing Automation...\n')

    start_chrome(headless=infos.show_browser_when_automating)

    print(f'Logging in to pinterest...  Email: {infos.email}, Password: {re.sub(".", "*", infos.password)}')
    login_to_pinterest()
    print(f'Logged in successfully to pinterest\n')
    
    if infos.pin_multiple_images_using_the_same_title_and_desc:
        new_products = []

        for product in products:

            for i in range(len(product['images'])):

                new_products.append({'title': product['title'], 'images': [product['images'][i]], 'description': product['description'], 'link': product['link']})

        products = new_products

    no_of_pins = infos.no_of_pins_to_post if infos.no_of_pins_to_post > 0 else len(products)
    if infos.shuffle_pins: shuffle(products) 
    
    print(f'Creating {no_of_pins} {"random" if infos.shuffle_pins else ""} pin(s)...\n\n')

    for i in range(no_of_pins):
        try:
            pin_response = create_pins(products[i])

            print(f'A Pin with \ntitle: {pin_response["title"]} \nand image: {pin_response["image"]}, \ncreated successfully\n\n', 'Creating next pin...\n')
        except: 
            print(f'This pin failed for some reason, ([We] mov[e])ing to the next one....\n')
    else:
        print('All pins created successfully\n', 'Exiting Automation...')

        sleep(3)

    kill_browser()

init()

