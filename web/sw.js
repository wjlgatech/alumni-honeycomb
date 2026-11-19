// Exists only so browsers offer "Install". No caching, on purpose: a caching worker serves stale pages.
self.addEventListener('install', () => self.skipWaiting());
self.addEventListener('activate', e => e.waitUntil(self.clients.claim()));
self.addEventListener('fetch', () => {});
