"""Utilities file that provide some static methods"""
import configparser
import os
import smtplib
import urllib
from datetime import datetime, timedelta
from email.message import EmailMessage

import cv2
import numpy as np
import requests
import scipy
from bs4 import BeautifulSoup
from lxml import etree

from database import Database, Images

db = Database()
cfg = configparser.ConfigParser()
cfg.read('configuration.ini')


def report_message():
    """Generate report message"""
    report_message_data = '''
      <!DOCTYPE html><html>
      <head>
        <link rel="stylesheet" type="text/css" hs-webfonts="true" href="https://fonts.googleapis.com/css?family=Lato|Lato:i,b,bi">
        <meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style type="text/css">
          h1{font-size:56px}
          h2{font-size:28px;font-weight:900}
          p{font-weight:100}
          td{vertical-align:top}
          table {
            border-collapse: collapse;
            width: 100%;
            }

          th, td {
            text-align: left;
            padding: 8px;
            }

          tr:nth-child(even) {
            background-color: #D6EEEE;
            }
          </style>
    </head>
    <body bgcolor="#F5F8FA" style="width: 100%; font-family:Lato, sans-serif; font-size:18px;">
    <div>
    '''
    return report_message_data


# convert hash array of 0 or 1 to hash string in hex
def hash_array_to_hash_hex(hash_array):
    """Generate hash from array"""
    hash_array = np.array(hash_array, dtype=np.uint8)
    hash_str = ''.join(str(i) for i in 1 * hash_array.flatten())
    return hex(int(hash_str, 2))


# convert hash string in hex to hash values of 0 or 1
def hash_hex_to_hash_array(hash_hex):
    """Generate array from hash """
    hash_str = int(hash_hex, 16)
    array_str = bin(hash_str)[2:]
    return np.array([i for i in array_str], dtype=np.float32)


def get_image_hash(image_url):
    """get image hash"""
    # image calculate PHash value
    # img = cv2.imread(name)
    req = urllib.request.urlopen(image_url)
    arr = np.asarray(bytearray(req.read()), dtype=np.uint8)
    img = cv2.imdecode(arr, -1)  # 'Load it as it is'

    # resize image and convert to gray scale
    img = cv2.resize(img, (64, 64))
    img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    img = np.array(img, dtype=np.float32)
    # calculate dct of image
    dct = cv2.dct(img)
    # to reduce hash length take only 8*8 top-left block
    # as this block has more information than the rest
    dct_block = dct[: 8, : 8]
    # calculate mean of dct block excluding first term i.e, dct(0, 0)
    dct_average = (dct_block.mean() * dct_block.size - dct_block[0, 0]) / (dct_block.size - 1)
    # convert dct block to binary values based on dct_average
    dct_block[dct_block < dct_average] = 0.0
    dct_block[dct_block != 0] = 1.0

    return dct_block.flatten()


