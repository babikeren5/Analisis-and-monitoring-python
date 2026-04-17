# ðŸ–¥ï¸ Python Program Monitor & Analyzer

A GUI-based tool for monitoring, analyzing, and executing Python programs with real-time logging, system diagnostics, and resource tracking.

---

## ðŸš€ Overview

**Python Program Monitor & Analyzer** adalah aplikasi berbasis GUI yang dirancang untuk:

- Menganalisis kode Python secara statis
- Mengecek ketersediaan library
- Menjalankan program Python
- Memantau penggunaan CPU & RAM secara real-time
- Menyimpan log eksekusi secara terstruktur

Tool ini menggabungkan konsep:
> ðŸ”§ Mini IDE + ðŸ“Š System Monitor + ðŸ§¾ Logger

---

## âœ¨ Features

### ðŸ“ File Handling
- Upload file Python (.py)
- Preview dan analisis kode

### ðŸ” Static Code Analysis
- Deteksi library menggunakan `ast`
- Identifikasi dependensi program

### ðŸ“¦ Library Checker
- Cek apakah library tersedia
- Menampilkan versi library
- Rekomendasi instalasi (`pip install`)

### â–¶ï¸ Program Execution
- Jalankan program langsung dari GUI
- Stop (SIGTERM) dan Force Stop (SIGKILL)

### ðŸ“Š Real-time Monitoring
- CPU Usage (%)
- Memory Usage (MB)
- Process ID (PID)
- Execution time tracking

### ðŸ–¥ï¸ Dual Output System
- **Frontend** â†’ Output program (stdout/stderr)
- **Backend** â†’ Monitoring & logs

### ðŸ§¾ Logging System
- Log otomatis tersimpan
- Format log terstruktur
- Bisa disimpan ke file

---

## Technologies Used

- Python 3.8+
- tkinter (GUI)
- psutil (resource monitoring)
- subprocess (program execution)
- ast (code analysis)
- threading & queue (real-time processing)

---

##  Preview

*(Tambahkan screenshot di sini nanti)*

---

## Installation

### 1. Clone repository
```bash
git clone https://github.com/username/python-program-monitor.git
cd python-program-monitor
```

### 2. Install dependencies
```bash
pip install psutil
```

### 3. Run program
```bash
python a_n_m5.py
```

---

## How It Works

1. Upload file Python
2. Sistem akan:
   - Menganalisis library
   - Mengecek environment
3. Klik RUN
4. Program akan:
   - Dieksekusi
   - Dimonitor (CPU, RAM)
   - Dicatat dalam log

---

## Project Structure

```
.
â”œâ”€â”€ a_n_m5.py
â”œâ”€â”€ monitor_logs/
â””â”€â”€ README.md
```

---

## Disclaimer

Tool ini menjalankan file Python secara langsung menggunakan subprocess.
Pastikan file yang dijalankan aman.
Tidak disarankan untuk menjalankan script dari sumber tidak terpercaya.

---

## Future Improvements

- Modular architecture (plugin system)
- AI-based error analysis
- Code recommendation system
- Integration with web-based editor
- Sandbox execution environment

---

## Contributing

1. Fork repository
2. Buat branch baru
3. Commit perubahan
4. Submit pull request

---

## License

MIT License

---

## ðuthor

Developed by BABI KEREN 🐷

---

> Jika project ini membantu, jangan lupa beri star Python Program Monitor & Analyzer

A GUI-based tool for monitoring, analyzing, and executing Python programs with real-time logging, system diagnostics, and resource tracking.

---

## Overview

**Python Program Monitor & Analyzer** adalah aplikasi berbasis GUI yang dirancang untuk:

- Menganalisis kode Python secara statis
- Mengecek ketersediaan library
- Menjalankan program Python
- Memantau penggunaan CPU & RAM secara real-time
- Menyimpan log eksekusi secara terstruktur

Tool ini menggabungkan konsep:
> ðŸ”§ Mini IDE + ðŸ“Š System Monitor + ðŸ§¾ Logger

---

## Features

### File Handling
- Upload file Python (.py)
- Preview dan analisis kode

### Static Code Analysis
- Deteksi library menggunakan `ast`
- Identifikasi dependensi program

### Library Checker
- Cek apakah library tersedia
- Menampilkan versi library
- Rekomendasi instalasi (`pip install`)

### Program Execution
- Jalankan program langsung dari GUI
- Stop (SIGTERM) dan Force Stop (SIGKILL)

### Real-time Monitoring
- CPU Usage (%)
- Memory Usage (MB)
- Process ID (PID)
- Execution time tracking

### Dual Output System
- **Frontend** â†’ Output program (stdout/stderr)
- **Backend** â†’ Monitoring & logs

### Logging System
- Log otomatis tersimpan
- Format log terstruktur
- Bisa disimpan ke file

---

## Technologies Used

- Python 3.8+
- tkinter (GUI)
- psutil (resource monitoring)
- subprocess (program execution)
- ast (code analysis)
- threading & queue (real-time processing)

---

## Preeview

*(Tambahkan screenshot di sini nanti)*

---

##  Installation

### 1. Clone repository
```bash
git clone https://github.com/username/python-program-monitor.git
cd python-program-monitor
```

### 2. Install dependencies
```bash
pip install psutil
```

### 3. Run program
```bash
python a_n_m5.py
```

---

## How It Works

1. Upload file Python
2. Sistem akan:
   - Menganalisis library
   - Mengecek environment
3. Klik RUN
4. Program akan:
   - Dieksekusi
   - Dimonitor (CPU, RAM)
   - Dicatat dalam log

---

## Project Structure

```
.
â”œâ”€â”€ a_n_m5.py
â”œâ”€â”€ monitor_logs/
â””â”€â”€ README.md
```

---

## Disclaimer

Tool ini menjalankan file Python secara langsung menggunakan subprocess.
Pastikan file yang dijalankan aman.
Tidak disarankan untuk menjalankan script dari sumber tidak terpercaya.

---

## Future Improvements

- Modular architecture (plugin system)
- AI-based error analysis
- Code recommendation system
- Integration with web-based editor
- Sandbox execution environment

---

## Contributing

1. Fork repository
2. Buat branch baru
3. Commit perubahan
4. Submit pull request

---

## License

MIT License

---

## Aythor

Developed by Your Name

---

> â­ Jika project ini membantu, jangan lupa beri star!
