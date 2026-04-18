import threading
import time
import tkinter as tk
from tkinter import messagebox, scrolledtext, ttk
from urllib.parse import urlparse

import httpx
import requests
import speedtest

_BG = "#0d1117"
_SURFACE = "#161b22"
_SURFACE2 = "#21262d"
_BORDER = "#30363d"
_ACCENT = "#58a6ff"
_SUCCESS = "#3fb950"
_ERROR = "#f85149"
_TEXT = "#c9d1d9"
_TEXT_DIM = "#8b949e"
_TEXT_BRIGHT = "#f0f6fc"
_ROW_OK = "#0d2818"
_ROW_FAIL = "#2d1616"


class ProxySpeedTester:
    def __init__(self, root):
        self.root = root
        self.root.title("ProSpeed — Proxy Speed Tester")
        self.root.geometry("1100x780")
        self.root.minsize(900, 600)
        self.root.resizable(True, True)
        self.root.configure(bg=_BG)

        self.system_speed = None
        self.testing = False
        self._proxy_total = 0
        self._proxy_done = 0

        self._configure_styles()
        self.setup_ui()

    def _configure_styles(self):
        style = ttk.Style()
        style.theme_use("clam")

        style.configure(".", background=_BG, foreground=_TEXT, font=("Segoe UI", 9))
        style.configure("TFrame", background=_BG)

        style.configure(
            "TLabelframe", background=_SURFACE, bordercolor=_BORDER,
            relief="groove", lightcolor=_BORDER, darkcolor=_BORDER,
        )
        style.configure(
            "TLabelframe.Label", background=_SURFACE, foreground=_ACCENT,
            font=("Segoe UI", 9, "bold"),
        )

        style.configure("TLabel", background=_SURFACE, foreground=_TEXT, font=("Segoe UI", 9))
        style.configure("Dim.TLabel", background=_SURFACE, foreground=_TEXT_DIM, font=("Segoe UI", 8))

        style.configure(
            "TButton", background=_SURFACE2, foreground=_TEXT, relief="flat",
            borderwidth=1, bordercolor=_BORDER, font=("Segoe UI", 9), padding=(10, 5),
        )
        style.map(
            "TButton",
            background=[("active", _BORDER), ("disabled", _SURFACE)],
            foreground=[("disabled", _TEXT_DIM)],
        )

        style.configure(
            "Primary.TButton", background="#238636", foreground="#ffffff",
            font=("Segoe UI", 9, "bold"), padding=(12, 5),
        )
        style.map(
            "Primary.TButton",
            background=[("active", "#2ea043"), ("disabled", _SURFACE2)],
            foreground=[("disabled", _TEXT_DIM)],
        )

        style.configure(
            "Danger.TButton", background="#b91c1c", foreground="#ffffff",
            font=("Segoe UI", 9, "bold"), padding=(12, 5),
        )
        style.map(
            "Danger.TButton",
            background=[("active", _ERROR), ("disabled", _SURFACE2)],
            foreground=[("disabled", _TEXT_DIM)],
        )

        style.configure(
            "Info.TButton", background="#1d4ed8", foreground="#ffffff",
            font=("Segoe UI", 9), padding=(10, 5),
        )
        style.map(
            "Info.TButton",
            background=[("active", "#2563eb"), ("disabled", _SURFACE2)],
            foreground=[("disabled", _TEXT_DIM)],
        )

        style.configure(
            "TProgressbar", background=_ACCENT, troughcolor=_SURFACE2,
            bordercolor=_BORDER, lightcolor=_ACCENT, darkcolor=_ACCENT,
        )

        style.configure(
            "Treeview", background=_SURFACE, fieldbackground=_SURFACE,
            foreground=_TEXT, bordercolor=_BORDER, relief="flat",
            font=("Segoe UI", 9), rowheight=26,
        )
        style.configure(
            "Treeview.Heading", background=_SURFACE2, foreground=_ACCENT,
            font=("Segoe UI", 9, "bold"), relief="flat",
        )
        style.map(
            "Treeview",
            background=[("selected", "#1f6feb")],
            foreground=[("selected", _TEXT_BRIGHT)],
        )
        style.map("Treeview.Heading", background=[("active", _BORDER)])

        style.configure(
            "TScrollbar", background=_SURFACE2, bordercolor=_BORDER,
            arrowcolor=_TEXT_DIM, troughcolor=_SURFACE, relief="flat",
        )
        style.map("TScrollbar", background=[("active", _BORDER)])

    def setup_ui(self):
        # Header bar
        header = tk.Frame(self.root, bg="#010409", height=50)
        header.pack(fill=tk.X, side=tk.TOP)
        header.pack_propagate(False)

        tk.Label(
            header, text="ProSpeed", bg="#010409", fg=_TEXT_BRIGHT,
            font=("Segoe UI", 15, "bold"),
        ).pack(side=tk.LEFT, padx=16, pady=10)

        tk.Label(
            header, text="Proxy Speed Tester", bg="#010409", fg=_TEXT_DIM,
            font=("Segoe UI", 10),
        ).pack(side=tk.LEFT, pady=14)

        # Status bar
        status_bar = tk.Frame(self.root, bg=_SURFACE2, height=26)
        status_bar.pack(fill=tk.X, side=tk.BOTTOM)
        status_bar.pack_propagate(False)

        self.status_var = tk.StringVar(value="Ready")
        tk.Label(
            status_bar, textvariable=self.status_var,
            bg=_SURFACE2, fg=_TEXT_DIM, font=("Segoe UI", 8), anchor="w",
        ).pack(side=tk.LEFT, padx=12, pady=4)

        self.counter_var = tk.StringVar(value="")
        tk.Label(
            status_bar, textvariable=self.counter_var,
            bg=_SURFACE2, fg=_TEXT_DIM, font=("Segoe UI", 8), anchor="e",
        ).pack(side=tk.RIGHT, padx=12, pady=4)

        # Main content
        main_frame = ttk.Frame(self.root, padding="12")
        main_frame.pack(fill=tk.BOTH, expand=True)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(4, weight=1)

        # System Bandwidth
        system_frame = ttk.LabelFrame(main_frame, text="  System Bandwidth", padding="10")
        system_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 8))
        system_frame.columnconfigure(0, weight=1)

        self.system_label = ttk.Label(
            system_frame,
            text="Click 'Test System Speed' to measure your direct connection",
            style="Dim.TLabel",
        )
        self.system_label.grid(row=0, column=0, sticky=tk.W, padx=(0, 12))

        self.test_system_btn = ttk.Button(
            system_frame, text="Test System Speed",
            command=self.test_system_speed, style="Info.TButton",
        )
        self.test_system_btn.grid(row=0, column=1, sticky=tk.E)

        # Proxy List
        input_frame = ttk.LabelFrame(main_frame, text="  Proxy List", padding="10")
        input_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 8))
        input_frame.columnconfigure(0, weight=1)

        ttk.Label(
            input_frame,
            text="One proxy per line  \u2022  Format: protocol://[user:pass@]host:port"
                 "  \u2022  Supported: http, https, socks4, socks5",
            style="Dim.TLabel",
        ).grid(row=0, column=0, sticky=tk.W, pady=(0, 6))

        self.proxy_input = scrolledtext.ScrolledText(
            input_frame, height=5, width=80,
            bg=_SURFACE2, fg=_TEXT, insertbackground=_TEXT_BRIGHT,
            relief="flat", borderwidth=0,
            highlightthickness=1, highlightbackground=_BORDER, highlightcolor=_ACCENT,
            font=("Consolas", 9),
            selectbackground="#1f6feb", selectforeground=_TEXT_BRIGHT,
        )
        self.proxy_input.grid(row=1, column=0, sticky=(tk.W, tk.E))

        # Control Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=2, column=0, sticky=tk.W, pady=(8, 8))

        self.test_btn = ttk.Button(
            button_frame, text="\u25b6  Test Proxies",
            command=self.start_testing, style="Primary.TButton",
        )
        self.test_btn.grid(row=0, column=0, padx=(0, 6))

        self.clear_btn = ttk.Button(
            button_frame, text="Clear Results", command=self.clear_results,
        )
        self.clear_btn.grid(row=0, column=1, padx=6)

        self.stop_btn = ttk.Button(
            button_frame, text="\u25a0  Stop",
            command=self.stop_testing, state=tk.DISABLED, style="Danger.TButton",
        )
        self.stop_btn.grid(row=0, column=2, padx=6)

        # Progress Bar
        self.progress = ttk.Progressbar(main_frame, mode="indeterminate")
        self.progress.grid(row=3, column=0, sticky=(tk.W, tk.E), pady=(0, 8))

        # Bottom: Log + Results
        bottom = ttk.Frame(main_frame)
        bottom.grid(row=4, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        bottom.columnconfigure(0, weight=1)
        bottom.rowconfigure(1, weight=1)

        log_frame = ttk.LabelFrame(bottom, text="  Activity Log", padding="6")
        log_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 8))
        log_frame.columnconfigure(0, weight=1)

        self.log_text = scrolledtext.ScrolledText(
            log_frame, height=4, state=tk.DISABLED,
            bg="#010409", fg=_TEXT_DIM,
            insertbackground=_TEXT_BRIGHT, relief="flat", borderwidth=0,
            font=("Consolas", 8), selectbackground="#1f6feb",
        )
        self.log_text.tag_configure("error", foreground=_ERROR)
        self.log_text.tag_configure("speed", foreground=_ACCENT)
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E))

        # Results Table
        results_frame = ttk.LabelFrame(bottom, text="  Test Results", padding="8")
        results_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        results_frame.columnconfigure(0, weight=1)
        results_frame.rowconfigure(0, weight=1)

        columns = (
            "Proxy", "IP Address", "Country", "City", "ISP",
            "Download (Mbps)", "Upload (Mbps)", "Latency (ms)", "Status",
        )
        self.tree = ttk.Treeview(results_frame, columns=columns, show="headings", height=12)

        col_widths = {
            "Proxy": 200, "IP Address": 115, "Country": 90, "City": 90, "ISP": 155,
            "Download (Mbps)": 115, "Upload (Mbps)": 105, "Latency (ms)": 90, "Status": 75,
        }
        col_anchors = {
            "Download (Mbps)": tk.CENTER, "Upload (Mbps)": tk.CENTER,
            "Latency (ms)": tk.CENTER, "Status": tk.CENTER,
        }
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=col_widths.get(col, 100), anchor=col_anchors.get(col, tk.W))

        self.tree.tag_configure("ok", background=_ROW_OK)
        self.tree.tag_configure("failed", background=_ROW_FAIL)

        scrollbar = ttk.Scrollbar(results_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)

        self.tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))

    def log(self, msg):
        import datetime
        ts = datetime.datetime.now().strftime("%H:%M:%S")
        self.log_text.config(state=tk.NORMAL)
        line = f"[{ts}] {msg}\n"
        msg_lower = msg.lower()
        if "error" in msg_lower or "failed" in msg_lower:
            self.log_text.insert(tk.END, line, "error")
        elif "download:" in msg_lower or "upload:" in msg_lower or "latency:" in msg_lower:
            self.log_text.insert(tk.END, line, "speed")
        else:
            self.log_text.insert(tk.END, line)
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)

    def test_system_speed(self):
        def run_test():
            self.test_system_btn.config(state=tk.DISABLED)
            self.system_label.config(text="Testing system speed...")

            try:
                system_info = self.get_system_info()
                download_speed, upload_speed, latency = self.measure_speed(None)

                self.system_speed = {
                    "ip": system_info["ip"],
                    "country": system_info["country"],
                    "city": system_info["city"],
                    "isp": system_info["isp"],
                    "download": download_speed,
                    "upload": upload_speed,
                    "latency": latency,
                }

                self.system_label.config(
                    text=f"IP: {system_info['ip']}  \u2022  {system_info['country']}, {system_info['city']}"
                    f"  \u2022  {system_info['isp']}"
                    f"  \u2022  \u2193 {download_speed:.2f} Mbps"
                    f"  \u2022  \u2191 {upload_speed:.2f} Mbps"
                    f"  \u2022  {latency:.0f} ms"
                )
            except Exception as e:
                self.system_label.config(text=f"Error: {str(e)}")
            finally:
                self.test_system_btn.config(state=tk.NORMAL)

        threading.Thread(target=run_test, daemon=True).start()

    def get_system_info(self):
        try:
            response = requests.get("http://ip-api.com/json", timeout=10)
            if response.status_code == 200:
                data = response.json()
                return {
                    "country": data.get("country", "Unknown"),
                    "city": data.get("city", "Unknown"),
                    "isp": data.get("isp", "Unknown"),
                    "ip": data.get("query", "Unknown"),
                }
        except Exception as e:
            print(f"Error getting system info: {e}")

        return {"country": "Unknown", "city": "Unknown", "isp": "Unknown", "ip": "Unknown"}

    def parse_proxy(self, proxy_string):
        proxy_string = proxy_string.strip()
        if not proxy_string:
            return None

        try:
            parsed = urlparse(proxy_string)
            protocol = parsed.scheme if parsed.scheme else "http"
            host = parsed.hostname
            port = parsed.port

            if not host or not port:
                return None

            return {
                "protocol": protocol,
                "host": host,
                "port": port,
                "username": parsed.username,
                "password": parsed.password,
                "full": proxy_string,
            }
        except Exception:
            return None

    def check_proxy_info(self, proxy_dict):
        try:
            proxies = {"http": proxy_dict["full"], "https": proxy_dict["full"]}
            response = requests.get("http://ip-api.com/json", proxies=proxies, timeout=10)
            if response.status_code == 200:
                data = response.json()
                return {
                    "country": data.get("country", "Unknown"),
                    "city": data.get("city", "Unknown"),
                    "isp": data.get("isp", "Unknown"),
                    "ip": data.get("query", "Unknown"),
                }
        except Exception as e:
            print(f"Error checking proxy info: {e}")

        return {"country": "Unknown", "city": "Unknown", "isp": "Unknown", "ip": "Unknown"}

    def measure_speed(self, proxy_dict):
        try:
            if proxy_dict:
                return self._measure_speed_with_speedtest_proxy(proxy_dict)

            st = speedtest.Speedtest()
            st.get_best_server()
            latency = st.results.ping
            download_speed_mbps = st.download() / 1_000_000
            upload_speed_mbps = st.upload() / 1_000_000
            return download_speed_mbps, upload_speed_mbps, latency

        except Exception as e:
            print(f"Speedtest error: {e}")
            return 0, 0, 9999

    def _measure_speed_with_speedtest_proxy(self, proxy_dict):
        try:
            if proxy_dict.get("username") and proxy_dict.get("password"):
                proxy_url = (
                    f"{proxy_dict['protocol']}://{proxy_dict['username']}:"
                    f"{proxy_dict['password']}@{proxy_dict['host']}:{proxy_dict['port']}"
                )
            else:
                proxy_url = f"{proxy_dict['protocol']}://{proxy_dict['host']}:{proxy_dict['port']}"

            proxy_label = f"{proxy_dict['host']}:{proxy_dict['port']}"
            headers = {
                "User-Agent": (
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
                )
            }

            with httpx.Client(proxy=proxy_url, timeout=60.0, headers=headers) as client:
                base = "https://speed.cloudflare.com"

                self.root.after(0, self.log, f"[{proxy_label}] Measuring latency...")
                latency_tests = []
                for _ in range(3):
                    start = time.time()
                    client.get(f"{base}/__down?bytes=0")
                    latency_tests.append((time.time() - start) * 1000)
                latency = sum(latency_tests) / len(latency_tests)
                self.root.after(0, self.log, f"[{proxy_label}] Latency: {latency:.1f} ms")

                self.root.after(0, self.log, f"[{proxy_label}] Measuring download...")
                total_bytes = 0
                start_time = time.time()
                for chunk in [1_000_000, 5_000_000, 10_000_000, 25_000_000]:
                    resp = client.get(f"{base}/__down?bytes={chunk}")
                    total_bytes += len(resp.content)
                download_time = time.time() - start_time
                download_speed_mbps = (total_bytes * 8) / (download_time * 1_000_000)
                self.root.after(0, self.log, f"[{proxy_label}] Download: {download_speed_mbps:.2f} Mbps")

                self.root.after(0, self.log, f"[{proxy_label}] Measuring upload...")
                total_uploaded = 0
                start_time = time.time()
                for chunk in [1_000_000, 5_000_000, 10_000_000]:
                    client.post(f"{base}/__up", content=b"0" * chunk)
                    total_uploaded += chunk
                upload_time = time.time() - start_time
                upload_speed_mbps = (total_uploaded * 8) / (upload_time * 1_000_000)
                self.root.after(0, self.log, f"[{proxy_label}] Upload: {upload_speed_mbps:.2f} Mbps")

                return download_speed_mbps, upload_speed_mbps, latency

        except Exception as e:
            proxy_label = f"{proxy_dict.get('host', '?')}:{proxy_dict.get('port', '?')}"
            self.root.after(0, self.log, f"[{proxy_label}] ERROR: {type(e).__name__}: {e}")
            return 0, 0, 9999

    def test_proxy(self, proxy_string):
        proxy_dict = self.parse_proxy(proxy_string)

        if not proxy_dict:
            return {
                "proxy": proxy_string, "ip": "Invalid", "country": "Invalid",
                "city": "Invalid", "isp": "Invalid",
                "download": 0, "upload": 0, "latency": 0, "status": "Failed",
            }

        try:
            proxy_label = f"{proxy_dict['host']}:{proxy_dict['port']}"
            self.root.after(0, self.log, f"[{proxy_label}] Checking IP info...")
            info = self.check_proxy_info(proxy_dict)
            self.root.after(
                0, self.log,
                f"[{proxy_label}] IP: {info['ip']} ({info['country']}, {info['isp']})",
            )

            download, upload, latency = self.measure_speed(proxy_dict)
            status = "OK" if download > 0 and latency < 10000 else "Slow/Failed"

            return {
                "proxy": proxy_string, "ip": info["ip"],
                "country": info["country"], "city": info["city"], "isp": info["isp"],
                "download": download, "upload": upload, "latency": latency, "status": status,
            }
        except Exception as e:
            self.root.after(0, self.log, f"[{proxy_string}] FAILED: {type(e).__name__}: {e}")
            return {
                "proxy": proxy_string, "ip": "Error", "country": "Error",
                "city": "Error", "isp": "Error",
                "download": 0, "upload": 0, "latency": 0, "status": "Failed",
            }

    def start_testing(self):
        proxy_list = self.proxy_input.get("1.0", tk.END).strip().split("\n")
        proxy_list = [p.strip() for p in proxy_list if p.strip()]

        if not proxy_list:
            messagebox.showwarning("Warning", "Please enter at least one proxy")
            return

        self._proxy_total = len(proxy_list)
        self._proxy_done = 0
        self.status_var.set(f"Testing {self._proxy_total} proxy(ies)...")
        self.counter_var.set(f"0 / {self._proxy_total}")

        self.testing = True
        self.test_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.NORMAL)
        self.progress.start()

        def run_tests():
            for proxy in proxy_list:
                if not self.testing:
                    break
                result = self.test_proxy(proxy)
                self._proxy_done += 1
                self.root.after(0, self.counter_var.set, f"{self._proxy_done} / {self._proxy_total}")
                self.root.after(0, self.add_result, result)
            self.root.after(0, self.finish_testing)

        threading.Thread(target=run_tests, daemon=True).start()

    def add_result(self, result):
        self.tree.insert(
            "", tk.END,
            values=(
                result["proxy"], result["ip"], result["country"], result["city"],
                result["isp"],
                f"{result['download']:.2f}", f"{result['upload']:.2f}",
                f"{result['latency']:.2f}", result["status"],
            ),
        )
        item = self.tree.get_children()[-1]
        self.tree.item(item, tags=("ok" if result["status"] == "OK" else "failed",))

    def finish_testing(self):
        self.testing = False
        self.test_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)
        self.progress.stop()
        self.status_var.set("Testing complete")
        messagebox.showinfo("Complete", "Proxy testing completed!")

    def stop_testing(self):
        self.testing = False
        self.test_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)
        self.progress.stop()
        self.status_var.set("Testing stopped")

    def clear_results(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        self.counter_var.set("")
        self.status_var.set("Ready")
