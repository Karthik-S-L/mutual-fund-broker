# FastAPI Mutual Fund Portfolio App

This is a FastAPI application for managing mutual fund portfolios. It provides endpoints to view and update the user's portfolio, fetch the latest NAV (Net Asset Value) of mutual fund schemes, and more.

## Requirements

- Docker (for running the application in a containerized environment)
- Docker Compose (for managing multi-container environments, optional if you're using multiple services like databases)

## Project Structure

- `app/` - Contains FastAPI application and logic
- `Dockerfile` - Dockerfile to build the FastAPI application container
- `docker-compose.yml` - Docker Compose file to run the application along with other services (like MongoDB)
- `requirements.txt` - Python dependencies

## Setup

### 1. Clone the repository

```bash
git clone <your-repository-url>
cd <your-project-directory>
```

### 2. add .env file

Add your secrets in .env file refer to .env-example for reference
Paste your Rapid api key here

### 3. Running the application

Have docker desktop running

Then use below commands:

docker build -t fastapi-app .
docker-compose up --build
After the container is up and running, you should be able to access your FastAPI application at http://localhost:8000.

### 4. Hitting the endpoints

Use postman collection provided within app/documentation

[optional : you can also install the dependencies locally and run using uvicorn app.main:app --reload]
