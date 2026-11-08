"""
数据库表结构更新脚本
添加用户表的latitude和longitude字段
"""
import pymysql
from app.database import DB_HOST, DB_PORT, DB_USER, DB_PASSWORD, DB_NAME

def add_latitude_longitude():
    """更新users表，添加latitude和longitude字段"""
    try:
        # 连接到MySQL数据库
        connection = pymysql.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME,
            charset='utf8mb4'
        )
        
        with connection.cursor() as cursor:
            # 检查并添加latitude字段
            cursor.execute("""
                SELECT COUNT(*) 
                FROM information_schema.COLUMNS 
                WHERE TABLE_SCHEMA = %s 
                AND TABLE_NAME = 'users' 
                AND COLUMN_NAME = 'latitude'
            """, (DB_NAME,))
            if cursor.fetchone()[0] == 0:
                cursor.execute("""
                    ALTER TABLE users 
                    ADD COLUMN latitude FLOAT NULL COMMENT '纬度'
                """)
                print("✓ 添加latitude字段成功")
            else:
                print("✓ latitude字段已存在")
            
            # 检查并添加longitude字段
            cursor.execute("""
                SELECT COUNT(*) 
                FROM information_schema.COLUMNS 
                WHERE TABLE_SCHEMA = %s 
                AND TABLE_NAME = 'users' 
                AND COLUMN_NAME = 'longitude'
            """, (DB_NAME,))
            if cursor.fetchone()[0] == 0:
                cursor.execute("""
                    ALTER TABLE users 
                    ADD COLUMN longitude FLOAT NULL COMMENT '经度'
                """)
                print("✓ 添加longitude字段成功")
            else:
                print("✓ longitude字段已存在")
            
            connection.commit()
            print("\n数据库表结构更新完成！")
            
    except Exception as e:
        print(f"更新数据库表结构失败: {e}")
        import traceback
        traceback.print_exc()
        raise
    finally:
        if connection:
            connection.close()

if __name__ == "__main__":
    print("开始添加latitude和longitude字段...")
    add_latitude_longitude()

