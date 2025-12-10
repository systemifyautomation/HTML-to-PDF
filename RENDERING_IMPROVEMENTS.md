# HTML Rendering Improvements

This document describes the enhancements made to improve HTML to PDF rendering quality and reliability.

## 🎯 Problems Solved

### 1. **Malformed HTML Structure**
- **Problem**: Missing DOCTYPE, html, head, or body tags caused rendering issues
- **Solution**: Automatic HTML structure validation and correction
- **Result**: PDFs render correctly even with incomplete HTML

### 2. **External Resources Not Loading**
- **Problem**: Images, stylesheets, and fonts with relative URLs failed to load
- **Solution**: Added `base_url` parameter to resolve relative paths
- **Result**: External resources load properly when base URL is provided

### 3. **Awkward Page Breaks**
- **Problem**: Content split inappropriately across pages
- **Solution**: Smart CSS rules prevent breaks in tables, headings, and figures
- **Result**: Professional-looking page breaks that respect content structure

### 4. **Poor Typography**
- **Problem**: Text rendering looked rough and unprofessional
- **Solution**: Added antialiasing and optimizeLegibility rules
- **Result**: Smooth, crisp text rendering

### 5. **Images Overflowing Pages**
- **Problem**: Large images extended beyond page boundaries
- **Solution**: Automatic responsive image sizing (`max-width: 100%`)
- **Result**: Images scale appropriately to fit pages

### 6. **Large File Sizes**
- **Problem**: PDFs were unnecessarily large
- **Solution**: Added font and image optimization
- **Result**: Smaller file sizes without quality loss

### 7. **Inconsistent Page Sizing**
- **Problem**: No control over page dimensions
- **Solution**: Added `page_size` and `margin` parameters
- **Result**: Full control over page layout (A4, Letter, Legal, etc.)

### 8. **Character Encoding Issues**
- **Problem**: Special characters rendered incorrectly
- **Solution**: Explicit UTF-8 encoding and charset meta tag
- **Result**: Proper rendering of international characters

## 🚀 New Features

### 1. Automatic HTML Sanitization
The API now automatically:
- Adds missing DOCTYPE declaration
- Creates html, head, and body tags if absent
- Adds UTF-8 charset meta tag
- Inserts base tag for URL resolution

```python
# Before: Incomplete HTML
html = "<h1>Title</h1><p>Content</p>"

# After: Automatically enhanced
# <!DOCTYPE html>
# <html>
# <head>
#     <meta charset="UTF-8">
# </head>
# <body>
#     <h1>Title</h1>
#     <p>Content</p>
# </body>
# </html>
```

### 2. Base URL Support
Load external resources by providing a base URL:

```json
{
    "html": "<img src='images/logo.png'>",
    "base_url": "https://example.com/"
}
```

The image will be loaded from: `https://example.com/images/logo.png`

### 3. Custom Page Sizing
Control page dimensions and margins:

```json
{
    "html": "...",
    "page_size": "Letter",
    "margin": "1in"
}
```

**Supported page sizes:**
- A4 (default)
- A3, A5
- Letter
- Legal
- Tabloid

**Margin formats:**
- cm: `2cm`
- inches: `1in`
- mm: `20mm`
- Combined: `2cm 1cm` (vertical horizontal)

### 4. PDF Optimization
Reduce file size without quality loss:

```json
{
    "html": "...",
    "optimize": true
}
```

Optimizations include:
- Font subsetting (only include used characters)
- Image compression
- Metadata reduction

### 5. Smart Page Breaks
Automatic CSS rules prevent awkward breaks:

```css
/* Auto-applied rules */
h1, h2, h3, h4, h5, h6 {
    page-break-after: avoid;
    page-break-inside: avoid;
}

table, figure, img {
    page-break-inside: avoid;
}
```

**Manual control:**
```html
<!-- Force page break -->
<div style="page-break-after: always;"></div>

<!-- Prevent break inside element -->
<div style="page-break-inside: avoid;">
    <h2>Section Title</h2>
    <p>Content that stays together</p>
</div>
```

### 6. Enhanced Typography
Better text rendering with:
- Font smoothing
- Optimized legibility
- Proper kerning and spacing

## 📝 API Parameters

### Request Body

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `html` | string | ✓ | - | HTML content to convert |
| `css` | string | ✗ | - | Additional CSS styles |
| `filename` | string | ✗ | document.pdf | Output filename |
| `base_url` | string | ✗ | null | Base URL for relative resources |
| `page_size` | string | ✗ | A4 | Page size (A4, Letter, etc.) |
| `margin` | string | ✗ | 2cm | Page margins (CSS units) |
| `optimize` | boolean | ✗ | true | Enable PDF optimization |

