# Contract: component-lib-0331

**Frozen at**: 2026-03-31T11:45:00Z
**Status**: FROZEN — do not modify. File AMENDMENT.md if changes are needed.

---

## Shared Types

All Howlers importing shared types MUST use the paths defined here. Do not re-declare these types.

### ComponentProps (base interface — all components extend this)
```typescript
// src/tokens/index.ts (re-exported alongside tokens)
export interface ComponentProps {
  className?: string;
  style?: React.CSSProperties;
  "data-testid"?: string;
  children?: React.ReactNode;
}
```

### DesignTokens (source: howler-tokens)
```typescript
// src/tokens/index.ts
export interface DesignTokens {
  colors: Record<string, string>;     // e.g., { "blue-500": "#3b82f6" }
  spacing: Record<string, string>;    // e.g., { "4": "1rem" }
  typography: {
    fontFamily: Record<string, string>;
    fontSize: Record<string, string>;
    fontWeight: Record<string, string>;
  };
}
```

---

## Naming Conventions

- **Component files**: PascalCase (`Button.tsx`, `Stack.tsx`)
- **Token files**: camelCase nouns (`colors.ts`, `spacing.ts`, `typography.ts`)
- **Story files**: `{ComponentName}.stories.tsx` in `src/stories/`
- **CSS custom properties**: `--token-{category}-{name}` (e.g., `--token-color-blue-500`)
- **Test IDs**: components accept `data-testid` via `ComponentProps` base interface
- **Exports**: all public components exported from `src/index.ts` (barrel export)

---

## Integration Points

| From | To | Interface | Where |
|------|----|-----------|-------|
| howler-tokens | howler-primitives | CSS custom properties + `DesignTokens` | primitives consume token CSS vars |
| howler-tokens | howler-layout | CSS custom properties (spacing) | layout uses spacing tokens for gap/padding |
| howler-tokens | howler-feedback | CSS custom properties (colors) | feedback uses color tokens for status states |
| howler-primitives | howler-stories | Component exports | stories import from `@/components/primitives` |
| howler-layout | howler-stories | Component exports | stories import from `@/components/layout` |
| howler-feedback | howler-stories | Component exports | stories import from `@/components/feedback` |

---

## Design-by-Contract: howler-tokens

### Preconditions
- Tailwind CSS configured (tokens supplement Tailwind, not replace it)

### Postconditions
- `src/tokens/colors.ts` exports `colors` object matching `DesignTokens["colors"]` shape
- `src/tokens/spacing.ts` exports `spacing` object matching `DesignTokens["spacing"]` shape
- `src/tokens/typography.ts` exports `typography` object matching `DesignTokens["typography"]` shape
- `src/tokens/index.ts` exports `tokens: DesignTokens` (merged), `ComponentProps` interface, and injects CSS custom properties as a side effect when imported in the app root
- All token values are also available as CSS custom properties (`--token-color-*`, `--token-spacing-*`)

### Invariants
- Token values are string literals (no computed values at module load time)
- CSS custom property injection is idempotent (safe to import multiple times)

---

## Design-by-Contract: howler-primitives

### Preconditions
- None (runs parallel to howler-tokens; uses CSS custom properties via class names, not JS imports)

### Postconditions
- `Button.tsx` exports `Button: React.FC<ButtonProps>` where `ButtonProps extends ComponentProps`
- `Input.tsx` exports `Input: React.FC<InputProps>` where `InputProps extends ComponentProps`
- `Checkbox.tsx` exports `Checkbox: React.FC<CheckboxProps>` where `CheckboxProps extends ComponentProps`
- `Radio.tsx` exports `Radio: React.FC<RadioProps>` where `RadioProps extends ComponentProps`
- `Select.tsx` exports `Select: React.FC<SelectProps>` where `SelectProps extends ComponentProps`
- All components pass WCAG 2.1 AA accessibility (aria attributes, keyboard nav, focus visible)

### Invariants
- All `*Props` interfaces extend `ComponentProps` — no component omits `className` or `data-testid`
- No component imports from `src/tokens/` directly (uses CSS custom properties via class names only)

---

## Design-by-Contract: howler-layout

### Preconditions
- None (runs parallel to howler-tokens; uses CSS custom properties via class names)

### Postconditions
- `Stack.tsx` exports `Stack: React.FC<StackProps>` where `StackProps extends ComponentProps`
- `Grid.tsx` exports `Grid: React.FC<GridProps>` where `GridProps extends ComponentProps`
- `Divider.tsx` exports `Divider: React.FC<DividerProps>` where `DividerProps extends ComponentProps`
- `Container.tsx` exports `Container: React.FC<ContainerProps>` where `ContainerProps extends ComponentProps`
- All layout components use CSS custom properties for spacing values

### Invariants
- Layout components are purely structural — no color or typography tokens applied directly
- All `*Props` interfaces extend `ComponentProps`

---

## Design-by-Contract: howler-feedback

### Preconditions
- None (runs parallel to howler-tokens; uses CSS custom properties via class names)

### Postconditions
- `Toast.tsx` exports `Toast: React.FC<ToastProps>` where `ToastProps extends ComponentProps`
- `Alert.tsx` exports `Alert: React.FC<AlertProps>` where `AlertProps extends ComponentProps`
- `Badge.tsx` exports `Badge: React.FC<BadgeProps>` where `BadgeProps extends ComponentProps`
- `Spinner.tsx` exports `Spinner: React.FC<SpinnerProps>` where `SpinnerProps extends ComponentProps`
- All feedback components use `role` and `aria-live` appropriately for screen readers

### Invariants
- All `*Props` interfaces extend `ComponentProps`
- Animation uses CSS transitions (not JS-based) for reduced-motion compatibility

---

## Conventions Only: howler-stories

_(Sequential Howler — simplified contract)_

- Use Storybook 7 with `@storybook/react-vite`
- Each story file exports `default` (meta) and named exports (stories)
- Use `args` + `argTypes` for all controllable props
- Install and configure `@storybook/addon-a11y` for accessibility checks
- Visual regression baseline: run `chromatic` against the stories on first run
- Each component must have at minimum: Default story, Disabled story (where applicable), and a story demonstrating `data-testid` usage
