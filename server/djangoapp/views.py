# Uncomment the required imports before adding the code

from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth import logout
from django.contrib import messages
from datetime import datetime

from django.http import JsonResponse
from django.contrib.auth import login, authenticate
import logging
import json
from django.views.decorators.csrf import csrf_exempt
from .populate import initiate
from .restapis import get_request, post_review

# Get an instance of a logger
logger = logging.getLogger(__name__)


# Create your views here.

# Create a `login_request` view to handle sign in request
@csrf_exempt
def login_user(request):
    # Get username and password from request.POST dictionary
    data = json.loads(request.body)
    username = data['userName']
    password = data['password']
    # Try to check if provide credential can be authenticated
    user = authenticate(username=username, password=password)
    data = {"userName": username}
    if user is not None:
        # If user is valid, call login method to login current user
        login(request, user)
        data = {"userName": username, "status": "Authenticated"}
    return JsonResponse(data)

# Create a `logout_request` view to handle sign out request
def logout_request(request):
    logout(request) # Terminate user session
    data = {"userName":""} # Return empty username
    return JsonResponse(data)


# Create a `registration` view to handle sign up request
@csrf_exempt
def registration(request):
    context = {}

	# Load JSON data from the request body
    data = json.loads(request.body)
    username = data['userName']
    password = data['password']
    first_name = data['firstName']
    last_name = data['lastName']
    email = data['email']
    username_exist = False
    email_exist = False
    try:
        # Check if user already exists
        User.objects.get(username=username)
        username_exist = True
    except:
        # If not, simply log this is a new user
        logger.debug("{} is new user".format(username))

    # If it is a new user
    if not username_exist:
        # Create user in auth_user table
        user = User.objects.create_user(username=username, first_name=first_name, last_name=last_name,password=password, email=email)
        # Login the user and redirect to list page
        login(request, user)
        data = {"userName":username,"status":"Authenticated"}
        return JsonResponse(data)
    else :
        data = {"userName":username,"error":"Already Registered"}
        return JsonResponse(data)

def get_dealers(request, state=None):
    try:
        if state:
            # Nếu có truyền state (ví dụ: /get_dealers/Texas), gọi sang API lọc của Node.js
            endpoint = f"/fetchDealers/{state}"
        else:
            # Nếu không có state, gọi lấy toàn bộ đại lý
            endpoint = "/fetchDealers"
            
        dealerships = get_request(endpoint)
        return JsonResponse({"status": 200, "dealers": dealerships})
    except Exception as e:
        logger.error(f"Error in get_dealers: {str(e)}")
        return JsonResponse({"status": 500, "message": "Error fetching dealer documents"})
# # Update the `get_dealerships` view to render the index page with
# a list of dealerships
def get_dealerships(request):

    if request.GET.get("state"):
        state = request.GET.get("state")
        dealerships = get_request(
            "/fetchDealers/" + state
        )
    else:
        dealerships = get_request(
            "/fetchDealers"
        )

    return JsonResponse({
        "status": 200,
        "dealers": dealerships
    })

# Create a `get_dealer_reviews` view to render the reviews of a dealer
def get_dealer_reviews(request,dealer_id):
    reviews = get_request(
        "/fetchReviews/dealer/" + str(dealer_id)
    )

    return JsonResponse(
        {
            "status": 200,
            "reviews": reviews
        },
        safe=False
    )

# Create a `get_dealer_details` view to render the dealer details
# Create a `get_dealer_details` view to render the dealer details
def get_dealer_details(request, dealer_id):
    dealer = get_request(
        "/fetchDealer/" + str(dealer_id)
    )
    return JsonResponse(
        {
            "status": 200,
            "dealer": dealer
        }
    )

# Create a `add_review` view to submit a review
@csrf_exempt
def add_review(request):
    if request.user.is_authenticated == False:
        return JsonResponse({"status": 403, "message": "Unauthorized"})
        
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            # Sửa từ post_request("/insert_review", data) thành dòng dưới đây:
            response = post_review(data) 
            return JsonResponse({"status": 200, "message": "Review submitted successfully"})
        except Exception as e:
            logger.error(f"Error in add_review: {str(e)}")
            return JsonResponse({"status": 400, "message": "Error in posting review"})
    else:
        return JsonResponse({"status": 405, "message": "Method Not Allowed"})

# Create a `get_cars` view to fetch car makes and models from backend
def get_cars(request):
    try:
        # Gọi trực tiếp sang microservice cổng 3030 để lấy dữ liệu từ car_records.json
        carmodels = get_request("/fetchCars")
        return JsonResponse({"CarModels": carmodels})
    except Exception as e:
        logger.error(f"Error in get_cars: {str(e)}")
        return JsonResponse({"status": 500, "message": "Error fetching car models"})

# Create an `analyze_review` view to handle sentiment analysis request
def analyze_review(request, text):
    try:
        response = analyze_review_sentiments(text)
        return JsonResponse(response)
    except Exception as e:
        logger.error(f"Error in analyze_review: {str(e)}")
        return JsonResponse({"status": 500, "message": "Error analyzing sentiment"})