from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import requests
from database import SessionLocal, Video

# FastAPIの正体（システム本体）
app = FastAPI()

# HTMLを使う準備
templates = Jinja2Templates(directory="templates")

# --- あなたの本物のIDに書き換えてください ---
API_ID = "97BNTaqL2r6X9qX6VPYd"
AFFILIATE_ID = "12595-990"
# ----------------------------------------

# ★ 今回新しく追加した部分：1. サイトの玄関（トップページ）
@app.get("/", response_class=HTMLResponse)
def show_top(request: Request):
    # トップURLにアクセスが来たら、「top.html（年齢確認画面）」を表示する
    return templates.TemplateResponse("top.html", {"request": request})


# 2. ギャラリー表示（ページ分け機能付き）
@app.get("/gallery", response_class=HTMLResponse)
def show_gallery(request: Request, page: int = 1):
    db = SessionLocal()
    
    limit = 50 
    offset = (page - 1) * limit 
    
    total_videos = db.query(Video).count()
    total_pages = (total_videos + limit - 1) // limit 
    
    videos = db.query(Video).offset(offset).limit(limit).all()
    db.close()
    
    return templates.TemplateResponse("index.html", {
        "request": request, 
        "videos": videos,
        "current_page": page,
        "total_pages": total_pages
    })


# 3. 詳細ページ表示
@app.get("/video/{content_id}", response_class=HTMLResponse)
def show_detail(request: Request, content_id: str):
    db = SessionLocal()
    video = db.query(Video).filter(Video.content_id == content_id).first()
    db.close()
    
    if not video:
        return "動画が見つかりませんでした。"
    
    sample_list = video.sample_images.split(",") if video.sample_images else []
    
    return templates.TemplateResponse("detail.html", {
        "request": request, 
        "video": video,
        "samples": sample_list
    })


# 4. 女優別の作品一覧
@app.get("/actress/{name}", response_class=HTMLResponse)
def show_actress_works(request: Request, name: str, page: int = 1):
    db = SessionLocal()
    limit = 50
    offset = (page - 1) * limit

    query = db.query(Video).filter(Video.actress.contains(name))
    
    total_videos = query.count()
    total_pages = (total_videos + limit - 1) // limit
    videos = query.offset(offset).limit(limit).all()
    db.close()

    return templates.TemplateResponse("index.html", {
        "request": request,
        "videos": videos,
        "current_page": page,
        "total_pages": total_pages,
        "actress_name": name 
    })


# 5. ジャンル別の作品一覧
@app.get("/genre/{name}", response_class=HTMLResponse)
def show_genre_works(request: Request, name: str, page: int = 1):
    db = SessionLocal()
    limit = 50
    offset = (page - 1) * limit

    query = db.query(Video).filter(Video.genre.contains(name))
    
    total_videos = query.count()
    total_pages = (total_videos + limit - 1) // limit
    videos = query.offset(offset).limit(limit).all()
    db.close()

    return templates.TemplateResponse("index.html", {
        "request": request,
        "videos": videos,
        "current_page": page,
        "total_pages": total_pages,
        "genre_name": name 
    })