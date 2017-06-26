from API.InstagramAPI import InstagramAPI


def run():
    api = InstagramAPI("akaemee", "napster3680fabiosilva")
    api.login()  # login

    # InstagramAPI.tagFeed("flowers") # get media list by tag #cat
    # media_id = InstagramAPI.LastJson # last response JSON
    # InstagramAPI.like(media_id["ranked_items"][0]["pk"]) # like first media
    # Changed API to getSelfUserFollowers receive a argument to permit pagiation

    api.getSelfUserFollowers('AQBeBCNjxpVN503LwVNv9Llm02-fOhBWVm-Rl4ehS_AX6AN9t5PpMJQxMLWhqjHIPYn9LuhxY9jUSjfVec7y6iIcoen4cQ1Jrmnuq5Zu-szQcw')
    # last response JSON
    followers = api.LastJson
    print(len(followers['users']))
    print(followers)

    # print(type(InstagramAPI.getUserFollowers(media_id["ranked_items"][0]["user"]["pk"]))) # get first media owner
    # followers

if __name__ == "__main__":
    run()
