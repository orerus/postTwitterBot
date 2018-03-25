class TwitterAPIKey:
# CK = 'HOGEHOGE'                             # Consumer Key
# CS = 'FUGAFUGA'         # Consumer Secret
# AT = '000000000-HOGEFUGA' # Access Token
# AS = 'FUGAHOGE'         # Accesss Token Secret
    consumerKey = ""
    consumerSecret = ""
    accessToken = ""
    accessTokenSecret = ""
    
    def __init__(self, consumerKey, consumerSecret, accessToken, accessTokenSecret):
        self.consumerKey = consumerKey
        self.consumerSecret = consumerSecret
        self.accessToken = accessToken
        self.accessTokenSecret = accessTokenSecret
