"""
个人档案相关数据库表结构更新脚本
添加用户统计字段和成长记录、技能评分表
"""
import pymysql
from app.database import DB_HOST, DB_PORT, DB_USER, DB_PASSWORD, DB_NAME

def update_profile_tables():
    """更新users表，添加统计字段，创建成长记录和技能评分表"""
    try:
        connection = pymysql.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME,
            charset='utf8mb4'
        )
        
        with connection.cursor() as cursor:
            # 检查并添加matches_count字段
            cursor.execute("""
                SELECT COUNT(*) 
                FROM information_schema.COLUMNS 
                WHERE TABLE_SCHEMA = %s 
                AND TABLE_NAME = 'users' 
                AND COLUMN_NAME = 'matches_count'
            """, (DB_NAME,))
            if cursor.fetchone()[0] == 0:
                cursor.execute("""
                    ALTER TABLE users 
                    ADD COLUMN matches_count INT DEFAULT 0 COMMENT '比赛场次'
                """)
                print("✓ 添加matches_count字段成功")
            else:
                print("✓ matches_count字段已存在")
            
            # 检查并添加goals_count字段
            cursor.execute("""
                SELECT COUNT(*) 
                FROM information_schema.COLUMNS 
                WHERE TABLE_SCHEMA = %s 
                AND TABLE_NAME = 'users' 
                AND COLUMN_NAME = 'goals_count'
            """, (DB_NAME,))
            if cursor.fetchone()[0] == 0:
                cursor.execute("""
                    ALTER TABLE users 
                    ADD COLUMN goals_count INT DEFAULT 0 COMMENT '进球数'
                """)
                print("✓ 添加goals_count字段成功")
            else:
                print("✓ goals_count字段已存在")
            
            # 检查并添加assists_count字段
            cursor.execute("""
                SELECT COUNT(*) 
                FROM information_schema.COLUMNS 
                WHERE TABLE_SCHEMA = %s 
                AND TABLE_NAME = 'users' 
                AND COLUMN_NAME = 'assists_count'
            """, (DB_NAME,))
            if cursor.fetchone()[0] == 0:
                cursor.execute("""
                    ALTER TABLE users 
                    ADD COLUMN assists_count INT DEFAULT 0 COMMENT '助攻数'
                """)
                print("✓ 添加assists_count字段成功")
            else:
                print("✓ assists_count字段已存在")
            
            # 检查并创建user_growth_records表
            cursor.execute("""
                SELECT COUNT(*) 
                FROM information_schema.TABLES 
                WHERE TABLE_SCHEMA = %s 
                AND TABLE_NAME = 'user_growth_records'
            """, (DB_NAME,))
            if cursor.fetchone()[0] == 0:
                cursor.execute("""
                    CREATE TABLE user_growth_records (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        user_id INT NOT NULL,
                        date DATETIME NOT NULL,
                        event VARCHAR(500) NOT NULL COMMENT '事件描述',
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
                        INDEX idx_user_id (user_id),
                        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
                    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='用户成长记录表'
                """)
                print("✓ 创建user_growth_records表成功")
            else:
                print("✓ user_growth_records表已存在")
            
            # 检查并创建user_skills表
            cursor.execute("""
                SELECT COUNT(*) 
                FROM information_schema.TABLES 
                WHERE TABLE_SCHEMA = %s 
                AND TABLE_NAME = 'user_skills'
            """, (DB_NAME,))
            if cursor.fetchone()[0] == 0:
                cursor.execute("""
                    CREATE TABLE user_skills (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        user_id INT NOT NULL,
                        skill_name VARCHAR(50) NOT NULL COMMENT '技能名称',
                        score INT DEFAULT 0 COMMENT '技能评分（0-100）',
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
                        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
                        INDEX idx_user_id (user_id),
                        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
                    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='用户技能评分表'
                """)
                print("✓ 创建user_skills表成功")
            else:
                print("✓ user_skills表已存在")
            
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
    print("开始更新个人档案相关数据库表结构...")
    update_profile_tables()

