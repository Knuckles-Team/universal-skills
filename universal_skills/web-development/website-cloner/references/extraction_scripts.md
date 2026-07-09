# Extraction Scripts (JavaScript Reference)

Use these snippets with your browser tool (e.g., `agent-browser`) to perform deep style and asset discovery. Run these results in your browser's console or via an MCP tool execution.

## 1. Deep Asset Discovery
Discover all images, videos, background images, and SVGs on the page.

```javascript
/* Run this via browser console or MCP to discover all assets */
(function() {
  const assets = {
    images: [...document.querySelectorAll('img')].map(img => ({
      src: img.src || img.currentSrc,
      alt: img.alt,
      width: img.naturalWidth,
      height: img.naturalHeight,
      // Include parent info to detect layered compositions
      parentClasses: img.parentElement?.className,
      siblings: img.parentElement ? [...img.parentElement.querySelectorAll('img')].length : 0,
      position: getComputedStyle(img).position,
      zIndex: getComputedStyle(img).zIndex
    })),
    videos: [...document.querySelectorAll('video')].map(v => ({
      src: v.src || v.querySelector('source')?.src,
      poster: v.poster,
      autoplay: v.autoplay,
      loop: v.loop,
      muted: v.muted
    })),
    backgroundImages: [...document.querySelectorAll('*')].filter(el => {
      const bg = getComputedStyle(el).backgroundImage;
      return bg && bg !== 'none';
    }).map(el => ({
      url: getComputedStyle(el).backgroundImage,
      element: el.tagName + '.' + el.className?.split(' ')[0]
    })),
    svgCount: document.querySelectorAll('svg').length,
    fonts: [...new Set([...document.querySelectorAll('*')].slice(0, 200).map(el => getComputedStyle(el).fontFamily))],
    favicons: [...document.querySelectorAll('link[rel*="icon"]')].map(l => ({ href: l.href, sizes: l.sizes?.toString() }))
  };
  return JSON.stringify(assets, null, 2);
})();
```

## 2. Per-Component Style Extraction
Extract every relevant CSS property for a specific element and its layout hierarchy.

```javascript
/* Per-component extraction — replace 'SELECTOR' with the actual CSS selector */
(function(selector) {
  const el = document.querySelector(selector);
  if (!el) return JSON.stringify({ error: 'Element not found: ' + selector });
  const props = [
    'fontSize','fontWeight','fontFamily','lineHeight','letterSpacing','color',
    'textTransform','textDecoration','backgroundColor','background',
    'padding','paddingTop','paddingRight','paddingBottom','paddingLeft',
    'margin','marginTop','marginRight','marginBottom','marginLeft',
    'width','height','maxWidth','minWidth','maxHeight','minHeight',
    'display','flexDirection','justifyContent','alignItems','gap',
    'gridTemplateColumns','gridTemplateRows',
    'borderRadius','border','borderTop','borderBottom','borderLeft','borderRight',
    'boxShadow','overflow','overflowX','overflowY',
    'position','top','right','bottom','left','zIndex',
    'opacity','transform','transition','cursor',
    'objectFit','objectPosition','mixBlendMode','filter','backdropFilter',
    'whiteSpace','textOverflow','WebkitLineClamp'
  ];
  function extractStyles(element) {
    const cs = getComputedStyle(element);
    const styles = {};
    props.forEach(p => {
      const v = cs[p];
      if (v && v !== 'none' && v !== 'normal' && v !== 'auto' && v !== '0px' && v !== 'rgba(0, 0, 0, 0)')
        styles[p] = v;
    });
    return styles;
  }
  function walk(element, depth) {
    if (depth > 4) return null;
    const children = [...element.children];
    return {
      tag: element.tagName.toLowerCase(),
      classes: element.className?.toString().split(' ').slice(0, 5).join(' '),
      text: element.childNodes.length === 1 && element.childNodes[0].nodeType === 3 ? element.textContent.trim().slice(0, 200) : null,
      styles: extractStyles(element),
      images: element.tagName === 'IMG' ? { src: element.src, alt: element.alt, naturalWidth: element.naturalWidth, naturalHeight: element.naturalHeight } : null,
      childCount: children.length,
      children: children.slice(0, 20).map(c => walk(c, depth + 1)).filter(Boolean)
    };
  }
  return JSON.stringify(walk(el, 0), null, 2);
})('SELECTOR');
```

## 3. Behavior Diff (Multi-State Extraction)
To capture scroll-triggered or hover behaviors:
1.  **State A**: Capture styles at current state (e.g., scroll position 0).
2.  **Trigger**: Scroll, click, or hover via your browser tool.
3.  **State B**: Re-run the extraction script on the same element.
4.  **Diff**: Document precisely which properties changed and the transition timing.
