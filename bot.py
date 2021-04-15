import alpaca_trade_api as tradeapi
import datetime
import numpy as np
import os
import pandas as pd
import re
import redis
import schedule
from textblob import TextBlob
import time
import tweepy

### Twitter
consumer_key = os.getenv("CONSUMER_KEY")
consumer_secret = os.getenv("CONSUMER_SECRET")
key = os.getenv("KEY")
secret = os.getenv("SECRET")

### Redis
client = redis.Redis(host="10.10.10.1", port=6379, db=0,
                     password=os.getenv("REDIS_PASS"))

### Tweepy
auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(key, secret)
auth.secure = True
api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)

### Alpaca
APCA_API_BASE_URL = os.getenv("APCA_API_BASE_URL")
APCA_API_KEY_ID = os.getenv("APCA_API_KEY_ID")
APCA_API_SECRET_KEY = os.getenv("APCA_API_SECRET_KEY")
alpaca = tradeapi.REST(APCA_API_KEY_ID,
                       APCA_API_SECRET_KEY,
                       APCA_API_BASE_URL,
                       api_version='v2'
                       )

### Global Variables
correct = 0
wrong = 0


def read_last_seen():
    last_seen_id = int(client.get('last_seen_id'))
    return last_seen_id


def store_last_seen(last_seen_id):
    client.set('last_seen_id', str(last_seen_id))
    return


def reply():
    tweets = api.mentions_timeline(read_last_seen(), tweet_mode='extended')
    for tweet in reversed(tweets):
        client.incr("tendie_read")
        try:
            username = tweet.user.screen_name
            # if check_reply(username, tweet):
            #     if 'follow back' in tweet.full_text.lower() and 'thanks' not in tweet.full_text.lower():
            #         api.update_status("@" + username +
            #                           " please be patient.")
            #         print("Replied to follow back request")
            #         try:
            #             api.destroy_friendship(username)
            #             print(f"Terminated friendship with {username}")
            #         except tweepy.TweepError as e:
            #             print(e)
            #         store_last_seen(tweet.id)
            #         return
            #     print("Replied to - " + username +
            #           " - " + tweet.full_text)
            #     api.update_status("@" + username +
            #                         " Hello, " + username + ", just a moment. " + 
            #                         "@CalendarKy @statutorywheel, can I please get some help?", tweet.id)
            #     store_last_seen(tweet.id)
            
            print("Favorited " + username +
                    " - " + tweet.full_text)
            api.create_favorite(tweet.id)
            store_last_seen(tweet.id)
        except tweepy.TweepError as e:
            store_last_seen(tweet.id)
            print(e.reason)
        time.sleep(2)


def check_reply(username, tweet):
    if username != "CalendarKy" and username != "statutorywheel" and tweet.full_text[:11] != "@CalendarKy" \
            and tweet.full_text[:11] != "@statutorywheel" and tweet.full_text[:17] != "@InternTendie and" \
            and tweet.full_text[:14] != "@InternTendie @":
        return True
    return False

def dm_reply():
    last_seen = int(client.get('dm_seen'))
    messages = api.list_direct_messages(last_seen)
    for message in reversed(messages):
        sender_id = message.message_create['sender_id']
        ## moving this if statement for quicker runtime ;]
        if not client.sismember('sent_dm', str(sender_id)):
            text = message.message_create['message_data']['text']
            # print(text)
            if check_dm(text.lower()):
                github_dm(sender_id)
        last_seen = message.id
    client.set('dm_seen', str(last_seen))


def check_dm(text):
    if 'yes' in text.lower() or 'yea' in text.lower() or 'send it' in text.lower() or 'yep' in text.lower() or 'sure' in text.lower() or 'ya' in text.lower() or 'yuh' in text.lower():
        return True
    return False

def github_dm(sender_id):
    client.sadd('sent_dm', str(sender_id))
    to_string = "\nAwesome, here is the link! Let me know what you think!\n" + \
        "https://github.com/abspen1/twitter-bot"
    api.send_direct_message(sender_id, to_string)

    # Subtract one here since I added my ID to ignore also
    num = client.scard('sent_dm') - 1
    print(f"Sent github dm : {num}")


