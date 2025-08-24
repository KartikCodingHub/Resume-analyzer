# YourBrand — Static Website Starter

A clean, responsive static site with accessibility, dark mode, and small, maintainable CSS/JS.

## Quick start

- Open `index.html` directly in a browser, or serve locally:

```bash
python3 -m http.server 8000
# then visit http://localhost:8000
```

## Project structure

```
/workspace
├── index.html
├── css/
│  └── styles.css
├── js/
│  └── script.js
└── assets/
   └── img/
```

## Features

- Responsive layout with semantic HTML
- Accessible: skip link, focus styles, labels, `aria-live` statuses
- Dark mode: respects system preference + user toggle (stored in localStorage)
- Smooth scrolling and mobile navigation
- Simple contact form validation (client-side only)

## Customize

- Update text and sections in `index.html`.
- Tweak colors and spacing tokens in `css/styles.css` under `:root`.
- Extend interactivity in `js/script.js`.

## Deploy

- GitHub Pages: push to a repo and enable Pages for the branch root.
- Netlify/Vercel: drag-drop the folder or connect your repo; output is the project root.

## License

MIT