def scrape_data(hotels):
    """scraper data method"""
    scrape_status = False
    date_time_value = datetime.now()
    today = date_time_value.strftime('%A')
    current_time = (date_time_value + timedelta(hours=1)).strftime("%H:%M")
    for item in hotels:
        hotel = db.fetch_hotel_by_id(item)
        url = hotel.item_url
        item_description = ''
        item_images = []
        # ========= scrape data ================
        headers = ({
            'User-Agent': '''Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36
                            (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36''',
            'Accept-Language': 'en-US, en;q=0.5'})
        try:
            get = requests.get(url, headers=headers, verify=False, timeout=10)
            downloaded_data = get.text
            soup = BeautifulSoup(downloaded_data, 'html.parser')
            dom = etree.HTML(str(soup))
            elements = dom.xpath('//*[@id="hotel_main_content"]/div/div[1]/div[4]/a')
            if len(elements) > 0:
                item_images.append(elements[0].get("data-thumb-url"))
            elements = dom.xpath('//*[@id="hotel_main_content"]/div/div[1]/div[5]/a')
            if len(elements) > 0:
                item_images.append(elements[0].get("data-thumb-url"))
            elements = dom.xpath('//*[@id="hotel_main_content"]/div/div[1]/div[3]/a')
            if len(elements) > 0:
                item_images.append(elements[0].get("data-thumb-url"))
            elements = dom.xpath('//*[@id="hotel_main_content"]/div/div[1]/div[6]/div/div[1]/a/img')
            if len(elements) > 0:
                item_images.append(elements[0].get("src"))
            elements = dom.xpath('//*[@id="hotel_main_content"]/div/div[1]/div[6]/div/div[2]/a/img')
            if len(elements) > 0:
                item_images.append(elements[0].get("src"))
            elements = dom.xpath('//*[@id="hotel_main_content"]/div/div[1]/div[6]/div/div[3]/a/img')
            if len(elements) > 0:
                item_images.append(elements[0].get("src"))
            elements = soup.find("a", {"class": "bh-photo-grid-item bh-photo-grid-thumb"})
            if elements:
                for element in elements:
                    try:
                        element_child = element.find("img")
                        item_images.append(element_child.get("src"))

                    except ValueError:
                        continue

            item_match = False
            elements = dom.xpath('//*[@id="hp_hotel_name"]/div/h2')
            if elements:
                item_name = elements[0].text
                if hotel.item_name in item_name:
                    item_match = True

            elements = dom.xpath('//*[@id="showMap2"]/span[1]')
            if elements:
                item_address = elements[0].text
                if hotel.item_address == item_address:
                    item_match = True

            element = soup.find("div", {"id": "property_description_content"})
            if element:
                item_description = element.text

            item_rating = ""
            elements = dom.xpath('//*[@id="js--hp-gallery-scorecard"]/a/div/div/div/div[2]/div[1]')
            if len(elements) > 0:
                item_rating = elements[0].text

            elements = dom.xpath('//*[@id="js--hp-gallery-scorecard"]/a/div/div/div/div[1]')
            if len(elements) > 0:
                item_rating = item_rating + " with " + elements[0].text
            db.update_scrapped_hotel(hotel.id, item_description,
                                     item_rating, today, current_time, item_match)
            db.update_schedule(hotel.id, today, current_time, 'D')
            if len(item_images) > 0:
                old_images = db.fetch_all_images(hotel.id)
                image_index = 0
                for item_image in item_images:
                    image_hash = get_image_hash(item_image)
                    if len(old_images) > 0:
                        distance = scipy.spatial.distance.hamming(
                            hash_hex_to_hash_array(old_images[image_index].item_hash),
                            image_hash)
                        if distance == 0.0:
                            image_status = "Same"
                        else:
                            image_status = "Update"
                    else:
                        image_status = "New"
                    image_index += 1
                    if image_status == "Same":
                        continue
                    image_hash = hash_array_to_hash_hex(image_hash)
                    if image_status == "New":
                        image = Images(item_hotel=hotel.id,
                                       item_url=item_image, item_hash=image_hash)
                        db.add_image(image)
                        if not os.path.exists('static/images/' + str(hotel.id)):
                            os.mkdir('static/images/' + str(hotel.id))
                    else:
                        image_name = old_images[image_index].item_url.rsplit('/', 1)[-1]
                        image_name = image_name.split('?')[0]

                        db.update_image(old_images[image_index].id, item_image, image_hash)
                        if os.path.exists('static/images/' + str(hotel.id) + '/' + image_name):
                            os.remove('static/images/' + str(hotel.id) + '/' + image_name)

                    image_name = item_image.rsplit('/', 1)[-1]
                    image_name = image_name.split('?')[0]

                    with open('static/images/' + str(hotel.id) + '/' +
                              image_name, 'wb') as handle:
                        response = requests.get(item_image, stream=True, timeout=10)

                        if not response.ok:
                            print(response)

                        for block in response.iter_content(1024):
                            if not block:
                                break

                            handle.write(block)
            scrape_status = True
        except ValueError as exception_value:
            print(exception_value)
            db.update_hotel_scrapper_fail(hotel.id, today, current_time)
    return scrape_status


def schedule_data():
    """get schedule data"""

    # get current datetime
    date_time_value = datetime.now()
    today = date_time_value.strftime('%A')
    current_time = (date_time_value + timedelta(hours=1)).strftime("%H:%M")

    # Reset schedules
    if today == cfg["Schedules.reset"]["day"] and \
            current_time == cfg["Schedules.reset"]["time"]:
        db.update_all_schedule('P')

    # Check updated data and invalid URLs
    if current_time == cfg["Report"]["time"]:
        hotels = db.fetch_hotel_by_match(False)
        hotel_data = '''<h3>List of not matched data Hotels</h3>
        <table role='presentation' border='0' cellpadding='0' cellspacing='10px' style='padding: 30px 30px 30px 60px;'>
        <tr><th>Market ID</th><th>Name</th><th>Address</th></tr>'''
        if hotels:
            for hotel in hotels:
                hotel_data += "<tr><td>" + hotel.item_market_id + \
                              "</td><td>" + hotel.item_name + "</td><td>" + \
                              hotel.item_address + "</td></tr>"

        hotel_data += "</table>"
        schedule_data_sr = '''<h3>List of failed URLs</h3>
        <table role='presentation' border='0' cellpadding='0' cellspacing='10px' style='padding: 30px 30px 30px 60px;'>
        <tr><th>Market ID</th><th>URL</th></tr>'''

        schedules_data = db.fetch_schedule_by_run("F")
        if schedules_data:
            for schedule in schedules_data:
                hotel = db.fetch_hotel_by_id(schedule.item_hotel)
                schedule_data_sr += "<tr><td>" + hotel.item_market_id + \
                                    "</td><td>" + hotel.item_url + "</td></tr>"

        schedule_data_sr += "</table>"

        # create report
        message = report_message()
        message += hotel_data + schedule_data_sr + "</div></body></html>"

        # send email
        email_address = cfg["Report"]["email_from"]
        email_password = cfg["Report"]["email_password"]

        msg = EmailMessage()
        msg['Subject'] = 'Booking-Scrapper Daily Report'
        msg['From'] = cfg["Report"]["email_from"]
        msg['To'] = cfg["Report"]["email_to"]
        msg.set_content(message, subtype='html')

        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(email_address, email_password)
            smtp.send_message(msg)

    schedules_data = db.fetch_all_schedules('', today, current_time)

    if schedules_data:
        schedules = []
        for item in schedules_data:
            schedules.append(item.item_hotel)

        scrape_data(schedules)
    return "Data scrapped"