### Example Request

```python
import requests

response = requests.post(
    'http://localhost:5000/convert',
    headers={'X-API-Key': 'your-api-key'},
    json={
        'html': '<h1>Hello World</h1>',
        'css': 'h1 { color: blue; }',
        'filename': 'output.pdf',
        'base_url': 'https://example.com/',
        'page_size': 'Letter',
        'margin': '1in',
        'optimize': True
    }
)

with open('output.pdf', 'wb') as f:
    f.write(response.content)
```

## 🎨 CSS Best Practices

### 1. Use Print-Safe Colors
```css
/* Avoid very light backgrounds */
body {
    background-color: white;
    color: #333;  /* Dark text for readability */
}
```

### 2. Define Print Styles
```css
@media print {
    .no-print {
        display: none;
    }
    a {
        text-decoration: underline;
    }
}
```

### 3. Control Page Breaks
```css
/* Keep sections together */
.section {
    page-break-inside: avoid;
}

/* Start chapters on new page */
.chapter {
    page-break-before: always;
}

/* Prevent orphans/widows */
p {
    orphans: 3;
    widows: 3;
}
```

### 4. Use Web-Safe Fonts
```css
body {
    font-family: Arial, Helvetica, sans-serif;
    /* Or use web fonts with @font-face */
}
```

### 5. Set Proper Image Sizes
```css
img {
    max-width: 100%;
    height: auto;
    page-break-inside: avoid;
}
```

## 🔧 Troubleshooting

### Images Not Loading
**Problem**: External images don't appear in PDF

**Solutions**:
1. Provide `base_url` parameter
2. Use absolute URLs in HTML: `<img src="https://...">`
3. Embed images as base64: `<img src="data:image/png;base64,..."`

### Fonts Look Different
**Problem**: Custom fonts not rendering

**Solutions**:
1. Use web-safe fonts (Arial, Georgia, etc.)
2. Include @font-face in CSS with absolute URLs
3. Ensure font files are accessible via base_url

### Page Breaks in Wrong Places
**Problem**: Content split awkwardly

**Solutions**:
```css
/* Prevent breaks */
.keep-together {
    page-break-inside: avoid;
}

/* Force breaks */
.new-page {
    page-break-before: always;
}
```

### Text Looks Blurry
**Problem**: Poor text rendering quality

**Solution**: Add these CSS rules (now auto-applied):
```css
body {
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
    text-rendering: optimizeLegibility;
}
```

### Large File Sizes
**Problem**: PDF files are too large

**Solutions**:
1. Set `optimize: true` (default)
2. Compress images before conversion
3. Limit font usage
4. Avoid unnecessary graphics

### Special Characters Not Showing
**Problem**: Unicode characters render incorrectly

**Solution**: Ensure UTF-8 encoding (now automatic):
```html
<meta charset="UTF-8">
```

## 🔍 Advanced Examples

### Multi-Page Report with Headers/Footers
```css
@page {
    size: A4;
    margin: 3cm 2cm;
    
    @top-center {
        content: "Company Report 2024";
        font-size: 10pt;
        color: #666;
    }
    
    @bottom-right {
        content: "Page " counter(page);
        font-size: 10pt;
    }
}
```

### Two-Column Layout
```css
.content {
    column-count: 2;
    column-gap: 2cm;
}
```

### Professional Tables
```css
table {
    width: 100%;
    border-collapse: collapse;
    page-break-inside: avoid;
}

thead {
    display: table-header-group;  /* Repeat on each page */
}

th {
    background-color: #007bff;
    color: white;
    padding: 12px;
}

td {
    padding: 10px;
    border-bottom: 1px solid #ddd;
}

tr:nth-child(even) {
    background-color: #f8f9fa;
}
```

### Invoice with Watermark
```css
body::before {
    content: "DRAFT";
    position: fixed;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%) rotate(-45deg);
    font-size: 120pt;
    color: rgba(0, 0, 0, 0.1);
    z-index: -1;
}
```

## 📚 Additional Resources

- [WeasyPrint Documentation](https://doc.courtbouillon.org/weasyprint/)
- [CSS Paged Media](https://www.w3.org/TR/css-page-3/)
- [Print Stylesheet Guide](https://www.smashingmagazine.com/2018/05/print-stylesheets-in-2018/)

## 🤝 Contributing

Found a rendering issue? Please report it with:
1. Sample HTML that demonstrates the problem
2. Expected vs actual output
3. Any error messages from the API

## 📄 License

Same as the main project.
