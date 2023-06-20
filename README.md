# Crypto Market Sentiment
Analyze the sentiment of the cryptocurrency market based on Google News and Twitter feeds.

# Overview
The program is a Flask API, which accepts the details of the currency to be analyzed in the API request and returns the percentage of the positive or negative score of the market. The GNews (https://github.com/ranahaani/GNews) package is used for getting related news articles based on the keyword given. Snscrape (https://github.com/JustAnotherArchivist/snscrape), is used for scraping tweets from Twitter. The collected data is preprocessed and used for finding the respective sentiment.

# Analyzing the Data

The sentiment of the gathered data is analyzed using the fine-tuned CryptoBERT model, using HuggingFace API.

# Result

![image](https://github.com/KishoreKumar1308/CryptoMarketSentiment/assets/62205360/8fdd0f69-2567-49c6-bf06-59f0368c3b3d)
