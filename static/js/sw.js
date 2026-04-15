const CACHE_NAME = 'futadmin-v2';
const ASSETS = [
  '/',
  '/static/css/style.css',
  '/static/js/main.js',
  '/static/img/sidebar-logo.png',
  '/static/manifest.json'
];

// Install event - Cache basic assets
self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => {
      return cache.addAll(ASSETS);
    })
  );
});

// Activate event - Cleanup old caches
self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((keys) => {
      return Promise.all(
        keys.filter((key) => key !== CACHE_NAME).map((key) => caches.delete(key))
      );
    })
  );
});

// Fetch event - Network first, fallback to cache (Only for GET requests)
self.addEventListener('fetch', (event) => {
  // Skip non-GET requests (POST, PUT, DELETE should always go to network)
  if (event.request.method !== 'GET') return;

  event.respondWith(
    fetch(event.request).catch(() => {
      return caches.match(event.request).then(response => {
        // Return match or a generic failure response if both fail
        return response || new Response('Network error occurred', {
          status: 408,
          headers: { 'Content-Type': 'text/plain' }
        });
      });
    })
  );
});
