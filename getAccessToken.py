from InstagramOAuthAPI import InstagramOAuthAPI

client_id = input("Client ID: ").strip()
client_secret = input("Client Secret: ").strip()
redirect_uri = input("Redirect URI: ").strip()
scope = ['basic', 'public_content', 'follower_list', 'comments', 'relationships', 'likes']

client = InstagramOAuthAPI(client_id=client_id, client_secret=client_secret, redirect_uri=redirect_uri)

# Build the authorization url
url = client.auth_url(scope=scope, response_type='code')

print("Visit this page and authorize access in your browser: " + url)

code = (str(input("Paste in code in query string after redirect: ").strip()))

access_token = client.exchange_code_for_access_token(code)
print("access token: ")
print(access_token)
