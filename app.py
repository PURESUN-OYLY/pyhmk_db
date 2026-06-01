from flask import Flask, render_template, request, redirect, url_for, flash
from models import db, Author, Book, BookInfo, Category
from datetime import datetime

# for multiple ports
import threading

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///library.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

# 修复：使用 app_context() 替代 before_first_request
with app.app_context():
    db.create_all()
    # 添加初始数据
    if not Category.query.first():
        categories = ['科幻小说', '文学小说', '历史', '科学', '哲学', '艺术']
        for cat in categories:
            db.session.add(Category(name=cat))
        
        author1 = Author(name='刘慈欣', birth_date=datetime(1963, 6, 23), country='中国', 
                        biography='中国科幻小说代表作家，《三体》系列作者')
        author2 = Author(name='村上春树', birth_date=datetime(1949, 1, 12), country='日本',
                        biography='日本当代著名作家，作品风格独特')
        db.session.add_all([author1, author2])
        
        book1 = Book(title='三体', isbn='9787536692930', publication_year=2008, 
                    pages=302, price=23.00, author=author1,
                    description='地球文明向宇宙发出的第一声啼鸣，改变了人类的命运')
        book2 = Book(title='挪威的森林', isbn='9787532742929', publication_year=2001,
                    pages=384, price=28.00, author=author2,
                    description='关于青春、爱情与成长的经典小说')
        
        book1_info = BookInfo(publisher='重庆出版社', language='中文', edition='第1版',
                            cover_type='平装', book=book1)
        book2_info = BookInfo(publisher='上海译文出版社', language='中文', edition='第2版',
                            cover_type='平装', book=book2)
        
        book1.categories.append(Category.query.filter_by(name='科幻小说').first())
        book2.categories.append(Category.query.filter_by(name='文学小说').first())
        
        db.session.add_all([book1, book2, book1_info, book2_info])
        db.session.commit()

# 主页
@app.route('/')
def index():
    total_books = Book.query.count()
    total_authors = Author.query.count()
    total_categories = Category.query.count()
    recent_books = Book.query.order_by(Book.added_date.desc()).limit(3).all()
    return render_template('index.html', total_books=total_books, 
                          total_authors=total_authors,
                          total_categories=total_categories,
                          recent_books=recent_books)

# 书籍列表页
@app.route('/books')
def books():
    all_books = Book.query.all()
    return render_template('books.html', books=all_books)

# 书籍详情页
@app.route('/book/<int:book_id>')
def book_detail(book_id):
    book = Book.query.get_or_404(book_id)
    return render_template('book_detail.html', book=book)

# 添加书籍表单
@app.route('/add-book', methods=['GET', 'POST'])
def add_book():
    authors = Author.query.all()
    categories = Category.query.all()
    
    if request.method == 'POST':
        # 表单验证
        errors = []
        title = request.form['title'].strip()
        isbn = request.form['isbn'].strip()
        author_id = request.form['author_id']
        publication_year = request.form['publication_year']
        pages = request.form['pages']
        price = request.form['price']
        description = request.form['description'].strip()

        print(f"{title}, {isbn}, {author_id}, {publication_year}, {pages}, {description}")
        
        if not title:
            errors.append('书名不能为空')
        if not isbn or len(isbn) != 13:
            errors.append('ISBN必须是13位数字')
        if not author_id:
            errors.append('请选择作者')
        
        if errors:
            return render_template('add_book.html', authors=authors, 
                                  categories=categories, errors=errors)
        
        # 创建书籍
        try:
            book = Book(
                title=title,
                isbn=isbn,
                author_id=author_id,
                publication_year=int(publication_year) if publication_year else None,
                pages=int(pages) if pages else None,
                price=float(price) if price else None,
                description=description
            )
            
            # 添加详细信息
            book_info = BookInfo(
                publisher=request.form['publisher'].strip(),
                language=request.form['language'].strip(),
                edition=request.form['edition'].strip(),
                cover_type=request.form['cover_type'],
                book=book
            )
            
            # 添加类别
            selected_categories = request.form.getlist('categories')
            for cat_id in selected_categories:
                category = Category.query.get(cat_id)
                if category:
                    book.categories.append(category)
            
            db.session.add(book)
            db.session.add(book_info)
            db.session.commit()
            
            flash('书籍添加成功！', 'success')
            return redirect(url_for('books'))
            
        except Exception as e:
            db.session.rollback()
            errors.append(f'添加失败：{str(e)}')
            return render_template('add_book.html', authors=authors, 
                                  categories=categories, errors=errors)
    
    return render_template('add_book.html', authors=authors, categories=categories)

# 删除书籍（可选功能）
@app.route('/delete-book/<int:book_id>', methods=['POST'])
def delete_book(book_id):
    book = Book.query.get_or_404(book_id)
    db.session.delete(book)
    db.session.commit()
    flash('书籍已删除', 'success')
    return redirect(url_for('books'))

def listen_port_80():
    app.run(debug=False, host='0.0.0.0', port=80, use_reloader=False)

def listen_port_443():
    # need dependency cryptography: pip install cryptography
    app.run(debug=False, host='0.0.0.0', port=443, use_reloader=False, 
            ssl_context=('/root/Python_Task/flask/cert/www.puresun.lib+2.pem', '/root/Python_Task/flask/cert/www.puresun.lib+2-key.pem'))

# Now can use domain name: puresun.lib and www.puresun.lib
# Use local https certificate
# Use mkcert to generate certificate: pip install mkcert
# Then run: mkcert puresun.lib www.puresun.lib
#   github: https://github.com/FiloSottile/mkcert/releases
if __name__ == '__main__':
    t1 = threading.Thread(target=listen_port_80)
    t2 = threading.Thread(target=listen_port_443)
    t1.start()
    t2.start()
