---
id: appearance_system
lang: en
category: references
type: reference
status: full
tags: [appearance, design-system, tokens, accessibility, ui, wcag]
---

# Appearance system — design guidance for a marketing surface

A token-driven, implementation-ready visual language. This document contains appearance
guidance only: tokens, components, state rules and acceptance criteria. It names no brand,
product, audience or funnel. Everything here applies to a content surface that ships
static, readable, accessible pages.

## 1. Design intent

One sentence: **a structured, tokenized, content-first interface — high contrast, tight
scale, no decorative exceptions.**

Context and goals:
- Consistency first: one spacing scale, one type scale, one radius ramp, one shadow ramp.
- Accessibility is an acceptance criterion, not a nice-to-have: keyboard-first
  interactions, visible focus, measured contrast, tested in implementation.
- Fast, predictable delivery: every color, size, radius and shadow referenced by a
  component must come from a named token, never from a raw value typed inline.
- Content over canvas: this system decorates the reading experience; it never competes
  with it.
- Non-negotiables are written with **must**. Recommendations are written with **should**.

## 2. Foundations and semantic tokens

Spacing ramp — use only these values:

| token | value | usage |
|---|---|---|
| `space.1` | 2px | hairline gaps, icon insets |
| `space.2` | 3px | compact inline gaps |
| `space.3` | 4px | tight gaps inside controls |
| `space.4` | 6px | control inner padding (small) |
| `space.5` | 8px | control inner padding (default), badge gaps |
| `space.6` | 10px | card inner padding |
| `space.7` | 11px | list row padding |
| `space.8` | 12px | section padding, table cell padding |

Radius ramp:

| token | value | usage |
|---|---|---|
| `radius.xs` | 3px | code chips, micro tags |
| `radius.sm` | 4px | small inputs, small buttons |
| `radius.md` | 6px | buttons, inputs, default controls |
| `radius.lg` | 7px | menu rows, cards |
| `radius.xl` | 8px | panels, dialogs |
| `radius.2xl` | 10px | large panels, hero containers |
| `radius.step7` | 19px | pill badges, circular affordances |
| `radius.step8` | 21px | avatar crops |

Shadows — never hand-author a box-shadow inside a component:

| token | value | usage |
|---|---|---|
| `shadow.1` | `rgb(231, 229, 228) 0 0 0 1px inset` | resting border on raised surface |
| `shadow.2` | `rgba(6, 60, 46, 0.06) 0 0 0 1px, rgba(6, 60, 46, 0.04) 0 2px 4px 0, rgba(6, 60, 46, 0.35) 0 20px 40px -16px` | dropdowns, raised panels |

Color tokens (semver-free names; themes remap them, components never change):

| token | value | usage |
|---|---|---|
| `color.text.primary` | `#1c1917` | body and headings on light surfaces |
| `color.text.secondary` | `#78716c` | muted copy, captions, meta rows |
| `color.text.tertiary` | `#57534e` | ghost links, footer copy |
| `color.text.inverse` | `#44403c` | copy on raised mint surfaces |
| `color.surface.base` | `#000000` | high-contrast dark scheme base |
| `color.surface.muted` | `#ffffff` | page background, light scheme |
| `color.surface.raised` | `#e4f6f2` | mint accents, active rows, chips |
| `color.surface.strong` | `#f6faf8` | alternate section background |
| `color.line` | `rgb(231, 229, 228)` | hairline rules, inset borders |
| `color.accent` | `#10796b` | interactive accent on light surfaces (passes AA on white) |

Typography:

| token | value |
|---|---|
| `font.family.primary` | Inter, Inter Fallback, system-ui, sans-serif |
| `font.family.stack` | `Inter, Inter Fallback, Inter, system-ui, sans-serif` |
| `font.size.base` | 14px |
| `font.weight.base` | 400 |
| `font.lineHeight.base` | 20px |

Type scale:

| token | value | usage |
|---|---|---|
| `font.size.xs` | 10px | micro labels, licenses |
| `font.size.sm` | 11px | badge text |
| `font.size.md` | 12px | captions, kbd |
| `font.size.lg` | 13px | table cells, list rows |
| `font.size.xl` | 14px | body copy |
| `font.size.2xl` | 15px | lead paragraphs |
| `font.size.3xl` | 16px | section headings |
| `font.size.4xl` | 17px | page subheading |

## 3. Component rules

Every interactive component **must** define all states: default, hover, focus-visible,
active, disabled, loading, error. States are semantic; the visuals always trace back to
tokens.

**Button** — anatomy: label + optional leading icon. Variants: primary (accent fill),
secondary (muted surface + hairline, `shadow.1`), ghost (transparent), destructive (error
text/fill). Keyboard: Enter and Space activate; focus-visible shows a 3px outline at
≥ 2px offset (see §4). Touch target ≥ 44×44px on small screens; ≥ 32px is not enough for
marketing surfaces. Loading state replaces the label with a spinner and disables the
button (`aria-disabled="true"`, `aria-busy="true"`) — it must not disappear (layout
shift). Long labels truncate with ellipsis, never wrap mid-word.

