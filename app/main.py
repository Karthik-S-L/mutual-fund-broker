from fastapi import FastAPI
from app.auth.routes import router as auth_router
from app.portfolio.routes import router as portfolio_router

app = FastAPI()

app.include_router(auth_router, prefix="/auth", tags=["Authentication"])
app.include_router(portfolio_router, prefix="/portfolio", tags=["Portfolio"])


