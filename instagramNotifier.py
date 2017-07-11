import argparse
# from fbchat.models import *
import logging
import os
import sys
import urllib.request
from getpass import getpass
from time import sleep

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from fbchat import Client
from pyshorteners import Shortener

from API.InstagramAPI import InstagramAPI
from databaseUtils import Database

logger = logging.getLogger('instagramNotifier')
hdlr = logging.FileHandler('instagramNotifier.log')
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
hdlr.setFormatter(formatter)
logger.addHandler(hdlr)
logger.setLevel(logging.INFO)

database = Database('InstagramNotifier.db')
MESSAGE_HEADER = 'Check out the new %s\'s photo on instagram! \n'
MESSAGE_BODY = 'The photo was taken in %s, it has size %sx%s and as we can see it is of great quality :) \n'
MESSAGE_FOOTER = 'This was generated by a bot to help you by notifying you of everything that is important. ' \
                 'Do not consider it as spam.\n'
shortener = Shortener('Tinyurl')


def login(user_, passw):
    """Login on Instagram"""
    instagram_api = InstagramAPI(username=user_, password=passw)
    if instagram_api.login():  # login
        return True, instagram_api
    else:
        return False, ''


def follow_closely(api_, follow_username):
    """Search for the user"""
    big_list = True
    max_id = ''
    following = []

    while big_list:
        api_.getSelfUsersFollowing(maxid=max_id)
        followers_ = api_.LastJson
        for f in followers_['users']:
            following.append(f)
            big_list = followers_['big_list']
        if not big_list:
            break
        # this key only exists if there is more pages
        max_id = followers_['next_max_id']

    for f in following:
        if f['username'] == follow_username:
            return True, f


def get_message(message_type, source, data=None):
    """Get the notify message"""
    if message_type == 'image':
        header = (MESSAGE_HEADER % source)
        body = (MESSAGE_BODY % (data['location'], data['width'], data['height']))
        urllib.request.urlretrieve(data['last_media'], 'tmp.jpg')
        return header + body
    else:
        header = (MESSAGE_HEADER % source)
        return header + MESSAGE_FOOTER


def alert(user, follow, data, client_fb):
    """Get the notify message"""
    users_notify = database.get_from_notify(username=user, username_follow=follow)
    for user in users_notify:
        if user['thread_type'] == '0':
            if user['image_flag']:
                message = get_message(message_type='image', source=follow, data=data)
                client_fb.sendLocalImage(image_path='tmp.jpg', message=message, thread_id=str(user['thread_id']))
                client_fb.sendMessage(message=MESSAGE_FOOTER, thread_id=str(user['thread_id']))
                logger.info('User %s notified %s on facebook.', user, str(user['thread_id']))
                # clean image created
                os.remove('tmp.jpg')
            else:
                message = get_message(message_type='no_image', source=follow)
                client_fb.sendMessage(message=message, thread_id=str(user['thread_id']))
                logger.info('%s  got notified on facebook.', str(user['thread_id']))


def run(api_, user_):
    """Run bot"""
    email_fb = input('Facebook email: ')
    pass_fb = getpass(prompt='Facebook password: ')
    client_fb = Client(email=email_fb, password=pass_fb, logging_level=logging.CRITICAL)
    try:
        print('Running..')
        while True:
            follows = database.get_from_follows(username=user_)
            medias = database.get_from_media(username=user_)

            for f_closely, username_follow, id_ in follows:
                data = dict(last_media_id=0, media_count=0, user_id=0, last_media='', width=0, height=0, location='')
                data['user_id'] = f_closely
                api_.getUsernameInfo(str(f_closely))
                media_results = api_.LastJson
                data['media_count'] = media_results['user']['media_count']
                api_.getUserFeed(str(f_closely))
                media_results = api_.LastJson
                last_media = media_results['items'][0]
                try:
                    data['last_media_id'] = int(last_media['pk'])
                    data['last_media'] = last_media['image_versions2']['candidates'][0]['url']
                    data['width'] = last_media['image_versions2']['candidates'][0]['width']
                    data['height'] = last_media['image_versions2']['candidates'][0]['height']
                    data['location'] = last_media['location']['name']
                except KeyError:
                    # for debugging
                    print('KeyError')
                data_ = [media for media in medias if media['user_id'] == data['user_id']][0]
                if data['last_media_id'] != data_['last_media_id']:
                    alert(user=user_, follow=username_follow, data=data, client_fb=client_fb)
                    # Update info on database
                    database.update_media(last_media_id=data['last_media_id'], media_count=data['media_count'],
                                          foreign_id=id_, last_media=data['last_media'], width=data['width'],
                                          height=data['height'],
                                          location=data['location'], last_media_id_=data_['last_media_id'])
                    logger.info('Update media for user %s.', data['user_id'])
            print('Sleeping')
            sleep(120)
    except KeyboardInterrupt:
        print('Interrupted!')


def get_info(api_, user_id):
    """Save info of the follower"""
    data = dict(last_media_id=0, media_count=0, user_id=0, last_media='', width=0, height=0, location='')
    data['user_id'] = user_id
    api_.getUsernameInfo(user_id)
    media_results = api_.LastJson
    data['media_count'] = media_results['user']['media_count']
    api_.getUserFeed(user_id)
    media_results = api_.LastJson
    last_media = media_results['items'][0]
    try:
        data['last_media_id'] = int(last_media['pk'])
        data['last_media'] = last_media['image_versions2']['candidates'][0]['url']
        data['width'] = last_media['image_versions2']['candidates'][0]['width']
        data['height'] = last_media['image_versions2']['candidates'][0]['height']
        data['location'] = last_media['location']['name']
    except KeyError:
        # for debugging
        print('KeyError')
        exit()
    return data


