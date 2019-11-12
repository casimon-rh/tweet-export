import gspread
import time
import urllib.parse
import csv
from datetime import datetime, timedelta

from oauth2client.service_account import ServiceAccountCredentials

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import WebDriverException


def drive():
    """google drive"""
    scope = ['https://spreadsheets.google.com/feeds',
             'https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_name(
        'secret.json', scope)
    client = gspread.authorize(creds)
    sheet = client.open('Tweets')
    content = open('file_to_import.csv', 'r').read()
    client.import_csv(sheet.id, content)
    return sheet


def write_tweet(tweet, lastdate, writer):
    try:
        # FIREFOX.find_element_by_id('stream-items-id')
        header = tweet.find_element_by_class_name('stream-item-header')
        datestr = header.find_element_by_class_name(
            'tweet-timestamp').get_property('title')
        date = datetime.strptime(datestr, '%I:%M %p - %d %b %Y')
        content = tweet.find_element_by_class_name('tweet-text').text
        try:
            imgsrc = tweet.find_element_by_class_name(
                'AdaptiveMediaOuterContainer').find_element_by_tag_name('video').get_attribute('poster')
        except NoSuchElementException:
            imgsrc = tweet.find_element_by_class_name(
                'AdaptiveMediaOuterContainer').find_element_by_tag_name('img').get_attribute('src')
        # urllib.urlretrieve()
        if date > lastdate:
            arr = [datestr, content, imgsrc, datetime.timestamp(date)]
            # sheet.append_row()
            writer.writerow(arr)
            print(arr)
    except NoSuchElementException:
        pass


def scroll(FIREFOX):
    """scroll"""
    i = 0
    while i < 150:
        FIREFOX.execute_script(
            "window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(3)
        i = i+1
        print(i)


def main():
    '''Basic twitter crawling export to gdocs'''
    FIREFOX = webdriver.Firefox('/home/csimon/src/github/tweet-export/')
    FIREFOX.get('https://twitter.com/search?l=&q={}&src=typd'.format(
        urllib.parse.quote('from:cultura_mx since:2019-02-01 until:2019-07-13')))
    time.sleep(2)
    lastdate = datetime.today() - timedelta(7*365/12)
    scroll(FIREFOX)
    tweets = FIREFOX.find_element_by_id(
        'stream-items-id').find_elements_by_tag_name('li')
    with open('tweets.csv', mode='w') as file:
        writer = csv.writer(file, delimiter=',',
                            quotechar='"', quoting=csv.QUOTE_MINIMAL)
        writer.writerow(['Fecha - Hora', 'Contenido', 'Imagen', 'Timestamp'])
        for tweet in tweets:
            write_tweet(tweet, lastdate, writer)


if __name__ == '__main__':
    main()
