# Server Components (React 19 / Next.js)

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
