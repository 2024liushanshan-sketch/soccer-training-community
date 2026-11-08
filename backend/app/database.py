import os
import re
from sqlalchemy.engine import URL
from app import config  # Load the local .env before reading settings.
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import pymysql
import threading

# 数据库配置
DB_HOST = os.getenv("DB_HOST", "127.0.0.1")
DB_PORT = int(os.getenv("DB_PORT", "3306"))
DB_USER = os.getenv("DB_USER", "soccer_app")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
DB_NAME = os.getenv("DB_NAME", "soccer_app")
if not re.fullmatch(r"[A-Za-z0-9_]+", DB_NAME):
    raise ValueError("DB_NAME must contain only letters, digits and underscores")
DATABASE_URL = URL.create(
    "mysql+pymysql", username=DB_USER, password=DB_PASSWORD,
    host=DB_HOST, port=DB_PORT, database=DB_NAME,
    query={"charset": "utf8mb4"},
)

# 创建Base类（需要在创建engine之前）
Base = declarative_base()

# 全局变量，延迟初始化
engine = None
SessionLocal = None
_init_lock = threading.Lock()  # 初始化锁，防止多线程竞态


def create_database():
    """创建数据库（如果不存在）"""
    try:
        # 连接到MySQL服务器（不指定数据库）
        connection = pymysql.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASSWORD,
            charset='utf8mb4'
        )
        try:
            with connection.cursor() as cursor:
                # 创建数据库
                cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{DB_NAME}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
                print(f"数据库 {DB_NAME} 创建成功或已存在")
            connection.commit()
        finally:
            connection.close()
    except Exception as e:
        print(f"创建数据库失败: {e}")
        raise


def init_engine():
    """初始化数据库引擎（线程安全）"""
    global engine, SessionLocal
    
    # 双重检查锁定模式，确保线程安全
    if engine is None:
        with _init_lock:
            # 再次检查，防止在获取锁的过程中其他线程已经初始化
            if engine is None:
                # 先确保数据库存在
                create_database()
                
                # 创建数据库引擎
                engine = create_engine(
                    DATABASE_URL,
                    pool_pre_ping=True,
                    pool_recycle=3600,
                    echo=False  # 设置为True可以看到SQL语句
                )
                
                # 创建SessionLocal类
                SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
                print("数据库引擎初始化成功")


# 获取数据库会话
def get_db():
    if SessionLocal is None:
        init_engine()
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# 创建数据库和表
def init_db():
    """初始化数据库和表"""
    try:
        # 初始化引擎（会自动创建数据库）
        init_engine()
        
        # 创建所有表
        Base.metadata.create_all(bind=engine)
        print("数据库表创建成功")
    except Exception as e:
        print(f"数据库初始化失败: {e}")
        import traceback
        traceback.print_exc()
        raise

