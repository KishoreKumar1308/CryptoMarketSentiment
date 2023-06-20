import re
from gnews import GNews
import time
import pandas as pd
import snscrape.modules.twitter as sntwitter
from flask import Flask, request, jsonify
import requests


API_URL = "https://api-inference.huggingface.co/models/kk08/CryptoBERT"
headers = {"Authorization": "YOUR HUGGING FACE API KEY"}

app = Flask(__name__)

def getNewsData(keyword:str, duration:int, num_results:int = 20) -> pd.DataFrame:
    """
    Scrape data from Google News.
    Given key word which should be searched for, the function would scrape the news articles from Google News
    """

    scraper = GNews(language = "en", country = "US", max_results = num_results, period = f"{duration}h")
    json_response = scraper.get_news(keyword)

    df = pd.DataFrame(json_response)
    df = df[["published date","description"]]

    return df


def getTweetData(keyword:str, duration:int, num_results:int = 100) -> pd.DataFrame:
    """
    Scrape data from Twitter
    Given the key word which should be searched for, the function would scrape Tweets from Twitter
    """
    tweets_list = []

    for i,tweet in enumerate(sntwitter.TwitterSearchScraper(f"{keyword}",mode = sntwitter.TwitterSearchScraperMode.TOP).get_items()):
        if i > num_results:
            break
        tweets_list.append([tweet.date,tweet.rawContent])

    df = pd.DataFrame(tweets_list, columns = ["Date","Tweet"])

    return df


def query(payload):
    response = requests.post(API_URL, headers=headers, json=payload)
    if "error" in list(response.json()):
        while True:
            print("\nSentiment API starting. Program Execution will continue in 30 seconds\n")
            time.sleep(30)
            response = requests.post(API_URL, headers=headers, json=payload)
            if "error" in list(response.json()):
                continue
            else:
                break
    
    return response.json()


def getSentiment(data:pd.DataFrame,text_col:str) -> pd.DataFrame:
    sentiments = list(query(data[text_col].to_list()))
    labels = [s[0]["label"] for s in sentiments]
    scores = [s[0]["score"] for s in sentiments]
    data["Sentiment"] = labels
    data["Score"] = scores

    return data


def sliceText(text, keyword):
    text = re.sub(r'@\S+',' ',text)
    text = re.sub(r'http\S+',' ',text)
    text = re.sub(r"[^a-zA-Z0-9]"," ",text)
    words = text.lower().split()
    if keyword.lower() not in words:
        return None
    keyword_index = words.index(keyword.lower())
    start_index = max(keyword_index - 3, 0)
    end_index = min(keyword_index + 4, len(words))
    return ' '.join(words[start_index:end_index])


@app.route("/sentiment",methods = ["GET","POST"])
def findSentiment():

    json_ = request.json
    keyword = json_["Keyword"]
    duration = json_["Duration"]
    num_results = json_["NumResults"]
    
    news_data = getNewsData(keyword, duration, num_results)
    tweet_data = getTweetData(keyword,duration,num_results)

    news_data.to_csv(f"{keyword}_news_unprocessed.csv",index = False)
    tweet_data.to_csv(f"{keyword}_tweet_unprocessed.csv",index = False)

    news_data["description"] = news_data["description"].apply(sliceText,keyword = keyword)
    tweet_data["Tweet"] = tweet_data["Tweet"].apply(sliceText,keyword = keyword)

    news_data.dropna(inplace = True)
    tweet_data.dropna(inplace = True)

    news_data = getSentiment(news_data,"description")
    tweet_data = getSentiment(tweet_data,"Tweet")

    news_values = news_data["Sentiment"].value_counts()
    tweet_values = tweet_data["Sentiment"].value_counts()

    news_data.to_csv(f"{keyword}_news.csv",index = False)
    tweet_data.to_csv(f"{keyword}_tweet.csv",index = False)

    try:
        market_negative_values = news_values["LABEL_0"] 
    except:
        market_negative_values = 0

    try:
        tweet_negative_values = tweet_values["LABEL_0"]
    except:
        tweet_negative_values = 0
    
    try:
        market_positive_values = news_values["LABEL_1"] 
    except:
        market_positive_values = 0
    
    try:
        tweet_positive_values = tweet_values["LABEL_1"]
    except:
        tweet_positive_values = 0

    out_response = {}

    if market_negative_values > market_positive_values:
        out_response["News"] = "Negative"
        try:
            out_response["News Sentiment Percent"] = (market_negative_values / (market_positive_values + market_negative_values)) * 100
        except:
            out_response["News Sentiment Percent"] = 0
    else:
        out_response["News"] = "Positive"
        try:
            out_response["News Sentiment Percent"] = (market_positive_values / (market_positive_values + market_negative_values)) * 100
        except:
            out_response["News Sentiment Percent"] = 0

    if tweet_negative_values > tweet_positive_values:
        out_response["Twitter"] = "Negative"
        try:
            out_response["Twitter Sentiment Percent"] = (tweet_negative_values / (tweet_positive_values + tweet_negative_values)) * 100
        except:
            out_response["Twitter Sentiment Percent"] = 0
    else:
        out_response["Twitter"] = "Positive"
        try:
            out_response["Twitter Sentiment Percent"] = (tweet_positive_values / (tweet_positive_values + tweet_negative_values)) * 100
        except:
            out_response["Twitter Sentiment Percent"] = 0

    return jsonify(out_response)


if __name__ == "__main__":
    app.run(debug = True,port = 5500)