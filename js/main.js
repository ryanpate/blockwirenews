// main.js - Core functionality for BlockwireNews

// Initialize on DOM load
document.addEventListener('DOMContentLoaded', function() {
    initializeCryptoPrices();
    loadOriginalArticles();
    setupNewsletterForm();
    setupMobileMenu();
    trackPageView();
});

// Crypto Price Ticker
async function initializeCryptoPrices() {
    const cryptoContainer = document.getElementById('crypto-prices');
    if (!cryptoContainer) return;

    try {
        // Using CoinGecko API (free tier)
        const response = await fetch('https://api.coingecko.com/api/v3/simple/price?ids=bitcoin,ethereum,binance-coin,ripple,cardano,solana&vs_currencies=usd&include_24hr_change=true');
        const data = await response.json();
        
        const symbols = {
            bitcoin: 'BTC',
            ethereum: 'ETH',
            'binance-coin': 'BNB',
            ripple: 'XRP',
            cardano: 'ADA',
            solana: 'SOL'
        };
        
        let tickerHTML = '';
        for (const [coin, details] of Object.entries(data)) {
            const changeClass = details.usd_24h_change >= 0 ? 'positive' : 'negative';
            const changePrefix = details.usd_24h_change >= 0 ? '+' : '';
            
            tickerHTML += `
                <div class="ticker-item">
                    <span class="symbol">${symbols[coin]}</span>
                    <span class="price">$${details.usd.toLocaleString()}</span>
                    <span class="change ${changeClass}">${changePrefix}${details.usd_24h_change.toFixed(2)}%</span>
                </div>
            `;
        }
        
        // Duplicate for seamless scrolling
        cryptoContainer.innerHTML = tickerHTML + tickerHTML;
    } catch (error) {
        console.error('Error fetching crypto prices:', error);
        cryptoContainer.innerHTML = '<p>Unable to load prices</p>';
    }
}

// Load Original Articles
async function loadOriginalArticles() {
    const articlesContainer = document.getElementById('original-articles');
    if (!articlesContainer) return;

    // Sample articles - in production, this would fetch from your CMS or JSON file
    const articles = [
        {
            id: 1,
            title: 'Bitcoin Halving 2024: What Investors Need to Know',
            excerpt: 'An in-depth analysis of the upcoming Bitcoin halving event and its potential impact on cryptocurrency markets.',
            author: 'John Doe',
            date: '2024-01-15',
            image: '/images/bitcoin-halving.jpg',
            slug: 'bitcoin-halving-2024-investors-guide'
        },
        {
            id: 2,
            title: 'DeFi Revolution: Top 5 Protocols to Watch in 2024',
            excerpt: 'Exploring the most promising DeFi protocols that are reshaping the financial landscape.',
            author: 'Jane Smith',
            date: '2024-01-14',
            image: '/images/defi-protocols.jpg',
            slug: 'defi-revolution-top-protocols-2024'
        },
        {
            id: 3,
            title: 'Ethereum 2.0: The Complete Upgrade Guide',
            excerpt: 'Everything you need to know about Ethereum\'s transition to proof-of-stake and beyond.',
            author: 'Mike Johnson',
            date: '2024-01-13',
            image: '/images/ethereum-upgrade.jpg',
            slug: 'ethereum-2-complete-upgrade-guide'
        }
    ];

    let articlesHTML = '';
    articles.forEach(article => {
        articlesHTML += `
            <article class="article-card">
                <img src="${article.image}" alt="${article.title}" loading="lazy">
                <div class="article-content">
                    <h3><a href="/articles/${article.slug}.html">${article.title}</a></h3>
                    <div class="article-meta">
                        <span class="author">By ${article.author}</span>
                        <span class="date">${formatDate(article.date)}</span>
                    </div>
                    <p class="article-excerpt">${article.excerpt}</p>
                </div>
            </article>
        `;
    });

    articlesContainer.innerHTML = articlesHTML;
}

// Newsletter Form Handler
function setupNewsletterForm() {
    const form = document.getElementById('newsletter-form');
    if (!form) return;

    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        const email = form.querySelector('input[type="email"]').value;
        
        // In production, send to your email service
        try {
            // Simulate API call
            await new Promise(resolve => setTimeout(resolve, 1000));
            
            // Show success message
            form.innerHTML = '<p style="color: white;">Thank you for subscribing! Check your email for confirmation.</p>';
            
            // Track conversion
            if (typeof gtag !== 'undefined') {
                gtag('event', 'newsletter_signup', {
                    'event_category': 'engagement',
                    'event_label': email
                });
            }
        } catch (error) {
            console.error('Newsletter signup error:', error);
            alert('There was an error. Please try again.');
        }
    });
}

// Mobile Menu Toggle
function setupMobileMenu() {
    // Add mobile menu functionality
    const mobileMenuBtn = document.createElement('button');
    mobileMenuBtn.className = 'mobile-menu-btn';
    mobileMenuBtn.innerHTML = '☰';
    mobileMenuBtn.style.display = 'none';
    
    const navbar = document.querySelector('.navbar .container');
    navbar.appendChild(mobileMenuBtn);
    
    // Check if mobile
    if (window.innerWidth <= 768) {
        mobileMenuBtn.style.display = 'block';
    }
    
    mobileMenuBtn.addEventListener('click', () => {
        const navMenu = document.querySelector('.nav-menu');
        navMenu.classList.toggle('mobile-active');
    });
}

// Utility Functions
function formatDate(dateString) {
    const options = { year: 'numeric', month: 'short', day: 'numeric' };
    return new Date(dateString).toLocaleDateString('en-US', options);
}

// Analytics and Performance
function trackPageView() {
    // Google Analytics
    if (typeof gtag !== 'undefined') {
        gtag('config', 'GA_MEASUREMENT_ID', {
            page_path: window.location.pathname,
            page_title: document.title
        });
    }
    
    // Performance monitoring
    if ('performance' in window) {
        window.addEventListener('load', () => {
            const perfData = window.performance.timing;
            const pageLoadTime = perfData.loadEventEnd - perfData.navigationStart;
            console.log(`Page load time: ${pageLoadTime}ms`);
            
            // Send to analytics
            if (typeof gtag !== 'undefined') {
                gtag('event', 'timing_complete', {
                    'name': 'load',
                    'value': pageLoadTime,
                    'event_category': 'performance'
                });
            }
        });
    }
}

// Lazy Loading for Images
const imageObserver = new IntersectionObserver((entries, observer) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            const img = entry.target;
            img.src = img.dataset.src;
            img.classList.add('loaded');
            observer.unobserve(img);
        }
    });
});

// Observe all images with data-src
document.querySelectorAll('img[data-src]').forEach(img => {
    imageObserver.observe(img);
});