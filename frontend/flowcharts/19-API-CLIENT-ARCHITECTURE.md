# API Client Architecture

**Document**: Axios Configuration, Interceptors  
**Version**: 2.0.0  
**Date**: October 16, 2026

---

## 🎯 Features

1. **Axios Instance Configuration**
2. **Request Interceptors** (Auth, Logging)
3. **Response Interceptors** (Error Handling, Transform)
4. **Automatic Token Refresh**
5. **Request Cancellation**

---

## 📁 File Structure

```
shared/api/
├── client.ts                # Axios instance
├── interceptors/
│   ├── auth-interceptor.ts
│   ├── error-interceptor.ts
│   └── logging-interceptor.ts
└── types.ts                 # API types
```

---

## ⚙️ Client Configuration

```typescript
// shared/api/client.ts
import axios from 'axios';

export const apiClient = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add interceptors
apiClient.interceptors.request.use(authInterceptor);
apiClient.interceptors.response.use(
  (response) => response,
  errorInterceptor
);
```

---

## 🔐 Auth Interceptor

```typescript
const authInterceptor = (config) => {
  const token = useAuthStore.getState().accessToken;
  if (token) {
    config.headers.Authorization = \`Bearer \${token}\`;
  }
  return config;
};
```

---

## 🔄 Auto Refresh

```typescript
const errorInterceptor = async (error) => {
  const originalRequest = error.config;
  
  if (error.response?.status === 401 && !originalRequest._retry) {
    originalRequest._retry = true;
    
    try {
      await useAuthStore.getState().refreshAccessToken();
      return apiClient(originalRequest);
    } catch {
      useAuthStore.getState().logout();
      router.push('/login');
    }
  }
  
  return Promise.reject(error);
};
```

---

## 📊 Request Types

```typescript
interface ApiResponse<T> {
  success: boolean;
  data: T;
  message?: string;
}

interface PaginatedResponse<T> {
  data: T[];
  total: number;
  page: number;
  pageSize: number;
}
```

---

**Next Document**: 20-FORM-HANDLING-PATTERN.md
