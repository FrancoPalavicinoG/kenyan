# Kenyan — Frontend Design System

> **For AI agents**: This document defines Kenyan's visual language and component rules. Follow these strictly when building or modifying UI. When in doubt, look at what already exists in `src/components/` before inventing something new.

---

## Design Philosophy

Kenyan is built for **one serious athlete** — focused, data-dense, performance-oriented. The aesthetic is a dark sports science dashboard: precise, energetic, and legible at a glance.

**Core principles:**
- **Dark-first.** Athletic apps live at 5am and after night runs. The base is a deep blue-slate, not black.
- **Data-dense but scannable.** Metrics are the content. Surface numbers big. Use typographic hierarchy to guide the eye, not decorative chrome.
- **Color encodes meaning.** Green = optimal / recovery good. Orange = load / intensity / warning. Blue = informational / stable. Red = danger / critical. Never use color decoratively.
- **Glow and gradient for charts only.** Lines with glow, area fills with gradient opacity — only inside chart surfaces, never on cards or text.
- **Minimal borders, maximum contrast.** Cards are defined by background contrast against the page, not by thick borders. A single 1px top-edge highlight replaces drop shadows.

---

## Color System

All colors are CSS custom properties. **Never hardcode hex values in components.**

```css
:root {
  /* Backgrounds — layered depth */
  --color-bg-base: #0D1117;        /* Page — deep blue-slate, not pure black */
  --color-bg-surface: #161B26;     /* Cards, panels — one step lighter */
  --color-bg-elevated: #1E2736;    /* Inputs, hover, nested surfaces */
  --color-bg-overlay: #252F3F;     /* Dropdowns, tooltips */

  /* Top-edge card highlight (replaces shadows) */
  --color-card-highlight: rgba(100, 180, 255, 0.12);

  /* Brand accent — electric lime green */
  --color-brand: #4ADE80;
  --color-brand-dim: #22C55E;
  --color-brand-glow: rgba(74, 222, 128, 0.25);

  /* Secondary accent — athletic orange */
  --color-accent: #FB923C;
  --color-accent-dim: #F97316;
  --color-accent-glow: rgba(251, 146, 60, 0.20);

  /* Text */
  --color-text-primary: #F0F0F0;
  --color-text-secondary: #C9D1E0;
  --color-text-muted: #6B7FA3;
  --color-text-disabled: #3D4B63;
  --color-text-inverse: #0D1117;   /* Text on brand-colored backgrounds */

  /* Borders */
  --color-border: rgba(100, 120, 160, 0.18);
  --color-border-strong: rgba(100, 120, 160, 0.30);

  /* Training Zones — fixed semantic palette */
  --color-zone-1: #60A5FA;   /* Recovery — blue */
  --color-zone-2: #4ADE80;   /* Aerobic base — green */
  --color-zone-3: #FACC15;   /* Tempo — yellow */
  --color-zone-4: #FB923C;   /* Threshold — orange */
  --color-zone-5: #F87171;   /* VO2max — red */

  /* Status */
  --color-status-good: #4ADE80;
  --color-status-moderate: #FACC15;
  --color-status-low: #FB923C;
  --color-status-critical: #F87171;
  --color-status-neutral: #6B7FA3;

  /* Status badge fills */
  --color-status-good-bg: rgba(74, 222, 128, 0.12);
  --color-status-good-border: rgba(74, 222, 128, 0.25);
  --color-status-moderate-bg: rgba(250, 204, 21, 0.12);
  --color-status-moderate-border: rgba(250, 204, 21, 0.25);
  --color-status-low-bg: rgba(251, 146, 60, 0.12);
  --color-status-low-border: rgba(251, 146, 60, 0.25);
  --color-status-critical-bg: rgba(248, 113, 113, 0.12);
  --color-status-critical-border: rgba(248, 113, 113, 0.25);
  --color-info-bg: rgba(96, 165, 250, 0.12);
  --color-info-border: rgba(96, 165, 250, 0.20);
}
```

### Usage rules

```tsx
// CORRECT
<div style={{ background: 'var(--color-bg-surface)', color: 'var(--color-status-good)' }}>

// WRONG — never hardcode
<div style={{ background: '#161B26', color: '#4ADE80' }}>
```

---

## Typography

