# Manifest: component-lib-0331

**Rain ID**: component-lib-0331
**Mode**: full
**Base Branch**: main
**Base Commit**: 3a7d2f8

## Task List

| Howler | Scope | Effort | Serial Risk |
|--------|-------|--------|-------------|
| howler-tokens | Define design token system: color palette, spacing scale, typography, and CSS custom properties | S | no |
| howler-primitives | Build primitive components: Button, Input, Checkbox, Radio, Select with full accessibility | L | no |
| howler-layout | Build layout components: Stack, Grid, Divider, Container with responsive breakpoints | M | no |
| howler-feedback | Build feedback components: Toast, Alert, Badge, Spinner with animation support | M | no |
| howler-stories | Write Storybook stories for all components: controls, a11y addon, visual regression baselines | M | yes |

## File Ownership Matrix

| File | Howler | Action |
|------|--------|--------|
| `src/tokens/colors.ts` | howler-tokens | CREATES |
| `src/tokens/spacing.ts` | howler-tokens | CREATES |
| `src/tokens/typography.ts` | howler-tokens | CREATES |
| `src/tokens/index.ts` | howler-tokens | CREATES |
| `src/components/primitives/Button.tsx` | howler-primitives | CREATES |
| `src/components/primitives/Input.tsx` | howler-primitives | CREATES |
| `src/components/primitives/Checkbox.tsx` | howler-primitives | CREATES |
| `src/components/primitives/Radio.tsx` | howler-primitives | CREATES |
| `src/components/primitives/Select.tsx` | howler-primitives | CREATES |
| `src/components/layout/Stack.tsx` | howler-layout | CREATES |
| `src/components/layout/Grid.tsx` | howler-layout | CREATES |
| `src/components/layout/Divider.tsx` | howler-layout | CREATES |
| `src/components/layout/Container.tsx` | howler-layout | CREATES |
| `src/components/feedback/Toast.tsx` | howler-feedback | CREATES |
| `src/components/feedback/Alert.tsx` | howler-feedback | CREATES |
| `src/components/feedback/Badge.tsx` | howler-feedback | CREATES |
| `src/components/feedback/Spinner.tsx` | howler-feedback | CREATES |
| `src/stories/Button.stories.tsx` | howler-stories | CREATES |
| `src/stories/Input.stories.tsx` | howler-stories | CREATES |
| `src/stories/Stack.stories.tsx` | howler-stories | CREATES |
| `src/stories/Toast.stories.tsx` | howler-stories | CREATES |
| `src/stories/Alert.stories.tsx` | howler-stories | CREATES |

**CONFLICTS**: none (verified — no file appears in more than one Howler's ownership)

## Dependency Graph (DAG)

```yaml
- id: howler-tokens
  deps: []
  branch: spectrum/component-lib-0331/howler-tokens
  base_branch: main
  base_commit: 3a7d2f8

- id: howler-primitives
  deps: []
  branch: spectrum/component-lib-0331/howler-primitives
  base_branch: main
  base_commit: 3a7d2f8

- id: howler-layout
  deps: []
  branch: spectrum/component-lib-0331/howler-layout
  base_branch: main
  base_commit: 3a7d2f8

- id: howler-feedback
  deps: []
  branch: spectrum/component-lib-0331/howler-feedback
  base_branch: main
  base_commit: 3a7d2f8

- id: howler-stories
  deps: [howler-tokens, howler-primitives, howler-layout, howler-feedback]
  branch: spectrum/component-lib-0331/howler-stories
  base_branch: main
  base_commit: 3a7d2f8
```

## Decomposition Rationale

I chose 5 Howlers because tokens, primitive components, layout components, feedback components, and stories are clean separation of concerns. All four implementation Howlers are parallel — they create different files with no inter-Howler file modifications. howler-stories is sequential on all four because it imports from each component category and needs the components to exist to write story controls and baselines. Alternative: merging all components into one Howler — rejected because the primitive, layout, and feedback categories are large enough to parallelize meaningfully.

## Politico Review

_Not yet conducted — pre-freeze review scheduled._
