# Personal Blogging Platform API

A simple, yet powerful, **FastAPI-based** blogging platform that allows users to create, read, update, and delete articles. The API supports user authentication, article management, and database persistence using **PostgreSQL** and **SQLAlchemy**.

---

## 🚀 Features
- **User Authentication** (Signup, Login with JWT)
- **CRUD Operations for Articles**
- **PostgreSQL Database with SQLAlchemy ORM**
- **Alembic Migrations**
- **FastAPI with Automatic API Documentation (Swagger UI & Redoc)**

---

## 🛠 Tech Stack
- **FastAPI** - Modern web framework for APIs
- **SQLAlchemy** - ORM for database interactions
- **PostgreSQL** - Relational database
- **Alembic** - Database migrations
- **Uvicorn** - ASGI server for FastAPI

---

## 🏗 Setup & Installation

### 1️⃣ Clone the Repository
```bash
git clone https://github.com/yourusername/Personal-Blogging-Platform-API.git
cd Personal-Blogging-Platform-API
```

### 2️⃣ Create & Activate a Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate
```

### 3️⃣ Install Dependencies
```bash
pip install -r requirements.txt
```

### 4️⃣ Configure the Database
Update the `DATABASE_URL` in `config.py`:
```python
DATABASE_URL = "postgresql://username:password@localhost:5432/blogdb"
```

### 5️⃣ Run Migrations
```bash
alembic upgrade head
```

### 6️⃣ Start the API Server
```bash
uvicorn app:app --reload
```

API will be live at: **`http://127.0.0.1:8000`**

---

## 🔥 API Endpoints

### 📌 Authentication
- **POST** `/users/signup/` - Register a new user
- **POST** `/users/login/` - Login and receive an access token

### 📝 Articles
- **GET** `/articles/` - Fetch all articles
- **POST** `/articles/` - Create a new article
- **GET** `/articles/{id}/` - Get a single article by ID
- **PUT** `/articles/{id}/` - Update an article
- **DELETE** `/articles/{id}/` - Delete an article
- **DELETE** `/articles/{id}/` - Delete an article
- **POST** `/articles/{id}/like` - Like  Post
- **POST** `/articles/{id}/unlike` - Unlike Post
- **GET** `/articles/{id}/likes` - Get Likes
- **POST** `/comments/{article_id}/comments` - Add comment
- **GET** `/comments/{article_id}/comments` - Get comments
- **DELETE** `/comments/{comment_id}/comments` - Delete comments





### 🔍 API Documentation
- **Swagger UI:** `http://127.0.0.1:8000/docs`
- **ReDoc:** `http://127.0.0.1:8000/redoc`

---

## 📌 Contributing
1. Fork the repo
2. Create a feature branch (`git checkout -b feature-branch`)
3. Commit your changes (`git commit -m "Added a cool feature"`)
4. Push to the branch (`git push origin feature-branch`)
5. Open a Pull Request

---

## 📜 License
This project is licensed under the MIT License.

---

### ✅ Features Implemented in the Backend:
1. **User Authentication & Authorization**  
   - Register/Login system  
   - JWT authentication  
   - Role-based access control (Reader, Admin, Super Admin)  

2. **User Management**  
   - Promote/Demote users  
   - Super Admin creation  
   - Delete users (Only Super Admins)  

3. **Article Management**  
   - Create, Read, Update, Delete (CRUD) for articles  
   - Draft vs Published posts  
   - Categories & Tags  

4. **Engagement Features**  
   - Comments system  
   - Likes system  

5. **Search & Filtering**  
   - Filtering articles by category, tags, etc.  
   - Searching for articles  

6. **Media Uploads**  
   - Upload images/files  
   - Serve media files 

---

### ❓ Missing or Unconfirmed Features:
1. **Admin Panel (Optional)**  
   - A separate admin dashboard for managing users, articles, etc.  

2. **Pagination for Articles & Comments**  
   - If you have many posts or comments, you might need pagination.  

3. **Rate Limiting (Optional for security)**  
   - Prevent excessive requests (e.g., brute-force login attempts).  

4. **Notification System (Optional Enhancement)**  
   - Notify users when their article is liked or commented on.  
   
---