def searchBot():
    client.incr("tendie_read", 50)
    print("Running #python search.")
    tweets = tweepy.Cursor(api.search, "#python").items(50)
    # print("Running first search.")
    print(time.ctime())
    i = 0
    for tweet in tweets:
        i += 1
        try:
            # print("Retweet done!")
            if i % 50 == 0:
                # tweet.retweet()
                print(f"Favorited {i} #python tweets.")
            api.create_favorite(tweet.id)
            time.sleep(2)
        except tweepy.TweepError as e:
            if e.reason[:13] == "[{'code': 139":
                continue
            elif e.reason[:13] == "[{'code': 283" or e.reason[:13] == "[{'code': 429":
                print("Malicious activity suspected. Ending searchBot.")
                return
            else:
                print(e.reason)
            time.sleep(2)


def searchBot2():
    client.incr("tendie_read", 50)

    print("Running javascript search.")
    tweets = tweepy.Cursor(api.search, "javascript").items(40)
    print(time.ctime())
    i = 0
    for tweet in tweets:
        try:
            i += 1
            if i % 25 == 0:
                # tweet.retweet()
                print(f"Favorited {i} javascript tweets.")
            api.create_favorite(tweet.id)
            time.sleep(2)
        except tweepy.TweepError as e:
            if e.reason[:13] == "[{'code': 139":
                continue
            elif e.reason[:13] == "[{'code': 283" or e.reason[:13] == "[{'code': 429":
                print("Malicious activity suspected. Ending searchBot2.")
                return
            else:
                print(e.reason)
            time.sleep(2)


def searchBot3():
    client.incr("tendie_read", 30)

    print("Running algorithm search.")
    tweets = tweepy.Cursor(api.search, "algorithm").items(30)
    # print("Running third search.")
    print(time.ctime())
    i = 0
    for tweet in tweets:
        try:
            i += 1
            if i % 20 == 0:
                print(f"Favorited {i} algorithm tweets")
            api.create_favorite(tweet.id)
            time.sleep(2)
        except tweepy.TweepError as e:
            if e.reason[:13] == "[{'code': 139":
                continue
            elif e.reason[:13] == "[{'code': 283" or e.reason[:13] == "[{'code': 429":
                print("Malicious activity suspected. Ending searchBot3.")
                return
            else:
                print(e.reason)
            time.sleep(2)


def tweet_sentiment():
    print("Running tweet_sentiment()")
    client = redis.Redis(host="10.10.10.1", port=6379, db=0,
                         password=os.getenv("REDIS_PASS"))
    sentiment = client.get('twit_bot').decode("utf-8")
    status = f"I am currently {sentiment} the stock market."
    print(status)
    api.update_status(status)
    client.set("tendie_recent", status)


def scrape_twitter(maxTweets, searchQuery, redisDataBase):
    client.delete(redisDataBase)
    # print(f"Downloading max {maxTweets} tweets")
    retweet_filter = '-filter:retweets'
    q = searchQuery+retweet_filter
    tweetCount = 0
    max_id = -1
    tweetsPerQry = 100
    redisDataBase = 'tweets_scraped'
    sinceId = None
    while tweetCount < (maxTweets-50):
        try:
            if (max_id <= 0):
                if (not sinceId):
                    new_tweets = api.search(
                        q=q, lang="en", count=tweetsPerQry, tweet_mode='extended')
                else:
                    new_tweets = api.search(q=q, lang="en", count=tweetsPerQry,
                                            since_id=sinceId, tweet_mode='extended')
            else:
                if (not sinceId):
                    new_tweets = api.search(q=q, lang="en", count=tweetsPerQry,
                                            max_id=str(max_id - 1), tweet_mode='extended')
                else:
                    new_tweets = api.search(q=q, lang="en", count=tweetsPerQry,
                                            max_id=str(max_id - 1),
                                            since_id=sinceId, tweet_mode='extended')
            if not new_tweets:
                print("No more tweets found")
                break
            for tweet in new_tweets:
                client.sadd(redisDataBase, (str(tweet.full_text.replace(
                    '\n', '').encode("utf-8"))+"\n"))
            tweetCount += len(new_tweets)
            max_id = new_tweets[-1].id
        except tweepy.TweepError as e:
            # Just exit if any error
            print("some error : " + str(e))
            break
    client.incr('tendie_read', tweetCount)


