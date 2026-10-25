# Caching Strategy

**Document**: TanStack Query Cache Configuration  
**Version**: 2.0.0  
**Date**: October 16, 2026

---

## 🎯 Cache Levels

1. **Fresh** (0-5 min) - No refetch needed
2. **Stale** (5-10 min) - Background refetch
3. **Expired** (>10 min) - Garbage collected

---

## ⚙️ Configuration

```typescript
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 5 * 60 * 1000,      // 5 minutes
      cacheTime: 10 * 60 * 1000,     // 10 minutes
      refetchOnWindowFocus: true,
      refetchOnReconnect: true,
    },
  },
});
```

---

## 📊 Data-Specific Strategies

| Data Type | Stale Time | Cache Time | Refetch |
|-----------|------------|------------|---------|
| Notifications | 1 min | 2 min | On focus |
| Youths List | 5 min | 10 min | On focus |
| Youth Profile | 10 min | 15 min | On demand |
| Branches | 30 min | 1 hour | Manual |
| Analytics | 2 min | 5 min | Interval |

---

## 🔄 Invalidation Patterns

```typescript
// After mutation
queryClient.invalidateQueries({ queryKey: ['youths'] });

// Multiple related queries
queryClient.invalidateQueries({ queryKey: ['youths'] });
queryClient.invalidateQueries({ queryKey: ['attendance'] });

// Specific query
queryClient.invalidateQueries({ 
  queryKey: ['youth', youthId] 
});
```

---

**Next Document**: 24-OFFLINE-SUPPORT.md
