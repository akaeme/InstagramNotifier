import argparse
import sys
from getpass import getpass

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes

from API.InstagramAPI import InstagramAPI
from databaseUtils import Database

database = Database('InstagramNotifier.db')


def login(user, passw):
    instagram_api = InstagramAPI(username=user, password=passw)
    if instagram_api.login():  # login
        return True, instagram_api
    else:
        return False, ''


def follow_closely(api_, follow_username):
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


def compare_data(data):
    pass


def run(api_, user):
    follows = database.get_from_follows(username=user)
    for f_closely in follows:
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
        compare_data(data)


def validate_user(user, passw):
    results = database.get_from_users(username=user)
    if len(results) == 0:
        print('User not registered.')
        return False
    # it return a list of tuples, dunno why
    password_hash = str(results[0][0])
    digest_ = hashes.Hash(hashes.SHA256(), backend=default_backend())
    digest_.update(bytes(passw, 'utf8'))
    if password_hash == str(digest_.finalize().hex()):
        return True
    return False


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Instagram Notifier. it get new post from user that we want to follow closely.')
    parser.add_argument('-u', action="store_true", dest='user', help='Add a valid user to the database.')
    parser.add_argument('-f', action="store_true", dest='follow', help='Add someone to follow closely.')
    parser.add_argument('-r', action="store_true", dest='run', help='Run Instagram Notifier.')

    args = parser.parse_args()
    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)

    args = vars(args)
    username = input('Instagram username: ')
    password = getpass(prompt='Instagram password: ')
    if args['user']:
        flag, api = login(user=username, passw=password)
        if flag:
            print('Login success!')
            # Add confirmed user to database
            digest = hashes.Hash(hashes.SHA256(), backend=default_backend())
            digest.update(bytes(password, 'utf8'))
            database.insert_user(username=username, password=digest.finalize().hex())
        else:
            print('Invalid username or password. Try again!')
            exit()
    if args['follow']:
        if validate_user(user=username, passw=password):
            # flag will be always True
            flag, api = login(user=username, passw=password)
            follow_user = input('Let\'s follow (you must know the instagram username of the person ): ')
            flag, info = follow_closely(api_=api, follow_username=follow_user)
            if flag:
                # add to the database
                database.insert_follow(user_id=info['pk'], username=info['username'], user=username,
                                       full_name=info['full_name'], is_private=info['is_private'],
                                       profile_pic=info['profile_pic_url'])
            else:
                print('You are not following the user with the instagram username: ' + follow_user)
        else:
            print('Invalid username or password. Try again!')
            exit()
    if args['run']:
        if validate_user(user=username, passw=password):
            # flag will be always True
            flag, api = login(user=username, passw=password)
            run(api_=api, user=username)
