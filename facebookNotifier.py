from facebook import GraphAPI
import requests


def some_action(post):
    """ Here you might want to do something with each post. E.g. grab the
    post's message (post['message']) or the post's picture (post['picture']).
    In this implementation we just print the post's created time.
    """
    print(post['created_time'])


# You'll need an access token here to do anything.  You can get a temporary one
# here: https://developers.facebook.com/tools/explorer/
access_token = 'EAACEdEose0cBAD5XrJ8vfEVYRjKxq1Iw5FkNcuej6Mh3ZBMvcCXraOCT4sa7SEGaEbvst3eTSbMUAZCTUbTHnIZBp5FhRBbOMlmVeHYRX8Q4GWE9mCQ7vX7uaUQnmjZCmhdHcfcVnbfNsPwaLXDyhL5HcbTUiIFJhvxoePqd1HI7hMuoFQZA8Gm9c84YQ5wUUwOljnVOaRQZDZD'
# Look at Bill Gates's profile for this example by using his Facebook id.
user = 'akaemee'

graph = GraphAPI(access_token)
profile = graph.get_object(user)
posts = graph.get_connections(profile['id'], 'posts')

# Wrap this block in a while loop so we can keep paginating requests until
# finished.
while True:
    try:
        # Perform some action on each post in the collection we receive from
        # Facebook.
        [some_action(post=post) for post in posts['data']]
        # Attempt to make a request to the next page of data, if it exists.
        posts = requests.get(posts['paging']['next']).json()
    except KeyError:
        # When there are no more pages (['paging']['next']), break from the
        # loop and end the script.
        break
print(posts)
