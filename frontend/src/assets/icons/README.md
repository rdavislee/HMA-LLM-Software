# Custom Icons Guide

This folder is for storing custom icon images that will be used throughout the frontend.

## How to Add Icons

### Option 1: Static Icons (Recommended for icons that don't change)
Place your icon files directly in the `frontend/public` folder:

```
frontend/public/
├── my-icon.png
├── custom-logo.svg
└── favicon.ico
```

**Usage:**
```jsx
// In React components
<img src="/my-icon.png" alt="My Icon" />

// As favicon in index.html
<link rel="icon" type="image/png" href="/my-icon.png" />
```

### Option 2: Imported Icons (Recommended for dynamic icons)
Place your icon files in this folder (`frontend/src/assets/icons/`):

```
frontend/src/assets/icons/
├── button-icon.svg
├── menu-icon.png
└── logo.webp
```

**Usage:**
```jsx
// Import the icon
import buttonIcon from '../assets/icons/button-icon.svg';
import menuIcon from '../assets/icons/menu-icon.png';

// Use in component
<img src={buttonIcon} alt="Button Icon" />
<img src={menuIcon} alt="Menu Icon" />
```

## Using the CustomIcon Component

We've created a reusable `CustomIcon` component for consistent icon usage:

```jsx
import CustomIcon from '../components/ui/CustomIcon';

// Usage
<CustomIcon 
  src="/my-icon.png" 
  alt="My Icon" 
  size="md" 
  className="text-blue-500" 
/>
```

## Supported Formats

- **SVG** (recommended for icons - scalable, small file size)
- **PNG** (good for complex icons with transparency)
- **JPG/JPEG** (for photographic icons)
- **WebP** (modern format, good compression)
- **GIF** (for animated icons)

## Best Practices

1. **Use SVG for icons** when possible - they're scalable and have small file sizes
2. **Optimize images** before adding them to reduce bundle size
3. **Use descriptive filenames** that indicate the icon's purpose
4. **Include alt text** for accessibility
5. **Consider different sizes** - you might need 16x16, 32x32, and larger versions

## Example: Adding a New Icon

1. **Save your icon** as `my-feature-icon.svg` in `frontend/src/assets/icons/`
2. **Import it** in your component:
   ```jsx
   import myIcon from '../assets/icons/my-feature-icon.svg';
   ```
3. **Use it** in your JSX:
   ```jsx
   <img src={myIcon} alt="My Feature" className="w-6 h-6" />
   ```

## File Organization

```
frontend/
├── public/                    # Static assets (favicons, logos)
│   ├── hive-icon.svg         # Main app icon
│   └── favicon.ico           # Browser favicon
└── src/
    └── assets/
        └── icons/            # Component-specific icons
            ├── button-icon.svg
            ├── menu-icon.png
            └── README.md      # This file
``` 