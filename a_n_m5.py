#!/usr/bin/env python3
"""
Python Program Monitor & Analyzer
A GUI tool to monitor, analyze, and execute Python programs with logging capabilities.
"""

import tkinter as tk
from tkinter import ttk, filedialog, scrolledtext, messagebox
import subprocess
import sys
import os
import platform
import ast
import importlib
import importlib.util
from datetime import datetime
import threading
import queue
import time
import psutil
from pathlib import Path

# Gunakan importlib.metadata untuk Python 3.8+
if sys.version_info >= (3, 8):
    from importlib.metadata import version as get_version, PackageNotFoundError
else:
    def get_version(package):
        return "Unknown"

class PythonProgramMonitor:
    def __init__(self, root):
        self.root = root
        self.root.title("Python Program Monitor & Analyzer")
        self.root.geometry("1400x900")
        self.root.configure(bg='#2b2b2b')
        
        # Variables
        self.program_path = None
        self.process = None
        self.monitoring = False
        self.monitor_thread = None
        self.log_queue = queue.Queue()
        self.log_file = None
        self.program_code = ""
        
        # Terminal info variables
        self.current_pid = None
        self.current_program_path = None
        self.program_start_time = None
        
        # Color schemes
        self.colors = {
            'bg': '#2b2b2b',
            'fg': '#ffffff',
            'frontend_bg': '#1e1e1e',
            'backend_bg': '#252526',
            'success': '#4ec9b0',
            'error': '#f48771',
            'warning': '#ce9178',
            'info': '#9cdcfe',
            'gray': '#808080',
            'green': '#6a9955',
            'yellow': '#dcdcaa',
            'blue': '#569cd6',
            'terminal_green': '#0f0',
            'terminal_cyan': '#0ff',
            'terminal_yellow': '#ff0',
            'terminal_red': '#f00'
        }
        
        self.setup_styles()
        self.setup_logging()
        self.create_widgets()
        
    def setup_styles(self):
        """Configure ttk styles"""
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('TFrame', background=self.colors['bg'])
        style.configure('TLabel', background=self.colors['bg'], foreground=self.colors['fg'])
        style.configure('TLabelframe', background=self.colors['bg'], foreground=self.colors['fg'])
        style.configure('TLabelframe.Label', background=self.colors['bg'], foreground=self.colors['fg'])
        
        # Style untuk notebook (tab)
        style.configure('TNotebook', background=self.colors['bg'])
        style.configure('TNotebook.Tab', background=self.colors['backend_bg'], foreground=self.colors['fg'], padding=[10, 5])
        style.map('TNotebook.Tab', background=[('selected', self.colors['blue'])])
        
    def setup_logging(self):
        """Initialize logging session"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_dir = Path("monitor_logs")
        log_dir.mkdir(exist_ok=True)
        self.log_file = log_dir / f"session_{timestamp}.txt"
        
        with open(self.log_file, 'w', encoding='utf-8') as f:
            f.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]}] [SESSION_START] session_id={timestamp}\n")
        
    def log_event(self, source, event_type, data):
        """Log event to file and queue for GUI"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
        log_line = f"[{timestamp}] [{source}] {event_type}={data}\n"
        
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(log_line)
        
        self.log_queue.put({
            'timestamp': timestamp,
            'source': source,
            'event_type': event_type,
            'data': data,
            'full_line': log_line
        })
        
    def create_widgets(self):
        """Create all GUI widgets"""
        # Main container
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # === BAGIAN A: UPLOAD PROGRAM (DI ATAS) ===
        self.create_upload_section(main_frame)
        
        # === NOTEBOOK (TAB) UNTUK BAGIAN 1,2,3,4 ===
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True, pady=(10, 10))
        
        # Tab 1: System Device Analysis
        self.tab1 = ttk.Frame(self.notebook)
        self.notebook.add(self.tab1, text="1. System Device Analysis")
        self.create_system_section(self.tab1)
        
        # Tab 2: Library Check
        self.tab2 = ttk.Frame(self.notebook)
        self.notebook.add(self.tab2, text="2. Library Availability Check")
        self.create_library_section(self.tab2)
        
        # Tab 3: Program Output (Frontend & Backend)
        self.tab3 = ttk.Frame(self.notebook)
        self.notebook.add(self.tab3, text="3. Program Execution & Output")
        self.create_output_section(self.tab3)
        
        # Tab 4: System Analyzer & Log Storage (DENGAN TERMINAL)
        self.tab4 = ttk.Frame(self.notebook)
        self.notebook.add(self.tab4, text="4. System Analyzer & Log Storage")
        self.create_analyzer_section(self.tab4)
        
        # === TOMBOL KONTROL DI PALING BAWAH ===
        self.create_control_section(main_frame)
        
        # Start GUI log processor
        self.process_log_queue()
        
        # Initial analysis
        self.analyze_system()
        
    def create_upload_section(self, parent):
        """Bagian A: Upload Program (di atas notebook)"""
        frame = ttk.LabelFrame(parent, text="📁 A. Upload Program", padding=10)
        frame.pack(fill=tk.X, pady=(0, 10))
        
        self.upload_btn = tk.Button(frame, text="📂 Pilih File Python", command=self.upload_file,
                                   bg='#3c3c3c', fg='white', font=('Arial', 10, 'bold'))
        self.upload_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        self.file_label = tk.Label(frame, text="Belum ada file dipilih", bg=self.colors['bg'], 
                                   fg=self.colors['gray'], font=('Arial', 10, 'italic'))
        self.file_label.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
    def create_system_section(self, parent):
        """Tab 1: System Device (Saat Ini vs Rekomendasi)"""
        frame = ttk.Frame(parent)
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Left: Current System
        current_frame = ttk.LabelFrame(frame, text="🖥 SISTEM SAAT INI", padding=10)
        current_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        self.current_system_text = scrolledtext.ScrolledText(current_frame, height=15, 
                                                              bg=self.colors['frontend_bg'], 
                                                              fg=self.colors['fg'],
                                                              font=('Consolas', 10))
        self.current_system_text.pack(fill=tk.BOTH, expand=True)
        
        self.current_system_text.tag_config("warning", foreground=self.colors['warning'])
        self.current_system_text.tag_config("error", foreground=self.colors['error'])
        self.current_system_text.tag_config("success", foreground=self.colors['success'])
        self.current_system_text.tag_config("normal", foreground=self.colors['fg'])
        
        # Right: Recommendations
        rec_frame = ttk.LabelFrame(frame, text="💡 REKOMENDASI SISTEM", padding=10)
        rec_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))
        
        self.recommendation_text = scrolledtext.ScrolledText(rec_frame, height=15,
                                                              bg=self.colors['backend_bg'],
                                                              fg=self.colors['fg'],
                                                              font=('Consolas', 10))
        self.recommendation_text.pack(fill=tk.BOTH, expand=True)
        
        self.recommendation_text.tag_config("warning", foreground=self.colors['warning'])
        self.recommendation_text.tag_config("success", foreground=self.colors['success'])
        self.recommendation_text.tag_config("info", foreground=self.colors['info'])
        
    def create_library_section(self, parent):
        """Tab 2: Program Library Check"""
        frame = ttk.Frame(parent)
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Treeview untuk libraries
        columns = ('Library', 'Version', 'Status', 'Recommendation')
        self.library_tree = ttk.Treeview(frame, columns=columns, show='headings', height=15)
        
        for col in columns:
            self.library_tree.heading(col, text=col)
            self.library_tree.column(col, width=250)
        
        scrollbar = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=self.library_tree.yview)
        self.library_tree.configure(yscrollcommand=scrollbar.set)
        
        self.library_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.library_tree.tag_configure('success', foreground=self.colors['success'])
        self.library_tree.tag_configure('error', foreground=self.colors['error'])
        self.library_tree.tag_configure('warning', foreground=self.colors['warning'])
        self.library_tree.tag_configure('gray', foreground=self.colors['gray'])
        
    def create_output_section(self, parent):
        """Tab 3: Output (Frontend & Backend)"""
        frame = ttk.Frame(parent)
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Output panes (Frontend & Backend)
        output_frame = ttk.Frame(frame)
        output_frame.pack(fill=tk.BOTH, expand=True)
        
        # FRONTEND (kiri) - Program Output
        frontend_frame = ttk.LabelFrame(output_frame, text="📺 FRONTEND - Program Output (stdout/stderr)", padding=5)
        frontend_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        self.frontend_text = scrolledtext.ScrolledText(frontend_frame, bg=self.colors['frontend_bg'],
                                                        fg=self.colors['fg'], font=('Consolas', 10))
        self.frontend_text.pack(fill=tk.BOTH, expand=True)
        
        self.frontend_text.tag_config("stdout", foreground=self.colors['fg'])
        self.frontend_text.tag_config("stderr", foreground=self.colors['error'])
        
        # BACKEND (kanan) - Monitor Trace
        backend_frame = ttk.LabelFrame(output_frame, text="🔧 BACKEND - Monitor Trace (CPU/RAM/Logs)", padding=5)
        backend_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))
        
        self.backend_text = scrolledtext.ScrolledText(backend_frame, bg=self.colors['backend_bg'],
                                                       fg=self.colors['fg'], font=('Consolas', 9))
        self.backend_text.pack(fill=tk.BOTH, expand=True)
        
        self.backend_text.tag_config("info", foreground=self.colors['info'])
        self.backend_text.tag_config("success", foreground=self.colors['success'])
        self.backend_text.tag_config("error", foreground=self.colors['error'])
        self.backend_text.tag_config("warning", foreground=self.colors['warning'])
        
    def create_analyzer_section(self, parent):
        """Tab 4: System Analyzer & Log Storage DENGAN TERMINAL INFO"""
        frame = ttk.Frame(parent)
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # === BARIS 1: Tombol Save dan Status ===
        button_frame = ttk.Frame(frame)
        button_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.save_log_btn = tk.Button(button_frame, text="💾 Simpan Log", command=self.save_log,
                                     bg='#3c6e8f', fg='white', font=('Arial', 10, 'bold'))
        self.save_log_btn.pack(side=tk.LEFT, padx=5)
        
        self.status_label = tk.Label(button_frame, text="⚙ Status: SIAP", bg=self.colors['bg'],
                                     fg=self.colors['success'], font=('Arial', 10, 'bold'))
        self.status_label.pack(side=tk.LEFT, padx=20)
        
        # === BARIS 2: TERMINAL INFO (Seperti tampilan terminal) ===
        terminal_frame = ttk.LabelFrame(frame, text="🖥 TERMINAL INFO - Program Execution Status", padding=5)
        terminal_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.terminal_text = scrolledtext.ScrolledText(terminal_frame, height=8, 
                                                         bg='#0a0a0a',  # Hitam pekat seperti terminal
                                                         fg='#0f0',      # Hijau seperti terminal
                                                         font=('Consolas', 10),
                                                         insertbackground='white')
        self.terminal_text.pack(fill=tk.X, expand=True)
        
        # Tag untuk terminal
        self.terminal_text.tag_config("info", foreground='#0f0')      # Hijau
        self.terminal_text.tag_config("error", foreground='#f00')     # Merah
        self.terminal_text.tag_config("warning", foreground='#ff0')   # Kuning
        self.terminal_text.tag_config("pid", foreground='#0ff')       # Cyan
        self.terminal_text.tag_config("success", foreground='#0f0')   # Hijau terang
        self.terminal_text.tag_config("header", foreground='#0ff')    # Cyan untuk header
        
        # === BARIS 3: Log Summary ===
        log_frame = ttk.LabelFrame(frame, text="📋 LOG SUMMARY", padding=5)
        log_frame.pack(fill=tk.BOTH, expand=True)
        
        self.log_summary = scrolledtext.ScrolledText(log_frame, height=8, bg=self.colors['backend_bg'],
                                                      fg=self.colors['gray'], font=('Consolas', 9))
        self.log_summary.pack(fill=tk.BOTH, expand=True)
        
        # Tampilkan pesan awal di terminal
        self.update_terminal_info("="*60, "header")
        self.update_terminal_info("   PROGRAM MONITOR SIAP DIGUNAKAN", "header")
        self.update_terminal_info("="*60, "header")
        self.update_terminal_info(f"📁 Log file: {self.log_file}", "info")
        self.update_terminal_info("📂 Upload file Python untuk memulai", "info")
        self.update_terminal_info("="*60, "header")
        
    def create_control_section(self, parent):
        """Tombol kontrol RUN, STOP, END di paling bawah"""
        frame = ttk.Frame(parent)
        frame.pack(fill=tk.X, pady=(10, 0))
        
        # Separator line
        separator = ttk.Separator(frame, orient='horizontal')
        separator.pack(fill=tk.X, pady=(0, 10))
        
        # Button container
        button_frame = ttk.Frame(frame)
        button_frame.pack()
        
        self.run_btn = tk.Button(button_frame, text="▶ RUN", command=self.run_program,
                                bg='#2d5a27', fg='white', font=('Arial', 12, 'bold'),
                                width=12, height=1)
        self.run_btn.pack(side=tk.LEFT, padx=10)
        
        self.stop_btn = tk.Button(button_frame, text="⏹ STOP", command=self.stop_program,
                                 bg='#8a6c3f', fg='white', font=('Arial', 12, 'bold'),
                                 width=12, height=1, state=tk.DISABLED)
        self.stop_btn.pack(side=tk.LEFT, padx=10)
        
        self.end_btn = tk.Button(button_frame, text="⏏ END", command=self.end_program,
                                bg='#8a3f3f', fg='white', font=('Arial', 12, 'bold'),
                                width=12, height=1, state=tk.DISABLED)
        self.end_btn.pack(side=tk.LEFT, padx=10)
        
    def update_terminal_info(self, message, tag="info"):
        """Update terminal info di Tab 4 seperti tampilan terminal"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        terminal_line = f"[{timestamp}] $ {message}\n"
        
        self.terminal_text.insert(tk.END, terminal_line, tag)
        self.terminal_text.see(tk.END)
        
        # Keep only last 30 lines
        if int(self.terminal_text.index('end-1c').split('.')[0]) > 30:
            self.terminal_text.delete(1.0, 2.0)
    
    def get_program_duration(self):
        """Hitung durasi program berjalan"""
        if self.program_start_time:
            duration = datetime.now() - self.program_start_time
            seconds = duration.total_seconds()
            
            if seconds < 60:
                return f"{seconds:.1f} detik"
            elif seconds < 3600:
                return f"{seconds/60:.1f} menit"
            else:
                return f"{seconds/3600:.1f} jam"
        return "Tidak diketahui"
        
    def analyze_system(self):
        """Analyze current system and generate recommendations"""
        os_name = f"{platform.system()} {platform.release()}"
        python_ver = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
        cpu_count = psutil.cpu_count()
        ram = psutil.virtual_memory()
        ram_gb = ram.total / (1024**3)
        ram_available_gb = ram.available / (1024**3)
        
        # Display current system
        self.current_system_text.delete(1.0, tk.END)
        sys_info = f"""
