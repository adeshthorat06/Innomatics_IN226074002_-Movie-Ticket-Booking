# 🎬 Movie Ticket Booking System (FastAPI)

This is a complete backend project using **FastAPI** as part of the Innomatics Internship Final Project.

This project simulates a real-world movie ticket booking system. It includes features like browsing movies, booking tickets, managing seats, and more.

---

##  Features

### 🔹 Core Features
- REST APIs using FastAPI
- CRUD operations for movies
- Ticket booking system
- Seat availability management

### 🔹 Advanced Features
- Pydantic validation
- Multi-step workflow
- Search
- Sorting and filtering
- Pagination
- Combined browsing API

---

##  Project Structure
|-movie-ticket-booking/
│
├── main.py
├── requirements.txt
├── README.md
└── screenshots/



---

## ⚙️ Installation & Setup

### 1️⃣ Clone Repository
```bash
git clone https://github.com/your-username/your-repo-name.git
cd your-repo-name


---

## RUN SERVER

uvicorn main:app --reload


Implemented Endpoints
 Movies
GET /movies

GET /movies/{id}
POST /movies
PUT /movies/{id}
DELETE /movies/{id}

 Booking
POST /bookings

GET /bookings
Search, Sort, Pagination APIs
 Seat Management
POST /seat-hold
GET /seat-hold
POST /seat-confirm/{hold_id}
DELETE /seat-release/{hold_id}

 Advanced APIs

/movies/search
/movies/filter
/movies/sort
/movies/page
/movies/browse