```css
--text-xs: 10px;          /* axis labels, timestamps */
--text-sm: 11px;          /* card labels, badges, helper text */
--text-base: 13px;        /* card titles, body */
--text-lg: 15px;          /* section headings */
--text-xl: 20px;          /* page title */
--text-metric-sm: 22px;   /* secondary metric numbers */
--text-metric-lg: 28px;   /* primary metric numbers */

/* Weights — only these two */
--font-normal: 400;
--font-medium: 500;
/* Never use 600, 700, or 800 */

/* All metric numbers */
font-variant-numeric: tabular-nums;
letter-spacing: -0.02em;
```

| Role | Size | Weight | Color |
|------|------|--------|-------|
| Page title | `--text-xl` | 500 | `--color-text-primary` |
| Card / section title | `--text-base` | 500 | `--color-text-secondary` |
| Metric label | `--text-sm` | 400 | `--color-text-muted` |
| Primary metric number | `--text-metric-lg` | 500 | semantic status color |
| Unit suffix | `--text-base` | 400 | `--color-text-muted` |
| Helper / hint | `--text-sm` | 400 | `--color-text-muted` |
| Axis / timestamp | `--text-xs` | 400 | `--color-text-disabled` |

---

## Card System

Cards use **background contrast + a single top-edge highlight** instead of drop shadows. This is the defining visual pattern.

```css
.card {
  background: var(--color-bg-surface);
  border: 0.5px solid var(--color-border);
  border-radius: 12px;
  padding: 16px;
  position: relative;
  overflow: hidden;
}

/* Top-edge highlight — NEVER omit this */
.card::before {
  content: '';
  position: absolute;
  top: 0; left: 0; right: 0;
  height: 1px;
  background: linear-gradient(
    90deg,
    transparent,
    var(--color-card-highlight),
    transparent
  );
}
```

```tsx
// CORRECT — card class with ::before highlight
<div className="card"><MetricContent /></div>

// WRONG — inline style, no highlight
<div style={{ background: '#161B26', borderRadius: 12, padding: 16 }}>
```

### Metric card

```tsx
<MetricCard
  label="Training Readiness"
  value={76}
  unit={undefined}
  status="good"        // good | moderate | low | critical | neutral
  delta="+8 vs ayer"
/>

<MetricCard
  label="HRV"
  value={58}
  unit="ms"
  status="good"
/>
```

- Label: `--text-sm`, `--color-text-muted`
- Value: `--text-metric-lg`, weight 500, `tabular-nums`, colored by `--color-status-{status}`
- Unit: `--text-base`, `--color-text-muted`, inline after value
- Delta: `<StatusBadge>` below the number

### Status badge

```tsx
<StatusBadge status="good">Óptimo</StatusBadge>
<StatusBadge status="moderate">Moderado</StatusBadge>
<StatusBadge status="low">Bajo promedio</StatusBadge>
<StatusBadge status="critical">Crítico</StatusBadge>
<StatusBadge status="info">Estable</StatusBadge>
```

```css
.badge {
  display: inline-flex;
  align-items: center;
  font-size: var(--text-sm);
  font-weight: 500;
  padding: 2px 7px;
  border-radius: 20px;
}
.badge-good     { background: var(--color-status-good-bg);     color: var(--color-status-good);     border: 0.5px solid var(--color-status-good-border); }
.badge-moderate { background: var(--color-status-moderate-bg); color: var(--color-status-moderate); border: 0.5px solid var(--color-status-moderate-border); }
.badge-low      { background: var(--color-status-low-bg);      color: var(--color-status-low);      border: 0.5px solid var(--color-status-low-border); }
.badge-critical { background: var(--color-status-critical-bg); color: var(--color-status-critical); border: 0.5px solid var(--color-status-critical-border); }
.badge-info     { background: var(--color-info-bg);            color: #60A5FA;                      border: 0.5px solid var(--color-info-border); }
```

---

## Chart System

All charts use **Recharts**. These conventions are mandatory.

### Base config

```tsx
const chartDefaults = {
  grid: {
    stroke: 'rgba(100, 120, 160, 0.12)',
    strokeDasharray: '3 3',
  },
  axis: {
    tick: { fill: 'var(--color-text-disabled)', fontSize: 10 },
    axisLine: { stroke: 'transparent' },
    tickLine: { stroke: 'transparent' },
  },
  tooltip: {
    contentStyle: {
      background: 'var(--color-bg-overlay)',
      border: '0.5px solid var(--color-border-strong)',
      borderRadius: 8,
      color: 'var(--color-text-primary)',
      fontSize: 12,
    },
  },
};
```