╔══════════════════════════════════════════════════════════════╗
║                    INFORMASI SISTEM SAAT INI                 ║
╠══════════════════════════════════════════════════════════════╣
║  OS              : {os_name:<46} ║
║  Python Version  : {python_ver:<46} ║
║  CPU Cores       : {cpu_count:<46} ║
║  RAM Total       : {ram_gb:.2f} GB{' ' * (40 - len(f'{ram_gb:.2f} GB'))}║
║  RAM Available   : {ram_available_gb:.2f} GB{' ' * (40 - len(f'{ram_available_gb:.2f} GB'))}║
║  Architecture    : {platform.machine():<46} ║
╚══════════════════════════════════════════════════════════════╝
        """
        self.current_system_text.insert(1.0, sys_info, "normal")
        
        if ram_gb < 4:
            self.current_system_text.insert(tk.END, "\n⚠️ PERINGATAN: RAM rendah! (Minimal 4 GB direkomendasikan)", "warning")
        elif ram_gb >= 8:
            self.current_system_text.insert(tk.END, "\n✓ RAM memadai untuk sebagian besar program", "success")
            
        # Recommendations
        self.recommendation_text.delete(1.0, tk.END)
        recommendations = []
        
        recommendations.append("╔══════════════════════════════════════════════════════════════╗\n")
        recommendations.append("║                    REKOMENDASI SISTEM                       ║\n")
        recommendations.append("╠══════════════════════════════════════════════════════════════╣\n")
        
        if ram_gb < 4:
            recommendations.append("║  ⚠ RAM: Kurang dari 4 GB                                   ║\n")
            recommendations.append("║    → Upgrade ke minimal 4 GB untuk program Python standar  ║\n")
        elif ram_gb < 8:
            recommendations.append("║  ✓ RAM: Cukup untuk program sederhana                      ║\n")
            recommendations.append("║    → Upgrade ke 8 GB untuk machine learning/AI            ║\n")
        else:
            recommendations.append("║  ✓ RAM: Memadai untuk sebagian besar program Python        ║\n")
            
        if cpu_count < 4:
            recommendations.append("║  ⚠ CPU: Kurang dari 4 core                                 ║\n")
            recommendations.append("║    → Minimal 4 core direkomendasikan untuk multitasking    ║\n")
        else:
            recommendations.append("║  ✓ CPU: Memadai untuk parallel processing                  ║\n")
            
        if python_ver < "3.8":
            recommendations.append("║  ⚠ Python: Versi {:<5} (kuno)                              ║\n".format(python_ver))
            recommendations.append("║    → Upgrade ke Python 3.8+ untuk kompatibilitas terbaik   ║\n")
        else:
            recommendations.append("║  ✓ Python: Versi {:<5} (modern)                            ║\n".format(python_ver))
            
        recommendations.append("╚══════════════════════════════════════════════════════════════╝")
        
        self.recommendation_text.insert(1.0, "".join(recommendations))
        self.log_event("SYS_INFO", "system_data", f"os={os_name} python={python_ver} ram={ram_gb:.2f}gb cpu={cpu_count}")
        
    def upload_file(self):
        """Upload Python file for analysis"""
        file_path = filedialog.askopenfilename(
            title="Pilih file Python",
            filetypes=[("Python files", "*.py"), ("All files", "*.*")]
        )
        
        if file_path:
            self.program_path = file_path
            self.file_label.config(text=os.path.basename(file_path), fg=self.colors['success'])
            
            with open(file_path, 'r', encoding='utf-8') as f:
                self.program_code = f.read()
            
            self.analyze_libraries()
            
            self.log_event("UPLOAD", "file_selected", f"path={file_path}")
            self.update_backend(f"📁 Program diupload: {os.path.basename(file_path)}", "success")
            self.update_terminal_info(f"📂 FILE UPLOAD: {os.path.basename(file_path)}", "success")
            self.update_terminal_info(f"   Lokasi: {file_path}", "info")
            
    def get_library_version(self, lib_name):
        """Get library version using importlib.metadata"""
        try:
            if sys.version_info >= (3, 8):
                return get_version(lib_name)
            else:
                return "Unknown"
        except PackageNotFoundError:
            return None
        except Exception:
            return None
            
    def analyze_libraries(self):
        """Analyze required libraries from program"""
        if not self.program_code:
            return
            
        for item in self.library_tree.get_children():
            self.library_tree.delete(item)
            
        try:
            tree = ast.parse(self.program_code)
            imports = set()
            
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.add(alias.name.split('.')[0])
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        imports.add(node.module.split('.')[0])
        except SyntaxError as e:
            self.update_backend(f"Error parsing program: {e}", "error")
            return
            
        stdlib_modules = {'sys', 'os', 're', 'math', 'random', 'datetime', 'json', 
                         'csv', 'sqlite3', 'threading', 'multiprocessing', 'subprocess',
                         'socket', 'http', 'urllib', 'tkinter', 'collections', 'itertools',
                         'functools', 'typing', 'pathlib', 'argparse', 'logging', 'unittest'}
            
        for lib in sorted(imports):
            is_standard = lib in stdlib_modules or lib in sys.stdlib_module_names if hasattr(sys, 'stdlib_module_names') else False
            
            if is_standard:
                status = "✓ Built-in"
                version = "-"
                rec = "Tersedia secara default"
                tag = 'gray'
            else:
                try:
                    module = importlib.util.find_spec(lib)
                    if module:
                        version = self.get_library_version(lib)
                        if version:
                            status = "✓ Tersedia"
                            rec = "Siap digunakan"
                            tag = 'success'
                        else:
                            status = "✓ Tersedia"
                            rec = "Siap digunakan (versi tidak terdeteksi)"
                            tag = 'success'
                    else:
                        status = "✗ Tidak tersedia"
                        version = "-"
                        rec = f"pip install {lib}"
                        tag = 'error'
                except Exception:
                    status = "? Tidak diketahui"
                    version = "-"
                    rec = "Periksa manual"
                    tag = 'warning'
                    
            self.library_tree.insert('', 'end', values=(lib, version, status, rec), tags=(tag,))
            self.log_event("LIB_CHECK", lib, f"version={version} status={status}")
            
    def run_program(self):
        """Run the uploaded program"""
        if not self.program_path:
            messagebox.showwarning("Peringatan", "Silakan upload file Python terlebih dahulu!")
            return
            
        if self.process and self.process.poll() is None:
            messagebox.showwarning("Peringatan", "Program sedang berjalan!")
            return
            
        self.frontend_text.delete(1.0, tk.END)
        
        # Update terminal info
        self.current_program_path = self.program_path
        self.program_start_time = datetime.now()
        
        self.update_terminal_info("="*60, "header")
        self.update_terminal_info("🚀 MEMULAI PROGRAM", "header")
        self.update_terminal_info("="*60, "header")
        self.update_terminal_info(f"📁 File: {os.path.basename(self.program_path)}", "info")
        self.update_terminal_info(f"📂 Lokasi: {self.program_path}", "info")
        
        self.run_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.NORMAL)
        self.end_btn.config(state=tk.NORMAL)
        
        try:
            self.process = subprocess.Popen(
                [sys.executable, self.program_path],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                stdin=subprocess.PIPE,
                text=True,
                bufsize=1,
                universal_newlines=True
            )
            
            self.current_pid = self.process.pid
            self.monitoring = True
            self.monitor_thread = threading.Thread(target=self.monitor_program, daemon=True)
            self.monitor_thread.start()
            
            self.update_terminal_info(f"🆔 Process ID (PID): {self.current_pid}", "pid")
            self.update_terminal_info(f"⏰ Waktu mulai: {self.program_start_time.strftime('%Y-%m-%d %H:%M:%S')}", "info")
            self.update_terminal_info(f"💻 Python: {sys.executable}", "info")
            self.update_terminal_info("-"*60, "info")
            self.update_terminal_info(f"▶ Program sedang berjalan...", "success")
            
            self.log_event("RUN", "program_started", f"pid={self.process.pid} path={self.program_path}")
            self.update_backend(f"▶ Program dimulai (PID: {self.process.pid})", "success")
            self.status_label.config(text="⚙ Status: RUNNING", fg=self.colors['success'])
            
        except Exception as e:
            self.update_terminal_info(f"❌ ERROR: {str(e)}", "error")
            messagebox.showerror("Error", f"Gagal menjalankan program: {str(e)}")
            self.run_btn.config(state=tk.NORMAL)
            self.stop_btn.config(state=tk.DISABLED)
            self.end_btn.config(state=tk.DISABLED)
            self.log_event("ERROR", "run_failed", str(e))
            
    def monitor_program(self):
        """Monitor running program and capture output"""
        def read_stdout():
            while self.monitoring and self.process:
                try:
                    line = self.process.stdout.readline()
                    if not line:
                        break
                    self.log_queue.put({
                        'type': 'stdout',
                        'data': line.rstrip()
                    })
                except:
                    break
                    
        def read_stderr():
            while self.monitoring and self.process:
                try:
                    line = self.process.stderr.readline()
                    if not line:
                        break
                    self.log_queue.put({
                        'type': 'stderr',
                        'data': line.rstrip()
                    })
                except:
                    break
        
        stdout_thread = threading.Thread(target=read_stdout, daemon=True)
        stderr_thread = threading.Thread(target=read_stderr, daemon=True)
        stdout_thread.start()
        stderr_thread.start()
        
        last_resource_log = time.time()
        
        while self.monitoring and self.process and self.process.poll() is None:
            if time.time() - last_resource_log > 2:
                try:
                    proc = psutil.Process(self.process.pid)
                    cpu = proc.cpu_percent(interval=0.1)
                    mem = proc.memory_info().rss / (1024 * 1024)
                    
                    self.log_queue.put({
                        'type': 'resource',
                        'cpu': cpu,
                        'mem': mem
                    })
                    last_resource_log = time.time()
                except:
                    pass
            time.sleep(0.5)
        
        if self.process and self.process.poll() is not None:
            exit_code = self.process.poll()
            self.log_queue.put({
                'type': 'process_end',
                'exit_code': exit_code
            })
        
        self.monitoring = False
        
    def stop_program(self):
        """Stop the running program (SIGTERM)"""
        if self.process and self.process.poll() is None:
            try:
                self.update_terminal_info(f"⏹ Menghentikan program (SIGTERM)...", "warning")
                
                self.process.terminate()
                self.process.wait(timeout=5)
                
                self.update_terminal_info(f"✅ Program dihentikan (PID: {self.current_pid})", "success")
                self.update_terminal_info(f"⏱ Durasi berjalan: {self.get_program_duration()}", "info")
                
                self.log_event("STOP", "program_terminated", f"pid={self.process.pid}")
                self.update_backend("⏹ Program dihentikan (SIGTERM)", "warning")
                self.status_label.config(text="⚙ Status: STOPPED", fg=self.colors['warning'])
                
            except subprocess.TimeoutExpired:
                self.process.kill()
                self.update_terminal_info(f"⚠ Program di-kill karena timeout!", "error")
                self.log_event("STOP", "program_killed", "timeout")
                self.update_backend("⚠ Program di-kill karena timeout", "error")
            finally:
                self.cleanup_process()
                
    def end_program(self):
        """Force end the running program (SIGKILL)"""
        if self.process and self.process.poll() is None:
            try:
                self.update_terminal_info(f"⏏ MEMAKSA BERHENTI (SIGKILL)...", "error")
                
                self.process.kill()
                self.process.wait(timeout=2)
                
                self.update_terminal_info(f"⚠ Program dipaksa berhenti (PID: {self.current_pid})", "error")
                self.update_terminal_info(f"⏱ Durasi berjalan: {self.get_program_duration()}", "info")
                
                self.log_event("END", "program_killed", f"pid={self.process.pid}")
                self.update_backend("⏏ Program dipaksa berhenti (SIGKILL)", "error")
                self.status_label.config(text="⚙ Status: KILLED", fg=self.colors['error'])
            except Exception as e:
                self.update_terminal_info(f"❌ Gagal kill: {str(e)}", "error")
                self.log_event("ERROR", "kill_failed", str(e))
            finally:
                self.cleanup_process()
                
    def cleanup_process(self):
        """Clean up process resources"""
        if self.process:
            try:
                self.process.stdout.close()
                self.process.stderr.close()
                self.process.stdin.close()
            except:
                pass
            self.process = None
        
        if self.monitoring:
            self.update_terminal_info("-"*60, "info")
            self.update_terminal_info(f"🏁 PROGRAM SELESAI", "header")
            self.update_terminal_info(f"⏱ Total durasi: {self.get_program_duration()}", "info")
            self.update_terminal_info("="*60, "header")
            
        self.monitoring = False
        self.current_pid = None
        self.run_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)
        self.end_btn.config(state=tk.DISABLED)
        
    def process_log_queue(self):
        """Process logs from queue and update GUI"""
        try:
            while True:
                item = self.log_queue.get_nowait()
                
                if item.get('type') == 'stdout':
                    self.frontend_text.insert(tk.END, f"{item['data']}\n", "stdout")
                    self.frontend_text.see(tk.END)
                    self.log_event("FRONTEND", "stdout", item['data'])
                    
                elif item.get('type') == 'stderr':
                    self.frontend_text.insert(tk.END, f"{item['data']}\n", "stderr")
                    self.frontend_text.see(tk.END)
                    self.log_event("FRONTEND", "stderr", item['data'])
                    
                elif item.get('type') == 'resource':
                    self.update_backend(f"💻 CPU: {item['cpu']:.1f}% | RAM: {item['mem']:.1f} MB", "info")
                    self.update_terminal_info(f"💻 CPU: {item['cpu']:.1f}% | RAM: {item['mem']:.1f} MB", "info")
                    self.log_event("BACKEND", "resource", f"cpu={item['cpu']:.1f} mem={item['mem']:.1f}")
                    
                elif item.get('type') == 'process_end':
                    if item['exit_code'] == 0:
                        self.update_backend(f"✅ Program berhenti normal (exit code: {item['exit_code']})", "success")
                        self.update_terminal_info(f"✅ Program berhenti normal (exit code: {item['exit_code']})", "success")
                    else:
                        self.update_backend(f"⚠ Program berhenti dengan error (exit code: {item['exit_code']})", "error")
                        self.update_terminal_info(f"⚠ Program berhenti dengan error (exit code: {item['exit_code']})", "error")
                    self.log_event("BACKEND", "process_end", f"exit_code={item['exit_code']}")
                    self.cleanup_process()
                    self.status_label.config(text="⚙ Status: SELESAI", fg=self.colors['gray'])
                    
                elif 'full_line' in item:
                    self.log_summary.insert(tk.END, item['full_line'])
                    self.log_summary.see(tk.END)
                    if int(self.log_summary.index('end-1c').split('.')[0]) > 50:
                        self.log_summary.delete(1.0, 2.0)
                        
        except queue.Empty:
            pass
        finally:
            self.root.after(100, self.process_log_queue)
            
    def update_backend(self, message, tag="info"):
        """Update backend text widget"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.backend_text.insert(tk.END, f"[{timestamp}] {message}\n", tag)
        self.backend_text.see(tk.END)
        
    def save_log(self):
        """Save current log file with final summary"""
        if self.log_file and self.log_file.exists():
            with open(self.log_file, 'a', encoding='utf-8') as f:
                f.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]}] [SESSION_END] log_saved=True\n")
            
            messagebox.showinfo("Sukses", f"Log berhasil disimpan di:\n{self.log_file}")
            self.log_event("SAVE", "log_saved", f"path={self.log_file}")
            self.update_terminal_info(f"💾 LOG DISIMPAN: {self.log_file}", "success")
        else:
            messagebox.showerror("Error", "Log file tidak ditemukan!")

def main():
    root = tk.Tk()
    app = PythonProgramMonitor(root)
    
    try:
        import psutil
    except ImportError:
        root.after(100, lambda: messagebox.showwarning("Library Missing", 
                    "Install psutil: pip install psutil\n\nBeberapa fitur monitoring resource mungkin terbatas."))
    
    root.mainloop()

if __name__ == "__main__":
    main()