# 🧵 htmlweaver

> Split HTML into threads. Weave them back together.

A simple CLI tool that splits AI-generated HTML files into clean,
separate HTML, CSS, and JavaScript files — and exports them as
Vue or React components.

---

## ✨ Features

- 🔪 **Split** — Break a single HTML file into `.html`, `.css`, and `.js`
- 🧩 **Combine** — Merge separate files back into one HTML file
- ⚡ **Vue Export** — Convert HTML into a Vue Single File Component `.vue`
- ⚛️ **React Export** — Convert HTML into a React functional component `.jsx`

---

## 📦 Installation

```bash
pip install htmlweaver
```

---

## 🚀 Usage

### Split

```bash
htmlweaver split --html mypage.html --output ./output
```

**Output:**

```
output/
├── mypage.html
├── mypage.css
└── mypage.js
```

---

### Combine

```bash
htmlweaver combine --html ./output/mypage.html \
                   --css ./output/mypage.css \
                   --js ./output/mypage.js \
                   --output ./output/mypage_final.html
```

---

### Export to Vue

```bash
htmlweaver export --html mypage.html --format vue --output ./output
```

**Output:**

```
output/
└── Mypage.vue
```

---

### Export to React

```bash
htmlweaver export --html mypage.html --format react --output ./output
```

**Output:**

```
output/
├── Mypage.jsx
└── Mypage.css
```

---

## 🗂️ Project Structure

```
htmlweaver/
├── htmlweaver/
│   ├── __init__.py
│   ├── cli.py
│   ├── splitter.py
│   ├── combiner.py
│   ├── utils.py
│   └── exporters/
│       ├── __init__.py
│       ├── vue_exporter.py
│       └── react_exporter.py
├── tests/
├── pyproject.toml
└── README.md
```

---

## 🛣️ Roadmap

- [x] Split HTML into separate files
- [x] Combine files back into HTML
- [x] Export as Vue component
- [x] Export as React component
- [ ] `--watch` mode for auto-split on save
- [ ] TypeScript / TSX support
- [ ] SCSS export
- [ ] Angular component export
- [ ] VS Code Extension
- [ ] AI-powered smart component splitting
- [ ] Web app at htmlweaver.io

---

## 🤝 Contributing

Contributions are welcome!  
Feel free to open an issue or submit a pull request.

---

## 📄 License

MIT © [abutlb](https://github.com/abutlb)
