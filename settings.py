# ------------------- STILL IN DEV --------------------------
# Required
email = 'wanpenmak.dee.1.23.4.5@gmail.com'
password = 'Pass@123'
username = 'wanpenmakdee'

# Others
no_of_pin_per_day = 5
pinning_frequency = {
  'morning': [5, 20], # Any time from 60sec(1 min) to 180s(3mins)
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

################# WEBSITE SETTINGS ############################
website = 'http://wowu.shop'
min_image_res = 600
image_area_selector = ''
# edit below if it fails to grab products from website
title_selector = ''
description_selector = ''
