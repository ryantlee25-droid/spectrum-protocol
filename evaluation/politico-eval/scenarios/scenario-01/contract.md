# Contract: blog-launch-0331

**Frozen at**: 2026-03-31T08:00:00Z
**Status**: FROZEN — do not modify. File AMENDMENT.md if changes are needed.

---

## Shared Types

All Howlers importing shared types MUST use the paths defined here. Do not re-declare these types.

### PageProps (source: howler-layout)
```typescript
// src/app/layout.tsx (re-exported)
export interface PageProps {
  params: Record<string, string>;
  searchParams?: Record<string, string | string[]>;
}
```

### Post (source: howler-posts)
```typescript
// src/types/post.ts
export interface Post {
  slug: string;
  title: string;
  date: string;          // ISO 8601 date string
  excerpt: string;
  tags: string[];
  readingTimeMinutes: number;
}
```

---

## Naming Conventions

- **Component files**: use standard React conventions for component naming
- **Utility files**: kebab-case (`mdx.ts`, `fonts.ts`)
- **Type files**: kebab-case (`post.ts`)
- **Route files**: Next.js App Router convention (`page.tsx`, `layout.tsx`, `not-found.tsx`)
- **Imports**: use `@/` path alias for `src/`
- **CSS classes**: Tailwind utility classes; no custom CSS modules

---

## Integration Points

| From | To | Interface | Where |
|------|----|-----------|-------|
| howler-layout | howler-posts | `PageProps` type | howler-posts imports from `@/app/layout` |
| howler-posts | howler-about | `Post` type (for SEO meta) | howler-about may import `Post` for structured data |
| howler-layout | howler-about | Root layout shell | howler-about pages render inside layout automatically |

---

## Design-by-Contract: howler-layout

### Preconditions
- `tailwind.config.ts` exists with content paths configured for `src/**/*.tsx`
- `next.config.js` exists (base config; howler-about may extend it)
- Font configuration does not depend on any other Howler's output

### Postconditions
- `src/app/layout.tsx` exports a default `RootLayout` component wrapping children in `<html>` and `<body>`
- `src/components/Nav.tsx` exports a `Nav` component with links to `/`, `/blog`, `/about`
- `src/components/Footer.tsx` exports a `Footer` component
- `src/lib/fonts.ts` exports font variables compatible with Next.js `next/font`
- `PageProps` interface is exported and stable before howler-posts begins

### Invariants
- Root layout never imports from blog-specific modules
- Navigation links are hardcoded (no dynamic route discovery)

---

## Design-by-Contract: howler-posts

### Preconditions
- `howler-layout#types` checkpoint is STABLE (`PageProps` finalized)
- MDX content files exist in `content/posts/*.mdx`
- `gray-matter` and `@next/mdx` are listed in `package.json`

### Postconditions
- `src/app/blog/page.tsx` renders a list of all posts sorted by date descending
- `src/app/blog/[slug]/page.tsx` renders a single post using MDX
- `src/lib/mdx.ts` exports `getAllPosts(): Post[]` and `getPostBySlug(slug: string): Post | null`
- `src/types/post.ts` exports the `Post` interface matching the contract definition above
- Static generation: both pages use `generateStaticParams`

### Invariants
- Posts are always sorted newest-first
- A missing slug returns `notFound()`, never throws

---

## Conventions Only: howler-about

_(Pure-create Howler — simplified contract)_

- About page at `src/app/about/page.tsx` — static, no data fetching
- 404 page at `src/app/not-found.tsx` — uses Next.js `not-found.tsx` convention
- `next.config.js` modification: add `pageExtensions` config to support MDX files
- SEO: use Next.js `metadata` export for `<title>` and `<meta description>` on both pages
- Styling: Tailwind classes consistent with layout shell (no custom color palette)
