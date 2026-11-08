#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
删除users表中的email字段
运行方式：python3 migrations/remove_email_field.py
"""
import pymysql
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import DB_HOST, DB_PORT, DB_USER, DB_PASSWORD, DB_NAME

def remove_email_field():
    """删除users表的email字段"""
    try:
        # 连接到数据库
        connection = pymysql.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME,
            charset='utf8mb4'
        )
        
        try:
            with connection.cursor() as cursor:
                # 检查email字段是否存在
                cursor.execute("""
                    SELECT COUNT(*) 
                    FROM information_schema.COLUMNS 
                    WHERE TABLE_SCHEMA = %s 
                    AND TABLE_NAME = 'users' 
                    AND COLUMN_NAME = 'email'
                """, (DB_NAME,))
                
                exists = cursor.fetchone()[0]
                
                if exists:
                    print("正在删除email字段...")
                    # 删除email字段
                    cursor.execute("ALTER TABLE users DROP COLUMN email")
                    connection.commit()
                    print("✓ email字段已删除")
                else:
                    print("- email字段不存在，跳过")
                
        finally:
            connection.close()
            
    except Exception as e:
        print(f"❌ 删除email字段失败: {e}")
        import traceback
        traceback.print_exc()
        raise

if __name__ == "__main__":
    remove_email_field()

