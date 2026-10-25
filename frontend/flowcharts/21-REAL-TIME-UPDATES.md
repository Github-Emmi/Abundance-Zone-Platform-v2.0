# Real-Time Updates

**Document**: WebSocket + SSE Integration  
**Version**: 2.0.0  
**Date**: October 16, 2026

---

## 🎯 Strategies

1. **Server-Sent Events (SSE)** - One-way server push
2. **Polling** - Periodic refetch
3. **TanStack Query Invalidation** - On demand

---

## 📡 SSE Implementation

```typescript
useEffect(() => {
  const eventSource = new EventSource(
    \`\${API_URL}/events/stream?token=\${token}\`
  );
  
  eventSource.addEventListener('youth-created', (event) => {
    const youth = JSON.parse(event.data);
    queryClient.setQueryData(['youths'], (old) => [...old, youth]);
    toast.success(\`New youth registered: \${youth.fullname}\`);
  });
  
  eventSource.addEventListener('attendance-recorded', (event) => {
    queryClient.invalidateQueries({ queryKey: ['attendance'] });
  });
  
  return () => eventSource.close();
}, []);
```

---

## 🔄 Polling Strategy

```typescript
// Poll every 30 seconds
useQuery({
  queryKey: ['notifications'],
  queryFn: notificationsApi.getRecent,
  refetchInterval: 30000,
  refetchIntervalInBackground: false,
});
```

---

## ⚡ Optimistic Updates

```typescript
const { mutate } = useMutation({
  mutationFn: youthsApi.update,
  onMutate: async (updatedYouth) => {
    await queryClient.cancelQueries({ queryKey: ['youths'] });
    const previous = queryClient.getQueryData(['youths']);
    
    queryClient.setQueryData(['youths'], (old) =>
      old.map((y) => y.id === updatedYouth.id ? updatedYouth : y)
    );
    
    return { previous };
  },
  onError: (err, variables, context) => {
    queryClient.setQueryData(['youths'], context.previous);
  },
});
```

---

**Next Document**: 22-ERROR-HANDLING-PATTERN.md
