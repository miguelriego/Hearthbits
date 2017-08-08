from soundbot import *
"""
from soundbot import get_card_id, search_hearthpwn, get_card, connect
import re

def scrape(q):     
    db = connect('hearthsounds.db')
    c = db.cursor()

    # Initialize variables
    cards = []
    temp_list = []
    soundslist = []
    sound_dict = {'Name': '',}


    # If q, run search and store results into corresponding variables
    if q:
        q = q.lower().strip()
        results, in_cache = search_hearthpwn(q, db)
    
    # Run regex for card extraction and db insertion
        for card_id in results:
            card_id = re.split("\-", card_id)[0]
            cards.append(get_card(card_id, db))
            c.execute('SELECT cards.name, cards.image, cards.gif FROM cards WHERE cards.card_id = ?', (card_id,))
            temp_tup=c.fetchone()
            c.execute('SELECT cards.name, sounds.name, sounds.src FROM sounds INNER JOIN cards on sounds.card_id = cards.card_id WHERE sounds.card_id = ?', (card_id,))
            temp_list.append(c.fetchall())

            if results and not in_cache:
                c.execute('insert into searches (query, card_id) values (?, ?)', (q, card_id))
                db.commit()
                print(results, " added to DB!")
        
    # Structure data into dictionary form
        sound_dict.update({'Name': temp_list[0][0][0], 'Image':temp_tup[1], 'GIF':temp_tup[2],})
        #sound_dict.update({'Name': temp_list[0][0][0]})
        for row in temp_list:
            for item in row:
            	sound_dict[item[1]] = item[2]
        return(sound_dict)

        c.close()
    
    db.close()
"""
temp_list = []
sound_dict = scrape('elder')
for key, dictionary in sound_dict.items():
    for k, v in dictionary.items():
        temp_list.append(dictionary['Name']+"\'s ["+k+"] bit:\n"+v)

print(temp_list)