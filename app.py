from flask import Flask, render_template, request, redirect, url_for, flash
from models import db, Author, Book, Category, Language, CoverType
from datetime import datetime
import os
import sys
import json

# for multiple ports
import threading

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///library.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

# Home page
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

# Reset database
def reset_db():
    # backup database
    if not os.path.exists('./instance/library.db'):
        # if folder does not exist, create it
        if not os.path.exists('./instance'):
            os.makedirs('./instance')
    else:
        # copy database file to a backup file
        os.system('cp ./instance/library.db ./instance/library.db.bak')

    # check if json file exists
    if not os.path.exists('./instance/library.json'):
        return
    
    with app.app_context():
        db.drop_all()
        db.create_all()

        # load json file
        with open('./instance/library.json', 'r') as f:
            data = json.load(f)
            # print(data)

            # add categories
            for cat in data['categories']:
                # print(cat)
                db.session.add(Category(name=cat['name'], description=cat['description']))
            db.session.commit()

            # add languages
            for lang in data['languages']:
                # print(lang)
                db.session.add(Language(name=lang['name'], description=lang['description']))
            db.session.commit()

            # add cover types
            for cover_type in data['cover_types']:
                # print(cover_type)
                db.session.add(CoverType(name=cover_type))
            db.session.commit()

            # add authors
            for author in data['authors']:
                # print(author)
                # print(Language.query.filter_by(name=author['nationality']).first().id)
                db.session.add(Author(name=author['name'], nationality_id=Language.query.filter_by(name=author['nationality']).first().id,
                                      birth_date=datetime.strptime(author['birth_date'], '%Y-%m-%d'),
                                      is_alive=author['is_alive'], biography=author['biography']))
            db.session.commit()

            # add books
            for book in data['books']:
                # print(book)
                db.session.add(Book(title=book['title'], 
                                    author_id=Author.query.filter_by(name=book['author']).first().id,
                                    language_id=Language.query.filter_by(name=book['language']).first().id,
                                    cover_type_id=CoverType.query.filter_by(name=book['cover_type']).first().id,
                                    publisher=book['publisher'],
                                    publish_year=int(book['publish_year']), 
                                    edition=book['edition'],
                                    category_id=Category.query.filter_by(name=book['category']).first().id,
                                    description=book['description'],
                                    pages=int(book['pages']), 
                                    price=float(book['price']), 
                                    ))
            db.session.commit()

# Book list page
@app.route('/books')
def books():
    all_books = Book.query.all()
    return render_template('books.html', books=all_books)

# Book detail page
@app.route('/book/<int:book_id>')
def book_detail(book_id):
    book = Book.query.get_or_404(book_id)
    return render_template('book_detail.html', book=book)

# Add Book Form
@app.route('/add-book', methods=['GET', 'POST'])
def add_book():
    authors = Author.query.all()
    categories = Category.query.all()
    cover_types = CoverType.query.all()
    languages = Language.query.all()
    
    if request.method == 'POST':
        # Validate form data
        errors = []
        title = request.form['title'].strip()
        author_id = request.form['author_id']
        category_id = request.form['category_id']
        language_id = request.form['language_id']
        cover_type_id = request.form['cover_type_id']
        publish_year = request.form['publish_year']
        pages = request.form['pages']
        price = request.form['price']
        description = request.form['description'].strip()

        # print(f"{title}, {author_id}, {publish_year}, {pages}, {description}")
        
        if not title:
            errors.append('Book title cannot be empty')
        
        if errors:
            return render_template('add_book.html',
                                   authors=authors, 
                                   categories=categories,
                                   cover_types=cover_types,
                                   languages=languages,
                                   errors=errors)
        
        # Create book instance
        try:
            book = Book(
                title=title,
                author_id=author_id,
                publish_year=int(publish_year) if publish_year else None,
                pages=int(pages) if pages else None,
                price=float(price) if price else None,
                description=description,
                category_id=category_id,
                language_id=language_id,
                cover_type_id=cover_type_id,
                publisher=request.form['publisher'],
                edition=request.form['edition'],
            )

            db.session.add(book)
            db.session.commit()
            
            flash('Book added successfully!', 'success')
            return redirect(url_for('books'))
            
        except Exception as e:
            db.session.rollback()
            # book_info = f"Book title: {title}, Author: {author_id}, Language: {request.form['language']}, Cover type: {request.form['cover_type']}, Category: {request.form['category']}, Publish year: {publish_year}, Pages: {pages}, Price: {price}, Description: {description}"
            # errors.append(f'Add book failed: {str(e)}, {book_info}')
            errors.append(f'Add book failed: {str(e)}')
            return render_template('add_book.html',
                                   authors=authors, 
                                   categories=categories,
                                   cover_types=cover_types, 
                                   languages=languages,
                                   errors=errors)
    
    return render_template('add_book.html', authors=authors, categories=categories, cover_types=cover_types, languages=languages)

