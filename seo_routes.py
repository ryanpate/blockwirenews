# seo_routes.py - SEO Routes for BlockWire News

from flask import make_response, render_template, request, jsonify, render_template_string
from datetime import datetime
import pytz

def register_seo_routes(app, db):
    """Register SEO-related routes"""
    from models import Article, NewsItem
    
    @app.route('/sitemap.xml')
    def sitemap():
        """Generate dynamic XML sitemap"""
        pages = []
        
        # Static pages
        static_pages = [
            {'loc': '/', 'priority': '1.0', 'changefreq': 'hourly'},
            {'loc': '/news', 'priority': '0.9', 'changefreq': 'hourly'},
            {'loc': '/analysis', 'priority': '0.9', 'changefreq': 'daily'},
            {'loc': '/prices', 'priority': '0.8', 'changefreq': 'hourly'},
            {'loc': '/about', 'priority': '0.5', 'changefreq': 'monthly'},
            {'loc': '/contact', 'priority': '0.5', 'changefreq': 'monthly'},
            {'loc': '/privacy', 'priority': '0.3', 'changefreq': 'yearly'},
            {'loc': '/terms', 'priority': '0.3', 'changefreq': 'yearly'},
        ]
        
        for page in static_pages:
            pages.append({
                'loc': request.url_root.rstrip('/') + page['loc'],
                'lastmod': datetime.now(pytz.UTC).strftime('%Y-%m-%d'),
                'changefreq': page.get('changefreq', 'weekly'),
                'priority': page.get('priority', '0.5')
            })
        
        # Dynamic article pages
        articles = Article.query.filter_by(published=True).order_by(Article.updated_at.desc()).all()
        for article in articles:
            pages.append({
                'loc': request.url_root.rstrip('/') + f'/article/{article.slug}',
                'lastmod': article.updated_at.strftime('%Y-%m-%d'),
                'changefreq': 'monthly',
                'priority': '0.7'
            })
        
        # News category pages (get unique sources)
        news_sources = db.session.query(NewsItem.source).distinct().all()
        for source in news_sources:
            if source[0]:
                pages.append({
                    'loc': request.url_root.rstrip('/') + f'/news/source/{source[0].lower().replace(" ", "-")}',
                    'lastmod': datetime.now(pytz.UTC).strftime('%Y-%m-%d'),
                    'changefreq': 'daily',
                    'priority': '0.6'
                })
        
        # Generate sitemap XML
        sitemap_xml = """<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
{% for page in pages %}
    <url>
        <loc>{{ page.loc }}</loc>
        <lastmod>{{ page.lastmod }}</lastmod>
        <changefreq>{{ page.changefreq }}</changefreq>
        <priority>{{ page.priority }}</priority>
    </url>
{% endfor %}
</urlset>"""
        
        rendered_sitemap = render_template_string(sitemap_xml, pages=pages)
        response = make_response(rendered_sitemap)
        response.headers["Content-Type"] = "application/xml"
        return response
    
    @app.route('/robots.txt')
    def robots():
        """Generate robots.txt"""
        lines = [
            'User-agent: *',
            'Allow: /',
            'Disallow: /admin/',
            'Disallow: /api/',
            'Disallow: /login',
            'Disallow: /register',
            'Disallow: /profile',
            'Disallow: /dashboard',
            '',
            f'Sitemap: {request.url_root}sitemap.xml',
            '',
            '# Crawl-delay: 1',
            '',
            'User-agent: Googlebot',
            'Allow: /',
            '',
            'User-agent: Bingbot',
            'Allow: /',
        ]
        
        response = make_response('\n'.join(lines))
        response.headers["Content-Type"] = "text/plain"
        return response
    
    @app.route('/rss')
    @app.route('/feed')
    @app.route('/rss.xml')
    def rss_feed():
        """Generate RSS feed"""
        # Get latest articles and news
        articles = Article.query.filter_by(published=True).order_by(Article.published_at.desc()).limit(20).all()
        news_items = NewsItem.query.order_by(NewsItem.published_date.desc()).limit(20).all()
        
        # Combine and sort by date
        items = []
        
        for article in articles:
            items.append({
                'title': article.title,
                'description': article.summary or article.content[:200] + '...',
                'link': request.url_root.rstrip('/') + f'/article/{article.slug}',
                'guid': f'article-{article.id}',
                'pubDate': article.published_at if article.published_at else article.created_at,
                'author': article.author.username,
                'category': 'Analysis'
            })
        
        for news in news_items:
            items.append({
                'title': news.title,
                'description': news.summary,
                'link': news.url,
                'guid': f'news-{news.id}',
                'pubDate': news.published_date if news.published_date else news.scraped_at,
                'author': news.source,
                'category': 'News'
            })
        
        # Sort by date
        items.sort(key=lambda x: x['pubDate'], reverse=True)
        items = items[:30]  # Limit to 30 most recent
        
        # Generate RSS XML
        rss_xml = """<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" 
     xmlns:atom="http://www.w3.org/2005/Atom"
     xmlns:dc="http://purl.org/dc/elements/1.1/">
    <channel>
        <title>BlockWire News - Cryptocurrency News & Analysis</title>
        <link>{{ link }}</link>
        <description>Real-time cryptocurrency news and expert analysis</description>
        <language>en-us</language>
        <lastBuildDate>{{ items[0].pubDate.strftime('%a, %d %b %Y %H:%M:%S +0000') if items else '' }}</lastBuildDate>
        <atom:link href="{{ request.url }}" rel="self" type="application/rss+xml" />
        
        {% for item in items %}
        <item>
            <title><![CDATA[{{ item.title }}]]></title>
            <link>{{ item.link }}</link>
            <description><![CDATA[{{ item.description }}]]></description>
            <guid isPermaLink="false">{{ item.guid }}</guid>
            <pubDate>{{ item.pubDate.strftime('%a, %d %b %Y %H:%M:%S +0000') }}</pubDate>
            <dc:creator>{{ item.author }}</dc:creator>
            <category>{{ item.category }}</category>
        </item>
        {% endfor %}
    </channel>
</rss>"""
        
        rendered_rss = render_template_string(rss_xml, 
                                            items=items,
                                            link=request.url_root,
                                            request=request)
        
        response = make_response(rendered_rss)
        response.headers["Content-Type"] = "application/rss+xml"
        return response
    
    @app.route('/news')
    def news_page():
        """Dedicated news page with better SEO"""
        page = request.args.get('page', 1, type=int)
        source = request.args.get('source', None)
        
        query = NewsItem.query
        if source:
            query = query.filter_by(source=source)
        
        news = query.order_by(NewsItem.published_date.desc()).paginate(
            page=page, per_page=20, error_out=False
        )
        
        # Get all sources for filter
        sources = db.session.query(NewsItem.source).distinct().all()
        
        return render_template('news_page.html', 
                             news=news,
                             sources=[s[0] for s in sources if s[0]],
                             current_source=source)
    
    @app.route('/analysis')
    def analysis_page():
        """Dedicated analysis/articles page"""
        page = request.args.get('page', 1, type=int)
        
        articles = Article.query.filter_by(published=True).order_by(
            Article.published_at.desc()
        ).paginate(page=page, per_page=10, error_out=False)
        
        return render_template('analysis.html', articles=articles)
    
    @app.route('/prices')
    def prices_page():
        """Dedicated cryptocurrency prices page"""
        return render_template('prices.html')
    
    @app.route('/about')
    def about_page():
        """About page"""
        return render_template('about.html')
    
    @app.route('/contact')
    def contact_page():
        """Contact page"""
        return render_template('contact.html')
    
    @app.route('/privacy')
    def privacy_page():
        """Privacy policy page"""
        return render_template('privacy.html')
    
    @app.route('/terms')
    def terms_page():
        """Terms of service page"""
        return render_template('terms.html')
    
    @app.route('/api/search')
    def search_api():
        """Search API endpoint"""
        query = request.args.get('q', '')
        if len(query) < 3:
            return jsonify({'results': []})
        
        # Search articles
        articles = Article.query.filter(
            db.or_(
                Article.title.ilike(f'%{query}%'),
                Article.content.ilike(f'%{query}%')
            ),
            Article.published == True
        ).limit(5).all()
        
        # Search news
        news = NewsItem.query.filter(
            db.or_(
                NewsItem.title.ilike(f'%{query}%'),
                NewsItem.summary.ilike(f'%{query}%')
            )
        ).limit(5).all()
        
        results = {
            'articles': [
                {
                    'title': a.title,
                    'url': f'/article/{a.slug}',
                    'type': 'article',
                    'date': a.published_at.isoformat() if a.published_at else a.created_at.isoformat()
                } for a in articles
            ],
            'news': [
                {
                    'title': n.title,
                    'url': n.url,
                    'type': 'news',
                    'source': n.source,
                    'date': n.published_date.isoformat() if n.published_date else n.scraped_at.isoformat()
                } for n in news
            ]
        }
        
        return jsonify(results)
    
    @app.route('/api/related-articles/<slug>')
    def get_related_articles(slug):
        """Get related articles for better internal linking"""
        article = Article.query.filter_by(slug=slug).first_or_404()
        
        # Find related articles based on keywords in title
        keywords = article.title.lower().split()
        
        # Build query for related articles
        query = Article.query.filter(
            Article.id != article.id,
            Article.published == True
        )
        
        # Add keyword filters
        filters = []
        for keyword in keywords[:5]:  # Use top 5 keywords
            if len(keyword) > 3:  # Skip short words
                filters.append(Article.title.ilike(f'%{keyword}%'))
        
        if filters:
            query = query.filter(db.or_(*filters))
        
        related = query.order_by(Article.published_at.desc()).limit(4).all()
        
        return jsonify([{
            'title': a.title,
            'slug': a.slug,
            'summary': a.summary or a.content[:100] + '...',
            'published_at': a.published_at.isoformat() if a.published_at else a.created_at.isoformat()
        } for a in related])