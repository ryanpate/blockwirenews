// static/sw.js - Service Worker for caching

const CACHE_NAME = 'blockwire-v1';
const urlsToCache = [
  '/',
  '/static/styles.css',
  '/static/app.js',
  '/static/ticker_fix.css'
];

// Install event - cache essential files
self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => {
        console.log('Opened cache');
        return cache.addAll(urlsToCache);
      })
      .then(() => self.skipWaiting())
  );
});

// Activate event - clean up old caches
self.addEventListener('activate', event => {
  event.waitUntil(
    caches.keys().then(cacheNames => {
      return Promise.all(
        cacheNames.map(cacheName => {
          if (cacheName !== CACHE_NAME) {
            console.log('Deleting old cache:', cacheName);
            return caches.delete(cacheName);
          }
        })
      );
    }).then(() => self.clients.claim())
  );
});

// Fetch event - serve from cache when possible
self.addEventListener('fetch', event => {
  const { request } = event;
  const url = new URL(request.url);
  
  // Skip non-GET requests
  if (request.method !== 'GET') return;
  
  // Skip admin and API routes
  if (url.pathname.startsWith('/admin') || 
      url.pathname.startsWith('/api') ||
      url.pathname.startsWith('/login') ||
      url.pathname.startsWith('/register')) {
    return;
  }
  
  event.respondWith(
    caches.match(request)
      .then(response => {
        // Cache hit - return response
        if (response) {
          // Check if it's a static asset
          if (url.pathname.startsWith('/static/')) {
            return response;
          }
          
          // For HTML, fetch fresh version in background
          if (request.headers.get('accept').includes('text/html')) {
            fetchAndCache(request);
            return response;
          }
          
          return response;
        }
        
        // Cache miss - fetch and cache
        return fetchAndCache(request);
      })
      .catch(() => {
        // Offline fallback
        if (request.headers.get('accept').includes('text/html')) {
          return caches.match('/');
        }
      })
  );
});

function fetchAndCache(request) {
  return fetch(request)
    .then(response => {
      // Check if valid response
      if (!response || response.status !== 200 || response.type !== 'basic') {
        return response;
      }
      
      // Clone the response
      const responseToCache = response.clone();
      
      caches.open(CACHE_NAME)
        .then(cache => {
          // Set cache expiry based on content type
          const url = new URL(request.url);
          
          if (url.pathname.startsWith('/static/')) {
            // Cache static assets for 1 year
            cache.put(request, responseToCache);
          } else if (url.pathname === '/' || url.pathname.startsWith('/article/')) {
            // Cache HTML for 5 minutes
            const headers = new Headers(responseToCache.headers);
            headers.append('sw-cache-expire', Date.now() + (5 * 60 * 1000));
            
            const cachedResponse = new Response(responseToCache.body, {
              status: responseToCache.status,
              statusText: responseToCache.statusText,
              headers: headers
            });
            
            cache.put(request, cachedResponse);
          }
        });
      
      return response;
    });
}