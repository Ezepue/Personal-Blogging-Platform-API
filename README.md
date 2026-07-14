# Quill — Personal Blogging Platform

A full-stack blogging platform: a **FastAPI + PostgreSQL** backend and a **Next.js 14** frontend with an editorial, magazine-style design (paper/ink light & dark themes).

---

## 🚀 Features
- **Auth & accounts** — JWT access tokens + DB-backed refresh tokens, httpOnly cookies, role-based access control (Reader, Author, Admin, Super Admin), notification preferences
- **Writing** — rich-text editor, drafts vs published, subtitles, cover images, tags & categories, SEO-friendly slugs, auto reading-time estimates
- **Reading** — trending/top/latest feeds, personalized Following feed, related posts, auto table of contents, reading progress bar, view counts
- **Community** — follow authors, threaded comments with editing and likes, article likes, bookmarks/reading list, typed real-time notifications (WebSocket)
- **Discovery** — site-wide search (stories + writers), topic browse pages, RSS feed, sitemap, OpenGraph metadata
- **Author tools** — dashboard with per-story analytics (views/likes/comments), profile pages with socials and follower stats
- **Platform** — sanitized article HTML (stored-XSS safe), magic-byte upload validation, rate limiting, Alembic migrations, Swagger/ReDoc docs

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
SQLALCHEMY_DATABASE_URL = "postgresql://username:password@localhost/blog_db"
```

### 5️⃣ Run Migrations
```bash
alembic upgrade head
```

### 6️⃣ Start the API Server
```bash
uvicorn main:app --reload
```

API will be live at: **`http://127.0.0.1:8000`**

### 7️⃣ Start the Frontend
```bash
cd frontend
npm install
API_URL=http://127.0.0.1:8000 npm run dev
```

Frontend will be live at: **`http://localhost:3000`**

> In production also set `SITE_URL` (the site's public origin, e.g.
> `https://blog.example.com`) so OpenGraph/Twitter share images resolve to
> absolute URLs, and `NEXT_PUBLIC_WS_URL` (e.g. `wss://api.example.com`) for
> real-time notifications.

---

## 🔥 API Endpoints

### 📌 Authentication
- **POST** `/users/signup/` - Register a new user
- **POST** `/users/login/` - Login and receive an access token
- **POST** `/users/logout/` - Logout and deactivate tokens

### 📝 Articles
- **GET** `/articles/` - Fetch all articles
- **POST** `/articles/` - Create a new article
- **GET** `/articles/{id}/` - Get a single article by ID
- **PUT** `/articles/{id}/` - Update an article
- **DELETE** `/articles/{id}/` - Delete an article
- **POST** `/articles/{id}/like/` - Like a post
- **POST** `/articles/{id}/unlike/` - Unlike a post
- **GET** `/articles/{id}/likes/` - Get article likes

### 💬 Comments
- **POST** `/comments/{article_id}/` - Add a comment
- **GET** `/comments/{article_id}/` - Get comments
- **DELETE** `/comments/{comment_id}/` - Delete a comment

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
   - Logout system
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
   - Share System

5. **Search & Filtering**
   - Filtering articles by category, tags, etc.
   - Searching for articles

6. **Media Uploads**
   - Upload images/files
   - Serve media files

7. **Security Features**
   - Rate limiting for security
   - Multi-device login support
   - Active token/session management

---

### ❓ Upcoming Features:
   1. **Notification System (Work in Progress)**
   - Notify users when their article is liked or commented on.
   - Store notifications in the database for users to view later.
