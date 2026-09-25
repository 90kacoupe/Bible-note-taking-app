// Offline cache for the app shell. Bump VERSION whenever you change a file
// so phones pick up the update.
const VERSION = 'bible-notes-v10';
const FILES = ['./', './index.html', './styles.css', './manifest.webmanifest', './icons/icon.svg', './icons/icon-192.png', './icons/icon-512.png',
  './bible/bsb.js', './bible/kjv.js',
  './fonts/caveat-latin-600-normal.woff2',
  './fonts/cormorant-garamond-latin-600-normal.woff2',
  './fonts/cormorant-garamond-latin-700-normal.woff2',
  './fonts/eb-garamond-latin-400-italic.woff2',
  './fonts/eb-garamond-latin-400-normal.woff2',
  './fonts/eb-garamond-latin-600-normal.woff2',
  './fonts/fraunces-latin-500-italic.woff2',
  './fonts/fraunces-latin-600-normal.woff2',
  './fonts/literata-latin-400-italic.woff2',
  './fonts/literata-latin-400-normal.woff2',
  './fonts/literata-latin-600-normal.woff2',
];

self.addEventListener('install', event => {
  event.waitUntil(caches.open(VERSION).then(cache => cache.addAll(FILES)).then(() => self.skipWaiting()));
});

self.addEventListener('activate', event => {
  event.waitUntil(
    caches.keys()
      .then(keys => Promise.all(keys.filter(k => k !== VERSION).map(k => caches.delete(k))))
      .then(() => self.clients.claim())
  );
});

// Network first (so updates show up when online), falling back to the cache offline.
self.addEventListener('fetch', event => {
  if (event.request.method !== 'GET' || new URL(event.request.url).origin !== location.origin) return;
  event.respondWith(
    fetch(event.request)
      .then(res => {
        const copy = res.clone();
        caches.open(VERSION).then(cache => cache.put(event.request, copy));
        return res;
      })
      .catch(() => caches.match(event.request, { ignoreSearch: true }).then(r => r || caches.match('./index.html')))
  );
});