def clean(tweet):
    tweet = re.sub(r'^RT[\s]+', '', tweet)
    tweet = re.sub(r'https?:\/\/.*[\r\n]*', '', tweet)
    tweet = re.sub(r'#', '', tweet)
    tweet = re.sub(r'@[A-Za-z0–9]+', '', tweet)
    return tweet


def read_tweets(redis_set):
    f = client.smembers(redis_set)
    tweets = [clean(sentence.decode("utf-8").strip()) for sentence in f]
    return tweets


def polarity(x): return TextBlob(x).sentiment.polarity


def subjectivity(x): return TextBlob(x).sentiment.subjectivity


def run_scraper():
    print("Running data scraper.")
    redisDataBase = "tweets_scraped"
    scrape_twitter(3000, 'stock market', redisDataBase)
    f = read_tweets(redisDataBase)
    tweet_polarity = np.zeros(client.scard(redisDataBase))
    tweet_subjectivity = np.zeros(client.scard(redisDataBase))
    bullish_count = 0
    bearish_count = 0
    for idx, tweet in enumerate(f):
        tweet_polarity[idx] = polarity(tweet)
        tweet_subjectivity[idx] = subjectivity(tweet)
        if tweet_polarity[idx] > 0.15 and tweet_subjectivity[idx] < 0.5:
            bullish_count += 1
        elif tweet_polarity[idx] < 0.00 and tweet_subjectivity[idx] < 0.5:
            bearish_count += 1

    bullish_count -= 35
    sentiment = (bullish_count) - bearish_count
    client.incr('sent_number')
    sent_num = int(client.get('sent_number'))
    to_string = f"Reading #{sent_num} => Twitter's sentiment of the stock market is"
    if sentiment > 5:
        client.sadd("bullish_date", str(datetime.date.today()))
        to_string = f"{to_string} bullish with a reading of {sentiment}."
        current_high = int(client.get('highest_sentiment'))
        if sentiment > current_high:
            client.set('highest_sentiment', str(sentiment))
            to_string = f"{to_string} This is the highest reading to date."
    elif sentiment > -5:
        to_string = f"{to_string} nuetral with a reading of {sentiment}."
    else:
        client.sadd("bearish_date", str(datetime.date.today()))
        to_string = f"{to_string} bearish with a reading of {sentiment}."
        current_low = int(client.get('lowest_sentiment'))
        if sentiment < current_low:
            client.set('lowest_sentiment', str(sentiment))
            to_string = f"{to_string} This is the lowest reading to date."
    print(to_string)
    api.update_status(to_string)
    client.set("tendie_recent", to_string)


# This is purely to gain followers by following people that follow back
def auto_follow2():
    client.incr('tendie_read', 50)
    query = "ifb"
    print(f"Following users who have tweeted about the {query}")
    search = tweepy.Cursor(api.search, q=query,
                           result_type="recent", lang="en").items(50)
    num_followed = 0
    for tweet in search:
        if tweet.user.followers_count > 5000:
            continue
        try:
            api.create_favorite(tweet.id)
            time.sleep(2)
        except tweepy.TweepError as e:
            if e.reason[:13] != "[{'code': 139":
                print(e.reason)
            time.sleep(2)
        try:
            api.create_friendship(tweet.user.id)
            time.sleep(2)
            num_followed += 1
        except tweepy.TweepError as e:
            if e.reason[:13] == "[{'code': 160":
                continue
            elif e.reason[:13] == "[{'code': 429" or e.reason[:13] == "[{'code': 326":
                print("Followed too many people... ending auto_follow2")
                return
            time.sleep(2)
    client.incr('tendie_read', 50)
    query = "follow back"
    print(f"Following users who have tweeted about the {query}")
    search = tweepy.Cursor(api.search, q=query,
                           result_type="recent", lang="en").items(50)
    for tweet in search:
        if tweet.user.followers_count > 5000:
            continue
        try:
            api.create_favorite(tweet.id)
            time.sleep(2)
        except tweepy.TweepError as e:
            if e.reason[:13] != "[{'code': 139":
                print(e.reason)
            time.sleep(2)
        try:
            api.create_friendship(tweet.user.id)
            time.sleep(2)
            num_followed += 1
        except tweepy.TweepError as e:
            if e.reason[:13] == "[{'code': 160":
                continue
            elif e.reason[:13] == "[{'code': 429" or e.reason[:13] == "[{'code': 326":
                print("Followed too many people... ending auto_follow2")
                return
            time.sleep(2)
    print(f"Now following {num_followed} more users.")


