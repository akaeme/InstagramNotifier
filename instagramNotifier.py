from instagram.client import InstagramAPI


def run():
    #access_token = input('Access Token: ')
    #client_secret = input('Client Secret: ')

    access_token = '255290884.7729a55.cdbbd915e561453fa81f2c1c8b91fb54'
    client_secret = '57a594edb6e8495cb366ae42acd60f18'

    api = InstagramAPI(access_token=access_token, client_secret=client_secret)
    recent_media, next_ = api.user_recent_media(user_id='255290884')
    photos = []
    print(len(recent_media))
    for media in recent_media:
        print(media.id)
        photos.append('<img src="%s"/>' % media.images['thumbnail'].url)

    follows, next_ = api.user_follows()
    while next_:
        more_follows, next_ = api.user_follows(with_next_url=next_)
        follows.extend(more_follows)


    str='https://api.instagram.com/v1/media/1314630905147227181_255290884/likes?access_token=255290884.7729a55.cdbbd915e561453fa81f2c1c8b91fb54'

if __name__ == "__main__":
    run()
