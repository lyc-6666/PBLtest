#!/usr/bin/env python
"""
数据库连接测试脚本
用于诊断MySQL连接问题
"""

import mysql.connector
import sys

def test_connection():
    print("数据库连接测试")
    print("=" * 50)
    
    # 测试不同的连接配置
    configs = [
        {
            'name': '无密码配置',
            'host': 'localhost',
            'user': 'root',
            'password': ''
        },
        {
            'name': '密码为123456',
            'host': 'localhost',
            'user': 'root',
            'password': '123456'
        },
        {
            'name': '密码为password',
            'host': 'localhost',
            'user': 'root',
            'password': 'password'
        },
        {
            'name': 'XAMPP默认配置',
            'host': 'localhost',
            'user': 'root',
            'password': ''
        }
    ]
    
    for config in configs:
        print(f"\n测试配置: {config['name']}")
        print("-" * 30)
        
        try:
            conn = mysql.connector.connect(
                host=config['host'],
                user=config['user'],
                password=config['password']
            )
            print(f"✓ 连接成功!")
            conn.close()
            return config  # 返回成功的配置
        except mysql.connector.Error as err:
            print(f"✗ 连接失败: {err}")
    
    print("\n所有配置都失败了!")
    print("\n请尝试以下解决方案:")
    print("1. 确认MySQL服务正在运行")
    print("2. 检查MySQL用户名和密码")
    print("3. 如果使用XAMPP/WAMP，检查默认配置")
    print("4. 尝试重置MySQL root密码")
    
    return None

def main():
    print("MySQL数据库连接诊断工具")
    print("=" * 50)
    
    # 测试连接
    working_config = test_connection()
    
    if working_config:
        print("\n找到可用配置:")
        print(f"主机: {working_config['host']}")
        print(f"用户: {working_config['user']}")
        print(f"密码: {working_config['password']}")
        
        # 测试创建数据库
        try:
            conn = mysql.connector.connect(
                host=working_config['host'],
                user=working_config['user'],
                password=working_config['password']
            )
            cursor = conn.cursor()
            
            # 测试创建数据库
            print("\n测试创建数据库...")
            cursor.execute("CREATE DATABASE IF NOT EXISTS movie_test_db")
            print("✓ 成功创建数据库")
            
            # 删除测试数据库
            cursor.execute("DROP DATABASE movie_test_db")
            print("✓ 成功删除测试数据库")
            
            cursor.close()
            conn.close()
            
            print("\n数据库连接和权限测试通过!")
            print("您可以更新app.py中的数据库配置为:")
            print(f"'{working_config['password']}'")
            
        except mysql.connector.Error as err:
            print(f"数据库操作失败: {err}")
            print("可能是权限不足")

if __name__ == "__main__":
    main()