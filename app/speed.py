import random
import threading
import time
import tkinter as tk
from tkinter import messagebox, scrolledtext, ttk
from urllib.parse import urlparse

import httpx
import requests
import speedtest


class ProxySpeedTester:
    def __init__(self, root):
        self.root = root
        self.root.title("Proxy Speed Tester")
        self.root.geometry("1000x700")
        self.root.resizable(True, True)

        self.system_speed = None
        self.testing = False

        self.setup_ui()

    def setup_ui(self):
        # Main container
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(5, weight=1)

        # System bandwidth section
        system_frame = ttk.LabelFrame(main_frame, text="System Bandwidth", padding="10")
        system_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        system_frame.columnconfigure(1, weight=1)

        self.system_label = ttk.Label(system_frame, text="Not tested yet")
        self.system_label.grid(row=0, column=0, sticky=tk.W, padx=(0, 10))

        self.test_system_btn = ttk.Button(
            system_frame, text="Test System Speed", command=self.test_system_speed
        )
        self.test_system_btn.grid(row=0, column=1, sticky=tk.E)

        # Proxy input section
        input_frame = ttk.LabelFrame(main_frame, text="Proxy List Input", padding="10")
        input_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        input_frame.columnconfigure(0, weight=1)

        ttk.Label(
            input_frame,
            text="Enter proxies (format: protocol://ip:port or protocol://user:pass@ip:port)",
        ).grid(row=0, column=0, sticky=tk.W, pady=(0, 5))
        ttk.Label(
            input_frame,
            text="Example: socks5://192.168.1.1:1080 or http://user:pass@192.168.1.1:8080",
        ).grid(row=1, column=0, sticky=tk.W, pady=(0, 5))

        self.proxy_input = scrolledtext.ScrolledText(input_frame, height=6, width=80)
        self.proxy_input.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(5, 0))

        # Control buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(0, 10))

        self.test_btn = ttk.Button(
            button_frame, text="Test Proxies", command=self.start_testing
        )
        self.test_btn.grid(row=0, column=0, padx=(0, 5))

        self.clear_btn = ttk.Button(
            button_frame, text="Clear Results", command=self.clear_results
        )
        self.clear_btn.grid(row=0, column=1, padx=5)

        self.stop_btn = ttk.Button(
            button_frame, text="Stop", command=self.stop_testing, state=tk.DISABLED
        )
        self.stop_btn.grid(row=0, column=2, padx=5)

        # Progress bar
        self.progress = ttk.Progressbar(main_frame, mode="indeterminate")
        self.progress.grid(row=3, column=0, sticky=(tk.W, tk.E), pady=(0, 10))

        # Log section
        log_frame = ttk.LabelFrame(main_frame, text="Log", padding="5")
        log_frame.grid(row=4, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        log_frame.columnconfigure(0, weight=1)

        self.log_text = scrolledtext.ScrolledText(log_frame, height=5, state=tk.DISABLED, font=("Consolas", 9))
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E))

        # Results section
        results_frame = ttk.LabelFrame(main_frame, text="Test Results", padding="10")
        results_frame.grid(row=5, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        results_frame.columnconfigure(0, weight=1)
        results_frame.rowconfigure(0, weight=1)

        # Create Treeview for results
        columns = (
            "Proxy",
            "IP Address",
            "Country",
            "City",
            "ISP",
            "Download (Mbps)",
            "Upload (Mbps)",
            "Latency (ms)",
            "Status",
        )
        self.tree = ttk.Treeview(
            results_frame, columns=columns, show="headings", height=15
        )

        # Configure columns
        self.tree.heading("Proxy", text="Proxy")
        self.tree.heading("IP Address", text="IP Address")
        self.tree.heading("Country", text="Country")
        self.tree.heading("City", text="City")
        self.tree.heading("ISP", text="ISP")
        self.tree.heading("Download (Mbps)", text="Download (Mbps)")
        self.tree.heading("Upload (Mbps)", text="Upload (Mbps)")
        self.tree.heading("Latency (ms)", text="Latency (ms)")
        self.tree.heading("Status", text="Status")

        self.tree.column("Proxy", width=200)
        self.tree.column("IP Address", width=120)
        self.tree.column("Country", width=100)
        self.tree.column("City", width=100)
        self.tree.column("ISP", width=150)
        self.tree.column("Download (Mbps)", width=120)
        self.tree.column("Upload (Mbps)", width=120)
        self.tree.column("Latency (ms)", width=100)
        self.tree.column("Status", width=80)

        # Scrollbar for Treeview
        scrollbar = ttk.Scrollbar(
            results_frame, orient=tk.VERTICAL, command=self.tree.yview
        )
        self.tree.configure(yscroll=scrollbar.set)

        self.tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))

    def log(self, msg):
        import datetime
        ts = datetime.datetime.now().strftime("%H:%M:%S")
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, f"[{ts}] {msg}\n")
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)

    def test_system_speed(self):
        def run_test():
            self.test_system_btn.config(state=tk.DISABLED)
            self.system_label.config(text="Testing system speed...")

            try:
                # Get system IP info
                system_info = self.get_system_info()

                # Measure speed
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
                    text=f"IP: {system_info['ip']} | {system_info['country']}, {system_info['city']} | {system_info['isp']} | "
                    f"Download: {download_speed:.2f} Mbps | Upload: {upload_speed:.2f} Mbps | Latency: {latency:.2f} ms"
                )
            except Exception as e:
                self.system_label.config(text=f"Error: {str(e)}")
            finally:
                self.test_system_btn.config(state=tk.NORMAL)

        threading.Thread(target=run_test, daemon=True).start()

    def get_system_info(self):
        """Get system IP information without proxy"""
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

        return {
            "country": "Unknown",
            "city": "Unknown",
            "isp": "Unknown",
            "ip": "Unknown",
        }

    def parse_proxy(self, proxy_string):
        """Parse proxy string and return protocol, host, port, username, password"""
        proxy_string = proxy_string.strip()
        if not proxy_string:
            return None

        try:
            parsed = urlparse(proxy_string)
            protocol = parsed.scheme if parsed.scheme else "http"
            username = parsed.username
            password = parsed.password
            host = parsed.hostname
            port = parsed.port

            if not host or not port:
                return None

            return {
                "protocol": protocol,
                "host": host,
                "port": port,
                "username": username,
                "password": password,
                "full": proxy_string,
            }
        except Exception:
            return None

    def check_proxy_info(self, proxy_dict):
        """Check proxy information using ip-api.com"""
        try:
            proxies = {"http": proxy_dict["full"], "https": proxy_dict["full"]}

            response = requests.get(
                "http://ip-api.com/json", proxies=proxies, timeout=10
            )

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

        return {
            "country": "Unknown",
            "city": "Unknown",
            "isp": "Unknown",
            "ip": "Unknown",
        }

    def measure_speed(self, proxy_dict):
        """Measure download/upload speed and latency using speedtest-cli"""
        try:
            # Use httpx-based speedtest for all proxy types (HTTP/HTTPS/SOCKS4/SOCKS5)
            if proxy_dict:
                return self._measure_speed_with_speedtest_proxy(proxy_dict)

            # No proxy - standard speedtest
            st = speedtest.Speedtest()

            # Measure latency (ping to best server)
            st.get_best_server()
            latency = st.results.ping

            # Measure download speed
            download_bps = st.download()
            download_speed_mbps = download_bps / 1_000_000

            # Measure upload speed
            upload_bps = st.upload()
            upload_speed_mbps = upload_bps / 1_000_000

            return download_speed_mbps, upload_speed_mbps, latency

        except Exception as e:
            print(f"Speedtest error: {e}")
            return 0, 0, 9999

    def _measure_speed_with_speedtest_proxy(self, proxy_dict):
        """Measure proxy speed using Cloudflare Speed Test (no rate limiting)"""
        try:
            if proxy_dict.get("username") and proxy_dict.get("password"):
                proxy_url = f"{proxy_dict['protocol']}://{proxy_dict['username']}:{proxy_dict['password']}@{proxy_dict['host']}:{proxy_dict['port']}"
            else:
                proxy_url = f"{proxy_dict['protocol']}://{proxy_dict['host']}:{proxy_dict['port']}"

            proxy_label = f"{proxy_dict['host']}:{proxy_dict['port']}"
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            }

            with httpx.Client(proxy=proxy_url, timeout=60.0, headers=headers) as client:
                base = "https://speed.cloudflare.com"

                # 1. Latency
                self.root.after(0, self.log, f"[{proxy_label}] Measuring latency...")
                latency_tests = []
                for _ in range(3):
                    start = time.time()
                    client.get(f"{base}/__down?bytes=0")
                    latency_tests.append((time.time() - start) * 1000)
                latency = sum(latency_tests) / len(latency_tests)
                self.root.after(0, self.log, f"[{proxy_label}] Latency: {latency:.1f} ms")

                # 2. Download test
                self.root.after(0, self.log, f"[{proxy_label}] Measuring download...")
                download_chunks = [1_000_000, 5_000_000, 10_000_000, 25_000_000]
                total_bytes = 0
                start_time = time.time()
                for chunk in download_chunks:
                    resp = client.get(f"{base}/__down?bytes={chunk}")
                    total_bytes += len(resp.content)
                download_time = time.time() - start_time
                download_speed_mbps = (total_bytes * 8) / (download_time * 1_000_000)
                self.root.after(0, self.log, f"[{proxy_label}] Download: {download_speed_mbps:.2f} Mbps")

                # 3. Upload test
                self.root.after(0, self.log, f"[{proxy_label}] Measuring upload...")
                upload_chunks = [1_000_000, 5_000_000, 10_000_000]
                total_uploaded = 0
                start_time = time.time()
                for chunk in upload_chunks:
                    data = b"0" * chunk
                    client.post(f"{base}/__up", content=data)
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
        """Test a single proxy and return results"""
        proxy_dict = self.parse_proxy(proxy_string)

        if not proxy_dict:
            return {
                "proxy": proxy_string,
                "ip": "Invalid",
                "country": "Invalid",
                "city": "Invalid",
                "isp": "Invalid",
                "download": 0,
                "upload": 0,
                "latency": 0,
                "status": "Failed",
            }

        try:
            proxy_label = f"{proxy_dict['host']}:{proxy_dict['port']}"
            self.root.after(0, self.log, f"[{proxy_label}] Checking IP info...")
            info = self.check_proxy_info(proxy_dict)
            self.root.after(0, self.log, f"[{proxy_label}] IP: {info['ip']} ({info['country']}, {info['isp']})")

            # Measure speed
            download, upload, latency = self.measure_speed(proxy_dict)

            status = "OK" if download > 0 and latency < 10000 else "Slow/Failed"

            return {
                "proxy": proxy_string,
                "ip": info["ip"],
                "country": info["country"],
                "city": info["city"],
                "isp": info["isp"],
                "download": download,
                "upload": upload,
                "latency": latency,
                "status": status,
            }
        except Exception as e:
            self.root.after(0, self.log, f"[{proxy_string}] FAILED: {type(e).__name__}: {e}")
            return {
                "proxy": proxy_string,
                "ip": "Error",
                "country": "Error",
                "city": "Error",
                "isp": "Error",
                "download": 0,
                "upload": 0,
                "latency": 0,
                "status": "Failed",
            }

    def start_testing(self):
        proxy_list = self.proxy_input.get("1.0", tk.END).strip().split("\n")
        proxy_list = [p.strip() for p in proxy_list if p.strip()]

        if not proxy_list:
            messagebox.showwarning("Warning", "Please enter at least one proxy")
            return

        self.testing = True
        self.test_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.NORMAL)
        self.progress.start()

        def run_tests():
            for proxy in proxy_list:
                if not self.testing:
                    break

                result = self.test_proxy(proxy)

                # Update UI in main thread
                self.root.after(0, self.add_result, result)

            self.root.after(0, self.finish_testing)

        threading.Thread(target=run_tests, daemon=True).start()

    def add_result(self, result):
        """Add result to treeview"""
        self.tree.insert(
            "",
            tk.END,
            values=(
                result["proxy"],
                result["ip"],
                result["country"],
                result["city"],
                result["isp"],
                f"{result['download']:.2f}",
                f"{result['upload']:.2f}",
                f"{result['latency']:.2f}",
                result["status"],
            ),
        )

        # Tag rows by status
        item = self.tree.get_children()[-1]
        if result["status"] == "OK":
            self.tree.item(item, tags=("ok",))
        else:
            self.tree.item(item, tags=("failed",))

        self.tree.tag_configure("ok", background="#90EE90")
        self.tree.tag_configure("failed", background="#FFB6C6")

    def finish_testing(self):
        self.testing = False
        self.test_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)
        self.progress.stop()
        messagebox.showinfo("Complete", "Proxy testing completed!")

    def stop_testing(self):
        self.testing = False
        self.test_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)
        self.progress.stop()

    def clear_results(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
