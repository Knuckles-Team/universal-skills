---
name: react-development
description: Type-safe React development with TypeScript covering components, hooks, events, Server Components, and routing. Use when building React applications, React components, typing hooks, handling events, or working with React 18/19 features, Server Components, or routing (TanStack Router, React Router). Triggers include "React component", "TypeScript React", "React hooks", "Server Components", "React 19". Do NOT use for non-React TypeScript or vanilla JavaScript projects.
categories: [Development]
tags: [react, typescript, hooks, components, server-components, frontend, react-19]
---

# React Development (TypeScript)

Type-safe React patterns for React 18 and 19. Compile-time guarantees enable confident refactoring.

---

## React 19 Key Changes

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

---

## Component Patterns

### Props — extend native elements

```typescript
type ButtonProps = {
  variant: 'primary' | 'secondary';
} & React.ComponentPropsWithoutRef<'button'>;

function Button({ variant, children, ...props }: ButtonProps) {
  return <button className={variant} {...props}>{children}</button>;
}
```

### Children typing

```typescript
type Props = {
  children: React.ReactNode;             // Anything renderable
  icon: React.ReactElement;              // Single element
  render: (data: T) => React.ReactNode;  // Render prop
};
```

### Discriminated unions for variant props

```typescript
type ButtonProps =
  | { variant: 'link'; href: string }
  | { variant: 'button'; onClick: () => void };

function Button(props: ButtonProps) {
  if (props.variant === 'link') return <a href={props.href}>Link</a>;
  return <button onClick={props.onClick}>Button</button>;
}
```

### Generic components

```typescript
type Column<T> = {
  key: keyof T;
  header: string;
  render?: (value: T[keyof T], item: T) => React.ReactNode;
};

type TableProps<T> = {
  data: T[];
  columns: Column<T>[];
  keyExtractor: (item: T) => string | number;
};

function Table<T>({ data, columns, keyExtractor }: TableProps<T>) {
  return (
    <table>
      <thead>
        <tr>{columns.map(col => <th key={String(col.key)}>{col.header}</th>)}</tr>
      </thead>
      <tbody>
        {data.map(item => (
          <tr key={keyExtractor(item)}>
            {columns.map(col => (
              <td key={String(col.key)}>
                {col.render ? col.render(item[col.key], item) : String(item[col.key])}
              </td>
            ))}
          </tr>
        ))}
      </tbody>
    </table>
  );
}
```

---

## Hooks Typing

### useState — explicit for unions and null

```typescript
const [user, setUser] = useState<User | null>(null);
const [status, setStatus] = useState<'idle' | 'loading' | 'error'>('idle');
```

### useRef — null for DOM, value for mutable

```typescript
const inputRef = useRef<HTMLInputElement>(null);  // DOM: use ?. to access
const countRef = useRef<number>(0);               // Mutable: access directly
```

### useReducer — discriminated unions for actions

```typescript
type Action =
  | { type: 'increment' }
  | { type: 'set'; payload: number };

function reducer(state: State, action: Action): State {
  switch (action.type) {
    case 'set': return { ...state, count: action.payload };
    default: return state;
  }
}
```

### Custom hooks — tuple returns with `as const`

```typescript
function useToggle(initial = false) {
  const [value, setValue] = useState(initial);
  const toggle = () => setValue(v => !v);
  return [value, toggle] as const;
}
```

### useContext — null guard pattern

```typescript
const UserContext = createContext<User | null>(null);

function useUser() {
  const user = useContext(UserContext);
  if (!user) throw new Error('useUser must be used within UserProvider');
  return user;
}
```

---

## Event Handlers

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

---

## Server Components (React 19 / Next.js)

Server Components run on the server and can be async:

```typescript
// Server Component — async data fetching
export default async function UserPage({ params }: { params: { id: string } }) {
  const user = await fetchUser(params.id);
  return <div>{user.name}</div>;
}

// Server Action — mutations with 'use server'
'use server';
export async function updateUser(userId: string, formData: FormData) {
  await db.user.update({ where: { id: userId }, data: { ... } });
  revalidatePath(`/users/${userId}`);
}

// Client Component consuming a Server Action
'use client';
function UserForm({ userId }: { userId: string }) {
  const [state, formAction, isPending] = useActionState(
    (prev, formData) => updateUser(userId, formData), {}
  );
  return <form action={formAction}>...</form>;
}

// Server: pass promise without await
async function Page() {
  const userPromise = fetchUser('123');
  return <UserProfile userPromise={userPromise} />;
}

// Client: unwrap with use()
'use client';
function UserProfile({ userPromise }: { userPromise: Promise<User> }) {
  const user = use(userPromise); // Suspends until resolved
  return <div>{user.name}</div>;
}
```

---

## Routing

### TanStack Router — compile-time type safety

```typescript
import { createRoute } from '@tanstack/react-router';
import { z } from 'zod';

const userRoute = createRoute({
  path: '/users/$userId',
  component: UserPage,
  loader: async ({ params }) => ({ user: await fetchUser(params.userId) }),
  validateSearch: z.object({
    tab: z.enum(['profile', 'settings']).optional(),
    page: z.number().int().positive().default(1),
  }),
});

function UserPage() {
  const { user } = useLoaderData({ from: userRoute.id });
  const { tab, page } = useSearch({ from: userRoute.id });
  const { userId } = useParams({ from: userRoute.id });
}
```

### React Router v7 — automatic type generation

```typescript
import type { Route } from "./+types/user";

export async function loader({ params }: Route.LoaderArgs) {
  return { user: await fetchUser(params.userId) };
}

export default function UserPage({ loaderData }: Route.ComponentProps) {
  const { user } = loaderData;  // Typed from loader
  return <h1>{user.name}</h1>;
}
```

---

## Rules

**ALWAYS:**
- Use specific event types (MouseEvent, ChangeEvent, KeyboardEvent, etc.)
- Explicit `useState` generics for unions and null
- `ComponentPropsWithoutRef` for native element extension
- Discriminated unions for variant props
- `as const` for tuple returns from custom hooks
- `ref` as a regular prop in React 19 (no `forwardRef`)
- `useActionState` for form actions

**NEVER:**
- `any` for event handlers — always provide the specific element type
- `JSX.Element` for children — use `React.ReactNode`
- `forwardRef` in React 19+
- `useFormState` (deprecated, replaced by `useActionState`)
- Forget null handling for DOM refs (use `?.`)
- Mix Server and Client component boundaries in the same file
- `await` promises before passing to `use()`

---

## References

- [references/hooks.md](references/hooks.md) — useState, useRef, useReducer, useContext, custom hooks advanced patterns
- [references/event-handlers.md](references/event-handlers.md) — All event types: focus, drag, clipboard, touch, wheel
- [references/react-19-patterns.md](references/react-19-patterns.md) — useActionState, use(), useOptimistic, useTransition, migration checklist
- [examples/generic-components.md](examples/generic-components.md) — Table, Select, List, Modal generic patterns
- [examples/server-components.md](examples/server-components.md) — Async components, Server Actions, streaming, error boundaries
- [references/tanstack-router.md](references/tanstack-router.md) — TanStack Router typed routes, search params, navigation
- [references/react-router.md](references/react-router.md) — React Router v7 loaders, actions, type generation, forms
