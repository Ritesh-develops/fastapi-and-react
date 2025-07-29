from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routes import challenge, webhooks
from dotenv import load_dotenv
import os

load_dotenv()

app = FastAPI()
 
FRONTEND_URL = os.getenv("FRONTEND_URL")
origins=[]
if FRONTEND_URL:
    origins.append(FRONTEND_URL)
origins.append("http://localhost:5173")



app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

app.include_router(challenge.router, prefix="/api")
app.include_router(webhooks.router, prefix="/webhooks")