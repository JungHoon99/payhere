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
URL = "http://127.0.0.1:8000"

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
  
  payload = {
    "id" : id.id,
    "email" : id.email,
    "exp" : int(time.time()) + (60*60)
  }

  userJwt = jwt.encode(payload, SECRET_KEY, algorithm="HS256")

  return {"isSuccess" : True ,"token" : userJwt}

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

@app.get("/account/all/{token}")
def accountList(token):
  if(findBlackList(token) or not tokenEffectCheck(token)):
    return {"isSuccess" : False, "message" : "sign out token"}
  
  payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])

  data = session.query(Account).filter(Account.user_id == payload["id"]).all()

  requestData = {}
  for column in data:
    requestData[column.id] = {
      "memo" : column.memo,
      "price" : column.price,
      "date" : column.date
    }

  return requestData

@app.get("/account/{accountID}/{token}")
def accountView(accountID, token):
  message = UserAccountEffectCheck(token, accountID)

  if(message['isSuccess'] == False):
    return message
  
  account = message["message"]

  return account

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

@app.post("/account/copy/{accountID}/{token}")
def accountCopy(accountID, token):
  if(findBlackList(token) or not tokenEffectCheck(token)):
    return {"isSuccess" : False, "message" : "sign out token"}
  
  account = session.query(Account).filter(Account.id == accountID).first()
  payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
  
  accountCopy = Account()
  accountCopy.user_id = payload["id"]
  accountCopy.price = account.price
  accountCopy.memo = account.memo
  accountCopy.date = account.date

  session.add(accountCopy)
  session.commit()
  
  return {"isSuccess" : True, "message" : "Copy success"}

@app.put("/account/{accountID}/table/{tableName}/value/{value}/{token}")
def accountUpdate(accountID, tableName, value, token):
  message = UserAccountEffectCheck(token, accountID)

  if(message['isSuccess'] == False):
    return message
  
  account = message["message"]

  if tableName == "date":
    account.date = str(value)
  elif tableName == "memo":
    account.memo = str(value)
  elif tableName == "price":
    account.price = int(value)

  session.commit()

  return {"isSuccess" : True, "message" : "Update Success"}

@app.delete("/account/{accountID}/{token}")
def accountUpdate(accountID, token):
  message = UserAccountEffectCheck(token, accountID)

  if(message['isSuccess'] == False):
    return message
  
  account = message["message"]

  session.delete(account)
  session.commit()

  return {"isSuccess" : True, "message" : "delete success"}

@app.get("/account/make/link/{accountID}/{token}")
def accountMake(accountID, token):
  if(findBlackList(token) or not tokenEffectCheck(token)):
    return {"isSuccess" : False, "message" : "sign out token"}
  message = UserAccountEffectCheck(token, accountID)

  if(message['isSuccess'] == False):
    return message
  
  account = message["message"]
  
  payload = {
    "id" : account.id,
    "user_id" : account.user_id,
    "price" : account.price,
    "memo" : account.memo,
    "date" : account.date,
    "create_at" : str(account.register_at),
    "update_at" : str(account.update_at),
    "exp" : int(time.time()) + (60*60*2)
  }

  accountJwt = jwt.encode(payload, SECRET_KEY, algorithm="HS256")

  link = URL+"/account/share/link/"+accountJwt

  return {"isSuccess" : True, "url" : link}

@app.get("/account/share/link/{token}")
def accountView(token):
  if(findBlackList(token) or not tokenEffectCheck(token)):
    return {"isSuccess" : False, "message" : "sign out token"}
  
  payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])

  payload.pop("user_id")
  payload.pop("exp")

  return payload


def UserAccountEffectCheck(token, accountID):
  if(findBlackList(token) or not tokenEffectCheck(token)):
    return {"isSuccess" : False, "message" : "sign out token"}
  
  payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
  
  account = session.query(Account).filter(Account.id == accountID).first()
  
  if(account.user_id != payload["id"]):
    return {"isSuccess" : False, "message" : "access denied"}
  
  return {"isSuccess" : True, "message" : account}

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