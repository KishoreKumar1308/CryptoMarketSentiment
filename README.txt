Creating a Python Virtual Environment
-------------------------------------
1. Open command prompt on the same folder SentimentAnalysis folder is present
2. pip install --upgrade pip
3. mkdir python-env
4. cd python-env
5. python -m venv .
6. Scripts\activate
7. cd ..
8. cd SentimentAnalysis
9. pip install -r requirements.txt
-------------------------------------

Running the Program
-------------------------------------
1. The program is a Flask API

python .\MarketSentiment.py

This will run the API at http://127.0.0.1:5000
User data/queries can be passed to the API using Postman/Hoppscoth to make prediction.
The request must be sent to http://127.0.0.1:5000/sentiment

The Request body looks like

{
    "Keyword":"Bitcoin",
    "Duration":8,
    "NumResults":100
}

Keyword --> the word for which analysis must be done
Duration --> How many hours of data should be fetched
NumResults --> How many data should be fetched

2. After scraping data from both Google News and Twitter, the program uses pretrained CryptoBERT to identify overall market sentiment