// BlockwireNews Main JavaScript

// Generate floating coins on page load
document.addEventListener('DOMContentLoaded', function() {
    generateFloatingCoins();
    initializeSearch();
    initializeMobileMenu();
    updateMarketData();
    startPriceTicker();
});

// Generate floating cryptocurrency symbols
function generateFloatingCoins() {
    const floatingCoins = document.getElementById('floatingCoins');
    if (!floatingCoins) return;
    
    const coinEmojis = ['₿', 'Ξ', '◈', '🪙', '💎', '⟠', '₮', 'Ł'];
    
    for (let i = 0; i < 20; i++) {
        const coin = document.createElement('div');
        coin.className = 'coin';
        coin.textContent = coinEmojis[Math.floor(Math.random() * coinEmojis.length)];
        coin.style.left = Math.random() * 100 + '%';
        coin.style.animationDelay = Math.random() * 20 + 's';
        coin.style.animationDuration = (20 + Math.random() * 10) + 's';
        coin.style.fontSize = (15 + Math.random() * 15) + 'px';
        coin.style.color = `hsl(${Math.random() * 360}, 70%, 60%)`;
        floatingCoins.appendChild(coin);
    }
}

// Initialize search functionality
function initializeSearch() {
    const searchBar = document.getElementById('searchBar');
    const searchBtn = document.getElementById('searchBtn');
    
    if (!searchBar || !searchBtn) return;
    
    searchBtn.addEventListener('click', performSearch);
    searchBar.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            performSearch();
        }
    });
}

function performSearch() {
    const searchBar = document.getElementById('searchBar');
    const query = searchBar.value.trim();
    if (query) {
        window.location.href = `/search/?q=${encodeURIComponent(query)}`;
    }
}

// Initialize mobile menu
function initializeMobileMenu() {
    const mobileMenuToggle = document.getElementById('mobileMenuToggle');
    const navLinks = document.querySelector('.nav-links');
    
    if (!mobileMenuToggle || !navLinks) return;
    
    mobileMenuToggle.addEventListener('click', function() {
        navLinks.classList.toggle('active');
        mobileMenuToggle.classList.toggle('active');
    });
}

// Update market data (in production, this would fetch from an API)
function updateMarketData() {
    // This is placeholder functionality - in production, fetch from CoinGecko or similar API
    const marketData = {
        marketCap: { value: '$4.2T', change: 3.2, positive: true },
        volume24h: { value: '$142B', change: 12.5, positive: true },
        btcDominance: { value: '52.3%', change: -0.8, positive: false },
        activeCryptos: { value: '24,352', change: 142, positive: true }
    };
    
    // Update market overview cards
    updateMarketCard('marketCap', marketData.marketCap);
    updateMarketCard('volume24h', marketData.volume24h);
    updateMarketCard('btcDominance', marketData.btcDominance);
    updateMarketCard('activeCryptos', marketData.activeCryptos);
}

function updateMarketCard(id, data) {
    const valueEl = document.getElementById(id);
    const changeEl = document.getElementById(id + 'Change');
    
    if (valueEl) valueEl.textContent = data.value;
    if (changeEl) {
        const arrow = data.positive ? '↑' : '↓';
        const changeText = typeof data.change === 'number' && data.change % 1 !== 0 
            ? `${arrow} ${Math.abs(data.change)}%`
            : `${arrow} ${Math.abs(data.change)}`;
        changeEl.textContent = changeText;
        changeEl.className = `market-change ${data.positive ? 'positive' : 'negative'}`;
    }
}

// Start price ticker updates
function startPriceTicker() {
    // In production, this would fetch real-time prices
    // For now, we'll just ensure the ticker is running smoothly
    const ticker = document.querySelector('.ticker-content');
    if (!ticker) return;
    
    // Clone ticker content for seamless loop
    const tickerClone = ticker.cloneNode(true);
    ticker.parentElement.appendChild(tickerClone);
}

// Smooth scroll for anchor links
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            target.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }
    });
});

// Add glitch effect to titles on hover
document.querySelectorAll('.section-title').forEach(title => {
    title.addEventListener('mouseenter', function() {
        this.classList.add('glitch');
    });
    title.addEventListener('mouseleave', function() {
        this.classList.remove('glitch');
    });
});

// Newsletter form submission
document.addEventListener('submit', function(e) {
    if (e.target.classList.contains('newsletter-form')) {
        e.preventDefault();
        const email = e.target.querySelector('input[type="email"]').value;
        
        // In production, this would send to your newsletter service
        console.log('Newsletter signup:', email);
        
        // Show success message
        const button = e.target.querySelector('button');
        const originalText = button.textContent;
        button.textContent = 'Subscribed! ✓';
        button.style.background = 'var(--accent-green)';
        
        setTimeout(() => {
            button.textContent = originalText;
            button.style.background = '';
            e.target.reset();
        }, 3000);
    }
});

// Add retro CRT screen effect on scroll
let ticking = false;
function updateCRTEffect() {
    if (!ticking) {
        window.requestAnimationFrame(function() {
            const scrolled = window.pageYOffset;
            const heroSection = document.querySelector('.hero');
            if (heroSection) {
                heroSection.style.transform = `translateY(${scrolled * 0.5}px)`;
            }
            ticking = false;
        });
        ticking = true;
    }
}
window.addEventListener('scroll', updateCRTEffect);

// Add hover sound effects (optional - requires audio files)
function addHoverSounds() {
    const hoverSound = new Audio('/sounds/hover.mp3');
    hoverSound.volume = 0.1;
    
    document.querySelectorAll('.news-card, .market-card, .tag').forEach(element => {
        element.addEventListener('mouseenter', () => {
            hoverSound.currentTime = 0;
            hoverSound.play().catch(() => {}); // Catch and ignore if autoplay is blocked
        });
    });
}

// Initialize hover sounds if user has interacted with the page
document.addEventListener('click', function initSounds() {
    addHoverSounds();
    document.removeEventListener('click', initSounds);
}, { once: true });