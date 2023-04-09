from fastapi import FastAPI
import jwt
from jwt.exceptions import ExpiredSignatureError
import time
import hashlib
import re

from database import engineconn
from models import User, BlackList
from baseModels import SignInfor
from sqlalchemy.exc import IntegrityError

SECRET_KEY = "mysecretkey"
BLACK_LIST = []

engine = engineconn()
session = engine.sessionmaker()

app = FastAPI()

@app.post("/signup")
def signUp(sign : SignInfor):
  p = re.compile('^[a-zA-Z0-9+-_.]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$')
  if(p.match(sign.email) == None):
    return {"isSuccess" : False, "message" : "wrong email"}
  
  pwHashed = pwHashing(sign.pw)

  user = User()
  user.email = sign.email
  user.pw = pwHashed

  try:
    session.add(user)
    session.commit()
  except IntegrityError as e:
     return {"isSuccess" : False, "message" : "duplicated"}

  return {"isSuccess" : True, "message" : "SignUp success"}

@app.post("/signin")
def signIn(sign : SignInfor):
  pwHashed = pwHashing(sign.pw)

  id = session.query(User)\
    .filter((User.email == sign.email) & (User.pw == pwHashed))\
    .first()
  
  if(id == None):
    return {"isSuccess" : False, "message" : "id or pw error"}
  
  payload = {"id" : id.id, "email" : id.email, "exp" : int(time.time()) + (60*60)}

  userJwt = jwt.encode(payload, SECRET_KEY, algorithm="HS256")

  return { "token" : userJwt}

@app.delete("/signout/{token}")
def signOut(token):
  if(findBlackList(token) and tokenEffectCheck(token)):
    return {"isSuccess" : False, "message" : "already sign out token"}
  
  info = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
  
  endTime = time.localtime(info["exp"])

  blackToken = BlackList()

  blackToken.token = token
  blackToken.end_at = endTime

  session.add(blackToken)
  session.commit()

  return {"isSuccess" : True, "message" : "Sign Out success"}

@app.get("/Token/Infor/{token}")
def getUser(token):
  if(findBlackList(token) and tokenEffectCheck(token)):
    return {"isSuccess" : False, "message" : "sign out token"}
  return jwt.decode(token, SECRET_KEY, algorithms=["HS256"])


def tokenEffectCheck(token):
  try:
    jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
  except ExpiredSignatureError:
    return False
  return True

def findBlackList(token):
  tk = session.query(BlackList).filter(BlackList.token == token).first()
  
  if(tk == None):
    return False
  
  return True

def pwHashing(pw):
  pwByte = pw.encode('utf-8')
  pwHashed = hashlib.sha256(pwByte).hexdigest()
  return pwHashed