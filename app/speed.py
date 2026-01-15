import socket
import threading
import tkinter as tk
from tkinter import messagebox, scrolledtext, ttk
from urllib.parse import urlparse

import requests
import socks
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
        main_frame.rowconfigure(4, weight=1)

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

        # Results section
        results_frame = ttk.LabelFrame(main_frame, text="Test Results", padding="10")
        results_frame.grid(row=4, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
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
            # Configure proxy for speedtest-cli using socks proxy
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
        """Use speedtest-cli with SOCKS proxy by monkey patching"""
        original_socket = socket.socket
        try:
            # Configure SOCKS proxy
            proxy_type = socks.SOCKS5
            if proxy_dict["protocol"] == "socks4":
                proxy_type = socks.SOCKS4
            elif proxy_dict["protocol"] in ["http", "https"]:
                proxy_type = socks.HTTP

            # Set default proxy for all sockets
            socks.set_default_proxy(
                proxy_type,
                proxy_dict["host"],
                proxy_dict["port"],
                username=proxy_dict.get("username"),
                password=proxy_dict.get("password"),
            )
            socket.socket = socks.socksocket

            # Run speedtest through proxy
            st = speedtest.Speedtest()
            st.get_best_server()
            latency = st.results.ping

            download_bps = st.download()
            download_speed_mbps = download_bps / 1_000_000

            upload_bps = st.upload()
            upload_speed_mbps = upload_bps / 1_000_000

            return download_speed_mbps, upload_speed_mbps, latency

        except Exception as e:
            print(f"Speedtest proxy error: {e}")
            return 0, 0, 9999
        finally:
            # Always restore original socket
            socket.socket = original_socket
            socks.set_default_proxy(None)

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
            # Get proxy info
            info = self.check_proxy_info(proxy_dict)

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
            print(f"Error testing proxy {proxy_string}: {e}")
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
