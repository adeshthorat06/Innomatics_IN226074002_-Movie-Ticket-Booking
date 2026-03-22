from fastapi import FastAPI
from pydantic import BaseModel, Field
from fastapi import Query
from typing import Optional
import math


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

@app.get("/movies/browse")
def browse_movies(
    keyword: str = None,
    genre: str = None,
    language: str = None,
    sort_by: str = "ticket_price",
    order: str = "asc",
    page: int = 1,
    limit: int = 3
):
    result = movies

    #  Search
    if keyword:
        result = [
            m for m in result
            if keyword.lower() in m["title"].lower()
            or keyword.lower() in m["genre"].lower()
            or keyword.lower() in m["language"].lower()
        ]

    #  Filter
    if genre:
        result = [m for m in result if genre.lower() in m["genre"].lower()]

    if language:
        result = [m for m in result if language.lower() == m["language"].lower()]

    #  Sort
    reverse = True if order == "desc" else False
    result = sorted(result, key=lambda x: x[sort_by], reverse=reverse)

    #  Pagination
    total = len(result)
    start = (page - 1) * limit
    end = start + limit

    return {
        "total": total,
        "page": page,
        "results": result[start:end]
    }



@app.get("/movies/page")
def paginate_movies(page: int = 1, limit: int = 3):
    total = len(movies)
    total_pages = math.ceil(total / limit)

    start = (page - 1) * limit
    end = start + limit

    return {
        "page": page,
        "limit": limit,
        "total": total,
        "total_pages": total_pages,
        "movies": movies[start:end]
    }
@app.get("/movies/sort")
def sort_movies(
    sort_by: str = "ticket_price",
    order: str = "asc"
):
    valid_fields = ["ticket_price", "title", "duration_mins", "seats_available"]

    if sort_by not in valid_fields:
        return {"error": "Invalid sort field"}

    reverse = True if order == "desc" else False

    sorted_movies = sorted(movies, key=lambda x: x[sort_by], reverse=reverse)

    return {
        "sorted_movies": sorted_movies
    }

@app.get("/movies/search")
def search_movies(keyword: str):
    results = [
        m for m in movies
        if keyword.lower() in m["title"].lower()
        or keyword.lower() in m["genre"].lower()
        or keyword.lower() in m["language"].lower()
    ]

    if not results:
        return {"message": "No movies found"}

    return {
        "results": results,
        "total_found": len(results)
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


#NEW MOVIE ADDING MODEL:
class NewMovie(BaseModel):
    title: str = Field(..., min_length=2)
    genre: str = Field(..., min_length=2)
    language: str = Field(..., min_length=2)
    duration_mins: int = Field(..., gt=0)
    ticket_price: int = Field(..., gt=0)
    seats_available: int = Field(..., gt=0)

@app.post("/movies", status_code=201)
def add_movie(movie: NewMovie):
    # Check duplicates 
    for m in movies:
        if m["title"].lower() == movie.title.lower():
            return {"error": "Movie already exists"}

    new_movie = movie.dict()
    new_movie["id"] = len(movies) + 1

    movies.append(new_movie)
    return new_movie


@app.put("/movies/{movie_id}")
def update_movie(
    movie_id: int,
    ticket_price: int = None,
    seats_available: int = None
):
    movie = find_movie(movie_id)
    if not movie:
        return {"error": "Movie not found"}

    if ticket_price is not None:
        movie["ticket_price"] = ticket_price

    if seats_available is not None:
        movie["seats_available"] = seats_available

    return {"message": "Movie updated", "movie": movie}


@app.delete("/movies/{movie_id}")
def delete_movie(movie_id: int):
    movie = find_movie(movie_id)

    if not movie:
        return {"error": "Movie not found"}

    for b in bookings:
        if b["movie_title"] == movie["title"]:
            return {"error": "Cannot delete movie with existing bookings"}

    movies.remove(movie)
    return {"message": "Movie deleted"}

holds = []
hold_counter = 1

class SeatHoldRequest(BaseModel):
    customer_name: str
    movie_id: int
    seats : int

@app.post("/seat-hold")
def hold_seats(request: SeatHoldRequest):
    global hold_counter

    movie = find_movie(request.movie_id)

    if not movie:
        return {"error": "Movie not found"}

    if movie["seats_available"] < request.seats:
        return {"error": "Not enough seats"}

    # Reduce seats temporarily
    movie["seats_available"] -= request.seats

    hold = {
        "hold_id": hold_counter,
        "customer_name": request.customer_name,
        "movie_id": request.movie_id,
        "seats": request.seats
    }

    holds.append(hold)
    hold_counter += 1

    return hold

@app.get("/seat-hold")
def get_holds():
    return {"holds": holds, "total": len(holds)}

#
@app.post("/seat-confirm/{hold_id}")
def confirm_hold(hold_id: int):
    global booking_counter

    hold = None
    for h in holds:
        if h["hold_id"] == hold_id:
            hold = h
            break

    if not hold:
        return {"error": "Hold not found"}

    movie = find_movie(hold["movie_id"])

    booking = {
        "booking_id": booking_counter,
        "customer_name": hold["customer_name"],
        "movie_title": movie["title"],
        "seats": hold["seats"],
        "seat_type": "standard",
        "original_cost": movie["ticket_price"] * hold["seats"],
        "discounted_cost": movie["ticket_price"] * hold["seats"]
    }

    bookings.append(booking)
    booking_counter += 1

    holds.remove(hold)

    return {"message": "Booking confirmed", "booking": booking}

#Delete the Hold 
@app.delete("/seat-release/{hold_id}")
def release_hold(hold_id: int):
    hold = None
    for h in holds:
        if h["hold_id"] == hold_id:
            hold = h
            break

    if not hold:
        return {"error": "Hold not found"}

    movie = find_movie(hold["movie_id"])
    movie["seats_available"] += hold["seats"]

    holds.remove(hold)

    return {"message": "Hold released"}


@app.get("/bookings/search")
def search_bookings(name: str):
    result = [b for b in bookings if name.lower() in b["customer_name"].lower()]

    return {
        "results": result,
        "total": len(result)
    }

#Sort booking

@app.get("/bookings/sort")
def sort_bookings(sort_by: str = "discounted_cost"):
    valid_fields = ["discounted_cost", "seats"]

    if sort_by not in valid_fields:
        return {"error": "Invalid sort field"}

    sorted_data = sorted(bookings, key=lambda x: x[sort_by])

    return {"sorted_bookings": sorted_data}

#Booking pagination
@app.get("/bookings/page")
def paginate_bookings(page: int = 1, limit: int = 2):
    total = len(bookings)
    total_pages = math.ceil(total / limit)

    start = (page - 1) * limit
    end = start + limit

    return {
        "page": page,
        "total_pages": total_pages,
        "bookings": bookings[start:end]
    }


