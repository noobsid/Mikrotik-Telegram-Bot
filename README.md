# 🤖 Telegram Voucher Bot untuk Mikrotik

Bot Telegram ini digunakan untuk **membuat voucher Hotspot Mikrotik** secara otomatis melalui API Mikrotik.  
Dibangun menggunakan **python-telegram-bot** dan **librouteros**.

---

## ✨ Fitur

- 🔐 Autentikasi admin berdasarkan `chat_id`
- 🎫 Generate voucher otomatis langsung ke Mikrotik
- 📋 Menampilkan daftar profile hotspot
- 📌 Input manual via pesan (contoh: `4r 2`)
- ⚙️ Mendukung koneksi ke Mikrotik dengan **custom port** (`ip:port`)
- 💬 Navigasi menu interaktif (Inline Keyboard)

---

## 📦 Persyaratan

- Python 3.9 atau lebih baru
- Mikrotik dengan **API service aktif**
  - Cek dengan:
    ```
    /ip service print
    ```
  - Jika ingin menggunakan port custom (misal `1001`):
    ```
    /ip service set api port=1001 disabled=no
    ```

---

## ⚙️ Instalasi

1. **Clone repository** atau salin script bot ke folder:
   ```bash
   git clone https://github.com/noobsid/Mikrotik-Telegram-Bot.git
   cd Mikrotik-Telegram-Bot