### Line chart with glow (training load, HRV trend, VO2max)

```tsx
<AreaChart data={data}>
  <defs>
    <linearGradient id="ctlGradient" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stopColor="var(--color-brand)" stopOpacity={0.25} />
      <stop offset="100%" stopColor="var(--color-brand)" stopOpacity={0} />
    </linearGradient>
    <linearGradient id="atlGradient" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stopColor="var(--color-accent)" stopOpacity={0.20} />
      <stop offset="100%" stopColor="var(--color-accent)" stopOpacity={0} />
    </linearGradient>
  </defs>
  <CartesianGrid {...chartDefaults.grid} />
  <XAxis dataKey="date" {...chartDefaults.axis} />
  <YAxis {...chartDefaults.axis} />
  <Tooltip {...chartDefaults.tooltip} />
  <Area
    type="monotone"
    dataKey="ctl"
    stroke="var(--color-brand)"
    strokeWidth={2}
    fill="url(#ctlGradient)"
    dot={false}
    activeDot={{ r: 4, fill: 'var(--color-brand)', strokeWidth: 0 }}
  />
  <Area
    type="monotone"
    dataKey="atl"
    stroke="var(--color-accent)"
    strokeWidth={1.5}
    strokeDasharray="4 3"
    fill="url(#atlGradient)"
    dot={false}
  />
</AreaChart>
```

Rules:
- CTL / primary metric: `--color-brand`, solid, `strokeWidth: 2`
- ATL / secondary metric: `--color-accent`, dashed `4 3`, `strokeWidth: 1.5`
- Area fills: always `linearGradient` from `0.25` → `0` opacity
- `dot={false}` — no dots along the line, only `activeDot` on hover

### Bar chart with gradient (weekly volume, session intensity)

```tsx
<BarChart data={data}>
  <defs>
    <linearGradient id="barGradient" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stopColor="var(--color-brand)" stopOpacity={0.9} />
      <stop offset="100%" stopColor="var(--color-brand-dim)" stopOpacity={0.4} />
    </linearGradient>
  </defs>
  <Bar
    dataKey="minutes"
    fill="url(#barGradient)"
    radius={[4, 4, 0, 0]}
    maxBarSize={32}
  />
</BarChart>
```

Rules:
- Always gradient fill top → bottom
- Rounded top only: `radius={[4, 4, 0, 0]}`
- Max bar width: `32px`

### Zone distribution (horizontal bars)

Custom HTML component, not Recharts. Used for training zone intensity breakdown.

```tsx
<ZoneBar zone={2} label="Zona 2" percentage={62} />
```

```css
.zone-row { display: flex; align-items: center; gap: 8px; margin-bottom: 8px; }
.zone-dot { width: 8px; height: 8px; border-radius: 50%; flex-shrink: 0; }
.zone-bar-bg { flex: 1; height: 6px; background: var(--color-bg-elevated); border-radius: 3px; overflow: hidden; }
.zone-bar { height: 100%; border-radius: 3px; }
/* Zone bar fill: linear-gradient(90deg, var(--color-zone-N), dim version) */
```

### Chart container pattern

Always wrap in `.card` with standard header:

```tsx
<div className="card">
  <div className="card-header">  {/* flex, justify-between, align-center */}
    <span className="card-title">Carga de entrenamiento — 6 semanas</span>
    <StatusBadge status="info">CTL 68</StatusBadge>
  </div>
  <div style={{ height: 160 }}>
    <ResponsiveContainer width="100%" height="100%">
      {/* chart here */}
    </ResponsiveContainer>
  </div>
</div>
```

---

## Layout System

### Page shell

```css
.page-shell {
  display: grid;
  grid-template-columns: 220px 1fr;
  min-height: 100vh;
  background: var(--color-bg-base);
  color: var(--color-text-primary);
}

.page-content {
  padding: 28px 32px;
  overflow-y: auto;
}
```

### Sidebar

