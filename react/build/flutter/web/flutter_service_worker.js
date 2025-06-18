'use strict';
const MANIFEST = 'flutter-app-manifest';
const TEMP = 'flutter-temp-cache';
const CACHE_NAME = 'flutter-app-cache';

const RESOURCES = {"assets/AssetManifest.bin": "ed62d74c7f45e5ddba81961b6691aa2e",
"assets/AssetManifest.bin.json": "dbe7cbdae580f758548ce19cba9e5574",
"assets/AssetManifest.json": "51516a7867a501da928ae0521f19b4c1",
"assets/assets/animations/error.json": "1fd52c9b9641c5faeb02872e43eba78c",
"assets/assets/animations/error1.json": "c9d53b30162e4d36cb558936c03a06a4",
"assets/assets/animations/error2.json": "14adc48a53b3b19886b88dabc2b539ae",
"assets/assets/animations/error3.json": "09f888bd72db153f81d7d30dfc2c22ae",
"assets/assets/animations/loading.json": "ecb14b1d5c1e18003924158dac4fb5db",
"assets/assets/animations/loading1.json": "73b94438243d2cfda97bf7e80149cd9d",
"assets/assets/animations/loading2.json": "9e768c49b75ba1414f94c643280086ab",
"assets/assets/animations/loading3.json": "3817a4d1b3a161ef4b86b00aa6542cf8",
"assets/assets/animations/loading_pro_1.json": "90ad3eda30adcb6ecd01b6ea9a9543ba",
"assets/assets/animations/loading_pro_2.json": "2e75b63a1e572dfc758ddc6150d7febb",
"assets/assets/animations/loading_pro_3.json": "ac5c2f076df8d4aa67a39771d43352d4",
"assets/assets/animations/loading_pro_4.json": "dc4c87bc9fa3e89856c7b008f227be22",
"assets/assets/animations/network_error.json": "7c0a2b15c0f6a4718a504e097eab278e",
"assets/assets/fonts/be_vietnam_pro/BeVietnamPro-Bold.ttf": "48bbc99d88e5c99a2bc2780f28c137e3",
"assets/assets/fonts/be_vietnam_pro/BeVietnamPro-Light.ttf": "4880b6055406c3d07487cbcf665f4d39",
"assets/assets/fonts/be_vietnam_pro/BeVietnamPro-Medium.ttf": "1ac40fd79ee227d1457f552b22828aa3",
"assets/assets/fonts/be_vietnam_pro/BeVietnamPro-Regular.ttf": "ec23619ef59c67e6a69719e8f0780a7e",
"assets/assets/fonts/be_vietnam_pro/BeVietnamPro-SemiBold.ttf": "205935f41af371be49ba31b51187e36f",
"assets/assets/icons/chatbot_icon.png": "94254b83b095ba8ec11092f831fef993",
"assets/assets/icons/google_icon.svg": "b02770093748aa06a282ac5cd7fd2f0a",
"assets/assets/icons/logout_icon.png": "7e20a244b805297653ab63c883e742ae",
"assets/assets/icons/survey_icon.png": "9d55209bdd85cf51ef8cfabfcfcc5821",
"assets/assets/icons/survey_icon2.png": "44d7f5de8eefc27a620182f36f84ea20",
"assets/assets/icons/unknown_person.jpg": "bc23fb0699920e699baeb3298eb6eb9c",
"assets/assets/icons/vmu_icon_app.png": "4935fe713b958b049345944944c2fdf8",
"assets/assets/icons/vmu_logo.png": "20ad30e4ff6047bdec843f6029769c70",
"assets/assets/images/login_background.jpg": "a8c381d8c2a2dc61c85ae73105e5d235",
"assets/assets/images/vmu_background.jpg": "5d2331656e75271e382769cd686ee8e8",
"assets/FontManifest.json": "dccfbd380d6558e69e0b458eb0903746",
"assets/fonts/MaterialIcons-Regular.otf": "76307faf487ed711a0849e0190602d69",
"assets/NOTICES": "31d93b5c4b5f3e53e4c54d0331634f3a",
"assets/packages/cupertino_icons/assets/CupertinoIcons.ttf": "825e75415ebd366b740bb49659d7a5c6",
"assets/shaders/ink_sparkle.frag": "ecc85a2e95f5e9f53123dcaf8cb9b6ce",
"canvaskit/canvaskit.js": "728b2d477d9b8c14593d4f9b82b484f3",
"canvaskit/canvaskit.js.symbols": "27361387bc24144b46a745f1afe92b50",
"canvaskit/canvaskit.wasm": "a37f2b0af4995714de856e21e882325c",
"canvaskit/chromium/canvaskit.js": "8191e843020c832c9cf8852a4b909d4c",
"canvaskit/chromium/canvaskit.js.symbols": "f7c5e5502d577306fb6d530b1864ff86",
"canvaskit/chromium/canvaskit.wasm": "c054c2c892172308ca5a0bd1d7a7754b",
"canvaskit/skwasm.js": "ea559890a088fe28b4ddf70e17e60052",
"canvaskit/skwasm.js.symbols": "9fe690d47b904d72c7d020bd303adf16",
"canvaskit/skwasm.wasm": "1c93738510f202d9ff44d36a4760126b",
"favicon.png": "5dcef449791fa27946b3d35ad8803796",
"flutter.js": "83d881c1dbb6d6bcd6b42e274605b69c",
"flutter_bootstrap.js": "27ea3b06d33c2a5b23c8b3c8feeb22e2",
"icons/Icon-192.png": "ac9a721a12bbc803b44f645561ecb1e1",
"icons/Icon-512.png": "96e752610906ba2a93c65f8abe1645f1",
"icons/Icon-maskable-192.png": "c457ef57daa1d16f64b27b786ec2ea3c",
"icons/Icon-maskable-512.png": "301a7604d45b3e739efc881eb04896ea",
"index.html": "47221611d826e8a1a0bd042bd22fdd56",
"/": "47221611d826e8a1a0bd042bd22fdd56",
"main.dart.js": "8aee31a85ad736d48f7d9eb04936092a",
"manifest.json": "4e93747d97429277e29003e09165d396",
"version.json": "3611f3153e43b28bf1638cf59582feb1"};
// The application shell files that are downloaded before a service worker can
// start.
const CORE = ["main.dart.js",
"index.html",
"flutter_bootstrap.js",
"assets/AssetManifest.bin.json",
"assets/FontManifest.json"];

