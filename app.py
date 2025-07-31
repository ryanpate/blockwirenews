from flask import Flask, render_template, jsonify, request, redirect, url_for, flash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_migrate import Migrate
from datetime import datetime, timedelta
import os
from apscheduler.schedulers.background import BackgroundScheduler
import requests
from werkzeug.utils import secure_filename
import re
from functools import wraps

# Import our modules
from models import db, User, Article, NewsItem, PriceData, SiteSettings
from forms import LoginForm, RegistrationForm, ArticleForm, ProfileForm
from crypto_news_scraper import SimpleCryptoRSSFeedScraper

app = Flask(__name__)

# Configuration
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your-secret-key-here')

# Database configuration - try environment variable first, then use your macOS username
DATABASE_URL = os.environ.get('DATABASE_URL')
if not DATABASE_URL:
    # Use current macOS username for PostgreSQL connection
    import getpass
    username = getpass.getuser()
    DATABASE_URL = f'postgresql://{username}@localhost/blockwire'
    print(f"Using PostgreSQL with system user: {username}")

app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize extensions
db.init_app(app)
migrate = Migrate(app, db)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Please log in to access this page.'

# Initialize scheduler
scheduler = BackgroundScheduler()
scheduler.start()


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


def admin_required(f):
    """Decorator to require admin access"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            flash('You need administrator privileges to access this page.')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function


def create_slug(title):
    """Create URL-friendly slug from title"""
    slug = re.sub(r'[^\w\s-]', '', title.lower())
    slug = re.sub(r'[-\s]+', '-', slug)
    return slug[:50]

# Scheduled tasks


def update_news():
    """Update news from scraper and save to database"""
    print("Updating cryptocurrency news...")
    try:
        scraper = SimpleCryptoRSSFeedScraper()
        articles = scraper.scrape_all()

        with app.app_context():
            for article_data in articles:
                # Check if article already exists
                existing = NewsItem.query.filter_by(
                    external_id=article_data['id']).first()
                if not existing:
                    news_item = NewsItem(
                        external_id=article_data['id'],
                        title=article_data['title'],
                        url=article_data['url'],
                        summary=article_data.get('summary', ''),
                        source=article_data.get('source', 'Unknown'),
                        published_date=datetime.fromisoformat(
                            article_data.get('published', datetime.now().isoformat()))
                    )
                    db.session.add(news_item)

            db.session.commit()
            print(f"News update complete. Added new articles.")
    except Exception as e:
        print(f"Error updating news: {e}")


def update_prices():
    """Update cryptocurrency prices"""
    print("Updating cryptocurrency prices...")
    try:
        url = "https://api.coingecko.com/api/v3/simple/price"
        params = {
            'ids': 'bitcoin,ethereum,binancecoin,ripple,cardano,solana,polkadot,dogecoin',
            'vs_currencies': 'usd',
            'include_24hr_change': 'true',
            'include_market_cap': 'true',
            'include_24hr_vol': 'true'
        }

        # Disable SSL verification for macOS issues
        import urllib3
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        response = requests.get(url, params=params, verify=False)
        data = response.json()

        crypto_names = {
            'bitcoin': 'BTC',
            'ethereum': 'ETH',
            'binancecoin': 'BNB',
            'ripple': 'XRP',
            'cardano': 'ADA',
            'solana': 'SOL',
            'polkadot': 'DOT',
            'dogecoin': 'DOGE'
        }

        with app.app_context():
            for crypto_id, info in data.items():
                price_data = PriceData(
                    symbol=crypto_names.get(crypto_id, crypto_id).upper(),
                    name=crypto_names.get(crypto_id, crypto_id),
                    price_usd=info.get('usd', 0),
                    change_24h=info.get('usd_24h_change', 0),
                    market_cap=info.get('usd_market_cap', 0),
                    volume_24h=info.get('usd_24h_vol', 0)
                )
                db.session.add(price_data)

            db.session.commit()
            print("Price update complete.")
    except Exception as e:
        print(f"Error updating prices: {e}")


# Schedule tasks
scheduler.add_job(func=update_news, trigger="interval",
                  hours=1, id='news_updater')
scheduler.add_job(func=update_prices, trigger="interval",
                  minutes=5, id='price_updater')

# Routes


@app.route('/')
def index():
    """Main page with news and price ticker"""
    try:
        # Get latest news
        news = NewsItem.query.order_by(
            NewsItem.published_date.desc()).limit(15).all()
    except:
        news = []

    try:
        # Get latest articles
        articles = Article.query.filter_by(published=True).order_by(
            Article.published_at.desc()).limit(5).all()
    except:
        articles = []

    # Get latest prices
    latest_prices = {}
    try:
        symbols = ['BTC', 'ETH', 'BNB', 'XRP', 'ADA', 'SOL', 'DOT', 'DOGE']
        for symbol in symbols:
            price = PriceData.query.filter_by(symbol=symbol).order_by(
                PriceData.timestamp.desc()).first()
            if price:
                latest_prices[symbol.lower()] = {
                    'price': price.price_usd,
                    'change': price.change_24h
                }
    except:
        pass

    return render_template('index_enhanced.html',
                           news=news,
                           articles=articles,
                           prices=latest_prices)


@app.route('/login', methods=['GET', 'POST'])
def login():
    """User login"""
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            user.last_login = datetime.utcnow()
            db.session.commit()
            login_user(user, remember=form.remember_me.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('index'))
        else:
            flash('Invalid username or password')

    return render_template('login.html', form=form)


@app.route('/register', methods=['GET', 'POST'])
def register():
    """User registration"""
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    form = RegistrationForm()
    if form.validate_on_submit():
        try:
            user = User(username=form.username.data, email=form.email.data)
            user.set_password(form.password.data)

            # Make first user admin
            try:
                user_count = User.query.count()
                if user_count == 0:
                    user.is_admin = True
            except:
                # If we can't query, assume first user
                user.is_admin = True

            db.session.add(user)
            db.session.commit()
            flash('Registration successful! You can now log in.', 'success')
            return redirect(url_for('login'))
        except Exception as e:
            db.session.rollback()
            print(f"Registration error: {e}")
            flash(
                'Registration failed. Database permissions may need to be fixed.', 'error')
            return render_template('register.html', form=form,
                                   error_message="Database permission error. Please run: python fix_database_final.py")

    return render_template('register.html', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    """User profile management"""
    form = ProfileForm(current_user.username, current_user.email)

    if form.validate_on_submit():
        # Check current password if changing password
        if form.new_password.data:
            if not current_user.check_password(form.current_password.data):
                flash('Current password is incorrect')
                return render_template('profile.html', form=form)
            current_user.set_password(form.new_password.data)

        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash('Profile updated successfully!')
        return redirect(url_for('profile'))

    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email

    return render_template('profile.html', form=form)


@app.route('/article/new', methods=['GET', 'POST'])
@login_required
def new_article():
    """Create new article"""
    form = ArticleForm()

    if form.validate_on_submit():
        article = Article(
            title=form.title.data,
            slug=create_slug(form.title.data),
            content=form.content.data,
            summary=form.summary.data or form.content.data[:200] + '...',
            author_id=current_user.id,
            published=form.published.data
        )

        if form.published.data:
            article.published_at = datetime.utcnow()

        db.session.add(article)
        db.session.commit()

        flash('Article created successfully!')
        return redirect(url_for('view_article', slug=article.slug))

    return render_template('article_form.html', form=form, title='New Article')


@app.route('/article/<slug>')
def view_article(slug):
    """View article"""
    article = Article.query.filter_by(slug=slug).first_or_404()

    # Only show unpublished articles to author or admin
    if not article.published:
        if not current_user.is_authenticated or \
           (current_user.id != article.author_id and not current_user.is_admin):
            abort(404)

    # Increment views
    article.views += 1
    db.session.commit()

    return render_template('article.html', article=article)


@app.route('/article/<slug>/edit', methods=['GET', 'POST'])
@login_required
def edit_article(slug):
    """Edit article"""
    article = Article.query.filter_by(slug=slug).first_or_404()

    # Check permissions
    if current_user.id != article.author_id and not current_user.is_admin:
        flash('You do not have permission to edit this article.')
        return redirect(url_for('view_article', slug=slug))

    form = ArticleForm()

    if form.validate_on_submit():
        article.title = form.title.data
        article.slug = create_slug(form.title.data)
        article.content = form.content.data
        article.summary = form.summary.data or form.content.data[:200] + '...'
        article.published = form.published.data
        article.updated_at = datetime.utcnow()

        if form.published.data and not article.published_at:
            article.published_at = datetime.utcnow()

        db.session.commit()
        flash('Article updated successfully!')
        return redirect(url_for('view_article', slug=article.slug))

    elif request.method == 'GET':
        form.title.data = article.title
        form.content.data = article.content
        form.summary.data = article.summary
        form.published.data = article.published

    return render_template('article_form.html', form=form, title='Edit Article', article=article)

# Admin routes


@app.route('/admin')
@admin_required
def admin_dashboard():
    """Admin dashboard"""
    # Get statistics with error handling
    stats = {
        'total_users': 0,
        'total_articles': 0,
        'published_articles': 0,
        'total_news': 0,
        'news_today': 0,
        'latest_price_update': None
    }

    try:
        stats['total_users'] = User.query.count()
        stats['total_articles'] = Article.query.count()
        stats['published_articles'] = Article.query.filter_by(
            published=True).count()
        stats['total_news'] = NewsItem.query.count()
        stats['news_today'] = NewsItem.query.filter(
            NewsItem.scraped_at >= datetime.utcnow().date()
        ).count()
        stats['latest_price_update'] = PriceData.query.order_by(
            PriceData.timestamp.desc()).first()
    except Exception as e:
        print(f"Error getting stats: {e}")

    # Get recent activities
    try:
        recent_articles = Article.query.order_by(
            Article.created_at.desc()).limit(5).all()
    except:
        recent_articles = []

    try:
        recent_users = User.query.order_by(
            User.created_at.desc()).limit(5).all()
    except:
        recent_users = []

    return render_template('admin/dashboard.html',
                           stats=stats,
                           recent_articles=recent_articles,
                           recent_users=recent_users)


@app.route('/admin/users')
@admin_required
def admin_users():
    """Manage users"""
    page = request.args.get('page', 1, type=int)
    users = User.query.order_by(User.created_at.desc()).paginate(
        page=page, per_page=20, error_out=False
    )
    return render_template('admin/users.html', users=users)


@app.route('/admin/users/<int:user_id>/toggle-admin')
@admin_required
def toggle_admin(user_id):
    """Toggle admin status"""
    if user_id == current_user.id:
        flash('You cannot modify your own admin status.')
        return redirect(url_for('admin_users'))

    user = User.query.get_or_404(user_id)
    user.is_admin = not user.is_admin
    db.session.commit()

    flash(f'Admin status updated for {user.username}')
    return redirect(url_for('admin_users'))


@app.route('/admin/articles')
@admin_required
def admin_articles():
    """Manage articles"""
    page = request.args.get('page', 1, type=int)
    articles = Article.query.order_by(Article.created_at.desc()).paginate(
        page=page, per_page=20, error_out=False
    )
    return render_template('admin/articles.html', articles=articles)


@app.route('/admin/news')
@admin_required
def admin_news():
    """Manage news items"""
    page = request.args.get('page', 1, type=int)
    news = NewsItem.query.order_by(NewsItem.scraped_at.desc()).paginate(
        page=page, per_page=20, error_out=False
    )
    return render_template('admin/news.html', news=news)


@app.route('/admin/news/<int:news_id>/toggle-featured')
@admin_required
def toggle_featured(news_id):
    """Toggle featured status for news item"""
    news_item = NewsItem.query.get_or_404(news_id)
    news_item.is_featured = not news_item.is_featured
    db.session.commit()

    flash('Featured status updated')
    return redirect(url_for('admin_news'))


@app.route('/admin/settings', methods=['GET', 'POST'])
@admin_required
def admin_settings():
    """Site settings"""
    if request.method == 'POST':
        settings = [
            ('site_name', 'BlockWire News', 'Site name displayed in header'),
            ('site_description', request.form.get(
                'site_description'), 'Site meta description'),
            ('articles_per_page', request.form.get(
                'articles_per_page', '10'), 'Articles per page'),
            ('news_per_page', request.form.get(
                'news_per_page', '15'), 'News items per page'),
            ('enable_registration', request.form.get(
                'enable_registration', 'true'), 'Allow new user registration'),
        ]

        for key, value, desc in settings:
            if value:
                SiteSettings.set(key, value, desc)

        flash('Settings updated successfully!')
        return redirect(url_for('admin_settings'))

    # Get current settings
    settings = {
        'site_name': SiteSettings.get('site_name', 'BlockWire News'),
        'site_description': SiteSettings.get('site_description', ''),
        'articles_per_page': SiteSettings.get('articles_per_page', '10'),
        'news_per_page': SiteSettings.get('news_per_page', '15'),
        'enable_registration': SiteSettings.get('enable_registration', 'true') == 'true',
    }

    return render_template('admin/settings.html', settings=settings)


@app.route('/admin/update-news')
@admin_required
def admin_update_news():
    """Manually trigger news update"""
    update_news()
    flash('News update triggered successfully!')
    return redirect(url_for('admin_dashboard'))


@app.route('/admin/update-prices')
@admin_required
def admin_update_prices():
    """Manually trigger price update"""
    update_prices()
    flash('Price update triggered successfully!')
    return redirect(url_for('admin_dashboard'))

# API routes


@app.route('/api/news')
def api_news():
    """API endpoint for news data"""
    try:
        news = NewsItem.query.order_by(
            NewsItem.published_date.desc()).limit(20).all()
        return jsonify([item.to_dict() for item in news])
    except:
        return jsonify([])


@app.route('/api/prices')
def api_prices():
    """API endpoint for latest prices"""
    latest_prices = {}
    try:
        symbols = ['BTC', 'ETH', 'BNB', 'XRP', 'ADA', 'SOL', 'DOT', 'DOGE']

        for symbol in symbols:
            price = PriceData.query.filter_by(symbol=symbol).order_by(
                PriceData.timestamp.desc()).first()
            if price:
                latest_prices[symbol.lower()] = {
                    'price': price.price_usd,
                    'change_24h': price.change_24h,
                    'market_cap': price.market_cap,
                    'volume_24h': price.volume_24h,
                    'updated': price.timestamp.isoformat()
                }
    except:
        pass

    return jsonify(latest_prices)

# Error handlers


@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html'), 500

# CLI commands for database initialization


@app.cli.command()
def init_db():
    """Initialize the database."""
    db.create_all()
    print("Database initialized!")


@app.cli.command()
def create_admin():
    """Create an admin user."""
    username = input("Enter admin username: ")
    email = input("Enter admin email: ")
    password = input("Enter admin password: ")

    user = User(username=username, email=email, is_admin=True)
    user.set_password(password)

    db.session.add(user)
    db.session.commit()

    print(f"Admin user {username} created successfully!")


if __name__ == '__main__':
    print("\n" + "="*50)
    print("BlockWire News - Starting Application")
    print("="*50)

    with app.app_context():
        try:
            # Create tables if they don't exist
            db.create_all()
            print("✓ Database tables verified")

            # Check if we need to run initial setup
            user_count = 0
            try:
                user_count = User.query.count()
            except:
                print("! Could not access database tables")
                print("! Run 'python init_db.py' to initialize the database")

            if user_count == 0:
                print("\n! No users found in database")
                print("! Run 'python init_db.py' to create admin user")
            else:
                print(f"✓ Found {user_count} users in database")

        except Exception as e:
            print(f"\n✗ Database error: {e}")
            print("\nTroubleshooting:")
            print("1. Make sure PostgreSQL is running")
            print("2. Create database: createdb blockwire")
            print("3. Run: python init_db.py")

    print("\nStarting Flask application on http://localhost:5000")
    print("Press Ctrl+C to stop\n")

    app.run(debug=True, port=5000)
