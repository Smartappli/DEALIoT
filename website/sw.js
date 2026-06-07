const CACHE_NAME = "dealiot-pwa-v5";
const ASSET_VERSION = "20260607-cache-performance-v1";
const ROUTE_ASSETS = [
  "./",
  "./fr/",
  "./sv/",
  "./es/",
  "./sl/",
  "./sk/",
  "./ro/",
  "./pt/",
  "./pl/",
  "./mt/",
  "./lt/",
  "./lv/",
  "./it/",
  "./ga/",
  "./hu/",
  "./el/",
  "./de/",
  "./fi/",
  "./et/",
  "./nl/",
  "./da/",
  "./cs/",
  "./hr/",
  "./bg/",
];
const STATIC_ASSETS = [
  "./offline.html",
  `./styles.css?v=${ASSET_VERSION}`,
  `./app.js?v=${ASSET_VERSION}`,
  "./site.webmanifest",
  "./assets/mark.svg",
  "./assets/icon-192.png",
  "./assets/icon-512.png",
  "./assets/icon-maskable-512.png",
  "./assets/social-card.png",
];
const CORE_ASSETS = [...ROUTE_ASSETS, ...STATIC_ASSETS];

self.addEventListener("install", (event) => {
  event.waitUntil(caches.open(CACHE_NAME).then((cache) => cache.addAll(CORE_ASSETS)));
  self.skipWaiting();
});

self.addEventListener("activate", (event) => {
  event.waitUntil(
    caches.keys().then((cacheNames) =>
      Promise.all(
        cacheNames
          .filter((cacheName) => cacheName !== CACHE_NAME)
          .map((cacheName) => caches.delete(cacheName)),
      ),
    ),
  );
  self.clients.claim();
});

self.addEventListener("fetch", (event) => {
  const { request } = event;

  if (request.method !== "GET") {
    return;
  }

  const requestUrl = new URL(request.url);
  if (requestUrl.origin !== self.location.origin) {
    return;
  }

  const isNetworkFirstAsset =
    requestUrl.pathname.endsWith("/sw.js") ||
    requestUrl.pathname.endsWith("/site.webmanifest") ||
    requestUrl.pathname.endsWith("/robots.txt") ||
    requestUrl.pathname.endsWith("/sitemap.xml") ||
    requestUrl.pathname.endsWith("/llms.txt") ||
    requestUrl.pathname.endsWith("/humans.txt");

  if (request.mode === "navigate") {
    event.respondWith(networkFirst(request, "./offline.html"));
    return;
  }

  if (isNetworkFirstAsset) {
    event.respondWith(networkFirst(request));
    return;
  }

  event.respondWith(staleWhileRevalidate(request));
});

function cacheResponse(request, response) {
  if (!response || !response.ok) {
    return response;
  }

  const responseCopy = response.clone();
  caches.open(CACHE_NAME).then((cache) => cache.put(request, responseCopy));
  return response;
}

function networkFirst(request, fallbackUrl) {
  return fetch(request)
    .then((response) => cacheResponse(request, response))
    .catch(() =>
      caches.match(request).then((cached) => {
        if (cached) {
          return cached;
        }

        if (!fallbackUrl) {
          return Response.error();
        }

        return caches.match(fallbackUrl).then((fallback) => fallback || Response.error());
      }),
    );
}

function staleWhileRevalidate(request) {
  return caches.match(request).then((cached) => {
    const networkResponse = fetch(request)
      .then((response) => cacheResponse(request, response))
      .catch(() => cached || caches.match(request, { ignoreSearch: true }));

    return cached || networkResponse;
  });
}
