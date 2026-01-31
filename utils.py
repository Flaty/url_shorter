from random import randint, choice
import bcrypt
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from fastapi import Depends, HTTPException
from database import get_db, UserModel
import random

security = HTTPBearer()
SECRET_KEY = '7aef6f5bbec2d07b77c777f25a410e7e'

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db = Depends(get_db)
):
    token = credentials.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        user_id = payload.get('user_id')
        if user_id is None:
            raise HTTPException(401, 'Invalid Token')
    except JWTError:
        raise HTTPException(401, 'Invalid Token')
    
    user = db.query(UserModel).filter_by(id=user_id).first()

    if not user:
        raise HTTPException(401, 'User not found')

    return user

def hash_password(password: str):
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

def verify_password(plain: str, hashed: str):
    return bcrypt.checkpw(plain.encode('utf-8'), hashed.encode('utf-8'))

def generate_url(start=5, end=10):
        alf = 'QAZWSXEDCRFVTGBYHNUJMIKOLPqazwsxedcrfvtgbyhnujmikolp1234567890'
        length = randint(start, end)
        code = []
        for _ in range(length):
            code.append(choice(alf))
            
        return ''.join(code)
