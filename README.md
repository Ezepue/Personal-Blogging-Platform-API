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

## 💡 Future Improvements
- ✅ User Roles (Admin, Author, Reader)
- ✅ Comment System
- ✅ Image Uploads
- ✅ WebSocket for Real-time Updates

