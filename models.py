from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

# 多对多关系表：书籍 <-> 类别
book_category = db.Table('book_category',
    db.Column('book_id', db.Integer, db.ForeignKey('book.id'), primary_key=True),
    db.Column('category_id', db.Integer, db.ForeignKey('category.id'), primary_key=True)
)

# 实体1：作者 - 一对多关系（一个作者有多本书）
class Author(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    birth_date = db.Column(db.Date)
    country = db.Column(db.String(50))
    is_active = db.Column(db.Boolean, default=True)
    biography = db.Column(db.Text)
    
    # 一对多关系
    books = db.relationship('Book', backref='author', lazy=True)
    
    def __repr__(self):
        return f'<Author {self.name}>'

# 实体2：书籍 - 主实体
class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    isbn = db.Column(db.String(13), unique=True, nullable=False)
    publication_year = db.Column(db.Integer)
    pages = db.Column(db.Integer)
    price = db.Column(db.Float)
    available = db.Column(db.Boolean, default=True)
    description = db.Column(db.Text)
    added_date = db.Column(db.DateTime, default=datetime.utcnow)
    
    # 一对多关系（外键）
    author_id = db.Column(db.Integer, db.ForeignKey('author.id'), nullable=False)
    
    # 一对一关系
    book_info = db.relationship('BookInfo', backref='book', uselist=False, cascade='all, delete-orphan')
    
    # 多对多关系
    categories = db.relationship('Category', secondary=book_category, backref=db.backref('books', lazy='dynamic'))
    
    def __repr__(self):
        return f'<Book {self.title}>'

# 实体3：书籍详细信息 - 一对一关系（一本书对应一个详细信息）
class BookInfo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    publisher = db.Column(db.String(100))
    language = db.Column(db.String(50))
    edition = db.Column(db.String(50))
    cover_type = db.Column(db.Enum('硬壳', '平装', '电子书', name='cover_types'))
    summary = db.Column(db.Text)
    
    # 一对一关系外键
    book_id = db.Column(db.Integer, db.ForeignKey('book.id'), nullable=False, unique=True)
    
    def __repr__(self):
        return f'<BookInfo for Book {self.book_id}>'

# 实体4：类别 - 多对多关系（一本书可以属于多个类别）
class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True)
    description = db.Column(db.String(200))
    
    def __repr__(self):
        return f'<Category {self.name}>'