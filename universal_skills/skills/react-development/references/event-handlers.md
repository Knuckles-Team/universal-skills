# Event Handlers

Use specific event types for accurate `target` typing:

```typescript
// Mouse events
function handleClick(e: React.MouseEvent<HTMLButtonElement>) { ... }

// Form submission
function handleSubmit(e: React.FormEvent<HTMLFormElement>) {
  e.preventDefault();
  const formData = new FormData(e.currentTarget);
}

// Input change
function handleChange(e: React.ChangeEvent<HTMLInputElement>) {
  console.log(e.target.value);
}

// Keyboard
function handleKeyDown(e: React.KeyboardEvent<HTMLInputElement>) {
  if (e.key === 'Enter') e.currentTarget.blur();
}
```