```css
.sidebar {
  background: var(--color-bg-surface);
  border-right: 0.5px solid var(--color-border);
  padding: 20px 12px;
}

/* Active nav item — pill highlight */
.nav-item-active {
  background: var(--color-bg-elevated);
  border-radius: 8px;
  color: var(--color-text-primary);
  font-weight: 500;
}

.nav-item {
  color: var(--color-text-muted);
  border-radius: 8px;
  padding: 8px 12px;
  font-size: var(--text-base);
}

.nav-item:hover {
  background: var(--color-bg-elevated);
  color: var(--color-text-secondary);
}
```

### Metrics grid (dashboard top row)

```css
.metrics-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 12px;
  margin-bottom: 16px;
}

@media (max-width: 1024px) {
  .metrics-grid { grid-template-columns: repeat(2, 1fr); }
}
```

### Charts grid

```css
.charts-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
}
```

---

## Interaction States

### Loading — skeleton shimmer (never spinners inside cards)

```css
.skeleton {
  background: linear-gradient(
    90deg,
    var(--color-bg-elevated) 25%,
    var(--color-bg-overlay) 50%,
    var(--color-bg-elevated) 75%
  );
  background-size: 200% 100%;
  animation: shimmer 1.5s infinite;
  border-radius: 6px;
}
@keyframes shimmer {
  0%   { background-position: 200% 0; }
  100% { background-position: -200% 0; }
}
```

```tsx
{isLoading ? <MetricCardSkeleton /> : <MetricCard {...props} />}
```

### Agent call loading (2-5 seconds)

Only the result area enters loading state — never the whole page.

```tsx
{isPending ? (
  <div className="agent-loading">
    <PulsingDot />
    <span style={{ color: 'var(--color-text-muted)', fontSize: 'var(--text-base)' }}>
      Analizando tus datos...
    </span>
  </div>
) : (
  <WorkoutResult workout={agentResponse} />
)}
```

### Empty state

```tsx
<EmptyState
  icon="watch"
  title="Sin datos de Garmin"
  description="Conecta tu reloj para ver tus métricas y recibir tu entrenamiento personalizado."
  action={{ label: 'Sincronizar ahora', onClick: triggerSync }}
/>
```

---

## What Not To Do

- **Never hardcode colors.** Use `var(--color-*)`.
- **Never use a light background.** Dark-first throughout.
- **Never use font-weight 600, 700, or 800.** Max is 500.
- **Never add glow to cards, text, or UI chrome.** Glow is chart-only.
- **Never use gradients on backgrounds or card surfaces.** Gradients only inside `<linearGradient>` chart fills.
- **Never put a spinner inside a metric card.** Use skeleton shimmer.
- **Never omit the `::before` top-edge card highlight.** It is the system's defining detail.
- **Never use more than 2 data series per chart** unless they are the 5 training zones.
- **Never build a new chart component.** Use Recharts with the patterns here.
- **Never build a new form input from scratch.** Extend existing components in `src/components/`.
- **Never use emoji as icons.** Use Lucide React, 16px inline, 20px standalone.

---

## Quick Reference

| Element | Spec |
|---|---|
| Page bg | `var(--color-bg-base)` — `#0D1117` |
| Card bg | `var(--color-bg-surface)` — `#161B26` |
| Card border | `0.5px solid var(--color-border)` |
| Card radius | `12px` |
| Card top highlight | `::before` 1px gradient — always |
| Primary metric | `--text-metric-lg`, weight 500, `tabular-nums` |
| Primary CTA | `background: var(--color-brand)`, `color: var(--color-text-inverse)` |
| CTL line | `var(--color-brand)`, `strokeWidth: 2`, solid |
| ATL line | `var(--color-accent)`, `strokeWidth: 1.5`, dashed `4 3` |
| Chart area fill | `linearGradient` 0.25 → 0 opacity |
| Bar chart fill | `linearGradient` top-to-bottom, `radius [4,4,0,0]` |
| Zone 1–5 | `var(--color-zone-1)` … `var(--color-zone-5)` |
| Status good | `var(--color-status-good)` — `#4ADE80` |
| Status moderate | `var(--color-status-moderate)` — `#FACC15` |
| Status low | `var(--color-status-low)` — `#FB923C` |
| Status critical | `var(--color-status-critical)` — `#F87171` |
| Icons | Lucide React — 16px inline, 20px standalone |
| Grid gap | `12px` entre cards, `16px` entre secciones |
| Page padding | `28px 32px` |
