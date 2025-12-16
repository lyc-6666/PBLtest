# 电影推荐系统数据库设计

## 用户表 (users)
```sql
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    role ENUM('user', 'admin') DEFAULT 'user',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## 电影表 (movies)
```sql
CREATE TABLE movies (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    director VARCHAR(100),
    year INT,
    genre VARCHAR(50),
    description TEXT,
    image_url VARCHAR(255),
    rating DECIMAL(3,1) DEFAULT 0.0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## 评分表 (ratings)
```sql
CREATE TABLE ratings (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    movie_id INT NOT NULL,
    rating DECIMAL(2,1) NOT NULL,
    review TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (movie_id) REFERENCES movies(id),
    UNIQUE KEY unique_user_movie (user_id, movie_id)
);
```

## 电影分类表 (categories)
```sql
CREATE TABLE categories (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE
);
```

## 电影分类关联表 (movie_categories)
```sql
CREATE TABLE movie_categories (
    id INT AUTO_INCREMENT PRIMARY KEY,
    movie_id INT NOT NULL,
    category_id INT NOT NULL,
    FOREIGN KEY (movie_id) REFERENCES movies(id),
    FOREIGN KEY (category_id) REFERENCES categories(id)
);
```

## 插入示例数据
```sql
INSERT INTO categories (name) VALUES 
('动作片'), ('喜剧片'), ('爱情片'), ('科幻片'), ('恐怖片'), ('剧情片');

-- 添加管理员账号
INSERT INTO users (username, password, email, role) VALUES 
('admin', 'admin123', 'admin@movie.com', 'admin');
```