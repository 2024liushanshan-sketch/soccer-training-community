#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
手动初始化数据库脚本
如果自动初始化失败，可以运行此脚本手动创建数据库和表
"""
from app.database import init_db

if __name__ == "__main__":
    print("开始初始化数据库...")
    try:
        init_db()
        print("数据库初始化成功！")
    except Exception as e:
        print(f"数据库初始化失败: {e}")
        import traceback
        traceback.print_exc()

