# Design System

**Document**: Shadcn/ui Component Hierarchy  
**Version**: 2.0.0  
**Date**: October 16, 2026

---

## 🎨 Component Library

**Base**: Shadcn/ui + Radix UI + Tailwind CSS

---

## 📦 Components

### Primitives (50+ components)
- Button, Input, Label, Textarea
- Select, Checkbox, Radio, Switch
- Dialog, Sheet, Popover, Tooltip
- Card, Badge, Avatar, Separator
- Table, Tabs, Accordion, Alert
- Toast, Progress, Skeleton

---

## 🎨 Design Tokens

### Colors
```typescript
colors: {
  primary: {
    50: '#f0f9ff',
    500: '#0ea5e9',
    900: '#0c4a6e',
  },
  success: '#10b981',
  warning: '#f59e0b',
  danger: '#ef4444',
}
```

### Typography
- Font: Inter (Google Fonts)
- Scale: 12, 14, 16, 18, 20, 24, 32px
- Weights: 400, 500, 600, 700

### Spacing
- Base: 4px grid
- Scale: 0, 1, 2, 3, 4, 6, 8, 12, 16, 24, 32

---

## 🧩 Custom Components

```
shared/ui/
├── button.tsx
├── input.tsx
├── form.tsx
├── card.tsx
├── dialog.tsx
├── toast.tsx
└── ... (50+ more)
```

---

## 📱 Responsive

```typescript
screens: {
  sm: '640px',
  md: '768px',
  lg: '1024px',
  xl: '1280px',
  '2xl': '1536px',
}
```

---

**Next Document**: 26-SHARED-COMPONENTS.md
