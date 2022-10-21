# Shopify-Pinterest Python Bot

A Python Bot that grabs and pins products from A Shopify Store to A Pinterest Account

## How to Use 

install the dependencies in the requirements.txt file by running ```pip install -r requirements.txt``` on the command line

open settings.py in notepad or any text editor and edit/change the required settings i.e (email, password and username)

> Your username can be found in profile url pinterest.com/_username_

Edit other neccesary settings:
* Number of product to pin per day
* Pinning frequency(time in seconds before pinning the next product respective to part of the day ie in the afternoon(from 12pm to 16/4pm) pin the next product with a random gap of 180-420secs ).
* Daytime range is the hours when part of days start ie morning starts at 5am to 11am..

After editing settings.py, save changes and run main.py to start the bot
