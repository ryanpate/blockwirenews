#!/usr/bin/env python3
"""
Create missing template files for BlockWire News SEO implementation
"""

import os

# Template contents
templates = {
    'search.html': '''{% extends "base_enhanced.html" %}

{% block title %}Search - BlockWire News{% endblock %}

{% block content %}
<div style="max-width: 800px; margin: 0 auto;">
    <h1 style="color: var(--primary-color); margin-bottom: 2rem;">Search BlockWire News</h1>
    
    <!-- Search Form -->
    <form method="GET" action="{{ url_for('search_page') }}" style="margin-bottom: 2rem;">
        <div style="display: flex; gap: 1rem;">
            <input type="text" 
                   name="q" 
                   value="{{ query }}" 
                   placeholder="Search for articles, news, or topics..." 
                   style="flex: 1; padding: 0.75rem; border: 1px solid #ddd; border-radius: 4px; font-size: 1rem;">
            <button type="submit" class="btn">Search</button>
        </div>
    </form>
    
    {% if query and query|length >= 3 %}
        {% if results %}
            <!-- Search Results -->
            <div style="margin-bottom: 3rem;">
                {% if results.articles %}
                    <section style="margin-bottom: 2rem;">
                        <h2 style="color: var(--primary-color); margin-bottom: 1rem;">Articles</h2>
                        {% for article in results.articles %}
                            <div style="background: white; padding: 1.5rem; border-radius: 8px; margin-bottom: 1rem; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                                <h3 style="margin-bottom: 0.5rem;">
                                    <a href="{{ url_for('view_article', slug=article.slug) }}" 
                                       style="color: var(--primary-color); text-decoration: none;">
                                        {{ article.title }}
                                    </a>
                                </h3>
                                <p style="color: #666; margin-bottom: 0.5rem;">
                                    {{ article.summary or article.content[:150] }}...
                                </p>
                                <div style="font-size: 0.875rem; color: #999;">
                                    By {{ article.author.username }} • 
                                    {{ article.published_at.strftime('%B %d, %Y') if article.published_at else 'Draft' }}
                                </div>
                            </div>
                        {% endfor %}
                    </section>
                {% endif %}
                
                {% if results.news %}
                    <section>
                        <h2 style="color: var(--primary-color); margin-bottom: 1rem;">News</h2>
                        {% for news in results.news %}
                            <div style="background: white; padding: 1.5rem; border-radius: 8px; margin-bottom: 1rem; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                                <h3 style="margin-bottom: 0.5rem;">
                                    <a href="{{ news.url }}" 
                                       target="_blank"
                                       style="color: var(--primary-color); text-decoration: none;">
                                        {{ news.title }}
                                    </a>
                                </h3>
                                <p style="color: #666; margin-bottom: 0.5rem;">
                                    {{ news.summary }}
                                </p>
                                <div style="font-size: 0.875rem; color: #999;">
                                    {{ news.source }} • 
                                    {{ news.published_date.strftime('%B %d, %Y') if news.published_date else news.scraped_at.strftime('%B %d, %Y') }}
                                </div>
                            </div>
                        {% endfor %}
                    </section>
                {% endif %}
            </div>
        {% endif %}
    {% elif query %}
        <div style="text-align: center; padding: 3rem; color: #666;">
            <p>Please enter at least 3 characters to search.</p>
        </div>
    {% endif %}
</div>
{% endblock %}''',

    'news_page.html': '''{% extends "base_enhanced.html" %}

{% block title %}Latest Cryptocurrency News - BlockWire News{% endblock %}

{% block content %}
<div style="max-width: 1000px; margin: 0 auto;">
    <h1 style="color: var(--primary-color); margin-bottom: 2rem;">Latest Cryptocurrency News</h1>
    
    <!-- Source Filter -->
    {% if sources %}
    <div style="margin-bottom: 2rem;">
        <label style="font-weight: 600; margin-right: 1rem;">Filter by Source:</label>
        <select onchange="window.location.href=this.value" style="padding: 0.5rem; border: 1px solid #ddd; border-radius: 4px;">
            <option value="{{ url_for('news_page') }}">All Sources</option>
            {% for source in sources %}
            <option value="{{ url_for('news_page', source=source) }}" {% if current_source == source %}selected{% endif %}>
                {{ source }}
            </option>
            {% endfor %}
        </select>
    </div>
    {% endif %}
    
    <!-- News Items -->
    {% for item in news.items %}
    <article style="background: white; border-radius: 8px; padding: 1.5rem; margin-bottom: 1rem; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
        <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 0.5rem;">
            <span style="background: var(--accent-color); color: white; padding: 0.25rem 0.75rem; border-radius: 4px; font-size: 0.8rem; font-weight: 500;">
                {{ item.source }}
            </span>
            {% if item.is_featured %}
            <span style="color: var(--accent-color);">★ Featured</span>
            {% endif %}
        </div>
        <a href="{{ item.url }}" target="_blank" style="color: var(--primary-color); text-decoration: none; font-size: 1.2rem; font-weight: 600; line-height: 1.4; display: block; margin-bottom: 0.5rem;">
            {{ item.title }}
        </a>
        <p style="color: #666; font-size: 0.95rem; line-height: 1.5; margin-bottom: 0.5rem;">
            {{ item.summary }}
        </p>
        <time style="color: #999; font-size: 0.85rem;">
            {{ item.published_date.strftime('%B %d, %Y at %I:%M %p') if item.published_date else item.scraped_at.strftime('%B %d, %Y') }}
        </time>
    </article>
    {% endfor %}
    
    <!-- Pagination -->
    <div class="pagination">
        {% if news.has_prev %}
            <a href="{{ url_for('news_page', page=news.prev_num, source=current_source) }}">← Previous</a>
        {% endif %}
        
        <span class="active">Page {{ news.page }} of {{ news.pages }}</span>
        
        {% if news.has_next %}
            <a href="{{ url_for('news_page', page=news.next_num, source=current_source) }}">Next →</a>
        {% endif %}
    </div>
</div>
{% endblock %}''',

    'analysis.html': '''{% extends "base_enhanced.html" %}

{% block title %}Cryptocurrency Analysis & Insights - BlockWire News{% endblock %}

{% block content %}
<div style="max-width: 800px; margin: 0 auto;">
    <h1 style="color: var(--primary-color); margin-bottom: 2rem;">Cryptocurrency Analysis & Insights</h1>
    
    {% for article in articles.items %}
    <article style="background: white; border-radius: 8px; padding: 2rem; margin-bottom: 2rem; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
        <h2 style="margin-bottom: 0.5rem;">
            <a href="{{ url_for('view_article', slug=article.slug) }}" 
               style="color: var(--primary-color); text-decoration: none;">
                {{ article.title }}
            </a>
        </h2>
        
        <div style="color: #666; font-size: 0.9rem; margin-bottom: 1rem;">
            By <strong>{{ article.author.username }}</strong> • 
            Published {{ article.published_at.strftime('%B %d, %Y') if article.published_at else 'Draft' }} •
            {{ article.views }} views
        </div>
        
        <p style="color: #333; line-height: 1.6; margin-bottom: 1rem;">
            {{ article.summary or article.content[:200] }}...
        </p>
        
        <a href="{{ url_for('view_article', slug=article.slug) }}" 
           style="color: var(--accent-color); text-decoration: none; font-weight: 500;">
            Read full analysis →
        </a>
    </article>
    {% endfor %}
    
    {% if not articles.items %}
    <div style="text-align: center; padding: 3rem; color: #666;">
        <p>No analysis articles available yet.</p>
        {% if current_user.is_authenticated %}
        <a href="{{ url_for('new_article') }}" class="btn" style="margin-top: 1rem;">Write First Analysis</a>
        {% endif %}
    </div>
    {% endif %}
    
    <!-- Pagination -->
    {% if articles.pages > 1 %}
    <div class="pagination">
        {% if articles.has_prev %}
            <a href="{{ url_for('analysis_page', page=articles.prev_num) }}">← Previous</a>
        {% endif %}
        
        <span class="active">Page {{ articles.page }} of {{ articles.pages }}</span>
        
        {% if articles.has_next %}
            <a href="{{ url_for('analysis_page', page=articles.next_num) }}">Next →</a>
        {% endif %}
    </div>
    {% endif %}
</div>
{% endblock %}''',

    'prices.html': '''{% extends "base_enhanced.html" %}

{% block title %}Live Cryptocurrency Prices - BlockWire News{% endblock %}

{% block content %}
<div style="max-width: 1000px; margin: 0 auto;">
    <h1 style="color: var(--primary-color); margin-bottom: 2rem;">Live Cryptocurrency Prices</h1>
    
    <div id="price-grid" style="display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 1.5rem; margin-bottom: 3rem;">
        <!-- Prices will be loaded here -->
        <div style="grid-column: 1/-1; text-align: center; padding: 3rem;">
            <div class="spinner"></div>
            <p style="color: #666; margin-top: 1rem;">Loading prices...</p>
        </div>
    </div>
    
    <div style="background: #f8f9fa; padding: 2rem; border-radius: 8px;">
        <h2 style="color: var(--primary-color); margin-bottom: 1rem;">About Our Price Data</h2>
        <p style="color: #666; line-height: 1.6;">
            Prices are updated every 60 seconds from reliable cryptocurrency exchanges. 
            All prices are displayed in USD. Market cap and 24-hour volume data help you 
            understand the size and liquidity of each cryptocurrency.
        </p>
    </div>
</div>

<style>
    .spinner {
        border: 3px solid #f3f3f3;
        border-top: 3px solid var(--accent-color);
        border-radius: 50%;
        width: 40px;
        height: 40px;
        animation: spin 1s linear infinite;
        margin: 0 auto;
    }
    
    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
    
    .price-card {
        background: white;
        padding: 1.5rem;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        transition: transform 0.2s;
    }
    
    .price-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.15);
    }
    
    .price-symbol {
        font-size: 1.5rem;
        font-weight: 700;
        color: var(--primary-color);
        margin-bottom: 0.5rem;
    }
    
    .price-value {
        font-size: 2rem;
        font-weight: 600;
        margin-bottom: 0.5rem;
    }
    
    .price-change {
        font-size: 1.2rem;
        font-weight: 500;
        margin-bottom: 1rem;
    }
    
    .price-change.positive {
        color: var(--success);
    }
    
    .price-change.negative {
        color: var(--danger);
    }
    
    .price-stats {
        border-top: 1px solid #eee;
        padding-top: 1rem;
        margin-top: 1rem;
    }
    
    .stat-row {
        display: flex;
        justify-content: space-between;
        margin-bottom: 0.5rem;
        color: #666;
        font-size: 0.9rem;
    }
</style>

<script>
async function loadPrices() {
    try {
        const response = await fetch('/api/prices');
        const prices = await response.json();
        
        const priceGrid = document.getElementById('price-grid');
        priceGrid.innerHTML = '';
        
        const cryptoNames = {
            'btc': 'Bitcoin',
            'eth': 'Ethereum',
            'bnb': 'Binance Coin',
            'xrp': 'Ripple',
            'ada': 'Cardano',
            'sol': 'Solana',
            'dot': 'Polkadot',
            'doge': 'Dogecoin'
        };
        
        for (const [symbol, data] of Object.entries(prices)) {
            const change = data.change_24h || 0;
            const changeClass = change >= 0 ? 'positive' : 'negative';
            const changeSymbol = change >= 0 ? '+' : '';
            
            const card = document.createElement('div');
            card.className = 'price-card';
            card.innerHTML = `
                <div class="price-symbol">${symbol.toUpperCase()} - ${cryptoNames[symbol]}</div>
                <div class="price-value">$${data.price.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}</div>
                <div class="price-change ${changeClass}">${changeSymbol}${change.toFixed(2)}%</div>
                <div class="price-stats">
                    <div class="stat-row">
                        <span>Market Cap:</span>
                        <span>$${(data.market_cap / 1e9).toFixed(2)}B</span>
                    </div>
                    <div class="stat-row">
                        <span>24h Volume:</span>
                        <span>$${(data.volume_24h / 1e9).toFixed(2)}B</span>
                    </div>
                    <div class="stat-row">
                        <span>Last Updated:</span>
                        <span>${new Date(data.updated).toLocaleTimeString()}</span>
                    </div>
                </div>
            `;
            priceGrid.appendChild(card);
        }
    } catch (error) {
        console.error('Error loading prices:', error);
        document.getElementById('price-grid').innerHTML = '<div style="grid-column: 1/-1; text-align: center; color: var(--danger);">Error loading prices. Please refresh the page.</div>';
    }
}

// Load prices on page load
loadPrices();

// Refresh prices every 60 seconds
setInterval(loadPrices, 60000);
</script>
{% endblock %}''',

    'about.html': '''{% extends "base_enhanced.html" %}

{% block title %}About BlockWire News - Your Trusted Crypto News Source{% endblock %}

{% block content %}
<div style="max-width: 800px; margin: 0 auto;">
    <h1 style="color: var(--primary-color); margin-bottom: 2rem;">About BlockWire News</h1>
    
    <div style="background: white; padding: 2rem; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
        <h2 style="color: var(--primary-color); margin-bottom: 1rem;">Your Trusted Source for Cryptocurrency News</h2>
        
        <p style="font-size: 1.1rem; line-height: 1.8; color: #333; margin-bottom: 1.5rem;">
            BlockWire News is a comprehensive cryptocurrency news aggregation and analysis platform. 
            We bring together the latest updates from leading crypto news sources, providing you with 
            real-time insights into the rapidly evolving digital asset landscape.
        </p>
        
        <h3 style="color: var(--secondary-color); margin-top: 2rem; margin-bottom: 1rem;">Our Mission</h3>
        <p style="line-height: 1.8; color: #333; margin-bottom: 1.5rem;">
            To democratize access to cryptocurrency information by providing timely, accurate, and 
            comprehensive coverage of the blockchain and digital asset ecosystem. We believe that 
            informed investors make better decisions.
        </p>
        
        <h3 style="color: var(--secondary-color); margin-top: 2rem; margin-bottom: 1rem;">What We Offer</h3>
        <ul style="line-height: 1.8; color: #333; margin-bottom: 1.5rem;">
            <li><strong>Real-time News Aggregation:</strong> Latest updates from top crypto news sources</li>
            <li><strong>Expert Analysis:</strong> In-depth articles and market insights from our contributors</li>
            <li><strong>Live Price Tracking:</strong> Real-time cryptocurrency prices and market data</li>
            <li><strong>Educational Content:</strong> Guides and explanations for crypto beginners</li>
            <li><strong>Community Insights:</strong> User-generated content and discussions</li>
        </ul>
        
        <h3 style="color: var(--secondary-color); margin-top: 2rem; margin-bottom: 1rem;">Our Values</h3>
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1.5rem; margin-bottom: 2rem;">
            <div style="text-align: center; padding: 1.5rem;">
                <div style="font-size: 2rem; margin-bottom: 0.5rem;">🎯</div>
                <h4 style="color: var(--primary-color); margin-bottom: 0.5rem;">Accuracy</h4>
                <p style="color: #666; font-size: 0.9rem;">We prioritize factual, verified information</p>
            </div>
            <div style="text-align: center; padding: 1.5rem;">
                <div style="font-size: 2rem; margin-bottom: 0.5rem;">⚡</div>
                <h4 style="color: var(--primary-color); margin-bottom: 0.5rem;">Speed</h4>
                <p style="color: #666; font-size: 0.9rem;">Breaking news delivered in real-time</p>
            </div>
            <div style="text-align: center; padding: 1.5rem;">
                <div style="font-size: 2rem; margin-bottom: 0.5rem;">🔍</div>
                <h4 style="color: var(--primary-color); margin-bottom: 0.5rem;">Transparency</h4>
                <p style="color: #666; font-size: 0.9rem;">Clear sources and unbiased reporting</p>
            </div>
        </div>
        
        <div style="background: var(--primary-color); color: white; padding: 2rem; border-radius: 8px; text-align: center; margin-top: 2rem;">
            <h3 style="margin-bottom: 1rem;">Join Our Community</h3>
            <p style="margin-bottom: 1.5rem;">Stay updated with the latest cryptocurrency news and analysis</p>
            <a href="{{ url_for('register') }}" class="btn" style="background: var(--accent-color); color: white;">Get Started</a>
        </div>
    </div>
</div>
{% endblock %}''',

    'contact.html': '''{% extends "base_enhanced.html" %}

{% block title %}Contact Us - BlockWire News{% endblock %}

{% block content %}
<div style="max-width: 600px; margin: 0 auto;">
    <h1 style="color: var(--primary-color); margin-bottom: 2rem;">Contact Us</h1>
    
    <div style="background: white; padding: 2rem; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
        <p style="font-size: 1.1rem; line-height: 1.8; color: #333; margin-bottom: 2rem;">
            We'd love to hear from you! Whether you have questions, feedback, or partnership inquiries, 
            feel free to reach out to our team.
        </p>
        
        <form method="POST" action="#" style="margin-bottom: 2rem;">
            <div class="form-group">
                <label class="form-label">Your Name</label>
                <input type="text" name="name" class="form-control" required>
            </div>
            
            <div class="form-group">
                <label class="form-label">Email Address</label>
                <input type="email" name="email" class="form-control" required>
            </div>
            
            <div class="form-group">
                <label class="form-label">Subject</label>
                <select name="subject" class="form-control">
                    <option>General Inquiry</option>
                    <option>News Submission</option>
                    <option>Partnership Opportunity</option>
                    <option>Technical Support</option>
                    <option>Feedback</option>
                </select>
            </div>
            
            <div class="form-group">
                <label class="form-label">Message</label>
                <textarea name="message" rows="5" class="form-control" required></textarea>
            </div>
            
            <button type="submit" class="btn" style="width: 100%;">Send Message</button>
        </form>
        
        <div style="border-top: 1px solid #eee; padding-top: 2rem;">
            <h3 style="color: var(--primary-color); margin-bottom: 1rem;">Other Ways to Reach Us</h3>
            
            <div style="margin-bottom: 1rem;">
                <strong>Email:</strong> contact@blockwirenews.com
            </div>
            
            <div style="margin-bottom: 1rem;">
                <strong>Social Media:</strong>
                <div style="margin-top: 0.5rem;">
                    <a href="#" style="color: var(--accent-color); text-decoration: none; margin-right: 1rem;">Twitter</a>
                    <a href="#" style="color: var(--accent-color); text-decoration: none; margin-right: 1rem;">LinkedIn</a>
                    <a href="#" style="color: var(--accent-color); text-decoration: none;">Telegram</a>
                </div>
            </div>
            
            <div>
                <strong>Response Time:</strong> We typically respond within 24-48 hours
            </div>
        </div>
    </div>
</div>
{% endblock %}''',

    'privacy.html': '''{% extends "base_enhanced.html" %}

{% block title %}Privacy Policy - BlockWire News{% endblock %}

{% block content %}
<div style="max-width: 800px; margin: 0 auto;">
    <h1 style="color: var(--primary-color); margin-bottom: 2rem;">Privacy Policy</h1>
    
    <div style="background: white; padding: 2rem; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
        <p style="color: #666; margin-bottom: 2rem;">Last updated: {{ current_year }}</p>
        
        <h2 style="color: var(--primary-color); margin-bottom: 1rem;">1. Information We Collect</h2>
        <p style="line-height: 1.8; color: #333; margin-bottom: 1.5rem;">
            We collect information you provide directly to us, such as when you create an account, 
            write articles, or contact us. This may include your name, email address, username, 
            and any other information you choose to provide.
        </p>
        
        <h2 style="color: var(--primary-color); margin-bottom: 1rem;">2. How We Use Your Information</h2>
        <ul style="line-height: 1.8; color: #333; margin-bottom: 1.5rem;">
            <li>To provide, maintain, and improve our services</li>
            <li>To send you technical notices and support messages</li>
            <li>To communicate with you about news, offers, and events</li>
            <li>To monitor and analyze trends and usage</li>
            <li>To detect, investigate, and prevent fraudulent activities</li>
        </ul>
        
        <h2 style="color: var(--primary-color); margin-bottom: 1rem;">3. Information Sharing</h2>
        <p style="line-height: 1.8; color: #333; margin-bottom: 1.5rem;">
            We do not sell, trade, or otherwise transfer your personal information to third parties. 
            This does not include trusted third parties who assist us in operating our website, 
            conducting our business, or serving our users, so long as those parties agree to keep 
            this information confidential.
        </p>
        
        <h2 style="color: var(--primary-color); margin-bottom: 1rem;">4. Data Security</h2>
        <p style="line-height: 1.8; color: #333; margin-bottom: 1.5rem;">
            We use appropriate technical and organizational measures to protect the information we 
            collect and store. However, no security system is impenetrable, and we cannot guarantee 
            the security of our systems 100%.
        </p>
        
        <h2 style="color: var(--primary-color); margin-bottom: 1rem;">5. Your Rights</h2>
        <p style="line-height: 1.8; color: #333; margin-bottom: 1.5rem;">
            You have the right to access, update, or delete your personal information. You can do 
            this by logging into your account or contacting us directly.
        </p>
        
        <h2 style="color: var(--primary-color); margin-bottom: 1rem;">6. Cookies</h2>
        <p style="line-height: 1.8; color: #333; margin-bottom: 1.5rem;">
            We use cookies and similar tracking technologies to track activity on our website and 
            hold certain information. You can instruct your browser to refuse all cookies or to 
            indicate when a cookie is being sent.
        </p>
        
        <h2 style="color: var(--primary-color); margin-bottom: 1rem;">7. Contact Us</h2>
        <p style="line-height: 1.8; color: #333;">
            If you have any questions about this Privacy Policy, please contact us at 
            <a href="mailto:privacy@blockwirenews.com" style="color: var(--accent-color);">privacy@blockwirenews.com</a>
        </p>
    </div>
</div>
{% endblock %}''',

    'terms.html': '''{% extends "base_enhanced.html" %}

{% block title %}Terms of Service - BlockWire News{% endblock %}

{% block content %}
<div style="max-width: 800px; margin: 0 auto;">
    <h1 style="color: var(--primary-color); margin-bottom: 2rem;">Terms of Service</h1>
    
    <div style="background: white; padding: 2rem; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
        <p style="color: #666; margin-bottom: 2rem;">Last updated: {{ current_year }}</p>
        
        <h2 style="color: var(--primary-color); margin-bottom: 1rem;">1. Acceptance of Terms</h2>
        <p style="line-height: 1.8; color: #333; margin-bottom: 1.5rem;">
            By accessing and using BlockWire News, you accept and agree to be bound by the terms 
            and provision of this agreement.
        </p>
        
        <h2 style="color: var(--primary-color); margin-bottom: 1rem;">2. Use License</h2>
        <p style="line-height: 1.8; color: #333; margin-bottom: 1.5rem;">
            Permission is granted to temporarily access the materials on BlockWire News for personal, 
            non-commercial transitory viewing only. This is the grant of a license, not a transfer of title.
        </p>
        
        <h2 style="color: var(--primary-color); margin-bottom: 1rem;">3. Disclaimer</h2>
        <p style="line-height: 1.8; color: #333; margin-bottom: 1.5rem;">
            The materials on BlockWire News are provided on an 'as is' basis. BlockWire News makes no 
            warranties, expressed or implied, and hereby disclaims and negates all other warranties including, 
            without limitation, implied warranties or conditions of merchantability, fitness for a particular 
            purpose, or non-infringement of intellectual property or other violation of rights.
        </p>
        
        <h2 style="color: var(--primary-color); margin-bottom: 1rem;">4. User Content</h2>
        <p style="line-height: 1.8; color: #333; margin-bottom: 1.5rem;">
            By posting content on BlockWire News, you grant us a non-exclusive, worldwide, royalty-free 
            license to use, reproduce, modify, and distribute your content in connection with our services.
        </p>
        
        <h2 style="color: var(--primary-color); margin-bottom: 1rem;">5. Prohibited Uses</h2>
        <ul style="line-height: 1.8; color: #333; margin-bottom: 1.5rem;">
            <li>Publishing false, misleading, or fraudulent content</li>
            <li>Violating any applicable laws or regulations</li>
            <li>Infringing on intellectual property rights</li>
            <li>Transmitting malware or other harmful code</li>
            <li>Attempting to gain unauthorized access to our systems</li>
        </ul>
        
        <h2 style="color: var(--primary-color); margin-bottom: 1rem;">6. Investment Disclaimer</h2>
        <p style="line-height: 1.8; color: #333; margin-bottom: 1.5rem; padding: 1rem; background: #fff3cd; border: 1px solid #ffeaa7; border-radius: 4px;">
            <strong>Important:</strong> The information provided on BlockWire News is for informational 
            purposes only and should not be considered investment advice. Cryptocurrency investments carry 
            significant risk. Always do your own research and consult with qualified financial advisors 
            before making investment decisions.
        </p>
        
        <h2 style="color: var(--primary-color); margin-bottom: 1rem;">7. Modifications</h2>
        <p style="line-height: 1.8; color: #333; margin-bottom: 1.5rem;">
            BlockWire News may revise these terms of service at any time without notice. By using this 
            website, you are agreeing to be bound by the then current version of these terms of service.
        </p>
        
        <h2 style="color: var(--primary-color); margin-bottom: 1rem;">8. Contact Information</h2>
        <p style="line-height: 1.8; color: #333;">
            If you have any questions regarding these Terms of Service, please contact us at 
            <a href="mailto:legal@blockwirenews.com" style="color: var(--accent-color);">legal@blockwirenews.com</a>
        </p>
    </div>
</div>
{% endblock %}''',

    'author_profile.html': '''{% extends "base_enhanced.html" %}

{% block title %}{{ author.username }} - Author Profile - BlockWire News{% endblock %}

{% block content %}
<div style="max-width: 800px; margin: 0 auto;">
    <div style="background: white; padding: 2rem; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); margin-bottom: 2rem;">
        <div style="display: flex; align-items: center; gap: 2rem;">
            <div style="width: 100px; height: 100px; background: var(--accent-color); border-radius: 50%; display: flex; align-items: center; justify-content: center; color: white; font-size: 2rem; font-weight: 700;">
                {{ author.username[0].upper() }}
            </div>
            <div>
                <h1 style="color: var(--primary-color); margin-bottom: 0.5rem;">{{ author.username }}</h1>
                {% if author.is_admin %}
                <span style="background: var(--accent-color); color: white; padding: 0.25rem 0.75rem; border-radius: 4px; font-size: 0.875rem;">Editor</span>
                {% endif %}
                <p style="color: #666; margin-top: 0.5rem;">
                    Member since {{ author.created_at.strftime('%B %Y') }} • 
                    {{ articles.total }} articles published
                </p>
            </div>
        </div>
    </div>
    
    <h2 style="color: var(--primary-color); margin-bottom: 1.5rem;">Articles by {{ author.username }}</h2>
    
    {% for article in articles.items %}
    <article style="background: white; border-radius: 8px; padding: 1.5rem; margin-bottom: 1rem; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
        <h3 style="margin-bottom: 0.5rem;">
            <a href="{{ url_for('view_article', slug=article.slug) }}" 
               style="color: var(--primary-color); text-decoration: none;">
                {{ article.title }}
            </a>
        </h3>
        <p style="color: #666; line-height: 1.6; margin-bottom: 0.5rem;">
            {{ article.summary or article.content[:150] }}...
        </p>
        <div style="font-size: 0.875rem; color: #999;">
            {{ article.published_at.strftime('%B %d, %Y') }} • {{ article.views }} views
        </div>
    </article>
    {% endfor %}
    
    {% if not articles.items %}
    <p style="text-align: center; color: #666; padding: 2rem;">
        No articles published yet.
    </p>
    {% endif %}
    
    <!-- Pagination -->
    {% if articles.pages > 1 %}
    <div class="pagination">
        {% if articles.has_prev %}
            <a href="{{ url_for('author_profile', username=author.username, page=articles.prev_num) }}">← Previous</a>
        {% endif %}
        
        <span class="active">Page {{ articles.page }} of {{ articles.pages }}</span>
        
        {% if articles.has_next %}
            <a href="{{ url_for('author_profile', username=author.username, page=articles.next_num) }}">Next →</a>
        {% endif %}
    </div>
    {% endif %}
</div>
{% endblock %}'''
}

def create_templates():
    """Create all missing template files"""
    templates_dir = 'templates'
    
    # Ensure templates directory exists
    if not os.path.exists(templates_dir):
        os.makedirs(templates_dir)
        print(f"Created {templates_dir} directory")
    
    created = 0
    skipped = 0
    
    for filename, content in templates.items():
        filepath = os.path.join(templates_dir, filename)
        
        if os.path.exists(filepath):
            print(f"⚠️  {filename} already exists, skipping...")
            skipped += 1
        else:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✅ Created {filename}")
            created += 1
    
    print(f"\n📊 Summary: {created} files created, {skipped} files skipped")
    print("\n✨ All template files are now in place!")

if __name__ == "__main__":
    create_templates()