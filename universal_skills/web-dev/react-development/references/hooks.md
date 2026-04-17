# Hooks Typing

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
