import requests
import time
# ↓ Videoの呼び出し元を main から database に変更しました！
from database import engine, Base, SessionLocal, Video 

Base.metadata.create_all(bind=engine)

# --- あなたの本物のIDに書き換えてください ---
API_ID = "97BNTaqL2r6X9qX6VPYd"
AFFILIATE_ID = "12595-990"
# ----------------------------------------

def gather_data_bulk(max_pages=5):
    print(f"【動画URL対応版】最大 {max_pages * 100} 件の収集を開始します...")
    db = SessionLocal()
    total_new_count = 0

    try:
        for page in range(1, max_pages + 1):
            print(f"--- {page}ページ目を取得中... ---")
            offset = (page - 1) * 100 + 1
            url = f"https://api.dmm.com/affiliate/v3/ItemList?api_id={API_ID}&affiliate_id={AFFILIATE_ID}&site=FANZA&service=digital&floor=videoa&hits=100&offset={offset}&output=json"
            
            response = requests.get(url)
            data = response.json()
            
            if 'items' not in data['result']:
                break
                
            items = data['result']['items']
            
            for item in items:
                existing = db.query(Video).filter(Video.content_id == item['content_id']).first()
                if not existing:
                    
                    # 1. 女優名
                    actress_list = item.get('iteminfo', {}).get('actress', [])
                    actress_names = ", ".join([a['name'] for a in actress_list]) if actress_list else "不明"
                    
                    # 2. ジャンル
                    genre_list = item.get('iteminfo', {}).get('genre', [])
                    genre_names = ", ".join([g['name'] for g in genre_list]) if genre_list else "なし"
                    
                    # 3. サンプル画像
                    samples = item.get('sampleImageURL', {}).get('sample_l', {}).get('image', [])
                    sample_urls = ",".join(samples) if samples else ""

                    # 4. サンプル動画
                    sample_movie = item.get('sampleMovieURL', {})
                    movie_url = ""
                    if sample_movie:
                        for size in ['size_720_480', 'size_644_414', 'size_560_360', 'size_476_306', 'pc_flv']:
                            if size in sample_movie:
                                movie_url = sample_movie[size]
                                break
                    
                    # --- ★ ここから新しく追加した詳細データの取得 ★ ---
                    iteminfo = item.get('iteminfo', {})
                    
                    # メーカー
                    maker_list = iteminfo.get('maker', [])
                    maker_name = maker_list[0]['name'] if maker_list else ""
                    
                    # レーベル
                    label_list = iteminfo.get('label', [])
                    label_name = label_list[0]['name'] if label_list else ""
                    
                    # シリーズ
                    series_list = iteminfo.get('series', [])
                    series_name = series_list[0]['name'] if series_list else ""
                    
                    # 監督
                    director_list = iteminfo.get('director', [])
                    director_name = director_list[0]['name'] if director_list else ""
                    
                    # 発売日と収録時間
                    release_date = item.get('date', "")
                    volume = item.get('volume', "")
                    
                    # レビュー点数と件数（エラーにならないよう安全に変換）
                    review_data = item.get('review', {})
                    review_average = 0.0
                    review_count = 0
                    if isinstance(review_data, dict):
                        try:
                            review_average = float(review_data.get('average', 0.0))
                            review_count = int(review_data.get('count', 0))
                        except (ValueError, TypeError):
                            pass
                    # ------------------------------------------------
                    
                    # 金庫に保存
                    video = Video(
                        content_id=item['content_id'],
                        title=item['title'],
                        url=item['affiliateURL'],
                        image_url=item['imageURL']['large'],
                        price=str(item.get('prices', {}).get('price', '0')),
                        actress=actress_names,      
                        genre=genre_names,          
                        sample_images=sample_urls,
                        sample_movie_url=movie_url,
                        
                        # 新しいデータを追加保存！
                        maker=maker_name,
                        label=label_name,
                        series=series_name,
                        director=director_name,
                        release_date=release_date,
                        review_average=review_average,
                        review_count=review_count,
                        volume=volume
                    )
                    db.add(video)
                    total_new_count += 1
            
            db.commit()
            print(f"{page}ページ目完了（合計 {total_new_count} 件保存済み）")
            time.sleep(1)
            
        print(f"\n完了！ 新しい金庫に {total_new_count} 件の豪華データを蓄積しました。")
        
    except Exception as e:
        print(f"エラーが発生しました: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    gather_data_bulk()