# This is trying to get followers that will be active and interested in my content
def auto_follow():
    client.incr('tendie_read', 50)

    query = "computer science"
    # print(f"Following users who have tweeted about the {query}")
    search = tweepy.Cursor(api.search, q=query,
                           result_type="recent", lang="en").items(50)
    num_followed = 0
    for tweet in search:
        if tweet.user.followers_count > 3000:
            continue
        try:
            api.create_favorite(tweet.id)
            time.sleep(2)
        except tweepy.TweepError as e:
            if e.reason[:13] != "[{'code': 139":
                print(e.reason)
            time.sleep(2)
        try:
            api.create_friendship(tweet.user.id)
            time.sleep(5)
            num_followed += 1
        except tweepy.TweepError as e:
            if e.reason[:13] == "[{'code': 160":
                continue
            elif e.reason[:13] == "[{'code': 429" or e.reason[:13] == "[{'code': 283":
                print(f"Now following {num_followed} more users.")
                print("Followed too many people... ending auto_follow")
                return
            else:
                print(e.reason)
            time.sleep(2)

    # Switch up the query
    client.incr('tendie_read', 50)

    query = "programming"
    search = tweepy.Cursor(api.search, q=query,
                           result_type="recent", lang="en").items(50)
    for tweet in search:
        if tweet.user.followers_count > 3000:
            continue
        try:
            api.create_favorite(tweet.id)
            time.sleep(2)
        except tweepy.TweepError as e:
            if e.reason[:13] != "[{'code': 139":
                print(e.reason)
            time.sleep(2)
        try:
            api.create_friendship(tweet.user.id)
            time.sleep(5)
            num_followed += 1
        except tweepy.TweepError as e:
            if e.reason[:13] == "[{'code': 160":
                continue
            elif e.reason[:13] == "[{'code': 429" or e.reason[:13] == "[{'code': 283":
                print("Followed too many people... ending auto_follow")
                print(f"Now following {num_followed} more users.")
                return
            else:
                print(e.reason)
            time.sleep(2)
    print(f"Now following {num_followed} more users.")

    # Switch up the query
    client.incr('tendie_read', 20)

    query = "python program"
    search = tweepy.Cursor(api.search, q=query,
                           result_type="recent", lang="en").items(20)
    for tweet in search:
        if tweet.user.followers_count > 3000:
            continue
        try:
            api.create_favorite(tweet.id)
            time.sleep(2)
        except tweepy.TweepError as e:
            if e.reason[:13] != "[{'code': 139":
                print(e.reason)
            time.sleep(2)
        try:
            api.create_friendship(tweet.user.id)
            time.sleep(5)
            num_followed += 1
        except tweepy.TweepError as e:
            if e.reason[:13] == "[{'code': 160":
                continue
            elif e.reason[:13] == "[{'code': 429" or e.reason[:13] == "[{'code': 283":
                print("Followed too many people... ending auto_follow")
                print(f"Now following {num_followed} more users.")
                return
            else:
                print(e.reason)
            time.sleep(2)
    print(f"Now following {num_followed} more users.")


