from fastapi import FastAPI
from pydantic import BaseModel, Field
from fastapi import Query
from typing import Optional

app = FastAPI()
#FastAPI created 
@app.get("/")
def home():
    return {"message": "Hello! Welcome to CineStar Booking"}
#Movie list
movies = [
    {"id": 1, "title": "Spiderman", "genre": "Action", "language": "English", "duration_mins": 130, "ticket_price": 300, "seats_available": 50},
    {"id": 2, "title": "3 Idiots", "genre": "Drama", "language": "Hindi", "duration_mins": 170, "ticket_price": 200, "seats_available": 40},
    {"id": 3, "title": "KGF", "genre": "Action", "language": "Kannada", "duration_mins": 155, "ticket_price": 250, "seats_available": 60},
    {"id": 4, "title": "Tees Maar Khan", "genre": "Comedy", "language": "Hindi", "duration_mins": 135, "ticket_price": 150, "seats_available": 30},
    {"id": 5, "title": "Main Hoon Na", "genre": "Action/Drama", "language": "Hindi", "duration_mins": 180, "ticket_price": 220, "seats_available": 45},
    {"id": 6, "title": "Om Shanti Om", "genre": "Drama/Fantasy", "language": "Hindi", "duration_mins": 165, "ticket_price": 210, "seats_available": 35},
    {"id": 7, "title": "The Conjuring", "genre": "Horror", "language": "English", "duration_mins": 112, "ticket_price": 240, "seats_available": 25},
    {"id": 8, "title": "Hera Pheri", "genre": "Comedy", "language": "Hindi", "duration_mins": 156, "ticket_price": 190, "seats_available": 55},
]
#Movie list 
@app.get("/movies")
def get_movies():
    total_seats = sum(m["seats_available"] for m in movies)
    return {
        "movies": movies,
        "total_movies": len(movies),
        "total_seats_available": total_seats
    }
#Summary of all movies
@app.get("/movies/summary")
def movie_summary():
    genres = {}
    for m in movies:
        genres[m["genre"]] = genres.get(m["genre"], 0) + 1

    return {
        "total_movies": len(movies),
        "most_expensive": max(movies, key=lambda x: x["ticket_price"])["ticket_price"],
        "cheapest": min(movies, key=lambda x: x["ticket_price"])["ticket_price"],
        "total_seats": sum(m["seats_available"] for m in movies),
        "movies_by_genre": genres
    }
#Filtering of Movies
@app.get("/movies/filter")
def filter_movies(
    genre: Optional[str] = None,
    language: Optional[str] = None,
    max_price: Optional[int] = None,
    min_seats: Optional[int] = None
):
    result = movies

    if genre is not None:
        result = [m for m in result if genre.lower() in m["genre"].lower()]

    if language is not None:
        result = [m for m in result if language.lower() == m["language"].lower()]

    if max_price is not None:
        result = [m for m in result if m["ticket_price"] <= max_price]

    if min_seats is not None:
        result = [m for m in result if m["seats_available"] >= min_seats]

    return {
        "filtered_movies": result,
        "count": len(result)
    }


#Get movie by ID
@app.get("/movies/{movie_id}")
def get_movie(movie_id: int):
    for movie in movies:
        if movie["id"] == movie_id:
            return movie
    return {"error": "Movie not found"}

bookings = []
booking_counter = 1
@app.get("/bookings")
def get_bookings():
    total_revenue = sum(b["discounted_cost"] for b in bookings) if bookings else 0
    return {
        "bookings": bookings,
        "total_bookings": len(bookings),
        "total_revenue": total_revenue
    }



#Booking in FastApi

class BookingRequest(BaseModel):
    customer_name: str = Field(..., min_length=2)
    movie_id: int = Field(..., gt=0)
    seats: int = Field(..., gt=0, le=10)
    phone: str = Field(..., min_length=10)
    seat_type: str = "standard"
    promo_code: str = ""

def find_movie(movie_id: int):
    for movie in movies:
        if movie["id"] == movie_id:
            return movie
    return None

#Ticket Price Calculator
def calculate_ticket_cost(base_price, seats, seat_type, promo_code):
    multiplier = 1

    if seat_type == "premium":
        multiplier = 1.5
    elif seat_type == "recliner":
        multiplier = 2

    original_cost = base_price * seats * multiplier
#Added Discount feature for online bookings of movie tickets

    discount = 0
    if promo_code == "SAVE10":
        discount = 0.1
    elif promo_code == "SAVE20":
        discount = 0.2

    discounted_cost = original_cost * (1 - discount)

    return {
        "original_cost": original_cost,
        "discounted_cost": discounted_cost
    }
#Core booking System: 
@app.post("/bookings")
def create_booking(request: BookingRequest):
    global booking_counter

    movie = find_movie(request.movie_id)

    if not movie:
        return {"error": "Movie not found"}

    if movie["seats_available"] < request.seats:
        return {"error": "Not enough seats available"}

    cost = calculate_ticket_cost(
        movie["ticket_price"],
        request.seats,
        request.seat_type,
        request.promo_code
    )


    movie["seats_available"] -= request.seats

    booking = {
        "booking_id": booking_counter,
        "customer_name": request.customer_name,
        "movie_title": movie["title"],
        "seats": request.seats,
        "seat_type": request.seat_type,
        "original_cost": cost["original_cost"],
        "discounted_cost": cost["discounted_cost"]
    }

    bookings.append(booking)
    booking_counter += 1

    return booking

