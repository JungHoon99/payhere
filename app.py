from fastapi import FastAPI
import jwt
from jwt.exceptions import ExpiredSignatureError
import time
from datetime import datetime
import hashlib
import re

from database import engineconn
from models import User, BlackList, Account
from baseModels import SignInfor, AccountInfor
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
  if(findBlackList(token) or not tokenEffectCheck(token)):
    return {"isSuccess" : False, "message" : "sign out token"}
  
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
  if(findBlackList(token) or not tokenEffectCheck(token)):
    return {"isSuccess" : False, "message" : "sign out token"}
  return jwt.decode(token, SECRET_KEY, algorithms=["HS256"])

@app.post("/account/{token}")
def accountApply(token, accountInfo : AccountInfor):
  if(findBlackList(token) or not tokenEffectCheck(token)):
    return {"isSuccess" : False, "message" : "sign out token"}
  try:
    datetime.strptime(accountInfo.date,"%Y-%m-%d")
  except ValueError:
    return {"isSuccess" : False, "message" : "date error"}
  
  payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
  account = Account()

  account.user_id = payload["id"]
  account.price = accountInfo.price
  account.memo = accountInfo.memo
  account.date = accountInfo.date

  session.add(account)
  session.commit()

  return {"isSuccess" : True, "message" : "Apply success"}

@app.get("/account/List/all/{token}")
def accountList(token):
  if(findBlackList(token) or not tokenEffectCheck(token)):
    return {"isSuccess" : False, "message" : "sign out token"}
  
  payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])

  data = session.query(Account).filter(Account.user_id == payload["id"]).all()

  requestData = {}
  for column in data:
    requestData[column.id] = {"memo" : column.memo, "price" : column.price, "date" : column.date }

  return requestData

@app.put("/account/{id}/table/{tableName}/value/{value}/{token}")
def accountUpdate(id, tableName, value, token):
  if(findBlackList(token) or not tokenEffectCheck(token)):
    return {"isSuccess" : False, "message" : "sign out token"}
  
  account = session.query(Account).filter(Account.user_id == id).first()

  if tableName == "date":
    account.date = str(value)
  elif tableName == "memo":
    account.memo = str(value)
  elif tableName == "price":
    account.price = int(value)

  session.commit()

  return {"isSuccess" : True, "message" : "Update Success"}

@app.delete("/account/{id}/{token}")
def accountUpdate(id, token):
  if(findBlackList(token) or not tokenEffectCheck(token)):
    return {"isSuccess" : False, "message" : "sign out token"}
  
  payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
  
  account = session.query(Account).filter(Account.user_id == id).first()
  if(account.user_id != payload["id"]):
    return {"isSuccess" : False, "message" : "access denied"}

  session.delete(account)
  session.commit()

  return {"isSuccess" : True, "message" : "delete complite"}

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