def unfollow():
    print("Running unfollow()")
    friendNames, followNames = [], []
    try:
        for friend in tweepy.Cursor(api.friends).items(300):
            if friend.followers_count < 5000:
                friendNames.append(friend.screen_name)

        for follower in tweepy.Cursor(api.followers).items(300):
            followNames.append(follower.screen_name)

    except tweepy.TweepError as e:
        print(e.reason)
        time.sleep(2)
    friendset = set(friendNames)
    followset = set(followNames)
    not_fback = friendset.difference(followset)
    unfollow_count = 0
    for not_following in not_fback:
        try:
            unfollow_count += 1
            api.destroy_friendship(not_following)
        except tweepy.TweepError as e:
            print(e.reason)
        time.sleep(5)
    print(f"Unfollowed: {unfollow_count} losers.")


def thank_new_followers():
    total_followers = client.scard('followers_thanked')
    followers_thanked = []
    followers = []
    for follower in list(client.smembers('followers_thanked')):
        followers_thanked.append(follower.decode("utf-8"))
    followers_thanked = set(followers_thanked)
    follow_count = 0
    limit = False
    for follower in tweepy.Cursor(api.followers).items(100):
        followers.append(str(follower.id))
        #follower has a long list of possible things to see.. kinda neat
        if not follower.following:
            try:
                follower.follow()
                follow_count += 1
                # Moved this print statement so that if there is an error we don't print 
                # print(f"Following {follower.name}")
            except tweepy.TweepError as e:
                """ Ignores error that we've already tried to follow this person
                    The reason we're ignoring this error is because if someone is private
                    we will keep trying to follow them until they accept our follow. Which 
                    will give the error of already pending request.
                """
                if e.reason[:13] == "[{'code': 160":
                    continue
                elif e.reason[:13] == "[{'code': 161" or e.reason[:13] == "[{'code': 429":
                    print("Following limit hit!!")
                    limit = True
                    break
                elif e.reason[:13] == "[{'code': 283":
                    print("Malicious activity suspected. Can't follow back right now.")
                    limit = True
                    break
                else:
                    print(e.reason)
            time.sleep(3)
    if follow_count > 0:
        print(f"Tendie followed back {follow_count} people.")
    followers_set = set(followers)
    new_followers = followers_set.difference(followers_thanked)
    if new_followers:
        for follower in new_followers:
            client.sadd('followers_thanked', str(follower))
        trouble = False
        to_string = "\nAppreciate you following me! I am a fully automated twitter account. If you're interested in programming or if you'd like to create an automated twitter account of your own, I can send you a link to my GitHub Repository!\n" + \
            "If your next message has 'yes' anywhere in it I will send you a link!"
        if limit:
            to_string = f"{to_string}\nSorry, I've hit a following limit and will follow you back ASAP!"
        for follower in new_followers:
            if not trouble:
                try:
                    client.sadd('followers_thanked', str(follower))
                    # api.send_direct_message(follower, to_string)
                except tweepy.TweepError as e:
                    if e.reason[:13] == "[{'code': 226" or e.reason[:13] == "[{'code': 429":
                        print("They think this is spam...")
                        trouble = True
                    else:
                        print(e)
                time.sleep(3)
            else:
                try:
                    client.sadd('followers_thanked', str(follower))
                except tweepy.TweepError as e:                        
                    print(e)
        new_total_followers = client.scard('followers_thanked')
        total_followers = new_total_followers - total_followers
        print(f"Tendie Intern has {total_followers} new followers. Total of {new_total_followers} followers.")
    time.sleep(60)


def specific_favorite():
    client = redis.Redis(host="10.10.10.1", port=6379, db=0,
                         password=os.getenv("REDIS_PASS"))
    sinceId = 'ky_since_id'
    # client.set(sinceId, '1285706104433979392')
    tweet_id = int(client.get(sinceId))
    tweets = api.home_timeline(since_id=tweet_id, include_rts=1, count=200)
    for tweet in reversed(tweets):
        client.incr('tendie_read')
        client.set(sinceId, str(tweet.id))
        try:
            if tweet.user.screen_name == 'CalendarKy' or tweet.user.screen_name == 'statutorywheel':
                if str(tweet.text)[:1] != "@" and str(tweet.text)[:2] != "RT":
                    api.create_favorite(tweet.id)
                    # tweet.retweet()
                    # print(client.get(sinceId))
                    print(f"Favorited {tweet.user.screen_name}'s tweet.")
                    time.sleep(3)
        except tweepy.TweepError as e:
            if e.reason[:13] != "[{'code': 139":
                print(e.reason)
            time.sleep(3)
        time.sleep(1)


