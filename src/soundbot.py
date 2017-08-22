#!/usr/bin/env python
import sys, os
from bs4 import BeautifulSoup
import cgi
import json
from mako.template import Template
import sqlite3
import re
import requests
from pydub import AudioSegment
from urllib.request import urlretrieve, pathname2url
from urllib.parse import urljoin
import dropbox
from telegram import File

dbx = dropbox.Dropbox('cwlHfwFQ-54AAAAAAAACmaGldUd_SGTvp9ztWeL9ip-4aF_Plp9zb0injwF3bhcN')


def get_card_id(url):
    m = re.search('/cards/([^/]*)', url)
    return m.group(1)


def search_hearthpwn(query, db):
    c = db.cursor()
    c.execute('select card_id from searches where query = ?', (query,))
    cards = c.fetchall()
    c.close()

    if cards:
        results = [r['card_id'] for r in cards[0:4]]

        return (results, True)

    r = requests.get('https://www.hearthpwn.com/cards/',
                     params={'filter-name': query, 'filter-premium': 1})
    html = r.text
    soup = BeautifulSoup(html, 'html.parser')
    cards = soup.find('tbody').find_all('tr')

    if cards[0].find('td', class_='no-results'):
        return ([], True)

    results = []
    for card in cards:
        details = card.find('td', class_='visual-details-cell')
        card_url = details.find('h3').find('a')['href']
        card_id = get_card_id(card_url)
        results.append(card_id)

    return (results, False)


def get_card(card_id, db):
    card = Card(card_id, db)
    exists = card.from_sql()

    if not exists:
        r = requests.get('https://www.hearthpwn.com/cards/' + card_id)
        html = r.text.encode('utf-8')
        card.from_html(html)
        card.insert()

    return card


class Card:
    def __init__(self, card_id, db):
        self.card_id = card_id
        self.db = db

    def from_html(self, html):
        soup = BeautifulSoup(html, 'html.parser')
        self.name = soup.find('h2').text
        self.image = soup.find('img', class_='hscard-static')['src']
        # Hack for misplaced GIFs in HPwn:
        temp_list = (soup.find('', class_='hscard-static')['data-gifurl'])
        if 'png' in temp_list:
            temp_list = temp_list.split("/")
            temp_list[5] = str(int(temp_list[5])-1)
            temp_list = "/".join(temp_list)
            self.gif = temp_list.replace('png','gif')
        else: 
            self.gif = (soup.find('', class_='hscard-static')['data-gifurl'])
        audio = soup.find_all('audio')
        self.sounds = []
        for a in audio:
            id = a['id'].replace('sound', '').replace('1', '')
            src = a['src']

            self.sounds.append({'id': id, 'src': src})

    def from_sql(self):
        self.c = self.db.cursor()
        self.c.execute('select * from cards where card_id = ? limit 1', (self.card_id,))
        row = self.c.fetchone()

        if row:
            self.card_id = row['card_id']
            self.name = row['name']
            self.image = row['image']
            self.gif = row['gif']

            self.c.execute('select name, src from sounds where card_id = ?', (self.card_id,))

            self.sounds = []

            for row in self.c:
                self.sounds.append({'id': row['name'], 'src': row['src'],})

            self.c.close()
            return True

        self.c.close()
        return False

    def insert(self):
        self.c = self.db.cursor()
        self.c.execute('insert into cards (card_id, name, image, gif) values (?, ?, ?, ?)',
                       (self.card_id, self.name, self.image, self.gif))
        for sound in self.sounds:
            self.c.execute('insert into sounds (card_id, name, src) values (?, ?, ?)',
                           (self.card_id, sound['id'], sound['src']))
        self.db.commit()
        self.c.close()


def connect(db_file):
    db = sqlite3.connect(db_file)
    db.row_factory = sqlite3.Row
    c = db.cursor()
    c.execute('pragma foreign_keys = ON')
    c.close()

    return db


def scrape(q):
    db = connect('hearthsounds.db')
    c = db.cursor()

    # Initialize variables
    cards = []
    temp_list = []
    row_dict = {}
    sound_dict= {}

    # If q, run search and store results into corresponding variables
    if q:
        q = q.lower().strip()
        results, in_cache = search_hearthpwn(q, db)
    
    # Run regex for card extraction and db insertion
        for card_id in results:
            card_id = re.split("\-", card_id)[0]
            cards.append(get_card(card_id, db))

    # Run sequel queries for "header"and souds data
            c.execute('SELECT cards.name, cards.image, cards.gif FROM cards WHERE cards.card_id = ?', (card_id,))
            temp_tup=c.fetchone()
            c.execute('SELECT cards.name, sounds.name, sounds.src FROM sounds INNER JOIN cards on sounds.card_id = cards.card_id WHERE sounds.card_id = ?', (card_id,))
            temp_list.append(c.fetchall())

    # Structure data into dictionary form within same loop
            row_dict = {'Name': temp_tup[0], 'Image':temp_tup[1], 'GIF':temp_tup[2],}
            for row in temp_list:
                for item in row:
                    row_dict[item[1]] = item[2]
            
            sound_dict[card_id] = row_dict
            
            if results and not in_cache:
                c.execute('insert into searches (query, card_id) values (?, ?)', (q, card_id))
                db.commit()
                print(card_id, " added to DB!")

        return(sound_dict)
       
        c.close()
    
    db.close()

def convert(q):
    db = connect('hearthsounds.db')
    c = db.cursor()

    sound_dict = scrape(q)
    for key, sub_dict in sound_dict.items():
        for k, v in sub_dict.items():
            if k not in ('Name', 'Image', 'GIF'):
                fname = sub_dict['Name']+"\'s_["+k+"]_bit"
                fullfilename = str(os.path.join(os.getcwd(), 'temp', fname))

                c.execute('select card_id, name, src from c_sounds where card_id = ? AND name = ?', (key, k))
                c_sounds = c.fetchall()

                # Convert files if not on DropBox
                if not c_sounds:
                    vogg = urlretrieve(v,fullfilename+'.ogg')[0]
                    vogg = AudioSegment.from_ogg(fullfilename+'.ogg')
                    vogg.export(fullfilename+'.mp3', 
                                format='mp3', 
                                cover=urlretrieve(sub_dict['Image'], fullfilename+'.png')[0],
                                tags={'title':sub_dict['Name']+'\'s_['+k+']','album':'Hearthstone'})
                    file = File(file_id=k+v, bot=None, file_size=None, file_path=fullfilename+".mp3")
                    print(file)
                    with open(fullfilename+'.mp3', 'rb') as f:
                        v = fname+'.mp3'
                        dbx.files_upload(f.read(), '/test/'+v, mute=True)
                        #sub_dict[k] = dbx.files_get_temporary_link('/test/'+v).link
                        sub_dict[k] = dbx.sharing_create_shared_link('/test/'+v).url

                    os.remove(fullfilename+'.ogg')
                    os.remove(fullfilename+'.png')

                    c.execute('insert into c_sounds (card_id, name, src) values (?, ?, ?)', (key, k, sub_dict[k]))
                    db.commit()
                
                # Pull file links if on DropBox
                if c_sounds:
                    for item in c_sounds:
                        sub_dict[k] = item[2][:-5]

    return(sound_dict)

    c.close()
    db.close()
