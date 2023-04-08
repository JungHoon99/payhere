from fastapi import FastAPI
import jwt
import time
import hashlib

from database import engineconn
from models import User


SECRET_KEY = "mysecretkey"

engine = engineconn()
session = engine.sessionmaker()
app = FastAPI()


@app.get("/")
def 이름():
  return '보낼 값'

@app.get("/test")
async def first_get():
    example = session.query(User).all()
    return example

@app.get("/secondpage")
def 야옹():
  return {'고양이' : '야옹'}