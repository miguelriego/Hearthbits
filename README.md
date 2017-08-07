# Hearthbits

A functional hearthstone audio-sending-bot. Because sometimes, gifs just aren't enough :)

To run the bot, install python 3 (I recommend via Anaconda) and use pip install python-telegram-bot to install required libraries. 

bot.py is for direct messages to the bot (more for testing purposes), while inbot handles inline queries. Soundbot is a modified script that gathers the card into a local db.

**Change log**
* Added requirements.txt for easy installation
* Made card images display inline
* Added images and gifs for cards in inline queries (shiny animations!). Make sure to import run the new SQL schema or manually add the gif column to cards

**To-do's:**
- [x] Make a requirements.txt file
- [x] Make card images display in in-line query
- [ ] Try and fix audio so it'll play on iphone as well
- [ ] 

All credit for scraping code (soundbot) goes to Max Timkovich. Check out his project here: http://maxtimkovich.com/hearthsounds.py
