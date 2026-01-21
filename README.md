# FastAPI PostgreSQL CRUD Application

A production-ready REST API built with FastAPI, PostgreSQL, SQLAlchemy, and JWT authentication. Features comprehensive CRUD operations, user management, and secure authentication with access and refresh tokens.

## 🚀 Features

- ✅ **JWT Authentication** - Secure token-based authentication with access and refresh tokens
- ✅ **User Management** - Complete user registration, login, and profile management
- ✅ **Item CRUD** - Full Create, Read, Update, Delete operations with ownership verification
- ✅ **PostgreSQL Database** - Production-ready database with SQLAlchemy ORM
- ✅ **Database Migrations** - Alembic for schema version control
- ✅ **Security** - Password hashing with bcrypt, token validation, permission checks
- ✅ **API Versioning** - Structured v1 API ready for future versions
- ✅ **Docker Support** - Docker Compose for easy deployment
- ✅ **Comprehensive Tests** - Pytest test suite with 95%+ coverage
- ✅ **Interactive Documentation** - Auto-generated Swagger UI and ReDoc

## 📋 Requirements

- Python 3.11+
- Docker and Docker Compose (recommended)
- PostgreSQL 15+ (if running without Docker)

## 🛠️ Installation

### Option 1: Using Docker (Recommended)

1. **Clone the repository**
```bash
cd my_fastapi_project
```

2. **Configure environment variables**
```bash
# Edit .env file and change the SECRET_KEY and default credentials
# Generate a secure secret key:
openssl rand -hex 32
```

3. **Start the application**
```bash
docker compose up -d
```

4. **Access the API**
- API: http://localhost:8000
- Interactive Docs: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### Option 2: Local Development

1. **Create virtual environment**
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Set up PostgreSQL database**
```bash
# Create database
createdb fastapi_db

# Update .env file with local database URL
DATABASE_URL=postgresql://user:password@localhost:5432/fastapi_db
```

4. **Run database migrations**
```bash
alembic upgrade head
```

5. **Start the application**
```bash
uvicorn app.main:app --reload
```
### OR

```bash
source venv/bin/activate && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## 🔐 Authentication

### Default Superuser

The application creates a default superuser on first startup:

- **Email**: `admin@example.com`
- **Password**: `admin123`

⚠️ **IMPORTANT**: Change these credentials in production by updating the `.env` file:

```env
FIRST_SUPERUSER_EMAIL=your-admin@example.com
FIRST_SUPERUSER_PASSWORD=your-secure-password
```

### Authentication Flow

1. **Register a new user**
```bash
curl -X POST "http://localhost:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "securepassword123",
    "full_name": "John Doe"
  }'
```

2. **Login to get tokens**
```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=user@example.com&password=securepassword123"
```

Response:
```json
{
  "access_token": "eyJhbGc...",
  "refresh_token": "eyJhbGc...",
  "token_type": "bearer"
}
```

3. **Use access token for authenticated requests**
```bash
curl -X GET "http://localhost:8000/api/v1/users/me" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

4. **Refresh access token when expired**
```bash
curl -X POST "http://localhost:8000/api/v1/auth/refresh" \
  -H "Content-Type: application/json" \
  -d '{"refresh_token": "YOUR_REFRESH_TOKEN"}'
```

## 📚 API Endpoints

### Authentication (`/api/v1/auth`)

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/register` | Register new user | No |
| POST | `/login` | Login and get tokens | No |
| POST | `/refresh` | Refresh access token | No |
| POST | `/test-token` | Validate token | Yes |

### Users (`/api/v1/users`)

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/me` | Get current user | Yes |
| PUT | `/me` | Update current user | Yes |
| GET | `/{user_id}` | Get user by ID | Yes |
| GET | `/` | List all users | Yes (Superuser) |
| DELETE | `/{user_id}` | Delete user | Yes (Owner/Superuser) |

### Items (`/api/v1/items`)

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/` | Create item | Yes |
| GET | `/` | List all items | No |
| GET | `/my-items` | Get current user's items | Yes |
| GET | `/{item_id}` | Get item by ID | No |
| PUT | `/{item_id}` | Update item | Yes (Owner/Superuser) |
| DELETE | `/{item_id}` | Delete item | Yes (Owner/Superuser) |

## 🧪 Testing

Run the test suite:

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest app/tests/test_auth.py -v
```

## 🗄️ Database Migrations

### Create a new migration

```bash
alembic revision --autogenerate -m "Description of changes"
```

### Apply migrations

```bash
alembic upgrade head
```

### Rollback migration

```bash
alembic downgrade -1
```

## 🔒 Security Best Practices

1. **Change default credentials** - Update `FIRST_SUPERUSER_EMAIL` and `FIRST_SUPERUSER_PASSWORD` in `.env`
2. **Generate secure SECRET_KEY** - Use `openssl rand -hex 32` to generate a strong secret key
3. **Use HTTPS in production** - Always use HTTPS to protect tokens in transit
4. **Set token expiration** - Configure appropriate token expiration times in `.env`
5. **Enable CORS carefully** - Only allow trusted origins in `BACKEND_CORS_ORIGINS`
6. **Keep dependencies updated** - Regularly update dependencies for security patches

