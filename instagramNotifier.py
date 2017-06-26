from InstagramAPI import InstagramAPI


def run():
    InstagramAPI = InstagramAPI("akaemee", "napster3680fabiosilva")
    InstagramAPI.login()  # login

    # InstagramAPI.tagFeed("flowers") # get media list by tag #cat
    # media_id = InstagramAPI.LastJson # last response JSON
    # InstagramAPI.like(media_id["ranked_items"][0]["pk"]) # like first media

    InstagramAPI.getSelfUserFollowers()
    # last response JSON
    media_id = InstagramAPI.LastJson
    print(media_id)

    # print(type(InstagramAPI.getUserFollowers(media_id["ranked_items"][0]["user"]["pk"]))) # get first media owner
    # followers

if __name__ == "__main__":
    run()
