from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
from datetime import datetime
from markupsafe import Markup  # CHANGED THIS LINE

# Initialize Flask app
app = Flask(__name__)

# PostgreSQL Database Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:root@localhost/flask_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize SQLAlchemy
db = SQLAlchemy(app)

# Test function to check database connection - ALTERNATIVE METHOD
@app.route('/test-db')
def test_db():
    try:
        # Method 1: Use engine directly which is more reliable
        with db.engine.connect() as connection:
            result = connection.execute(text("SELECT 1"))
            value = result.scalar()
            return f'Database connection successful! Result: {value}'
    except Exception as e:
        return f'Error connecting to database: {str(e)}'

# Alternative test route in case the first one still has issues
@app.route('/test-db2')
def test_db2():
    try:
        # Method 2: Use with statement for session
        with db.session() as session:
            result = session.execute(text("SELECT 1")).scalar_one()
            return f'Database connection successful! Result: {result}'
    except Exception as e:
        return f'Error connecting to database: {str(e)}'

@app.route('/')
def index():
    # Get 4 newest books for the homepage
    newest_books = Book.query.order_by(Book.added_date.desc()).limit(4).all()
    return render_template('index.html', newest_books=newest_books)

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/register')
def register():
    return render_template('register.html')

@app.route('/catalogue')
def catalogue():
    # Get all books from database
    books = Book.query.all()
    
    # Get all categories for the filter dropdown
    categories = Category.query.all()
    
    return render_template('catalogue.html', books=books, categories=categories)

@app.route('/book/<int:book_id>')
def book_detail(book_id):
    # Get the requested book or return 404 if not found
    book = Book.query.get_or_404(book_id)
    
    # Get the category of the book
    category = Category.query.get(book.category_id)
    
    # Get similar books (same category)
    similar_books = Book.query.filter(Book.category_id == book.category_id, 
                                     Book.id != book.id).limit(3).all()
    
    # If we don't have enough similar books, get some other books
    if len(similar_books) < 3:
        more_books = Book.query.filter(Book.id != book.id).limit(3 - len(similar_books)).all()
        for b in more_books:
            if b not in similar_books:
                similar_books.append(b)
    
    return render_template('book_detail.html', 
                          book=book, 
                          category=category,
                          similar_books=similar_books)

# Define Models
class Category(db.Model):
    __tablename__ = 'categories'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True)
    
    def __repr__(self):
        return f'<Category {self.name}>'

class Book(db.Model):
    __tablename__ = 'books'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    author = db.Column(db.String(100), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'))
    description = db.Column(db.Text)
    image_url = db.Column(db.String(255))
    status = db.Column(db.String(20), default='available')  # 'available' or 'borrowed'
    added_date = db.Column(db.DateTime, default=datetime.utcnow)
    
    category = db.relationship('Category', backref='books')
    
    def __repr__(self):
        return f'<Book {self.title}>'

# Database initialization command - ADD THIS CODE HERE
@app.cli.command("init-db")
def init_db():
    db.create_all()
    print("Database tables created")
    
    # Add sample categories if they don't exist
    if Category.query.count() == 0:
        categories = [
            "Informatique", 
            "Science-Fiction", 
            "Roman", 
            "Histoire",
            "Philosophie",
            "Sciences"
        ]
        for cat_name in categories:
            db.session.add(Category(name=cat_name))
        db.session.commit()
        print("Sample categories added")
    
    # Add sample books if no books exist
    if Book.query.count() == 0:
        # Get category IDs
        info_cat = Category.query.filter_by(name="Informatique").first()
        sf_cat = Category.query.filter_by(name="Science-Fiction").first()
        roman_cat = Category.query.filter_by(name="Roman").first()
        history_cat = Category.query.filter_by(name="Histoire").first()
        
        # Sample books
        books = [
            Book(
                title="Apprendre PHP en 30 jours",
                author="Jean Dupont",
                category_id=info_cat.id,
                description="Un guide pratique pour apprendre PHP rapidement et efficacement.",
                status="available"
            ),
            Book(
                title="Dune",
                author="Frank Herbert",
                category_id=sf_cat.id,
                description="L'épopée de science-fiction la plus vendue au monde.",
                status="borrowed"
            ),
            Book(
                title="L'Étranger",
                author="Albert Camus",
                category_id=roman_cat.id,
                description="Un roman philosophique explorant l'absurdité de l'existence.",
                status="available"
            ),
            Book(
                title="Histoire de l'Europe",
                author="Marie Lambert",
                category_id=history_cat.id,
                description="Une exploration complète de l'histoire européenne.",
                status="available"
            ),
            Book(
                title="Neuromancien",
                author="William Gibson",
                category_id=sf_cat.id,
                description="Le roman fondateur du mouvement cyberpunk.",
                status="borrowed"
            ),
            Book(
                title="Python pour les débutants",
                author="Sophie Dubois",
                category_id=info_cat.id,
                description="Une introduction complète à la programmation Python.",
                status="available"
            )
        ]
        
        # Add books to database
        for book in books:
            db.session.add(book)
        db.session.commit()
        print("Sample books added")

# Add this after creating the Flask app
@app.template_filter('nl2br')
def nl2br_filter(text):
    if not text:
        return ""
    return Markup(text.replace('\n', '<br>'))

# This should be the last line in your file
if __name__ == '__main__':
    app.run(debug=True)
