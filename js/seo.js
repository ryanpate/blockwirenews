// seo.js - SEO enhancements and structured data

// Initialize SEO enhancements
document.addEventListener('DOMContentLoaded', function() {
    enhanceMetaTags();
    generateBreadcrumbs();
    addArticleStructuredData();
    implementInternalLinking();
    trackCoreWebVitals();
});

// Dynamic meta tag enhancement based on content
function enhanceMetaTags() {
    const path = window.location.pathname;
    const title = document.title;
    
    // Update meta description based on page content
    if (path.includes('/articles/')) {
        const article = document.querySelector('.article-content');
        if (article) {
            const excerpt = article.querySelector('.article-excerpt');
            if (excerpt) {
                updateMetaTag('description', excerpt.textContent.substring(0, 160));
            }
        }
    }
    
    // Add additional meta tags for SEO
    addMetaTag('og:site_name', 'BlockwireNews');
    addMetaTag('twitter:site', '@blockwirenews');
    
    // Add alternate language tags if needed
    addLinkTag('alternate', 'hreflang', 'en', window.location.href);
}

// Generate breadcrumb navigation
function generateBreadcrumbs() {
    const path = window.location.pathname;
    const segments = path.split('/').filter(Boolean);
    
    if (segments.length === 0) return;
    
    const breadcrumbData = {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {
                "@type": "ListItem",
                "position": 1,
                "name": "Home",
                "item": "https://www.blockwirenews.com"
            }
        ]
    };
    
    let currentPath = '';
    segments.forEach((segment, index) => {
        currentPath += '/' + segment;
        const name = segment.charAt(0).toUpperCase() + segment.slice(1).replace(/-/g, ' ');
        
        breadcrumbData.itemListElement.push({
            "@type": "ListItem",
            "position": index + 2,
            "name": name,
            "item": `https://www.blockwirenews.com${currentPath}`
        });
    });
    
    // Add breadcrumb structured data
    const script = document.createElement('script');
    script.type = 'application/ld+json';
    script.textContent = JSON.stringify(breadcrumbData);
    document.head.appendChild(script);
    
    // Add visual breadcrumbs
    if (segments.length > 0) {
        const breadcrumbNav = createBreadcrumbNav(segments);
        const main = document.querySelector('main');
        if (main) {
            main.insertBefore(breadcrumbNav, main.firstChild);
        }
    }
}

// Create visual breadcrumb navigation
function createBreadcrumbNav(segments) {
    const nav = document.createElement('nav');
    nav.className = 'breadcrumb';
    nav.setAttribute('aria-label', 'Breadcrumb');
    
    let html = '<ol class="breadcrumb-list"><li><a href="/">Home</a></li>';
    let currentPath = '';
    
    segments.forEach((segment, index) => {
        currentPath += '/' + segment;
        const name = segment.charAt(0).toUpperCase() + segment.slice(1).replace(/-/g, ' ');
        
        if (index === segments.length - 1) {
            html += `<li class="current">${name}</li>`;
        } else {
            html += `<li><a href="${currentPath}">${name}</a></li>`;
        }
    });
    
    html += '</ol>';
    nav.innerHTML = html;
    return nav;
}

// Add article structured data
function addArticleStructuredData() {
    const articleElement = document.querySelector('article.full-article');
    if (!articleElement) return;
    
    const articleData = {
        "@context": "https://schema.org",
        "@type": "Article",
        "headline": document.querySelector('h1').textContent,
        "datePublished": document.querySelector('meta[property="article:published_time"]')?.content || new Date().toISOString(),
        "dateModified": document.querySelector('meta[property="article:modified_time"]')?.content || new Date().toISOString(),
        "author": {
            "@type": "Person",
            "name": document.querySelector('.author-name')?.textContent || "BlockwireNews Team"
        },
        "publisher": {
            "@type": "Organization",
            "name": "BlockwireNews",
            "logo": {
                "@type": "ImageObject",
                "url": "https://www.blockwirenews.com/images/logo.png"
            }
        },
        "description": document.querySelector('meta[name="description"]')?.content,
        "mainEntityOfPage": {
            "@type": "WebPage",
            "@id": window.location.href
        }
    };
    
    // Add image if present
    const featuredImage = document.querySelector('.featured-image img');
    if (featuredImage) {
        articleData.image = featuredImage.src;
    }
    
    const script = document.createElement('script');
    script.type = 'application/ld+json';
    script.textContent = JSON.stringify(articleData);
    document.head.appendChild(script);
}

// Implement smart internal linking
function implementInternalLinking() {
    const content = document.querySelector('.article-content, .news-content');
    if (!content) return;
    
    // Keywords to link mapping
    const keywordLinks = {
        'bitcoin': '/category/bitcoin',
        'ethereum': '/category/ethereum',
        'defi': '/category/defi',
        'nft': '/category/nft',
        'blockchain': '/category/technology',
        'cryptocurrency': '/',
        'crypto market': '/market',
        'bitcoin price': '/market/bitcoin',
        'ethereum news': '/category/ethereum'
    };
    
    // Process text nodes to add links
    const textNodes = getTextNodes(content);
    textNodes.forEach(node => {
        let text = node.textContent;
        let modified = false;
        
        for (const [keyword, url] of Object.entries(keywordLinks)) {
            const regex = new RegExp(`\\b(${keyword})\\b`, 'gi');
            if (regex.test(text)) {
                text = text.replace(regex, `<a href="${url}" class="internal-link">$1</a>`);
                modified = true;
            }
        }
        
        if (modified) {
            const span = document.createElement('span');
            span.innerHTML = text;
            node.parentNode.replaceChild(span, node);
        }
    });
}

