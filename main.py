from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import requests
from database import SessionLocal, Video

# 1. ここで「app」の正体を宣言しています！（これが消えていたのが原因です）
app = FastAPI()

# 2. HTMLを使う準備
templates = Jinja2Templates(directory="templates")

# --- あなたの本物のIDに書き換えてください ---
API_ID = "97BNTaqL2r6X9qX6VPYd"
AFFILIATE_ID = "12595-990"
# ----------------------------------------

# 3. ギャラリー表示（ページ分け機能付き）
@app.get("/gallery", response_class=HTMLResponse)
def show_gallery(request: Request, page: int = 1):
    db = SessionLocal()
    
    # 1ページに表示する件数
    limit = 50 
    # 何件目から取り出すかの計算
    offset = (page - 1) * limit 
    
    # 金庫に入っている「全体の件数」を数える
    total_videos = db.query(Video).count()
    # 全体で何ページになるかを計算する
    total_pages = (total_videos + limit - 1) // limit 
    
    # 指定したページの50件だけを取り出す
    videos = db.query(Video).offset(offset).limit(limit).all()
    db.close()
    
    # index.html にデータを渡す
    return templates.TemplateResponse("index.html", {
        "request": request, 
        "videos": videos,
        "current_page": page,
        "total_pages": total_pages
    })
# --- main.py の一番下に追加 ---

@app.get("/video/{content_id}", response_class=HTMLResponse)
def show_detail(request: Request, content_id: str):
    db = SessionLocal()
    video = db.query(Video).filter(Video.content_id == content_id).first()
    db.close()
    
    if not video:
        return "動画が見つかりませんでした。"
    
    # --- ここが重要！ ---
    # カンマで繋がったサンプル画像URLを、1枚ずつの「リスト」に変換します
    sample_list = video.sample_images.split(",") if video.sample_images else []
    
    # テンプレートに video 情報と一緒に sample_list も渡します
    return templates.TemplateResponse("detail.html", {
        "request": request, 
        "video": video,
        "samples": sample_list
    })

# --- main.py に追記 ---

@app.get("/actress/{name}", response_class=HTMLResponse)
def show_actress_works(request: Request, name: str, page: int = 1):
    db = SessionLocal()
    limit = 50
    offset = (page - 1) * limit

    # 金庫の中から、女優名に「name」が含まれているものを検索！
    query = db.query(Video).filter(Video.actress.contains(name))
    
    total_videos = query.count()
    total_pages = (total_videos + limit - 1) // limit
    videos = query.offset(offset).limit(limit).all()
    db.close()

    # 既存の index.html を使い回して表示します（タイトルだけ「〇〇の作品一覧」に変更）
    return templates.TemplateResponse("index.html", {
        "request": request,
        "videos": videos,
        "current_page": page,
        "total_pages": total_pages,
        "actress_name": name  # 女優名を渡して、見出しを変えられるようにする
    })

# --- main.py に追記 ---

@app.get("/genre/{name}", response_class=HTMLResponse)
def show_genre_works(request: Request, name: str, page: int = 1):
    db = SessionLocal()
    limit = 50
    offset = (page - 1) * limit

    # 金庫の中から、ジャンル名に「name」が含まれているものを検索！
    query = db.query(Video).filter(Video.genre.contains(name))
    
    total_videos = query.count()
    total_pages = (total_videos + limit - 1) // limit
    videos = query.offset(offset).limit(limit).all()
    db.close()

    # index.html を使い回して表示
    return templates.TemplateResponse("index.html", {
        "request": request,
        "videos": videos,
        "current_page": page,
        "total_pages": total_pages,
        "genre_name": name  # ジャンル名を渡す
    })