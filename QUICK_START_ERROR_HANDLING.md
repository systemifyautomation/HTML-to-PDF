# Quick Start - Browser-Like HTML Error Handling

## Installation

1. **Install new dependencies:**

```bash
pip install -r requirements.txt
```

This will install:
- `html5lib` - Browser-standard HTML5 parser
- `beautifulsoup4` - HTML parsing library  
- `lxml` - Fast XML/HTML processor

2. **Restart your application:**

```bash
python app.py
```

## Test It

Test with the broken HTML file:

```bash
python test_broken_html.py
```

This will:
- ✅ Read `examples/simple_template.html` (has syntax errors)
- ✅ Convert it to PDF via your API
- ✅ Save as `test_broken_html_output.pdf`

## What Was Fixed

Your HTML had these errors that browsers ignore but broke PDF conversion:

1. ❌ Malformed DOCTYPE → ✅ Fixed by html5lib
2. ❌ `maxheight` (invalid CSS) → ✅ Changed to `max-height`
3. ❌ `font-size: undefinedpx` → ✅ Changed to `font-size: 16px`
4. ❌ `color: undefined` → ✅ Changed to `color: inherit`
5. ❌ `-margin:` (invalid) → ✅ Changed to `margin:`
6. ❌ Character encoding issues → ✅ Fixed with UTF-8 handling

**Result:** Your HTML now converts to PDF exactly as it displays in browsers! 🎉

## No API Changes

The API works exactly the same. Your existing code doesn't need changes:

```python
import requests

response = requests.post('http://localhost:5000/convert', json={
    'html': html_content,
    'filename': 'output.pdf'
})
```

## How It Works

**Before:**
```
HTML with errors → WeasyPrint → ❌ ERROR
```

**After:**
```
HTML with errors → html5lib (browser parser) → Fix CSS errors → WeasyPrint → ✅ PDF
```

## Learn More

- [BROWSER_LIKE_RENDERING.md](BROWSER_LIKE_RENDERING.md) - Full documentation
- [HTML_ERRORS_FIXED.md](HTML_ERRORS_FIXED.md) - Detailed error analysis

## Troubleshooting

**Import errors after installation?**
```bash
pip install --upgrade beautifulsoup4 html5lib lxml
```

**Server won't start?**
```bash
pip install -r requirements.txt --force-reinstall
```

**PDF still has errors?**
Check the server logs for details. The converter now logs what it fixes.
