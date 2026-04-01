# Manifest: blog-launch-0331

**Rain ID**: blog-launch-0331
**Mode**: full
**Base Branch**: main
**Base Commit**: f4e2a1b

## Task List

| Howler | Scope | Effort | Serial Risk |
|--------|-------|--------|-------------|
| howler-layout | Build root layout, global navigation, footer, and shared page shell for the Next.js blog | S | no |
| howler-posts | Implement blog post list page, individual post page, MDX rendering, and post metadata | M | no |
| howler-about | Create About and 404 error pages with custom styling and site-wide SEO meta tags | S | no |

## File Ownership Matrix

| File | Howler | Action |
|------|--------|--------|
| `src/app/layout.tsx` | howler-layout | CREATES |
| `src/components/Nav.tsx` | howler-layout | CREATES |
| `src/components/Footer.tsx` | howler-layout | CREATES |
| `src/lib/fonts.ts` | howler-layout | CREATES |
| `src/app/blog/page.tsx` | howler-posts | CREATES |
| `src/app/blog/[slug]/page.tsx` | howler-posts | CREATES |
| `src/lib/mdx.ts` | howler-posts | CREATES |
| `src/types/post.ts` | howler-posts | CREATES |
| `src/app/about/page.tsx` | howler-about | CREATES |
| `src/app/not-found.tsx` | howler-about | CREATES |
| `next.config.js` | howler-about | MODIFIES |

**CONFLICTS**: none (verified — no file appears in more than one Howler's ownership)

## Dependency Graph (DAG)

```yaml
- id: howler-layout
  deps: []
  branch: spectrum/blog-launch-0331/howler-layout
  base_branch: main
  base_commit: f4e2a1b

- id: howler-posts
  deps: [howler-layout#types]
  branch: spectrum/blog-launch-0331/howler-posts
  base_branch: main
  base_commit: f4e2a1b

- id: howler-about
  deps: []
  branch: spectrum/blog-launch-0331/howler-about
  base_branch: main
  base_commit: f4e2a1b
```

## Decomposition Rationale

I chose 3 Howlers because the layout shell, content pages, and auxiliary pages have clean file boundaries. howler-posts depends on howler-layout's `PageProps` type for shared page metadata, so it takes a `#types` checkpoint dep. howler-about is independent — it only creates its own pages and modifies next.config.js for the custom 404 redirect behavior. Alternative: 2 Howlers (layout+posts, about) — rejected because the layout/posts boundary is clean and splitting them reduces critical-path risk.

## Politico Review

_Not yet conducted — pre-freeze review scheduled._