// Get all text nodes in an element
function getTextNodes(element) {
    const textNodes = [];
    const walker = document.createTreeWalker(
        element,
        NodeFilter.SHOW_TEXT,
        {
            acceptNode: function(node) {
                // Skip if parent is already a link
                if (node.parentNode.tagName === 'A') {
                    return NodeFilter.FILTER_REJECT;
                }
                return NodeFilter.FILTER_ACCEPT;
            }
        }
    );
    
    let node;
    while (node = walker.nextNode()) {
        textNodes.push(node);
    }
    return textNodes;
}

// Track Core Web Vitals
function trackCoreWebVitals() {
    // Only track if Web Vitals API is available
    if ('PerformanceObserver' in window) {
        // Largest Contentful Paint (LCP)
        new PerformanceObserver((list) => {
            for (const entry of list.getEntries()) {
                console.log('LCP:', entry.startTime);
                // Send to analytics
                if (typeof gtag !== 'undefined') {
                    gtag('event', 'web_vitals', {
                        event_category: 'Web Vitals',
                        event_label: 'LCP',
                        value: Math.round(entry.startTime)
                    });
                }
            }
        }).observe({entryTypes: ['largest-contentful-paint']});
        
        // First Input Delay (FID)
        new PerformanceObserver((list) => {
            for (const entry of list.getEntries()) {
                const fid = entry.processingStart - entry.startTime;
                console.log('FID:', fid);
                if (typeof gtag !== 'undefined') {
                    gtag('event', 'web_vitals', {
                        event_category: 'Web Vitals',
                        event_label: 'FID',
                        value: Math.round(fid)
                    });
                }
            }
        }).observe({entryTypes: ['first-input']});
        
        // Cumulative Layout Shift (CLS)
        let clsValue = 0;
        new PerformanceObserver((list) => {
            for (const entry of list.getEntries()) {
                if (!entry.hadRecentInput) {
                    clsValue += entry.value;
                    console.log('CLS:', clsValue);
                }
            }
        }).observe({entryTypes: ['layout-shift']});
        
        // Send final CLS value when page is about to unload
        window.addEventListener('beforeunload', () => {
            if (typeof gtag !== 'undefined') {
                gtag('event', 'web_vitals', {
                    event_category: 'Web Vitals',
                    event_label: 'CLS',
                    value: Math.round(clsValue * 1000)
                });
            }
        });
    }
}

// Utility functions for meta tags
function updateMetaTag(name, content) {
    let meta = document.querySelector(`meta[name="${name}"]`);
    if (!meta) {
        meta = document.querySelector(`meta[property="${name}"]`);
    }
    if (meta) {
        meta.setAttribute('content', content);
    } else {
        addMetaTag(name, content);
    }
}

function addMetaTag(name, content) {
    const meta = document.createElement('meta');
    if (name.startsWith('og:') || name.startsWith('twitter:')) {
        meta.setAttribute('property', name);
    } else {
        meta.setAttribute('name', name);
    }
    meta.setAttribute('content', content);
    document.head.appendChild(meta);
}

function addLinkTag(rel, name, value, href) {
    const link = document.createElement('link');
    link.setAttribute('rel', rel);
    link.setAttribute(name, value);
    link.setAttribute('href', href);
    document.head.appendChild(link);
}

// Implement FAQ Schema for common questions
function addFAQSchema() {
    const faqData = {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": [
            {
                "@type": "Question",
                "name": "What is cryptocurrency?",
                "acceptedAnswer": {
                    "@type": "Answer",
                    "text": "Cryptocurrency is a digital or virtual form of currency that uses cryptography for security and operates on decentralized networks based on blockchain technology."
                }
            },
            {
                "@type": "Question",
                "name": "How often is BlockwireNews updated?",
                "acceptedAnswer": {
                    "@type": "Answer",
                    "text": "BlockwireNews aggregates cryptocurrency news from multiple sources and updates hourly to bring you the latest information from the crypto world."
                }
            },
            {
                "@type": "Question",
                "name": "What sources does BlockwireNews aggregate from?",
                "acceptedAnswer": {
                    "@type": "Answer",
                    "text": "We aggregate news from leading cryptocurrency news sources including CoinDesk, Cointelegraph, Bitcoin Magazine, and other reputable crypto news outlets."
                }
            }
        ]
    };
    
    const script = document.createElement('script');
    script.type = 'application/ld+json';
    script.textContent = JSON.stringify(faqData);
    document.head.appendChild(script);
}

// Add organization schema
function addOrganizationSchema() {
    const orgData = {
        "@context": "https://schema.org",
        "@type": "Organization",
        "name": "BlockwireNews",
        "url": "https://www.blockwirenews.com",
        "logo": "https://www.blockwirenews.com/images/logo.png",
        "sameAs": [
            "https://twitter.com/blockwirenews",
            "https://facebook.com/blockwirenews",
            "https://linkedin.com/company/blockwirenews"
        ],
        "contactPoint": {
            "@type": "ContactPoint",
            "contactType": "customer service",
            "email": "contact@blockwirenews.com"
        }
    };
    
    const script = document.createElement('script');
    script.type = 'application/ld+json';
    script.textContent = JSON.stringify(orgData);
    document.head.appendChild(script);
}

// Initialize additional schemas on homepage
if (window.location.pathname === '/') {
    addFAQSchema();
    addOrganizationSchema();
}