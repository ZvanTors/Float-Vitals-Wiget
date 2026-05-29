# 🪟 FloatVitals – Windows Floating System Monitor

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue)](https://python.org)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)

**A sleek, semi-transparent, always-on-top widget that shows your PC’s vital signs in real time.**

---

## ✨ Features

- 🖥️ **CPU & RAM** – Live usage percentage with crisp icons  
- 🌐 **Network Speed** – Download/Upload rate with automatic unit switching (KB/s ↔ MB/s)  
- 📊 **Live Network Graph** – Animated bar chart showing recent traffic (download & upload side‑by‑side)  
- 💾 **Drive List** – All drives with free space, total size, and a clean progress bar  
- 🎨 **Minimalist Design** – Dark rounded corners, transparency, frameless window  
- 🧲 **Draggable** – Move the widget by dragging the top status bar  
- ⚡ **Lightweight** – Low CPU/memory footprint, refreshes smartly

---

## 🖱️ Usage

Run the main script:

    python widget.py

- The widget appears as a floating overlay on your desktop.  
- Drag the top bar to reposition.  
- Click the **✕** button to close (the app exits completely).  
- All statistics update automatically:  
  - CPU/RAM & network speed every **1 second**  
  - Drive list every **30 seconds**

---

## 🛠️ Tech Stack

- **Python**  
- **PyQt5** – Modern GUI framework  
- **psutil** – System monitoring library

---

## 🤝 Contributions

Pull requests and ideas are welcome.  
If you find this useful, ⭐ star the repository!

---

**Enjoy a clean glance at your system’s performance – without the clutter.**