def validate_user(user_, passw, service):
    """Validate a user according to the service"""
    if service == 'instagram':
        results = database.get_from_users(username=user_, service=service)
    elif service == 'facebook':
        results = database.get_from_users(username=user_, service=service)
    else:
        print('Unknown service')
        return False
    if len(results) == 0:
        print('User not registered.')
        return False
    # it return a list of tuples, dunno why
    password_hash = str(results[0][0])
    digest_ = hashes.Hash(hashes.SHA256(), backend=default_backend())
    digest_.update(bytes(passw, 'utf8'))
    if password_hash == str(digest_.finalize().hex()):
        logger.info('User %s validated on %s', user_, service)
        return True
    logger.warning('User %s not validated on %s. Hash do not match.', user_, service)
    return False


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Instagram Notifier. It get new posts from user that we want to follow closely and notify other '
                    'users on facebook messenger')
    parser.add_argument('-u', action="store_true", dest='user', help='Add a valid user to the database.')
    parser.add_argument('-f', action="store_true", dest='follow', help='Add someone to follow closely.')
    parser.add_argument('-n', action="store_true", dest='notify', help='Add someone to get notified on facebook '
                                                                       'messenger.')
    parser.add_argument('-r', action="store_true", dest='run', help='Run Instagram Notifier.')
    args = parser.parse_args()
    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)

    args = vars(args)
    username = input('Instagram username: ')
    password = getpass(prompt='Instagram password: ')
    if args['user']:
        flag, api = login(user_=username, passw=password)
        if flag:
            print('Login success!')
            email = input('Facebook email: ')
            password_fb = getpass(prompt='Facebook password: ')
            try:
                client = Client(email, password_fb, logging_level=logging.CRITICAL)
            except Exception:
                print('Facebook - invalid username or password. Try again!')
            else:
                print('Login success!')
                # Add confirmed user to database
                digest = hashes.Hash(hashes.SHA256(), backend=default_backend())
                digest.update(bytes(password, 'utf8'))
                insta_hash = digest.finalize().hex()
                digest = hashes.Hash(hashes.SHA256(), backend=default_backend())
                digest.update(bytes(password_fb, 'utf8'))
                fb_hash = digest.finalize().hex()
                database.insert_user(username=username, password=insta_hash, email=email, password_fb=fb_hash)
                logger.info('User %s inserted on database.', username)
                client.logout()
        else:
            print('Invalid username or password. Try again!')
            exit()
    if args['follow']:
        if validate_user(user_=username, passw=password, service='instagram'):
            # flag will be always True
            flag, api = login(user_=username, passw=password)
            follow_user = input('Let\'s follow (you must know the instagram username of the person ): ')
            flag, info = follow_closely(api_=api, follow_username=follow_user)
            if flag:
                # add to the database
                id_row = database.insert_follow(user_id=info['pk'], username=info['username'], user=username,
                                                full_name=info['full_name'], is_private=info['is_private'],
                                                profile_pic=info['profile_pic_url'])
                # get actual info about feed and save it
                data = get_info(api_=api, user_id=info['pk'])
                database.insert_media(last_media_id=data['last_media_id'], media_count=data['media_count'],
                                      foreign_id=id_row, last_media=data['last_media'], width=data['width'],
                                      height=data['height'], location=data['location'])
                logger.info('User %s is now following closely %s.', username, follow_user)
            else:
                print('You are not following the user with the instagram username: ' + follow_user)
        else:
            print('Invalid username or password. Try again!')
            exit()
    if args['notify']:
        email = input('Facebook email: ')
        password_fb = getpass(prompt='Facebook password: ')
        if validate_user(user_=email, passw=password_fb, service='facebook'):
            client = Client(email=email, password=password_fb, logging_level=logging.CRITICAL)
            notify = input('Let\'s notify (you must know the facebook name of the person ): ')
            # It take in consideration only the first 10 friends, exclude non friends
            notify = client.searchForUsers(name=notify, limit=10)
            friends = sorted([x for x in notify if x.is_friend], key=lambda x: x.uid)
            print('There are many friends with this name: ')
            print('\n'.join('{} -> name: {}, photo: {}'.format(i, k.name, shortener.short(k.photo)) for i, k in
                            enumerate(friends)))
            io = input('Choose one of them: ')
            notify = friends[int(io)]

            print('This person should receive notifications about whom?')
            follow_ = sorted([f[1] for f in database.get_from_follows(username=username)])
            print('\n'.join('{}: {}'.format(*k) for k in enumerate(follow_)))

            to_notify = input('Choose the people you want to notify(ie: 1,2): ')
            to_notify = [int(s.replace(' ', '')) for s in to_notify.split(',')]
            to_notify = [follow_[x] for x in to_notify]
            for person in to_notify:
                id_follow = database.get_from_follows_find(username=username, username_follow=person)[0]
                database.insert_notify(foreign_id=id_follow, thread_id=notify.uid, thread_type=0, image_flag=1)
                logger.info('User %s will notify %s about something.', username, notify)

    if args['run']:
        if validate_user(user_=username, passw=password, service='instagram'):
            # flag will be always True
            flag, api = login(user_=username, passw=password)
            run(api_=api, user_=username)