# add author form
@app.route('/add-author', methods=['GET', 'POST'])
def add_author():
    if request.method == 'POST':
        errors = []
        name = request.form['name'].strip()
        birth_date_str = request.form['birth_date']
        nationality_id = request.form['nationality_id'].strip()
        biography = request.form['biography'].strip()

        if not name:
            errors.append('Author name cannot be empty')

        # Process birth date
        birth_date = None
        if birth_date_str:
            try:
                birth_date = datetime.strptime(birth_date_str, '%Y-%m-%d').date()
            except ValueError:
                errors.append('Invalid birth date format')

        if errors:
            return render_template('add_author.html', errors=errors)

        try:
            author = Author(
                name=name,
                birth_date=birth_date,
                nationality_id=nationality_id,
                biography=biography
            )
            db.session.add(author)
            db.session.commit()
            flash('Author added successfully!', 'success')
            return redirect(url_for('list_authors'))
        
        except Exception as e:
            db.session.rollback()
            errors.append(f'Add author failed: {str(e)}')
            return render_template('add_author.html', errors=errors)

    return render_template('add_author.html', nationalities=Language.query.all())

# List authors page
@app.route('/authors')
def list_authors():
    return render_template('authors.html', authors=Author.query.all())

# Edit author page
@app.route('/edit-author/<int:author_id>', methods=['GET', 'POST'])
def edit_author(author_id):
    author = Author.query.get_or_404(author_id)
    if request.method == 'POST':
        author.name = request.form['name'].strip()
        birth_date_str = request.form['birth_date']
        author.nationality_id = int(request.form['nationality_id'].strip())
        author.biography = request.form['biography'].strip()

        if birth_date_str:
            try:
                author.birth_date = datetime.strptime(birth_date_str, '%Y-%m-%d').date()
            except ValueError:
                return render_template('edit_author.html', author=author, errors=['Invalid birth date format'])
        else:
            author.birth_date = None

        db.session.commit()
        flash('Author updated successfully!', 'success')
        return redirect(url_for('list_authors'))
        
    return render_template('edit_author.html', author=author, nationalities=Language.query.all())

# Delete author page
@app.route('/delete-author/<int:author_id>', methods=['GET', 'POST'])
def delete_author(author_id):
    author = Author.query.get_or_404(author_id)
    # Get all books in the author's books relationship
    affected_books = author.books 

    if request.method == 'POST':
        try:
            # Cascade delete all books in the author's books relationship
            # delete book first
            for book in affected_books:
                db.session.delete(book)

            # delete author last
            db.session.delete(author)
            db.session.commit()
            flash(f'Author {author.name} and its {len(affected_books)} books have been deleted successfully!', 'success')
            return redirect(url_for('list_authors'))
        except Exception as e:
            db.session.rollback()
            flash(f'Delete failed: {str(e)}', 'danger')
            return redirect(url_for('list_authors'))

    # GET request, render delete confirm page
    return render_template('delete_confirm.html', 
                           type='author', 
                           item_name=author.name, 
                           books=affected_books, 
                           cancel_url=url_for('list_authors'))

# List categories page
@app.route('/categories')
def list_categories():
    categories = Category.query.all()
    return render_template('categories.html', categories=categories)

@app.route('/languages')
def list_languages():
    return render_template('languages.html', languages=Language.query.all())

@app.route('/add-language', methods=['GET', 'POST'])
def add_language():
    if request.method == 'POST':
        errors = []
        name = request.form['name'].strip()
        description = request.form['description'].strip()
        
        if not name:
            errors.append('Language name cannot be empty')
        
        elif Language.query.filter_by(name=name).first():
            errors.append('Language name already exists')

        if errors:
            return render_template('add_language.html', errors=errors)
        
        try:
            language = Language(name=name, description=description)
            db.session.add(language)
            db.session.commit()
            flash('Language added successfully!', 'success')
            return redirect(url_for('list_languages'))
        
        except Exception as e:
            db.session.rollback()
            errors.append(f'Add language failed: {str(e)}')
            return render_template('add_language.html', errors=errors)
        
    return render_template('add_language.html')

