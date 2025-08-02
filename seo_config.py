# seo_config.py - SEO Configuration and Utilities for BlockWire News

import os
from flask import url_for, request, redirect, render_template
from urllib.parse import quote as url_quote
import re
from datetime import datetime


class SEOConfig:
    """SEO configuration and utilities"""

    # Meta tag defaults
    DEFAULT_TITLE = "BlockWire News - Real-Time Cryptocurrency News & Analysis"
    DEFAULT_DESCRIPTION = "Stay updated with the latest cryptocurrency news, Bitcoin prices, Ethereum analysis, and blockchain insights. Real-time crypto market data and expert analysis."
    DEFAULT_KEYWORDS = "cryptocurrency news, bitcoin news, ethereum news, blockchain, crypto prices, bitcoin price, ethereum price, crypto analysis, digital assets, defi news, nft news"

    # Social media defaults
    DEFAULT_OG_IMAGE = "/static/images/blockwire-og.png"
    DEFAULT_TWITTER_IMAGE = "/static/images/blockwire-twitter.png"

    # SEO limits
    TITLE_MAX_LENGTH = 60
    DESCRIPTION_MAX_LENGTH = 160

    @staticmethod
    def generate_meta_tags(title=None, description=None, keywords=None,
                           article=None, news_item=None, page_type='website'):
        """Generate comprehensive meta tags for a page"""

        # Process title
        if title:
            if len(title) > SEOConfig.TITLE_MAX_LENGTH:
                title = title[:SEOConfig.TITLE_MAX_LENGTH-3] + '...'
            full_title = f"{title} - BlockWire News"
        else:
            full_title = SEOConfig.DEFAULT_TITLE

        # Process description
        if not description:
            if article:
                description = article.summary or article.content[:155]
            elif news_item:
                description = news_item.summary[:155]
            else:
                description = SEOConfig.DEFAULT_DESCRIPTION

        if len(description) > SEOConfig.DESCRIPTION_MAX_LENGTH:
            description = description[:SEOConfig.DESCRIPTION_MAX_LENGTH-3] + '...'

        # Process keywords
        if not keywords:
            if article:
                # Extract keywords from title and content
                title_words = re.findall(r'\w+', article.title.lower())
                keywords = ', '.join(
                    title_words[:5]) + ', ' + SEOConfig.DEFAULT_KEYWORDS
            else:
                keywords = SEOConfig.DEFAULT_KEYWORDS

        return {
            'title': full_title,
            'description': description,
            'keywords': keywords,
            'canonical': request.url,
            'og_type': 'article' if article or news_item else page_type,
            'og_image': SEOConfig.DEFAULT_OG_IMAGE,
            'twitter_card': 'summary_large_image'
        }

    @staticmethod
    def generate_breadcrumbs(current_page, parent_pages=None):
        """Generate breadcrumb navigation"""
        breadcrumbs = [{'name': 'Home', 'url': '/'}]

        if parent_pages:
            breadcrumbs.extend(parent_pages)

        breadcrumbs.append({'name': current_page, 'url': None})
        return breadcrumbs

    @staticmethod
    def generate_schema_article(article):
        """Generate Article schema markup"""
        from flask import url_for

        schema = {
            "@context": "https://schema.org",
            "@type": "NewsArticle",
            "headline": article.title,
            "description": article.summary or article.content[:160],
            "image": {
                "@type": "ImageObject",
                "url": url_for('static', filename='images/article-default.jpg', _external=True),
                "width": 1200,
                "height": 630
            },
            "datePublished": article.published_at.isoformat() if article.published_at else article.created_at.isoformat(),
            "dateModified": article.updated_at.isoformat(),
            "author": {
                "@type": "Person",
                "name": article.author.username
            },
            "publisher": {
                "@type": "Organization",
                "name": "BlockWire News",
                "logo": {
                    "@type": "ImageObject",
                    "url": url_for('static', filename='images/logo.png', _external=True)
                }
            },
            "mainEntityOfPage": {
                "@type": "WebPage",
                "@id": url_for('view_article', slug=article.slug, _external=True)
            }
        }
        return schema

    @staticmethod
    def slugify(text, max_length=50):
        """Create SEO-friendly URL slugs"""
        # Convert to lowercase
        slug = text.lower()

        # Replace spaces and special characters
        slug = re.sub(r'[^\w\s-]', '', slug)
        slug = re.sub(r'[-\s]+', '-', slug)

        # Remove leading/trailing hyphens
        slug = slug.strip('-')

        # Limit length
        if len(slug) > max_length:
            slug = slug[:max_length].rsplit('-', 1)[0]

        return slug


