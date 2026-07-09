# React 19 Key Changes

React 19 introduces breaking changes. Key patterns:

### ref as prop (forwardRef deprecated)

```typescript
// React 19 — ref as regular prop
type ButtonProps = {
  ref?: React.Ref<HTMLButtonElement>;
} & React.ComponentPropsWithoutRef<'button'>;

function Button({ ref, children, ...props }: ButtonProps) {
  return <button ref={ref} {...props}>{children}</button>;
}
```

### useActionState (replaces useFormState)

```typescript
import { useActionState } from 'react';

function Form() {
  const [state, formAction, isPending] = useActionState(submitAction, {});
  return <form action={formAction}>...</form>;
}
```

### use() — unwraps promises and context

```typescript
function UserProfile({ userPromise }: { userPromise: Promise<User> }) {
  const user = use(userPromise); // Suspends until resolved
  return <div>{user.name}</div>;
}
```
