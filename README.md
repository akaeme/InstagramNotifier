Instagram Notifier
===================

Instagram notifier is a script that let you launch one bot to notify you about the new activity of the people that 
you maybe want to follow closely.
For now just supports notifications about new photos polling them every 30 minutes. 
It only notifies the last photo placed, given the time interval.

Main Features:
 - Notifies many sources of information(people on instagram)
 - Notifies many people(on facebook)
 - One activity can be notified to n persons(on facebook)
 - It handle sensitive information securely
 - ...
 
InstagramNotifier uses two API's:
 - InstagramAPI, a changed version of https://github.com/ahmdrz/Instagram-API-python in order to support pagination 
 and error control.
 - fbchat, available at https://github.com/carpedm20/fbchat

It also uses sqlite3 to save securely some useful data 

All the code follows PEP 8 -- Style Guide for Python Code

General Usage
-----

    Usage:
        instagramNotifier [options] 

    Options:
        -u              Add a valid user to the database.
        -f              Add someone to follow closely.
        -n              Add someone to get notified on facebook messenger.
        -r              Run Instagram Notifier.
        

## Installation and Configuration ##
1. Clone this repository
2. Install the requirements `$ (sudo) pip install -r requirements.txt`
3. Create the database and add a user:`$ python3 instagramNotifier.py -u`
4. Add someone to follow closely on instagram: `$ python3 instagramNotifier.py -f`
5. Add someone to get notified: `$ python3 instagramNotifier.py -n`
6. Run the bot: `$ python3 instagramNotifier.py -r`
