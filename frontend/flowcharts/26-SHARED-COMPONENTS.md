# Shared Components

**Document**: Reusable Business Components  
**Version**: 2.0.0  
**Date**: October 16, 2026

---

## 📦 Component Categories

1. **Layout Components**
2. **Data Display Components**
3. **Form Components**
4. **Feedback Components**

---

## 🏗️ Layout Components

```
shared/components/layout/
├── Sidebar.tsx
├── Header.tsx
├── Footer.tsx
├── DashboardLayout.tsx
└── AuthLayout.tsx
```

---

## 📊 Data Display

```
shared/components/data-display/
├── DataTable.tsx         # Reusable table with sorting/filtering
├── StatCard.tsx          # Dashboard stat cards
├── EmptyState.tsx        # No data state
├── ErrorDisplay.tsx      # Error state
└── LoadingSkeleton.tsx   # Loading state
```

---

## 📝 Form Components

```
shared/components/forms/
├── FormField.tsx         # Field wrapper with error
├── DatePicker.tsx        # Date selection
├── FileUpload.tsx        # File upload with preview
├── SearchInput.tsx       # Search with debounce
└── MultiSelect.tsx       # Multi-select dropdown
```

---

## 🔔 Feedback Components

```
shared/components/feedback/
├── Toast.tsx             # Toast notifications
├── ConfirmDialog.tsx     # Confirmation modals
├── LoadingSpinner.tsx    # Loading indicator
└── ProgressBar.tsx       # Progress indicator
```

---

**Next Document**: 27-LAYOUT-PATTERNS.md
