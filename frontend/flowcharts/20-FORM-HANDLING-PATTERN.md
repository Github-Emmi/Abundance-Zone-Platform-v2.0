# Form Handling Pattern

**Document**: React Hook Form + Zod Validation  
**Version**: 2.0.0  
**Date**: October 16, 2026

---

## 🎯 Stack

- **React Hook Form**: Form state management
- **Zod**: Schema validation
- **@hookform/resolvers**: Zod integration

---

## 📁 Standard Pattern

```typescript
// 1. Define Zod schema
const youthSchema = z.object({
  fullname: z.string().min(2).max(150),
  email: z.string().email(),
  phoneNumber: z.string().regex(/^[0-9]{10}$/),
  dateOfBirth: z.date(),
  branchId: z.string().uuid(),
});

type YouthFormData = z.infer<typeof youthSchema>;

// 2. Create form component
const YouthForm = () => {
  const { register, handleSubmit, formState: { errors } } = 
    useForm<YouthFormData>({
      resolver: zodResolver(youthSchema),
    });
  
  const { mutate: createYouth } = useCreateYouth();
  
  const onSubmit = (data: YouthFormData) => {
    createYouth(data);
  };
  
  return (
    <form onSubmit={handleSubmit(onSubmit)}>
      <Input {...register('fullname')} error={errors.fullname} />
      <Input {...register('email')} error={errors.email} />
      <Button type="submit">Create Youth</Button>
    </form>
  );
};
```

---

## ✅ Validation Features

1. **Real-time validation**
2. **Custom error messages**
3. **Async validation**
4. **Conditional fields**
5. **Array fields**

---

## 🎨 Error Display

```typescript
const InputField = ({ label, error, ...props }) => (
  <div>
    <Label>{label}</Label>
    <Input {...props} className={error ? 'border-red-500' : ''} />
    {error && <p className="text-red-500 text-sm">{error.message}</p>}
  </div>
);
```

---

**Next Document**: 21-REAL-TIME-UPDATES.md