// During install, the TEMP cache is populated with the application shell files.
self.addEventListener("install", (event) => {
  self.skipWaiting();
  return event.waitUntil(
    caches.open(TEMP).then((cache) => {
      return cache.addAll(
        CORE.map((value) => new Request(value, {'cache': 'reload'})));
    })
  );
});
// During activate, the cache is populated with the temp files downloaded in
// install. If this service worker is upgrading from one with a saved
// MANIFEST, then use this to retain unchanged resource files.
self.addEventListener("activate", function(event) {
  return event.waitUntil(async function() {
    try {
      var contentCache = await caches.open(CACHE_NAME);
      var tempCache = await caches.open(TEMP);
      var manifestCache = await caches.open(MANIFEST);
      var manifest = await manifestCache.match('manifest');
      // When there is no prior manifest, clear the entire cache.
      if (!manifest) {
        await caches.delete(CACHE_NAME);
        contentCache = await caches.open(CACHE_NAME);
        for (var request of await tempCache.keys()) {
          var response = await tempCache.match(request);
          await contentCache.put(request, response);
        }
        await caches.delete(TEMP);
        // Save the manifest to make future upgrades efficient.
        await manifestCache.put('manifest', new Response(JSON.stringify(RESOURCES)));
        // Claim client to enable caching on first launch
        self.clients.claim();
        return;
      }
      var oldManifest = await manifest.json();
      var origin = self.location.origin;
      for (var request of await contentCache.keys()) {
        var key = request.url.substring(origin.length + 1);
        if (key == "") {
          key = "/";
        }
        // If a resource from the old manifest is not in the new cache, or if
        // the MD5 sum has changed, delete it. Otherwise the resource is left
        // in the cache and can be reused by the new service worker.
        if (!RESOURCES[key] || RESOURCES[key] != oldManifest[key]) {
          await contentCache.delete(request);
        }
      }
      // Populate the cache with the app shell TEMP files, potentially overwriting
      // cache files preserved above.
      for (var request of await tempCache.keys()) {
        var response = await tempCache.match(request);
        await contentCache.put(request, response);
      }
      await caches.delete(TEMP);
      // Save the manifest to make future upgrades efficient.
      await manifestCache.put('manifest', new Response(JSON.stringify(RESOURCES)));
      // Claim client to enable caching on first launch
      self.clients.claim();
      return;
    } catch (err) {
      // On an unhandled exception the state of the cache cannot be guaranteed.
      console.error('Failed to upgrade service worker: ' + err);
      await caches.delete(CACHE_NAME);
      await caches.delete(TEMP);
      await caches.delete(MANIFEST);
    }
  }());
});
// The fetch handler redirects requests for RESOURCE files to the service
// worker cache.
self.addEventListener("fetch", (event) => {
  if (event.request.method !== 'GET') {
    return;
  }
  var origin = self.location.origin;
  var key = event.request.url.substring(origin.length + 1);
  // Redirect URLs to the index.html
  if (key.indexOf('?v=') != -1) {
    key = key.split('?v=')[0];
  }
  if (event.request.url == origin || event.request.url.startsWith(origin + '/#') || key == '') {
    key = '/';
  }
  // If the URL is not the RESOURCE list then return to signal that the
  // browser should take over.
  if (!RESOURCES[key]) {
    return;
  }
  // If the URL is the index.html, perform an online-first request.
  if (key == '/') {
    return onlineFirst(event);
  }
  event.respondWith(caches.open(CACHE_NAME)
    .then((cache) =>  {
      return cache.match(event.request).then((response) => {
        // Either respond with the cached resource, or perform a fetch and
        // lazily populate the cache only if the resource was successfully fetched.
        return response || fetch(event.request).then((response) => {
          if (response && Boolean(response.ok)) {
            cache.put(event.request, response.clone());
          }
          return response;
        });
      })
    })
  );
});
self.addEventListener('message', (event) => {
  // SkipWaiting can be used to immediately activate a waiting service worker.
  // This will also require a page refresh triggered by the main worker.
  if (event.data === 'skipWaiting') {
    self.skipWaiting();
    return;
  }
  if (event.data === 'downloadOffline') {
    downloadOffline();
    return;
  }
});
// Download offline will check the RESOURCES for all files not in the cache
// and populate them.
async function downloadOffline() {
  var resources = [];
  var contentCache = await caches.open(CACHE_NAME);
  var currentContent = {};
  for (var request of await contentCache.keys()) {
    var key = request.url.substring(origin.length + 1);
    if (key == "") {
      key = "/";
    }
    currentContent[key] = true;
  }
  for (var resourceKey of Object.keys(RESOURCES)) {
    if (!currentContent[resourceKey]) {
      resources.push(resourceKey);
    }
  }
  return contentCache.addAll(resources);
}
// Attempt to download the resource online before falling back to
// the offline cache.
function onlineFirst(event) {
  return event.respondWith(
    fetch(event.request).then((response) => {
      return caches.open(CACHE_NAME).then((cache) => {
        cache.put(event.request, response.clone());
        return response;
      });
    }).catch((error) => {
      return caches.open(CACHE_NAME).then((cache) => {
        return cache.match(event.request).then((response) => {
          if (response != null) {
            return response;
          }
          throw error;
        });
      });
    })
  );
}
