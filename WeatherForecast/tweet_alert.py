import tweepy
import asyncio
from twitter_token import *


async def twitter_update_status(status):

    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)

    api = tweepy.API(auth)
    api.update_status(status=status)


async def main():

    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)

    tweepy.API(auth)
    print('success')


if __name__ == "__main__":

    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())