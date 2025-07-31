from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class User(UserMixin, db.Model):
    """User model for authentication"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255))
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    
    # Relationships
    articles = db.relationship('Article', backref='author', lazy='dynamic')
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<User {self.username}>'

class Article(db.Model):
    """Blog article model"""
    __tablename__ = 'articles'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    slug = db.Column(db.String(200), unique=True, nullable=False)
    content = db.Column(db.Text, nullable=False)
    summary = db.Column(db.String(500))
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    published = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    published_at = db.Column(db.DateTime)
    views = db.Column(db.Integer, default=0)
    
    def __repr__(self):
        return f'<Article {self.title}>'

class NewsItem(db.Model):
    """Scraped news items"""
    __tablename__ = 'news_items'
    
    id = db.Column(db.Integer, primary_key=True)
    external_id = db.Column(db.String(50), unique=True)  # ID from scraper
    title = db.Column(db.String(300), nullable=False)
    url = db.Column(db.String(500), nullable=False)
    summary = db.Column(db.Text)
    source = db.Column(db.String(100))
    published_date = db.Column(db.DateTime)
    scraped_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_featured = db.Column(db.Boolean, default=False)
    
    def to_dict(self):
        return {
            'id': self.external_id,
            'title': self.title,
            'url': self.url,
            'summary': self.summary,
            'source': self.source,
            'published': self.published_date.isoformat() if self.published_date else None,
            'scraped_at': self.scraped_at.isoformat()
        }
    
    def __repr__(self):
        return f'<NewsItem {self.title[:50]}...>'

class PriceData(db.Model):
    """Cryptocurrency price data"""
    __tablename__ = 'price_data'
    
    id = db.Column(db.Integer, primary_key=True)
    symbol = db.Column(db.String(20), nullable=False)
    name = db.Column(db.String(50))
    price_usd = db.Column(db.Float)
    change_24h = db.Column(db.Float)
    market_cap = db.Column(db.BigInteger)
    volume_24h = db.Column(db.BigInteger)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<PriceData {self.symbol} ${self.price_usd}>'

class SiteSettings(db.Model):
    """Site configuration settings"""
    __tablename__ = 'site_settings'
    
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(50), unique=True, nullable=False)
    value = db.Column(db.Text)
    description = db.Column(db.String(200))
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    @classmethod
    def get(cls, key, default=None):
        setting = cls.query.filter_by(key=key).first()
        return setting.value if setting else default
    
    @classmethod
    def set(cls, key, value, description=None):
        setting = cls.query.filter_by(key=key).first()
        if setting:
            setting.value = value
            if description:
                setting.description = description
        else:
            setting = cls(key=key, value=value, description=description)
            db.session.add(setting)
        db.session.commit()
        return setting
    
    def __repr__(self):
        return f'<SiteSettings {self.key}={self.value}>'