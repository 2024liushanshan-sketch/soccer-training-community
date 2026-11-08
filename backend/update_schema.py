"""
数据库表结构更新脚本
添加用户表的avatar、bio、nickname、location字段
"""
import pymysql
from app.database import DB_HOST, DB_PORT, DB_USER, DB_PASSWORD, DB_NAME

def update_user_table():
    """更新users表，添加新字段"""
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
            # 检查并添加avatar字段
            cursor.execute("""
                SELECT COUNT(*) 
                FROM information_schema.COLUMNS 
                WHERE TABLE_SCHEMA = %s 
                AND TABLE_NAME = 'users' 
                AND COLUMN_NAME = 'avatar'
            """, (DB_NAME,))
            if cursor.fetchone()[0] == 0:
                cursor.execute("""
                    ALTER TABLE users 
                    ADD COLUMN avatar VARCHAR(255) NULL COMMENT '头像路径'
                """)
                print("✓ 添加avatar字段成功")
            else:
                print("✓ avatar字段已存在")
            
            # 检查并添加bio字段
            cursor.execute("""
                SELECT COUNT(*) 
                FROM information_schema.COLUMNS 
                WHERE TABLE_SCHEMA = %s 
                AND TABLE_NAME = 'users' 
                AND COLUMN_NAME = 'bio'
            """, (DB_NAME,))
            if cursor.fetchone()[0] == 0:
                cursor.execute("""
                    ALTER TABLE users 
                    ADD COLUMN bio VARCHAR(500) NULL COMMENT '个人简介'
                """)
                print("✓ 添加bio字段成功")
            else:
                print("✓ bio字段已存在")
            
            # 检查并添加nickname字段
            cursor.execute("""
                SELECT COUNT(*) 
                FROM information_schema.COLUMNS 
                WHERE TABLE_SCHEMA = %s 
                AND TABLE_NAME = 'users' 
                AND COLUMN_NAME = 'nickname'
            """, (DB_NAME,))
            if cursor.fetchone()[0] == 0:
                cursor.execute("""
                    ALTER TABLE users 
                    ADD COLUMN nickname VARCHAR(50) NULL COMMENT '昵称'
                """)
                print("✓ 添加nickname字段成功")
            else:
                print("✓ nickname字段已存在")
            
            # 检查并添加location字段
            cursor.execute("""
                SELECT COUNT(*) 
                FROM information_schema.COLUMNS 
                WHERE TABLE_SCHEMA = %s 
                AND TABLE_NAME = 'users' 
                AND COLUMN_NAME = 'location'
            """, (DB_NAME,))
            if cursor.fetchone()[0] == 0:
                cursor.execute("""
                    ALTER TABLE users 
                    ADD COLUMN location VARCHAR(100) NULL COMMENT '位置'
                """)
                print("✓ 添加location字段成功")
            else:
                print("✓ location字段已存在")
            
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
    print("开始更新数据库表结构...")
    update_user_table()

