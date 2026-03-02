from sqlalchemy import create_engine, Column, Integer, String, Text, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# 1. データベース設定
SQLALCHEMY_DATABASE_URL = "sqlite:///./fanza.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# 2. 動画情報の新設計図（新しい詳細データの棚を追加！）
class Video(Base):
    __tablename__ = "videos"

    id = Column(Integer, primary_key=True, index=True)
    content_id = Column(String, unique=True, index=True) 
    title = Column(String)                               
    url = Column(Text)                                   
    image_url = Column(Text)                             
    price = Column(String)                               

    actress = Column(String)        
    genre = Column(String)          
    sample_images = Column(Text)    
    sample_movie_url = Column(Text) 
    
    # --- 今回新しく追加する項目 ---
    maker = Column(String)          # メーカー
    label = Column(String)          # レーベル
    series = Column(String)         # シリーズ
    director = Column(String)       # 監督
    release_date = Column(String)   # 発売日
    review_average = Column(Float)  # レビュー平均点（少数点あり）
    review_count = Column(Integer)  # レビュー件数（整数）
    volume = Column(String)         # 収録時間

# 3. データベース初期化命令
def init_db():
    Base.metadata.create_all(bind=engine)