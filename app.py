from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import mysql.connector
import bcrypt
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'movie_recommendation_system'

# 数据库配置
db_config = {
    'host': 'localhost',
    'user': 'root',      # 请替换为您的MySQL用户名
    'password': '',       # 请替换为您的MySQL密码
    'database': 'movie_db'
}

# 获取数据库连接
def get_db_connection():
    return mysql.connector.connect(**db_config)

# 创建数据库和表
def setup_database():
    try:
        # 连接到MySQL服务器（不指定数据库）
        conn = mysql.connector.connect(
            host='localhost',
            user='root',  # 请替换为您的MySQL用户名
            password=''    # 请替换为您的MySQL密码
        )
        cursor = conn.cursor()
        
        # 创建数据库
        cursor.execute("CREATE DATABASE IF NOT EXISTS movie_db")
        cursor.execute("USE movie_db")
        
        # 创建用户表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(50) NOT NULL UNIQUE,
                password VARCHAR(255) NOT NULL,
                email VARCHAR(100) NOT NULL UNIQUE,
                role ENUM('user', 'admin') DEFAULT 'user',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # 创建电影表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS movies (
                id INT AUTO_INCREMENT PRIMARY KEY,
                title VARCHAR(255) NOT NULL,
                director VARCHAR(100),
                year INT,
                genre VARCHAR(50),
                description TEXT,
                image_url VARCHAR(255),
                rating DECIMAL(3,1) DEFAULT 0.0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # 创建评分表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS ratings (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                movie_id INT NOT NULL,
                rating DECIMAL(2,1) NOT NULL,
                review TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id),
                FOREIGN KEY (movie_id) REFERENCES movies(id),
                UNIQUE KEY unique_user_movie (user_id, movie_id)
            )
        """)
        
        # 创建分类表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS categories (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(50) NOT NULL UNIQUE
            )
        """)
        
        # 创建电影分类关联表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS movie_categories (
                id INT AUTO_INCREMENT PRIMARY KEY,
                movie_id INT NOT NULL,
                category_id INT NOT NULL,
                FOREIGN KEY (movie_id) REFERENCES movies(id),
                FOREIGN KEY (category_id) REFERENCES categories(id)
            )
        """)
        
        # 检查是否有管理员账号
        cursor.execute("SELECT * FROM users WHERE username = 'admin'")
        if not cursor.fetchone():
            # 添加管理员账号
            hashed_password = bcrypt.hashpw('admin123'.encode('utf-8'), bcrypt.gensalt())
            cursor.execute(
                "INSERT INTO users (username, password, email, role) VALUES (%s, %s, %s, %s)",
                ('admin', hashed_password, 'admin@movie.com', 'admin')
            )
        
        # 检查是否有分类数据
        cursor.execute("SELECT * FROM categories")
        if not cursor.fetchone():
            # 添加电影分类
            categories = ['动作片', '喜剧片', '爱情片', '科幻片', '恐怖片', '剧情片']
            for category in categories:
                cursor.execute("INSERT INTO categories (name) VALUES (%s)", (category,))
        
        # 检查是否有电影数据
        cursor.execute("SELECT * FROM movies")
        if not cursor.fetchone():
            # 添加示例电影数据
            sample_movies = [
                ('盗梦空间', '克里斯托弗·诺兰', 2010, '科幻/悬疑', '一个专业的小偷，擅长潜入他人梦境窃取机密。', 'https://example.com/inception.jpg', 8.8),
                ('肖申克的救赎', '弗兰克·德拉邦特', 1994, '剧情', '一个被错误定罪的男人在监狱中寻找希望和自由的故事。', 'https://example.com/shawshank.jpg', 9.3),
                ('泰坦尼克号', '詹姆斯·卡梅隆', 1997, '爱情/灾难', '一艘豪华游轮上的爱情故事与海难。', 'https://example.com/titanic.jpg', 7.8),
                ('阿凡达', '詹姆斯·卡梅隆', 2009, '科幻/动作', '一个残疾的前海军陆战队员在一个外星球上的冒险。', 'https://example.com/avatar.jpg', 7.8),
                ('复仇者联盟：终局之战', '罗素兄弟', 2019, '动作/科幻', '超级英雄们集结，对抗终极威胁的史诗之战。', 'https://example.com/avengers.jpg', 8.4),
            ]
            
            for movie in sample_movies:
                cursor.execute(
                    "INSERT INTO movies (title, director, year, genre, description, image_url, rating) VALUES (%s, %s, %s, %s, %s, %s, %s)",
                    movie
                )
                
                # 获取刚插入的电影ID
                movie_id = cursor.lastrowid
                
                # 为电影分配分类（简单地将电影类型映射到分类）
                genre_to_category = {
                    '科幻/悬疑': 4,  # 科幻片
                    '剧情': 6,       # 剧情片
                    '爱情/灾难': 3,  # 爱情片
                    '科幻/动作': 4,  # 科幻片
                }
                
                if movie[3] in genre_to_category:
                    cursor.execute(
                        "INSERT INTO movie_categories (movie_id, category_id) VALUES (%s, %s)",
                        (movie_id, genre_to_category[movie[3]])
                    )
        
        conn.commit()
        cursor.close()
        conn.close()
        print("数据库初始化完成！")
        return True
    except Exception as e:
        print(f"数据库初始化错误: {e}")
        return False

# 首页路由
@app.route('/')
def index():
    # 检查用户是否登录
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    # 获取推荐电影（评分最高的前8部电影）
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("""
        SELECT * FROM movies 
        ORDER BY rating DESC 
        LIMIT 8
    """)
    movies = cursor.fetchall()
    
    # 获取所有分类
    cursor.execute("SELECT * FROM categories")
    categories = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return render_template('index.html', movies=movies, categories=categories, user=session)

# 登录路由
@app.route('/login', methods=['GET', 'POST'])
def login():
    # 如果已经登录，重定向到首页
    if 'user_id' in session:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
        user = cursor.fetchone()
        
        cursor.close()
        conn.close()
        
        # 注意：bcrypt.checkpw需要两个bytes参数，从数据库取出的密码已经是bytes格式
        if user and bcrypt.checkpw(password.encode('utf-8'), user['password']):
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['role'] = user['role']
            return redirect(url_for('index'))
        else:
            return render_template('login.html', error='用户名或密码错误')
    
    return render_template('login.html')

# 注册路由
@app.route('/register', methods=['GET', 'POST'])
def register():
    # 如果已经登录，重定向到首页
    if 'user_id' in session:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        
        # 简单验证
        if not username or not email or not password:
            return render_template('register.html', error='所有字段都是必填的')
        
        if len(password) < 6:
            return render_template('register.html', error='密码必须至少6个字符')
        
        # 检查用户名和邮箱是否已存在
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("SELECT * FROM users WHERE username = %s OR email = %s", (username, email))
        existing_user = cursor.fetchone()
        
        if existing_user:
            cursor.close()
            conn.close()
            return render_template('register.html', error='用户名或邮箱已存在')
        
        # 创建新用户
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        cursor.execute(
            "INSERT INTO users (username, email, password) VALUES (%s, %s, %s)",
            (username, email, hashed_password)
        )
        
        cursor.close()
        conn.close()
        
        return redirect(url_for('login'))
    
    return render_template('register.html')

# 登出路由
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# 搜索路由
@app.route('/search', methods=['POST'])
def search():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    query = request.form['query']
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("""
        SELECT * FROM movies 
        WHERE title LIKE %s OR director LIKE %s OR genre LIKE %s
        ORDER BY rating DESC
    """, (f'%{query}%', f'%{query}%', f'%{query}%'))
    
    movies = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return render_template('search_results.html', movies=movies, query=query, user=session)

# 分类路由
@app.route('/category/<int:category_id>')
def category(category_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # 获取分类名称
    cursor.execute("SELECT name FROM categories WHERE id = %s", (category_id,))
    category = cursor.fetchone()
    
    if not category:
        return redirect(url_for('index'))
    
    # 获取该分类下的电影
    cursor.execute("""
        SELECT m.* FROM movies m
        JOIN movie_categories mc ON m.id = mc.movie_id
        WHERE mc.category_id = %s
        ORDER BY m.rating DESC
    """, (category_id,))
    
    movies = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return render_template('category.html', movies=movies, category=category, user=session)

# 电影详情路由
@app.route('/movie/<int:movie_id>')
def movie_detail(movie_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # 获取电影详情
    cursor.execute("SELECT * FROM movies WHERE id = %s", (movie_id,))
    movie = cursor.fetchone()
    
    if not movie:
        return redirect(url_for('index'))
    
    # 获取用户评分
    cursor.execute("""
        SELECT r.rating, r.review, u.username
        FROM ratings r
        JOIN users u ON r.user_id = u.id
        WHERE r.movie_id = %s
        ORDER BY r.created_at DESC
    """, (movie_id,))
    
    ratings = cursor.fetchall()
    
    # 检查当前用户是否已评分
    user_rating = None
    cursor.execute(
        "SELECT * FROM ratings WHERE user_id = %s AND movie_id = %s",
        (session['user_id'], movie_id)
    )
    user_rating = cursor.fetchone()
    
    cursor.close()
    conn.close()
    
    return render_template('movie_detail.html', movie=movie, ratings=ratings, user_rating=user_rating, user=session)

# 评分路由
@app.route('/rate/<int:movie_id>', methods=['POST'])
def rate_movie(movie_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    rating = request.form['rating']
    review = request.form.get('review', '')
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 检查是否已评分
    cursor.execute(
        "SELECT * FROM ratings WHERE user_id = %s AND movie_id = %s",
        (session['user_id'], movie_id)
    )
    existing_rating = cursor.fetchone()
    
    if existing_rating:
        # 更新评分
        cursor.execute(
            "UPDATE ratings SET rating = %s, review = %s WHERE user_id = %s AND movie_id = %s",
            (rating, review, session['user_id'], movie_id)
        )
    else:
        # 添加新评分
        cursor.execute(
            "INSERT INTO ratings (user_id, movie_id, rating, review) VALUES (%s, %s, %s, %s)",
            (session['user_id'], movie_id, rating, review)
        )
    
    # 更新电影平均评分
    cursor.execute("""
        UPDATE movies SET rating = (
            SELECT AVG(rating) FROM ratings WHERE movie_id = %s
        ) WHERE id = %s
    """, (movie_id, movie_id))
    
    conn.commit()
    cursor.close()
    conn.close()
    
    return redirect(url_for('movie_detail', movie_id=movie_id))

# 管理员路由 - 添加电影
@app.route('/admin/add_movie', methods=['GET', 'POST'])
def admin_add_movie():
    # 检查是否登录且是管理员
    if 'user_id' not in session or session.get('role') != 'admin':
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        title = request.form['title']
        director = request.form['director']
        year = request.form['year']
        genre = request.form['genre']
        description = request.form['description']
        image_url = request.form.get('image_url', '')
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 添加电影
        cursor.execute(
            "INSERT INTO movies (title, director, year, genre, description, image_url) VALUES (%s, %s, %s, %s, %s, %s)",
            (title, director, year, genre, description, image_url)
        )
        
        movie_id = cursor.lastrowid
        
        # 添加分类关联
        categories = request.form.getlist('categories')
        for category_id in categories:
            cursor.execute(
                "INSERT INTO movie_categories (movie_id, category_id) VALUES (%s, %s)",
                (movie_id, category_id)
            )
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return redirect(url_for('admin_panel'))
    
    # 获取所有分类
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM categories")
    categories = cursor.fetchall()
    cursor.close()
    conn.close()
    
    return render_template('admin_add_movie.html', categories=categories, user=session)

# 管理员面板
@app.route('/admin')
def admin_panel():
    # 检查是否登录且是管理员
    if 'user_id' not in session or session.get('role') != 'admin':
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # 获取所有电影
    cursor.execute("SELECT * FROM movies ORDER BY created_at DESC")
    movies = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return render_template('admin_panel.html', movies=movies, user=session)

# 删除电影路由
@app.route('/admin/delete_movie/<int:movie_id>')
def admin_delete_movie(movie_id):
    # 检查是否登录且是管理员
    if 'user_id' not in session or session.get('role') != 'admin':
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 删除电影相关评分
    cursor.execute("DELETE FROM ratings WHERE movie_id = %s", (movie_id,))
    
    # 删除电影分类关联
    cursor.execute("DELETE FROM movie_categories WHERE movie_id = %s", (movie_id,))
    
    # 删除电影
    cursor.execute("DELETE FROM movies WHERE id = %s", (movie_id,))
    
    conn.commit()
    cursor.close()
    conn.close()
    
    return redirect(url_for('admin_panel'))

if __name__ == '__main__':
    # 初始化数据库
    if setup_database():
        print("数据库初始化成功，启动应用...")
        app.run(debug=True)
    else:
        print("数据库初始化失败，请检查配置。")