@app.route('/edit-language/<int:language_id>', methods=['GET', 'POST'])
def edit_language(language_id):
    language = Language.query.get_or_404(language_id)
    language_name_before = language.name

    if request.method == 'POST':
        errors = []

        language.name = request.form['name'].strip()
        language.description = request.form['description'].strip()
        
        # Check if the language name is unique
        if language_name_before != language.name and Language.query.filter_by(name=language.name).first():
            errors.append('Language name already exists')

        # Check if the language name is not empty
        elif not language.name:
            errors.append('Language name cannot be empty')
        
        # Check if the language description is not empty
        elif not language.description:
            errors.append('Language description cannot be empty')

        # if errors, return to form
        if errors:
            return render_template('edit_language.html', language=language, errors=errors)
        
        db.session.commit()
        flash('Language updated successfully!', 'success')
        return redirect(url_for('list_languages'))

    return render_template('edit_language.html', language=language)

@app.route('/delete-language/<int:language_id>', methods=['GET', 'POST'])
def delete_language(language_id):
    language = Language.query.get_or_404(language_id)
    if request.method == 'POST':
        try:
            db.session.delete(language)
            db.session.commit()
            flash(f'Language {language.name} has been deleted successfully!', 'success')
            return redirect(url_for('list_languages'))
        except Exception as e:
            db.session.rollback()
            flash(f'Delete failed: {str(e)}', 'danger')
            return redirect(url_for('list_languages'))

    # GET request, render delete confirm page
    return render_template('delete_confirm.html', 
                           type='language', 
                           item_name=language.name, 
                           cancel_url=url_for('list_languages'))

# Edit category page
@app.route('/edit-category/<int:category_id>', methods=['GET', 'POST'])
def edit_category(category_id):
    category = Category.query.get_or_404(category_id)
    if request.method == 'POST':
        errors = []
        if not Category.query.filter_by(name=request.form['name'].strip()).first():
            errors.append('Category name not exists')

        # category.name = request.form['name'].strip()
        category.description = request.form['description'].strip()
        
        # if errors, return to form
        if errors:
            return render_template('edit_category.html', category=category, errors=errors)
        
        db.session.commit()
        flash('Category updated successfully!', 'success')
        return redirect(url_for('list_categories'))
        
    return render_template('edit_category.html', category=category)

# Delete category page
@app.route('/delete-category/<int:category_id>', methods=['GET', 'POST'])
def delete_category(category_id):
    category = Category.query.get_or_404(category_id)

    # Fetch all books in the category's books relationship
    affected_books = category.books

    if request.method == 'POST':
        try:
            # Delete all books in the category's books relationship
            for book in affected_books:
                db.session.delete(book)
            db.session.delete(category)
            db.session.commit()
            flash(f'Category {category.name} and its {len(affected_books)} books have been deleted successfully!', 'success')
            return redirect(url_for('list_categories'))
        except Exception as e:
            db.session.rollback()
            flash(f'Delete failed: {str(e)}', 'danger')
            return redirect(url_for('list_categories'))

    # GET request, render delete confirm page
    return render_template('delete_confirm.html', 
                           type='category', 
                           item_name=category.name, 
                           books=affected_books, 
                           cancel_url=url_for('list_categories'))

# Add category page
@app.route('/add-category', methods=['GET', 'POST'])
def add_category():
    if request.method == 'POST':
        errors = []
        name = request.form['name'].strip()
        description = request.form['description'].strip()

        if not name:
            errors.append('Category name cannot be empty')
        
        # Check if category name already exists
        if Category.query.filter_by(name=name).first():
            errors.append('Category name already exists')

        if errors:
            return render_template('add_category.html', errors=errors)

        try:
            category = Category(name=name, description=description)
            db.session.add(category)
            db.session.commit()
            flash('Category added successfully!', 'success')
            return redirect(url_for('list_categories'))
        except Exception as e:
            db.session.rollback()
            errors.append(f'Add failed: {str(e)}')
            return render_template('add_category.html', errors=errors)

    return render_template('add_category.html')

# Delete book page
@app.route('/delete-book/<int:book_id>', methods=['POST'])
def delete_book(book_id):
    book = Book.query.get_or_404(book_id)
    db.session.delete(book)
    db.session.commit()
    flash('Book deleted successfully!', 'success')
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

    if len(sys.argv) > 1 and sys.argv[1] == 'reset':
        reset_db()
        print('Database reset successfully.')
    else:
        t1 = threading.Thread(target=listen_port_80)
        t2 = threading.Thread(target=listen_port_443)
        t1.start()
        t2.start()