# SEO Middleware and Helpers
def init_seo(app):
    """Initialize SEO features for the Flask app"""

    @app.context_processor
    def inject_seo():
        """Inject SEO utilities into templates"""
        return {
            'seo_config': SEOConfig,
            'current_year': datetime.now().year,
            'site_name': 'BlockWire News',
            'site_tagline': 'Real-Time Cryptocurrency News & Analysis'
        }

    @app.template_filter('seo_title')
    def seo_title_filter(title, max_length=60):
        """Template filter for SEO-friendly titles"""
        if len(title) > max_length:
            return title[:max_length-3] + '...'
        return title

    @app.template_filter('seo_description')
    def seo_description_filter(text, max_length=160):
        """Template filter for SEO-friendly descriptions"""
        # Remove HTML tags
        text = re.sub('<.*?>', '', text)
        # Truncate
        if len(text) > max_length:
            return text[:max_length-3] + '...'
        return text

    @app.template_filter('reading_time')
    def reading_time_filter(text):
        """Calculate reading time for articles"""
        words = len(text.split())
        minutes = max(1, round(words / 200))  # 200 words per minute
        return f"{minutes} min read"

    # Add security headers for SEO
    @app.after_request
    def add_security_headers(response):
        """Add security headers that also help with SEO"""
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'SAMEORIGIN'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'

        # Cache static assets
        if request.path.startswith('/static/'):
            response.headers['Cache-Control'] = 'public, max-age=31536000'

        return response

    # URL redirect for trailing slashes
    @app.before_request
    def redirect_trailing_slash():
        """Redirect URLs with trailing slashes for SEO consistency"""
        if request.path != '/' and request.path.endswith('/'):
            return redirect(request.path[:-1], code=301)


# Additional SEO routes
def register_additional_seo_routes(app, db):
    """Register additional SEO-friendly routes"""
    from models import User, Article, NewsItem

    @app.route('/author/<username>')
    def author_profile(username):
        """Author profile page"""
        author = User.query.filter_by(username=username).first_or_404()
        articles = Article.query.filter_by(
            author_id=author.id,
            published=True
        ).order_by(Article.published_at.desc()).paginate(
            page=request.args.get('page', 1, type=int),
            per_page=10,
            error_out=False
        )

        return render_template('author_profile.html',
                               author=author,
                               articles=articles)

    @app.route('/search')
    def search_page():
        """Search results page"""
        query = request.args.get('q', '')
        page = request.args.get('page', 1, type=int)

        if len(query) < 3:
            return render_template('search.html', query=query, results=None)

        # Search articles
        article_results = Article.query.filter(
            db.or_(
                Article.title.ilike(f'%{query}%'),
                Article.content.ilike(f'%{query}%')
            ),
            Article.published == True
        ).order_by(Article.published_at.desc())

        # Search news
        news_results = NewsItem.query.filter(
            db.or_(
                NewsItem.title.ilike(f'%{query}%'),
                NewsItem.summary.ilike(f'%{query}%')
            )
        ).order_by(NewsItem.published_date.desc())

        # Paginate combined results
        all_results = {
            'articles': article_results.limit(10).all(),
            'news': news_results.limit(10).all()
        }

        return render_template('search.html',
                               query=query,
                               results=all_results)
