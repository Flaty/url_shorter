from fastapi import FastAPI, HTTPException
from fastapi.responses import RedirectResponse
from models import CreateURL, URLResponse, URLState
from storage import url_storage
from datetime import datetime, timedelta
from utils import generate_url
app = FastAPI()

@app.post('/create_url')
def create_url(data: CreateURL):
    
    if data.custom_code is None:
        code = generate_url()
    else:
        code = data.custom_code

    if code in url_storage:
        raise HTTPException(400, 'Код занят')
    


    url_storage[code] = URLState(
    short_url=code,
    url=str(data.url),
    clicks=0,
    created_time=datetime.now(),
    expires_time=datetime.now() + timedelta(hours=data.expires_time) if data.expires_time else None
)
    return URLResponse(short_url=f'http://localhost:8000/{code}')

@app.get('/{code}')
def redirect_to_url(code: str):

    if code not in url_storage:
        raise HTTPException(404, 'Такой ссылки не существует')
    if url_storage[code].expires_time is not None:
        if url_storage[code].expires_time < datetime.now():
            del url_storage[code]
            raise HTTPException(410, 'Время жизни ссылки истекло')
    url_storage[code].clicks += 1 
    return RedirectResponse(url_storage[code].url, status_code=307)

@app.get('/stats/{code}')

def stats(code: str):
    if code not in url_storage:
        raise HTTPException(404, 'Такой ссылки не существует')
    
    return url_storage[code]