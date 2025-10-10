# Email Newsletter Management Application - Design Guidelines

## Design Approach
**System**: Bootstrap 5 component library enhanced with modern dashboard patterns inspired by **Mailchimp** and **SendGrid** aesthetics. Focus on data clarity, efficient workflows, and professional polish suitable for business users managing email campaigns.

## Core Design Elements

### A. Color Palette
**Light Mode (Primary)**
- Primary Blue: 214 88% 51% (professional, trustworthy brand color)
- Primary Hover: 214 88% 45%
- Success Green: 142 71% 45% (campaign sent, positive metrics)
- Warning Orange: 38 92% 50% (pending actions, draft status)
- Danger Red: 0 84% 60% (failed sends, critical alerts)
- Neutral Gray-100: 210 20% 98% (page backgrounds)
- Neutral Gray-200: 214 15% 91% (card backgrounds, subtle dividers)
- Neutral Gray-600: 215 16% 47% (secondary text)
- Neutral Gray-900: 220 13% 18% (primary text)
- White: Pure white for cards, modals, elevated surfaces

**Dark Mode**
- Background: 220 13% 12%
- Cards/Elevated: 220 13% 18%
- Primary Blue: 214 100% 65%
- Text Primary: 210 20% 98%
- Text Secondary: 215 16% 65%

### B. Typography
**Font Stack**: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', system-ui, sans-serif

**Hierarchy**:
- Dashboard Headers: 600 weight, 28-32px
- Section Titles: 600 weight, 20-24px
- Card Headers: 600 weight, 18px
- Body Text: 400 weight, 15px
- Table Data: 400 weight, 14px
- Labels/Captions: 500 weight, 13px, uppercase tracking
- Buttons: 500 weight, 15px

### C. Layout System
**Spacing Primitives**: Use Bootstrap's spacing scale exclusively - stick to units 2, 3, 4, 5 for consistency
- Component padding: p-3, p-4
- Section margins: mb-4, mb-5
- Card spacing: p-4 internally
- Form gaps: gap-3 between fields
- Table cell padding: px-3 py-2

**Grid Structure**: Bootstrap 12-column grid with consistent gutters (g-3, g-4)

### D. Component Library

**Statistics Cards (Dashboard Hero)**
- 4-column grid (lg), 2-column (md), 1-column (mobile)
- Each card: white background, subtle shadow (0 1px 3px rgba(0,0,0,0.1))
- Layout: Icon (48x48, colored background circle) + Label + Large metric + Percentage change badge
- Hover: Lift shadow (0 4px 12px rgba(0,0,0,0.08))

**Data Tables**
- Striped rows with hover state (gray-50 background)
- Sticky header with subtle bottom border
- Action column (right-aligned): icon buttons for Edit/Delete/View
- Status badges: Pill-shaped, colored backgrounds, white text
- Pagination: Bootstrap pagination centered below table

**Forms**
- Floating labels for all text inputs
- Grouped sections with subtle divider lines
- Full-width on mobile, 2-column layout (lg) for efficiency
- Required field indicators: red asterisk
- Helper text: gray-600, 13px below inputs
- Primary button: full blue background, white text
- Secondary button: outline-primary variant

**Navigation**
- Horizontal top navbar: white background, subtle shadow
- Logo left, user menu right
- Avatar circle with dropdown menu
- Active state: blue bottom border (3px)

**Campaign Cards** (List View)
- White cards with 16px padding
- Left accent border (4px) - color indicates status (blue=active, green=sent, gray=draft)
- Flexbox layout: Campaign name + metrics row + action buttons
- Grid: 1 column mobile, 2 columns tablet, 3 columns desktop

**Modals/Dialogs**
- Centered overlay with backdrop blur
- White card with rounded corners (8px)
- Header with close button, body with scrollable content
- Footer with action buttons (right-aligned)

### E. Imagery & Visual Assets

**Images Required**:
1. **Login/Landing Hero**: Full-width hero section (600px height) with professional stock image showing business professional at laptop or abstract email/communication theme. Apply gradient overlay (blue-to-transparent) for text legibility. Place centered white login card on top.

2. **Empty States**: Illustrated placeholders for:
   - No campaigns yet: Envelope illustration with "Create your first campaign" CTA
   - No subscribers: People/audience illustration
   - No statistics: Chart/graph illustration

3. **User Avatars**: Circular profile images in navigation and activity feeds

**Icon Library**: Bootstrap Icons (bi-*) exclusively for consistency
- Primary actions: bi-plus-lg, bi-pencil, bi-trash, bi-send
- Status indicators: bi-check-circle, bi-clock, bi-x-circle
- Navigation: bi-house, bi-envelope, bi-people, bi-graph-up

### F. Dashboard Layout Structure

**Main Dashboard Sections** (top to bottom):
1. Stats Grid: 4 metric cards (Total Campaigns, Active Subscribers, Open Rate, Click Rate)
2. Quick Actions Bar: "New Campaign", "Import Contacts", "View Reports" buttons (horizontal flex)
3. Recent Campaigns Table: 8-10 rows, sortable columns, inline actions
4. Activity Feed Card: Recent subscriber actions, timestamps (right sidebar on desktop, full-width on mobile)

**Campaign Management Page**:
- Split layout: Form (8 columns) + Preview pane (4 columns) on desktop
- Sticky preview pane scrolls with page
- Tabbed form sections: Details, Recipients, Content, Schedule

### G. Interactions & States

**Animations**: Minimal, performance-first
- Card hover: transform translateY(-2px), 200ms ease
- Button clicks: subtle scale(0.98) on active
- Table row hover: smooth background transition
- Toasts/Notifications: slide-in from top-right

**Loading States**:
- Skeleton screens for tables (gray shimmer animation)
- Spinner overlay for full-page loads
- Inline spinners for button actions

**Validation**:
- Error state: red border, red text below field
- Success state: green checkmark icon right-aligned in field
- Real-time validation on blur

This design system creates a professional, efficient dashboard experience optimized for business users managing email campaigns with clarity and speed.