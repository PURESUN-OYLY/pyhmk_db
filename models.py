from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

# Book Category
class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True)
    description = db.Column(db.String(200))

    def __repr__(self):
        return f'<Category {self.name}>'
    
# Book Language
class Language(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True)

    # One-to-many relationship with Book and Author, foreign key
    books = db.relationship('Book', backref='language', lazy=True)
    authors = db.relationship('Author', backref='nationality', lazy=True)
    
    def __repr__(self):
        return f'<Language {self.name}>'

# Book Cover Type
class CoverType(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True)

    # One-to-many relationship with Book, foreign key
    books = db.relationship('Book', backref='cover_type', lazy=True)
    
    def __repr__(self):
        return f'<CoverType {self.name}>'

# Book Author, one-to-many relationship
# One author can write multiple books.
class Author(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    birth_date = db.Column(db.Date)

    # Language foreign key
    nationality_id = db.Column(db.Integer, db.ForeignKey('language.id'), nullable=False)

    is_alive = db.Column(db.Boolean, default=True)
    biography = db.Column(db.Text)
    
    # One-to-many relationship with Book, foreign key
    books = db.relationship('Book', backref='author', lazy=True)
    
    def __repr__(self):
        return f'<Author {self.name}>'

# Book, main entity
class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    publish_year = db.Column(db.Integer)
    publisher = db.Column(db.String(256))
    edition = db.Column(db.String(50))
    pages = db.Column(db.Integer)
    price = db.Column(db.Float)
    description = db.Column(db.Text)
    added_date = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Author foreign key
    author_id = db.Column(db.Integer, db.ForeignKey('author.id'), nullable=False)
    
    # Category foreign key
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)
    category = db.relationship('Category', backref='books', lazy=True)

    # Language foreign key
    language_id = db.Column(db.Integer, db.ForeignKey('language.id'), nullable=False)

    # Cover Type foreign key
    cover_type_id = db.Column(db.Integer, db.ForeignKey('cover_type.id'), nullable=False)
    
    def __repr__(self):
        return f'<Book {self.title}>'
