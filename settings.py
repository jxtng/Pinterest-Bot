# Required
email = 'zm6ewsy@smartnator.com'
password = 'Pass@123'
username = 'zm6ewsy'

# Others
no_of_product_to_pin = 10
pinning_frequency = {
  'morning': [60, 180], # Any time from 60sec(1 min) to 180s(3mins)
  'afternoon': [180, 420],
  'evening': [500, 600],
  'night': [1000, 1200]
}
daytime_range = {
  'morning': [5, 11], 
  'afternoon': [12, 16], # from 12 O'clock to 16(i.e 4pm) O'clock
  'evening': [17, 22],
  'night': [23, 4], #Defaults to this: 23(i.e 11)pm to 4am
}
manual_description_shuffle = False
quillbot_description_shuffle = False

# Defaults
product_info = {'board': 'tiktok', 
'image': 'https://cdn.shopify.com/s/files/1/0549/8571/9854/products/H56dc2ee25c7b443cad5e45ff255def75s_1800x1800.jpg?v=1658888028', 
'title': 'Drainage Soap Holder', 
'description': "BUY 1 GET 1 FREE! Yes, you heard it right! order one and the second one is on us! You're soap will last longer You'll save more on soap purchases You'll stay more organized in you bathroom and kitche sinks Our Drainage Soap Holder is designed for a perfect drainage and avoids mushy bathroom soap which which is unattractive and encourages waste. FEATURES Material: ABS 45° inclined surface design Easy to setup stable suction cup base Multi-purpose usage, can be used in kitchen sink, and bathroom.", 
'link': 'https://wowu.shop/collections/tiktok/products/drainage-soap-holder'}
product_link = 'https://wowu.shop/collections/tiktok/products/drainage-soap-holder'

################# ADVANCE ############################
# Links
domain = 'http://wowu.shop'
all_collections_link = 'https://wowu.shop/collections/'

# Selectors
collections_link_selector = 'a[href*=collection]'
products_link_selector = 'a.grid-product__link'
product_image_link_container_selector = '.product__thumb-item'
product_title_selector= '.product-single__title'
product_description_selector = '[id*=content-description]'
board_name_position_in_url = -3