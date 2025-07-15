// news-aggregator.js - Handles aggregated news display and updates

let currentPage = 1;
const newsPerPage = 10;
let allNews = [];

// Initialize aggregated news
document.addEventListener('DOMContentLoaded', function() {
    loadAggregatedNews();
    setupLoadMoreButton();
    startAutoRefresh();
});

// Load aggregated news from JSON
async function loadAggregatedNews() {
    const newsContainer = document.getElementById('aggregated-news');
    const lastUpdateElement = document.getElementById('last-update');
    
    if (!newsContainer) return;

    try {
        // Fetch the aggregated news JSON created by scrape.py
        const response = await fetch('/data/aggregated-news.json');
        const data = await response.json();
        
        allNews = data.articles || [];
        
        // Update timestamp
        if (lastUpdateElement && data.lastUpdated) {
            lastUpdateElement.textContent = formatTimestamp(data.lastUpdated);
        }
        
        // Display initial news items
        displayNews(1);
        
    } catch (error) {
        console.error('Error loading aggregated news:', error);
        newsContainer.innerHTML = '<p>Unable to load news. Please try again later.</p>';
    }
}

// Display news items with pagination
function displayNews(page) {
    const newsContainer = document.getElementById('aggregated-news');
    const start = (page - 1) * newsPerPage;
    const end = start + newsPerPage;
    const newsToShow = allNews.slice(0, end);
    
    let newsHTML = '';
    newsToShow.forEach((item, index) => {
        // Add structured data for each news item
        const structuredData = {
            "@context": "https://schema.org",
            "@type": "NewsArticle",
            "headline": item.title,
            "datePublished": item.publishedAt,
            "url": item.url,
            "publisher": {
                "@type": "Organization",
                "name": item.source
            }
        };
        
        newsHTML += `
            <article class="news-item" data-index="${index}">
                <script type="application/ld+json">${JSON.stringify(structuredData)}</script>
                <h3><a href="${item.url}" target="_blank" rel="noopener noreferrer" onclick="trackOutboundLink('${item.url}', '${item.source}')">${item.title}</a></h3>
                <div class="news-meta">
                    <span class="source">${item.source}</span>
                    <span class="time">${formatRelativeTime(item.publishedAt)}</span>
                    ${item.category ? `<span class="category">${item.category}</span>` : ''}
                </div>
                ${item.description ? `<p class="news-description">${truncateText(item.description, 150)}</p>` : ''}
            </article>
        `;
    });
    
    newsContainer.innerHTML = newsHTML;
    
    // Update load more button visibility
    const loadMoreBtn = document.getElementById('load-more-news');
    if (loadMoreBtn) {
        loadMoreBtn.style.display = end >= allNews.length ? 'none' : 'block';
    }
    
    // Animate new items
    animateNewsItems();
}

// Setup load more functionality
function setupLoadMoreButton() {
    const loadMoreBtn = document.getElementById('load-more-news');
    if (!loadMoreBtn) return;
    
    loadMoreBtn.addEventListener('click', () => {
        currentPage++;
        displayNews(currentPage);
        
        // Track engagement
        if (typeof gtag !== 'undefined') {
            gtag('event', 'load_more_news', {
                'event_category': 'engagement',
                'page_number': currentPage
            });
        }
    });
}

// Auto-refresh news every hour
function startAutoRefresh() {
    // Refresh every 60 minutes
    setInterval(() => {
        loadAggregatedNews();
        showRefreshNotification();
    }, 60 * 60 * 1000);
}

// Show refresh notification
function showRefreshNotification() {
    const notification = document.createElement('div');
    notification.className = 'refresh-notification';
    notification.textContent = 'News updated with latest articles';
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: var(--success-color);
        color: white;
        padding: 1rem 2rem;
        border-radius: 5px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.2);
        z-index: 9999;
        animation: slideIn 0.3s ease;
    `;
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.style.animation = 'slideOut 0.3s ease';
        setTimeout(() => notification.remove(), 300);
    }, 3000);
}

// Utility Functions
function formatTimestamp(timestamp) {
    const date = new Date(timestamp);
    const options = { 
        month: 'short', 
        day: 'numeric', 
        hour: '2-digit', 
        minute: '2-digit'
    };
    return date.toLocaleDateString('en-US', options);
}

function formatRelativeTime(dateString) {
    const date = new Date(dateString);
    const now = new Date();
    const diffInHours = Math.floor((now - date) / (1000 * 60 * 60));
    
    if (diffInHours < 1) {
        const diffInMinutes = Math.floor((now - date) / (1000 * 60));
        return `${diffInMinutes} minutes ago`;
    } else if (diffInHours < 24) {
        return `${diffInHours} hour${diffInHours > 1 ? 's' : ''} ago`;
    } else {
        const diffInDays = Math.floor(diffInHours / 24);
        return `${diffInDays} day${diffInDays > 1 ? 's' : ''} ago`;
    }
}

function truncateText(text, maxLength) {
    if (text.length <= maxLength) return text;
    return text.substr(0, maxLength).trim() + '...';
}

// Track outbound links for analytics
function trackOutboundLink(url, source) {
    if (typeof gtag !== 'undefined') {
        gtag('event', 'click', {
            'event_category': 'outbound',
            'event_label': source,
            'transport_type': 'beacon',
            'event_callback': function() {
                // Ensure link opens even if tracking fails
            }
        });
    }
    return true;
}

// Animate news items on load
function animateNewsItems() {
    const newsItems = document.querySelectorAll('.news-item');
    newsItems.forEach((item, index) => {
        item.style.opacity = '0';
        item.style.transform = 'translateY(20px)';
        
        setTimeout(() => {
            item.style.transition = 'opacity 0.3s ease, transform 0.3s ease';
            item.style.opacity = '1';
            item.style.transform = 'translateY(0)';
        }, index * 50);
    });
}

// Search and filter functionality
function setupNewsFilters() {
    // Add search box
    const searchBox = document.createElement('input');
    searchBox.type = 'text';
    searchBox.placeholder = 'Search news...';
    searchBox.className = 'news-search';
    
    const newsSection = document.querySelector('.aggregated-news .container');
    if (newsSection) {
        newsSection.insertBefore(searchBox, newsSection.querySelector('.news-grid'));
        
        searchBox.addEventListener('input', (e) => {
            const searchTerm = e.target.value.toLowerCase();
            filterNews(searchTerm);
        });
    }
}

function filterNews(searchTerm) {
    const filteredNews = allNews.filter(item => 
        item.title.toLowerCase().includes(searchTerm) ||
        (item.description && item.description.toLowerCase().includes(searchTerm)) ||
        item.source.toLowerCase().includes(searchTerm)
    );
    
    // Temporarily replace allNews for display
    const tempNews = allNews;
    allNews = filteredNews;
    currentPage = 1;
    displayNews(1);
    allNews = tempNews;
}

// Initialize filters
setupNewsFilters();