**Link** — default: `color.text.primary` with underline on hover only; external links show
an arrow icon and carry `rel="noopener noreferrer"`. Inline links inside body copy **must**
keep `color.text.inverse` on mint-raised surfaces — never white on mint.

**Badge / chip** — `radius.step7`, `font.size.sm`, padding `space.2 space.5`. Never a
drop shadow; chips nest zero other interactives.

**Card** — `radius.xl`, padding `space.6`. Raised on `color.surface.strong` with
`shadow.1`; no free-form nested borders. Hover: border thickens to `shadow.2`; no
translate-Y motion unless `prefers-reduced-motion: no-preference`.

**Table** — cells `font.size.lg`, header `font.size.md`, row divider `color.line`;
overflow: wrap in `.table-scroll` (`overflow-x: auto`); never let a table widen the page.

**Input / search field** — `radius.md`, `space.4 space.5`, 14px text. Focus-visible =
3px outline + halo; error state = `color.text.tertiary` caption plus 1px `color.line`
and an `aria-invalid="true"` marker; helper text is programmatically associated.

**Navigation** — the header nav is a single row, horizontally scrollable below 640px;
the footer is 4 columns on ≥ 900px, collapses to stacked blocks below that. Каждый
pункт текущей страницы carries `aria-current="page"`.

**Overflow and empty states** — every list must specify: (a) empty state with a single
sentence and one action, (b) long-content handling (truncation or horizontal scroll),
(c) the maximum number of rendered rows before a “show more” control.

## 4. Accessibility requirements (testable)

Target: **WCAG 2.2 AA**, verified with axe on the built artifact, not on the mock.

1. Text on any surface must meet **≥ 4.5:1** (or ≥ 3:1 for ≥ 18pt/bold ≥ 14.5pt).
   Acceptance: axe `color-contrast` reports 0 violations on every route.
2. Focus-visible must be a ≥ **3:1** outline against the adjacent surface, never `none`,
   and never removed on `mousedown`.
   Acceptance: `:focus-visible` computed outline-width ≥ 3px and contrast ≥ 3:1.
3. Keyboard-only access: every interactive element reachable and operable by Tab /
   Shift+Tab / Enter / Space / Esc — including the mobile menu and the search dialog.
   Acceptance: open menu and search dialog via keyboard, close with Esc, restore focus
   to the trigger.
4. Skip link appears on first Tab and jumps to `#main`.
   Acceptance: first tabbable element is the skip link; activating it moves focus to
   `main`.
5. Touch targets ≥ 44×44px on viewports ≤ 640px.
   Acceptance: Playwright measurement on 390px width.
6. Motion respects `prefers-reduced-motion: reduce` (animations and smooth scrolling are
   disabled).
7. Semantic landmarks: one `<h1>` per page; `<nav aria-label="…">` names; `alt` text on
   all informative images.

## 5. Content and tone

Concise, confident, specific. Prefer a number over an adjective. Prefer a verb over a
noun. Never invent claims, figures or quotations. When something is unverified, say so
inline instead of hedging the whole site.

Examples (good → bad):
- “222 articles, two languages complete.” → “Totally amazing comprehensive multilingual
  library.”
- “Blender 5.2.1 removes `Mesh.use_auto_smooth`.” → “Some blender API details may differ.”
- “Shadow rules are derived from tokens.” → “Shadows look cool.”

## 6. Anti-patterns (prohibited)

- Raw hex or px values inside components.
- One-off spacing/type exceptions (“just this time”).
- Low-contrast secondary text (`color.text.secondary` on `#ffffff` below 4.5:1).
- Hidden or removed focus rings.
- Ambiguous labels (“Click here”, “More”).
- Whitespace collapsed by removing margin instead of using tokens.
- `nofollow` on editorial outbound links to authors' own documentation.
- Component states missing (no disabled/loading/error styling).
- Inline `onclick` handlers on a page whose CSP does not allow inline scripts.
- Visual flourishes without a semantic token (“shadow.2-ish, but lower”).

## 7. Migration notes

- Replace any raw palette with tokens from §2 in the same commit as any visual change.
- Dark scheme is allowed to remap the same token names; it must not introduce new tokens.
- Font stack changes go through `font.family.primary` only.
- Shadows are never edited per-component; if a panel needs a different elevation, add
  a new named shadow token to §2 and migrate all usages, then update this file.

## 8. QA checklist

- [ ] Every color used resolves to a named token; 0 raw hex outside `:root`.
- [ ] `npm run all` is green after the change.
- [ ] axe/Playwright pass on light and dark schemes, mobile and desktop.
- [ ] Contrast measured on the built pages (not in the editor preview).
- [ ] `prefers-reduced-motion` leaves nothing jumping or looping.
- [ ] Keyboard: Tab order matches visual order; focus ring visible everywhere.
- [ ] Search dialog opens, Esc closes, focus returns to the trigger.
- [ ] 390px viewport: no horizontal overflow; menu tap targets ≥ 44px.
- [ ] One `<h1>` per page; all landmarks labelled.
- [ ] Lighthouse a11y ≥ 95 and best practices ≥ 95 on the article template.
