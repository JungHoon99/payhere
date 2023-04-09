from fastapi import FastAPI
import jwt
import time
import hashlib

from database import engineconn
from models import User
from baseModels import SignUp
from sqlalchemy.exc import IntegrityError

SECRET_KEY = "mysecretkey"

engine = engineconn()
session = engine.sessionmaker()
app = FastAPI()


@app.post("/signup")
def signUp(sign : SignUp):
  pwByte = sign.pw.encode('utf-8')
  hashed_password = hashlib.sha256(pwByte).hexdigest()
  user = User()
  user.email = sign.email
  user.pw = hashed_password

  try:
    session.add(user)
    session.commit()
  except IntegrityError as e:
     return {"isSuccess" : False , "message" : "duplicated"}

  return {"isSuccess" : True , "message" : "SignUp success"}