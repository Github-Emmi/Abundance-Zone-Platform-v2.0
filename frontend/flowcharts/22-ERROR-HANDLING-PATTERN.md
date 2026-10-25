# Error Handling Pattern

**Document**: Global Error Boundaries  
**Version**: 2.0.0  
**Date**: October 16, 2026

---

## 🎯 Error Types

1. **Component Errors** - React Error Boundary
2. **API Errors** - Axios interceptors
3. **Form Validation Errors** - Zod
4. **Network Errors** - Offline detection

---

## 🚨 Error Boundary

```typescript
class ErrorBoundary extends React.Component {
  state = { hasError: false, error: null };
  
  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }
  
  componentDidCatch(error, errorInfo) {
    console.error('Error caught:', error, errorInfo);
    // Send to monitoring service (Sentry)
  }
  
  render() {
    if (this.state.hasError) {
      return <ErrorFallback error={this.state.error} />;
    }
    return this.props.children;
  }
}
```

---

## 📊 Error Display

```typescript
const ErrorFallback = ({ error }) => (
  <div className="flex flex-col items-center justify-center p-8">
    <AlertCircle className="w-16 h-16 text-red-500 mb-4" />
    <h2 className="text-2xl font-bold mb-2">Something went wrong</h2>
    <p className="text-gray-600 mb-4">{error.message}</p>
    <Button onClick={() => window.location.reload()}>
      Reload Page
    </Button>
  </div>
);
```

---

## 🔄 Retry Logic

```typescript
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: (failureCount, error) => {
        if (error.response?.status === 404) return false;
        return failureCount < 3;
      },
      retryDelay: (attemptIndex) => 
        Math.min(1000 * 2 ** attemptIndex, 30000),
    },
  },
});
```

---

**Next Document**: 23-CACHING-STRATEGY.md
