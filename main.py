from fastapi import FastAPI, HTTPException, Depends
from fastapi.responses import RedirectResponse
from models import CreateURL, URLResponse, User, LoginRequest
from database import get_db, URLModel, UserModel
from datetime import datetime, timedelta, timezone
from jose import jwt
from utils import generate_url, hash_password, verify_password, SECRET_KEY, get_current_user
app = FastAPI()

@app.post('/api/create_url')
def create_url(data: CreateURL, db = Depends(get_db), current_user = Depends(get_current_user)):

    if data.custom_code is None:
        code = generate_url()
    else:
        code = data.custom_code
    new_link = db.query(URLModel).filter_by(code=code).first()
    if new_link:
        raise HTTPException(400, 'Код занят')
    new_url = URLModel(
    code=code,
    url=str(data.url),
    clicks=0,
    created_time=datetime.now(),
    expires_time=datetime.now() + timedelta(hours=data.expires_time) if data.expires_time else None,
    user_id=current_user.id
)
    db.add(new_url)
    db.commit()
    return URLResponse(short_url=f'http://localhost:8000/{code}')

@app.get('/{code}')
def redirect_to_url(code: str, db = Depends(get_db)): 
    new_link = db.query(URLModel).filter_by(code=code).first()
    if not new_link:
        raise HTTPException(404, 'Такой ссылки не существует')
    if new_link.expires_time is not None:
        if new_link.expires_time < datetime.now():
            db.delete(new_link)
            db.commit()
            raise HTTPException(410, 'Время жизни ссылки истекло')
    new_link.clicks += 1
    db.commit()
    return RedirectResponse(new_link.url, status_code=307)

@app.get('/api/stats/{code}')
def stats(code: str, db = Depends(get_db)):
    new_link = db.query(URLModel).filter_by(code=code).first()
    if not new_link:
        raise HTTPException(404, 'Такой ссылки не существует')
    
    return new_link

@app.post('/api/register')
def register(data: User, db = Depends(get_db)):
    email = db.query(UserModel).filter_by(email=data.email).first()
    username = db.query(UserModel).filter_by(username=data.username).first()
    if email or username:
        raise HTTPException(409, 'Такая почта уже зарегана' if email else 'Такой юзернейм уже занят')
    new_user = UserModel(
        username=data.username,
        email=data.email,
        password_hash=hash_password(data.password),
        created_time=datetime.now()
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {'message': 'User Created', 'user_id': new_user.id}

@app.post('/api/login')
def login(data: LoginRequest, db = Depends(get_db)):

    user = db.query(UserModel).filter_by(email=data.email).first()

    if not user or not verify_password(data.password, user.password_hash):
        raise HTTPException(401, 'Invalid user or password')
    
    token = jwt.encode(
        {'user_id': user.id, 'exp': datetime.now(timezone.utc) + timedelta(days=7)},
        SECRET_KEY, 
        algorithm='HS256'
    )
    
    return {'access_token': token, 'token_type': 'bearer'}

@app.delete('/api/{code}')
def delete_url(code: str, db = Depends(get_db), current_user = Depends(get_current_user)):

    link = db.query(URLModel).filter_by(code=code).first()

    if not link:
        raise HTTPException(404, 'Такой страницы нет')
    
    if link.user_id != current_user.id:
        raise HTTPException(401, 'Не твоя ссылка')
    
    db.delete(link)
    db.commit()
    return {'message': 'url deleted succes'}

@app.get('/api/my-url')
def get_my_url(db = Depends(get_db), current_user = Depends(get_current_user)):

    urls = db.query(URLModel).filter_by(user_id=current_user.id).all()

    return urls

@app.get('/api/me')
def get_profile(db = Depends(get_db), current_user = Depends(get_current_user)):

    urls = db.query(URLModel).filter_by(user_id=current_user.id).all()

    total_clicks = sum(url.clicks for url in urls)
    total_urls = len(urls)
    
    return {
        'username': current_user.username,
        'total_clicks': total_clicks,
        'total_urls': total_urls
    }
