# Offline Support

**Document**: PWA + Service Workers  
**Version**: 2.0.0  
**Date**: October 16, 2026

---

## 🎯 Features

1. **PWA Configuration**
2. **Service Worker** for offline caching
3. **Background Sync**
4. **Offline Indicator**
5. **Queue Failed Requests**

---

## 📁 PWA Setup

```typescript
// next.config.js
const withPWA = require('next-pwa')({
  dest: 'public',
  register: true,
  skipWaiting: true,
});

module.exports = withPWA({
  // Next.js config
});
```

---

## 🔄 Service Worker

```javascript
// public/sw.js
self.addEventListener('fetch', (event) => {
  event.respondWith(
    caches.match(event.request).then((response) => {
      return response || fetch(event.request);
    })
  );
});
```

---

## 📡 Offline Detection

```typescript
const useOnlineStatus = () => {
  const [isOnline, setIsOnline] = useState(navigator.onLine);
  
  useEffect(() => {
    const handleOnline = () => setIsOnline(true);
    const handleOffline = () => setIsOnline(false);
    
    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);
    
    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
    };
  }, []);
  
  return isOnline;
};
```

---

## 💾 Failed Request Queue

```typescript
const queueRequest = (request) => {
  const queue = JSON.parse(localStorage.getItem('requestQueue') || '[]');
  queue.push(request);
  localStorage.setItem('requestQueue', JSON.stringify(queue));
};

const processQueue = async () => {
  const queue = JSON.parse(localStorage.getItem('requestQueue') || '[]');
  
  for (const request of queue) {
    try {
      await apiClient.request(request);
    } catch (error) {
      console.error('Failed to process queued request:', error);
    }
  }
  
  localStorage.removeItem('requestQueue');
};
```

---

**Next Document**: 25-DESIGN-SYSTEM.md
