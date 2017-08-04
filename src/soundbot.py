#!/usr/bin/env python
from bs4 import BeautifulSoup
import cgi
import json
from mako.template import Template
import sqlite3
import re
import requests

def get_card_id(url):
    m = re.search('/cards/([^/]*)', url)
    return m.group(1)


def search_hearthpwn(query, db):
    c = db.cursor()
    c.execute('select card_id from searches where query = ?', (query,))
    cards = c.fetchall()
    c.close()

    if cards:
        results = [r['card_id'] for r in cards]

        return (results, True)

    r = requests.get('http://www.hearthpwn.com/cards/minion',
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
        r = requests.get('http://www.hearthpwn.com/cards/' + card_id)
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

            self.c.execute('select name, src from sounds where card_id = ?', (self.card_id,))

            self.sounds = []

            for row in self.c:
                self.sounds.append({'id': row['name'], 'src': row['src']})

            self.c.close()
            return True

        self.c.close()
        return False

    def insert(self):
        self.c = self.db.cursor()
        self.c.execute('insert into cards (card_id, name, image) values (?, ?, ?)',
                       (self.card_id, self.name, self.image))
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
    
    card_name = ''
    error = ''
    cards = []
    soundbites = []
    
    if q:
        q = q.lower().strip()
        results, in_cache = search_hearthpwn(q, db)
    

        for card_id in results:
            card_id = re.split("\-", card_id)[0]
            cards.append(get_card(card_id, db))
            #soundbites.append(c.execute('select name, src from sounds where card_id = ?', (card_id,)))
            c.execute('select name, src from sounds where card_id = ?', (card_id,))
            soundbites.append(c.fetchall())

            if results and not in_cache:
                c.execute('insert into searches (query, card_id) values (?, ?)', (q, card_id))
                db.commit()
                print(results, " added to DB!")
        
        for row in soundbites:
            for item in row:
                for sound in item:
                    print(sound)
 
        return(results)
        c.close()
    
    db.close()

def scrape2(q):
    db = connect('hearthsounds.db')
    c = db.cursor()

    cards = []
    soundbites = []
    qlist = []
    
    if q:
        q = q.lower().strip()
        results, in_cache = search_hearthpwn(q, db)
    
        for card_id in results:
            card_id = re.split("\-", card_id)[0]
            cards.append(get_card(card_id, db))
            c.execute('SELECT cards.name, sounds.name, sounds.src FROM sounds INNER JOIN cards on sounds.card_id = cards.card_id WHERE sounds.card_id = ?', (card_id,))
            soundbites.append(c.fetchall())

            if results and not in_cache:
                c.execute('insert into searches (query, card_id) values (?, ?)', (q, card_id))
                db.commit()
                print(results, " added to DB!")
        
        for row in soundbites:
            for item in row:
                for sound in item:
                    qlist.append(sound)
        
        sb1 = (qlist[0], qlist[1], qlist[2])
        sb2 = (qlist[3], qlist[4], qlist[5])
        sb3 = (qlist[6], qlist[7], qlist[8])

        soundtup = (sb1, sb2, sb3)

        return(soundtup)

        c.close()
    
    db.close()

