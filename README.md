# 电影推荐系统

一个基于Flask和MySQL的完整电影推荐系统，支持用户注册、登录、电影浏览、评分和管理功能。

## 功能特点

- 用户注册和登录
- 管理员和普通用户两种角色
- 电影浏览和搜索
- 按分类查看电影
- 用户电影评分和评论
- 管理员电影管理功能
- 响应式UI设计

## 技术栈

- **前端**: HTML5, CSS3, Bootstrap 5
- **后端**: Python, Flask
- **数据库**: MySQL
- **认证**: bcrypt密码加密

## 安装和运行

### 1. 安装MySQL数据库

确保您的系统已安装MySQL数据库服务，并创建一个用户（如果尚未创建）。

### 2. 安装Python依赖

```bash
pip install -r requirements.txt
```

### 3. 配置数据库连接

编辑 `app.py` 文件，修改数据库配置:

```python
db_config = {
    'host': 'localhost',    # 数据库主机地址
    'user': 'root',         # 您的MySQL用户名
    'password': '',         # 您的MySQL密码
    'database': 'movie_db'  # 数据库名称
}
```

### 4. 运行应用

```bash
python app.py
```

应用将在 `http://127.0.0.1:5000` 上启动。

## 使用指南

### 默认账户

- 管理员账户:
  - 用户名: `admin`
  - 密码: `admin123`

### 主要功能

1. **用户功能**:
   - 注册新账户
   - 登录和退出
   - 浏览电影推荐
   - 搜索电影
   - 按分类查看电影
   - 查看电影详情
   - 为电影评分和评论

2. **管理员功能**:
   - 添加新电影
   - 删除电影
   - 查看管理面板

### 系统页面结构

```
首页 (/) - 显示推荐电影和分类
登录页 (/login) - 用户登录
注册页 (/register) - 用户注册
电影详情 (/movie/<id>) - 查看特定电影详情
搜索结果 (/search) - 显示搜索结果
分类页面 (/category/<id>) - 显示特定分类电影
管理面板 (/admin) - 管理员控制面板
添加电影 (/admin/add_movie) - 管理员添加电影
删除电影 (/admin/delete_movie/<id>) - 管理员删除电影
```

## 项目结构

```
PBLtest/
├── app.py                   # 主应用文件
├── requirements.txt         # Python依赖包
├── database_design.sql      # 数据库设计文档
├── templates/               # HTML模板文件夹
│   ├── base.html           # 基础模板
│   ├── index.html          # 首页模板
│   ├── login.html          # 登录页面模板
│   ├── register.html       # 注册页面模板
│   ├── movie_detail.html   # 电影详情页模板
│   ├── search_results.html # 搜索结果页模板
│   ├── category.html       # 分类页面模板
│   ├── admin_panel.html    # 管理面板模板
│   └── admin_add_movie.html # 添加电影模板
└── README.md               # 项目说明文档
```

## 注意事项

1. 确保MySQL服务正在运行
2. 首次运行时，应用会自动创建数据库和必要的表
3. 默认情况下，应用会添加一些示例电影数据
4. 生产环境中，请修改app.secret_key为更安全的值
5. 如需自定义电影海报图片URL，请在添加电影时提供

## 联系方式

如有问题或建议，请联系系统管理员。