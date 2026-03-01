# Changelog
---

## [Unreleased]

### Added
- **Mobile Navigation System**: Implemented a slide-out mobile overlay with high-end typography (2.8rem) and a CSS-only hamburger menu animation.
- **Design System (Tokens)**: Established a comprehensive CSS variable system in `root.css` featuring a 50–950 color scale, standardized spacing (4px base), and global transition speeds
- **Dark Mode Support**: Added full support for `[data-theme="dark"]` with inverted backgrounds and adjusted contrast for accessibility.
- **Privacy Notification**: Introduced a glassy, backdrop-blur privacy banner with distinct light and dark variants.
- **Typography & Icons**: Integrated Google Fonts (Montserrat) and the FontAwesome icon library.
- **New Blueprints**: Initialized routes for `blogs`, `projects`, and `others`.
- **UI Components**: Added global utility classes for buttons (`.btn-primary`, `.btn-outline`), flexible layouts, and animated filter drawers.

### Changed
- **Header Overhaul**: Redesigned the desktop navbar to be fixed with a `backdrop-filter` (glassmorphism) and centered navigation links.
- **Footer Redesign**: Reorganized the footer into a clean two-column grid (Brand and Links) with social icon integration and a legal links bar.
- **Hero & Content Sections**: Enhanced the index hero with a 3D-perspective card wrapper and refined project/blog preview cards with hover lift effects.
- **Project Structure**: Updated `.gitignore` to track `changelog.txt` and exclude `main.py`.
- **Configuration**: Simplified `settings.json` by removing legacy categories and local credentials (e.g., admin password).

### Fixed
- **Responsiveness**: Improved mobile layouts for the hero section, about grid, and footer to ensure proper alignment on smaller devices.

### Removed
- **Legacy Styling**: Deleted hardcoded pixel-based padding and colors in favor of the new design tokens.
- **Unused Data**: Removed legacy "Golf" related categories from the settings configuration.

---