def send_error_message(follower):
    try:
        to_string = "I errored out.. going to sleep for 2 hours.."
        api.send_direct_message(follower, to_string)
        print("Sent dm to 441228378 since we errored out.")
    except tweepy.TweepError as e:
        if e.reason[:13] != "[{'code': 139" or e.reason[:13] != "[{'code': 226" or e.reason[:13] != "[{'code': 429":
            print(e.reason)
        time.sleep(10*60)
        send_error_message(441228378)


def cleanDates():
    bullish = client.smembers("bullish_date")
    bearish = client.smembers("bearish_date")
    delete = 0
    for date in bullish:
        if date in bearish:
            print(date.decode("utf-8"))
            client.srem("bearish_date", date.decode("utf-8"))
            delete += 1
    print(f"removed {delete} dates from bearish")


def getSentimentAccuracy():
    cleanDates()
    bullishDates = client.smembers("bullish_date")
    bearishDates = client.smembers("bearish_date")
    for date in bullishDates:
        date = date.decode("utf-8") + "T09:30:00-04:00"
        checkBullish(date)

    for date in bearishDates:
        date = date.decode("utf-8") + "T09:30:00-04:00"
        checkBearish(date)
    getPct()

def checkBullish(date):
    global correct
    global wrong
    bars = alpaca.get_barset("SPY", "day", start=date, limit=100)
    day1 = bars["SPY"][0].c
    try:
        day2 = bars["SPY"][1].c
    except Exception as e:
        print(e)
        return

    if day2 > day1:
        correct += 1
    else:
        wrong += 1


def checkBearish(date):
    global correct
    global wrong
    bars = alpaca.get_barset("SPY", "day", start=date, limit=100)
    day1 = bars["SPY"][0].c
    try:
        day2 = bars["SPY"][1].c
    except Exception as e:
        if e != "list index out of range":
            print(e)
        return
    if day2 > day1:
        wrong += 1
    else:
        correct += 1

def getPct():
    pct = (correct / (correct + wrong)) * 100
    pct = "{:.2f}".format(pct)
    print(f"Correct: {correct} Incorrect: {wrong}")
    print(f"Percentage of accuracy: {pct}%")
    client.set("tendie_pct", pct)

def webapp_update():
    acct = api.get_user("interntendie")
    client.set("tendie_followers", str(acct.followers_count))
    client.set("tendie_favorites", str(acct.favourites_count))
    client.set("tendie_statuses", str(acct.statuses_count))


####### Set Our Scheduled Jobs ########
## Multiple runs per day
schedule.every(4).minutes.do(dm_reply)
# schedule.every(7).minutes.do(specific_favorite)
# schedule.every(9).minutes.do(webapp_update)
# schedule.every(30).minutes.do(reply)
schedule.every(15).minutes.do(thank_new_followers)
schedule.every(7).hours.do(run_scraper)
## Daily runs
schedule.every().day.at("01:00").do(cleanDates)
# schedule.every().day.at("08:26").do(auto_follow2)
# schedule.every().day.at("10:17").do(searchBot)
# schedule.every().day.at("13:26").do(auto_follow)
# schedule.every().day.at("12:12").do(searchBot2)
schedule.every().day.at("15:13").do(tweet_sentiment)
# schedule.every().day.at("17:07").do(searchBot3)
## Weekly runs
schedule.every().thursday.at("03:37").do(unfollow)
schedule.every().week.do(unfollow)

print("Running twitter-bot")
run_scraper()


while True:
    try:
        schedule.run_pending()
        time.sleep(1)
    except tweepy.TweepError as e:
        print(e.reason)
        send_error_message(441228378)
        time.sleep(2*60*60)
