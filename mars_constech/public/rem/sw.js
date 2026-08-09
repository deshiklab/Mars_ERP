// REM ERP PWA — service worker (v3.1.3)
// Strategy: NETWORK-ONLY. This SW exists to REPLACE any stale service worker
// from earlier deployments that cached index.html and served the old broken
// PWA forever. It never caches anything: every request goes to the network,
// and on install/activate it wipes all old caches so nothing stale survives.
self.addEventListener('install', function (e) {
  // Skip waiting so the new SW activates immediately, replacing the old one.
  self.skipWaiting();
  // Nuke every cache this scope ever created.
  if (self.caches) {
    e.waitUntil(
      self.caches.keys().then(function (keys) {
        return Promise.all(keys.map(function (k) { return self.caches.delete(k); }));
      })
    );
  }
});
self.addEventListener('activate', function (e) {
  e.waitUntil(
    Promise.all([
      // Claim all clients so this SW controls pages immediately.
      self.clients.claim(),
      // Again, clear any cache that may have appeared.
      (self.caches || Promise.resolve()).then(function () {
        return self.caches ? self.caches.keys().then(function (keys) {
          return Promise.all(keys.map(function (k) { return self.caches.delete(k); }));
        }) : Promise.resolve();
      })
    ])
  );
});
// Network-only fetch: never serve from cache, never cache responses.
self.addEventListener('fetch', function (e) {
  e.respondWith(fetch(e.request));
});
// Allow the page to request an immediate skipWaiting (used by the version
// notice to update the SW in place before reloading).
self.addEventListener('message', function (e) {
  if (e.data && e.data.type === 'SKIP_WAITING') {
    self.skipWaiting();
  }
});