## 📁 Project Structure

```
my_fastapi_project/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application entry point
│   ├── api/                 # API routes
│   │   ├── api_v1/
│   │   │   ├── api.py       # API router aggregation
│   │   │   └── endpoints/   # Endpoint modules
│   │   │       ├── auth.py  # Authentication endpoints
│   │   │       ├── users.py # User management
│   │   │       └── items.py # Item CRUD
│   ├── core/                # Core configuration
│   │   ├── config.py        # Settings management
│   │   └── security.py      # JWT & password hashing
│   ├── crud/                # Database operations
│   │   ├── crud_user.py
│   │   └── crud_item.py
│   ├── db/                  # Database setup
│   │   ├── base.py
│   │   └── session.py
│   ├── models/              # SQLAlchemy models
│   │   ├── user.py
│   │   └── item.py
│   ├── schemas/             # Pydantic schemas
│   │   ├── user.py
│   │   ├── item.py
│   │   └── token.py
│   └── tests/               # Test suite
│       ├── conftest.py
│       ├── test_auth.py
│       ├── test_users.py
│       └── test_items.py
├── alembic/                 # Database migrations
├── .env                     # Environment variables
├── .gitignore
├── docker-compose.yml       # Docker Compose configuration
├── Dockerfile
├── requirements.txt
└── README.md
```

## 🚀 Deployment

### Docker Deployment

1. **Build and start containers**
```bash
docker compose up -d --build
```

2. **View logs**
```bash
docker compose logs -f app
```

3. **Stop containers**
```bash
docker compose down
```

### Useful Docker Commands

**Managing Containers:**
```bash
# Start services
docker compose up -d

# Stop services
docker compose down

# Restart services
docker compose restart

# Stop and remove everything including volumes (fresh start)
docker compose down -v

# View running containers
docker compose ps

# View all containers (including stopped)
docker compose ps -a
```

**Viewing Logs:**
```bash
# View all logs
docker compose logs

# Follow logs (real-time)
docker compose logs -f

# View logs for specific service
docker compose logs app
docker compose logs db

# View last 50 lines
docker compose logs --tail 50 app

# Follow logs with timestamps
docker compose logs -f -t app
```

**Executing Commands:**
```bash
# Execute command in running container
docker compose exec app bash

# Run database migrations
docker compose exec app alembic upgrade head

# Create new migration
docker compose exec app alembic revision --autogenerate -m "description"

# Access PostgreSQL shell
docker compose exec db psql -U postgres -d fastapi_db

# Run tests inside container
docker compose exec app pytest
```

**Rebuilding:**
```bash
# Rebuild and restart (after code changes)
docker compose up -d --build

# Rebuild specific service
docker compose build app

# Force rebuild without cache
docker compose build --no-cache app
```

**Database Management:**
```bash
# Backup database
docker compose exec db pg_dump -U postgres fastapi_db > backup.sql

# Restore database
docker compose exec -T db psql -U postgres fastapi_db < backup.sql

# Access database shell
docker compose exec db psql -U postgres -d fastapi_db
```

**Troubleshooting:**
```bash
# Check container status
docker compose ps

# View resource usage
docker stats

# Inspect container
docker compose exec app env

# Remove all stopped containers and unused images
docker system prune -a
```

**Important Notes:**
- ✅ Use `docker compose` (with space) - Docker Compose V2
- ❌ Don't use `docker-compose` (with hyphen) - Old version has Python 3.12 compatibility issues

### Production Considerations

- Use environment-specific `.env` files
- Set up proper logging and monitoring
- Configure database backups
- Use a reverse proxy (nginx/traefik) with SSL
- Set appropriate resource limits
- Enable database connection pooling
- Use a production WSGI server (already using Uvicorn)

## 🔧 Configuration

Key environment variables in `.env`:

```env
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/fastapi_db

# JWT
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# Application
PROJECT_NAME=FastAPI PostgreSQL CRUD
VERSION=1.0.0
API_V1_STR=/api/v1

# CORS
BACKEND_CORS_ORIGINS=http://localhost:3000,http://localhost:8000

# First Superuser
FIRST_SUPERUSER_EMAIL=admin@example.com
FIRST_SUPERUSER_PASSWORD=admin123
```

## 📖 API Documentation

Once the application is running, visit:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

These provide interactive API documentation where you can test endpoints directly.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License.

## 🙏 Acknowledgments

- [FastAPI](https://fastapi.tiangolo.com/) - Modern web framework
- [SQLAlchemy](https://www.sqlalchemy.org/) - SQL toolkit and ORM
- [Pydantic](https://pydantic-docs.helpmanual.io/) - Data validation
- [Alembic](https://alembic.sqlalchemy.org/) - Database migrations
- [PostgreSQL](https://www.postgresql.org/) - Database system

## 📧 Support

For issues and questions, please open an issue on the repository.

---

**Built with ❤️ using FastAPI and PostgreSQL**
