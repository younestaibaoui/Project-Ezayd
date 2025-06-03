// Service Worker for offline functionality
const CACHE_NAME = "ezayd-v1"
const urlsToCache = [
  "./",
  "./css/critical.css",
  "./css/main.css",
  "./js/main.js",
  "./js/carousel.js",
  "./js/modal.js",
  "./logo-site.svg",
  "./images/mini_logo.png",
  "/fonts/outfit.woff2",
]

// Install event
self.addEventListener("install", (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => {
      return cache.addAll(urlsToCache)
    }),
  )
})

// Fetch event
self.addEventListener("fetch", (event) => {
  event.respondWith(
    caches.match(event.request).then((response) => {
      // Return cached version or fetch from network
      return response || fetch(event.request)
    }),
  )
})

// Activate event
self.addEventListener("activate", (event) => {
  event.waitUntil(
    caches.keys().then((cacheNames) => {
      return Promise.all(
        cacheNames.map((cacheName) => {
          if (cacheName !== CACHE_NAME) {
            return caches.delete(cacheName)
          }
        }),
      )
    }),
  )
})
