# Layout Patterns

**Document**: Dashboard Layouts, Modals, Drawers  
**Version**: 2.0.0  
**Date**: October 16, 2026

---

## 🏗️ Dashboard Layout

```
┌─────────────────────────────────────┐
│ Header (sticky)                     │
├──────────┬──────────────────────────┤
│ Sidebar  │ Main Content             │
│ (sticky) │ (scrollable)             │
│          │                          │
│          │                          │
└──────────┴──────────────────────────┘
```

---

## 📐 Layout Implementation

```typescript
const DashboardLayout = ({ children }) => (
  <div className="flex h-screen">
    <Sidebar />
    <div className="flex-1 flex flex-col">
      <Header />
      <main className="flex-1 overflow-auto p-6">
        {children}
      </main>
    </div>
  </div>
);
```

---

## 🪟 Modal Patterns

### 1. Dialog (Centered)
```typescript
<Dialog open={isOpen} onOpenChange={setIsOpen}>
  <DialogContent>
    <DialogHeader>
      <DialogTitle>Edit Youth</DialogTitle>
    </DialogHeader>
    <YouthForm />
  </DialogContent>
</Dialog>
```

### 2. Sheet (Slide-in)
```typescript
<Sheet open={isOpen} onOpenChange={setIsOpen}>
  <SheetContent side="right">
    <SheetHeader>
      <SheetTitle>Notifications</SheetTitle>
    </SheetHeader>
    <NotificationList />
  </SheetContent>
</Sheet>
```

---

## 📱 Mobile Layout

```typescript
const MobileSidebar = () => (
  <Sheet>
    <SheetTrigger>
      <MenuIcon />
    </SheetTrigger>
    <SheetContent side="left">
      <Sidebar />
    </SheetContent>
  </Sheet>
);
```

---

**Next Document**: 28-BUILD-OPTIMIZATION.md
