# Uncomment the imports below before you add the function code
import requests
import os
from dotenv import load_dotenv

load_dotenv()

backend_url = os.getenv(
    'backend_url', default="http://localhost:3030")
sentiment_analyzer_url = os.getenv(
    'sentiment_analyzer_url',
    default="http://localhost:5050/")

def get_request(endpoint, **kwargs):
    params = kwargs

    response = requests.get(
        url=backend_url + endpoint,
        params=params
    )

    return response.json()

# Analyze review sentiments
def analyze_review_sentiments(text):

    request_url = sentiment_analyzer_url + "analyze/" + text

    response = requests.get(request_url)

    return response.json()


# POST review to backend
def post_review(data_dict):

    response = requests.post(
        backend_url + "/insert_review",
        json=data_dict
    )

    return response.json()
