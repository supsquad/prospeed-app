# ProSpeed — Proxy Speed Tester

A desktop application for testing and comparing proxy server performance metrics including download speed, upload speed, latency, and geolocation information.

## Features

- **Dark modern UI** — GitHub-inspired dark theme with color-coded results
- **System bandwidth test** — Measure your direct internet connection as a baseline
- **Multi-proxy testing** — Test multiple proxy servers sequentially
- **Protocol support** — HTTP, HTTPS, SOCKS4, SOCKS5
- **Proxy authentication** — username:password support
- **Detailed metrics per proxy:**
  - IP address, Country, City, ISP (via ip-api.com)
  - Download speed (Mbps)
  - Upload speed (Mbps)
  - Latency (ms)
- **Color-coded results** — green rows for OK, red rows for failed/slow
- **Real-time activity log** — live output with color-highlighted speed metrics and errors
- **Progress counter** — status bar showing `tested / total`
- **Stop anytime** — halt testing mid-run without losing existing results

## Requirements

- Python 3.7+
- tkinter (included with Python on Windows)

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd prospeed-app
```

2. Create and activate a virtual environment:
```bash
python -m venv .venv
.venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create environment configuration (if not already present):
```bash
copy .env.example .env.local
```

## Usage

### Running the Application

```bash
script\run.bat local
```

Or directly:
```bash
python app/main.py
```

### Testing Proxies

1. *(Optional)* Click **Test System Speed** to measure your baseline connection
2. Enter proxy addresses in the input field, one per line
3. Click **▶ Test Proxies** to start
4. Results appear in the table as each proxy is tested
5. Use **■ Stop** to halt, or **Clear Results** to reset

**Supported proxy formats:**
```
http://192.168.1.1:8080
https://192.168.1.1:8443
socks4://192.168.1.1:1080
socks5://192.168.1.1:1080
http://user:pass@192.168.1.1:8080
socks5://user:pass@192.168.1.1:1080
```

## Project Structure

```
prospeed-app/
├── app/
│   ├── __init__.py
│   ├── main.py          # Entry point
│   └── speed.py         # UI and proxy testing logic
├── build/               # Build output
├── script/
│   ├── requirement.bat  # Freeze dependencies to requirements.txt
│   ├── run.bat          # Run the application
│   ├── build.bat        # Build executable with Nuitka
│   └── release.bat      # Tag and publish a GitHub release
├── requirements.txt
├── .env.example
└── README.md
```

## Dependencies

| Package | Purpose |
|---|---|
| `httpx` | HTTP client with native SOCKS proxy support |
| `socksio` | SOCKS protocol support for httpx |
| `PySocks` | SOCKS proxy library |
| `speedtest-cli` | System speed test (direct connection) |
| `requests` | IP geolocation lookup |
| `Nuitka` | Compile to standalone `.exe` |
| `zstandard` | Compression (Nuitka dependency) |

Install: `pip install -r requirements.txt`
Freeze: `script\requirement.bat`

## Building Executable

```bash
script\build.bat 1.0.0
```

Output: `build/prospeed-v1.0.0.exe` (uses `.env.prod`)

> Requires Nuitka and Visual Studio Build Tools (MSVC compiler).

### Releasing

```bash
script\release.bat 1.0.0
```

Creates a git tag, pushes to remote, and publishes a GitHub Release with the `.exe` attached.

### Saving Dependencies

```bash
script\requirement.bat
```

Freezes currently installed packages into `requirements.txt` (`pip freeze`).

## How It Works

1. **System Speed** — uses `speedtest-cli` to test direct internet speed
2. **Proxy Info** — queries `ip-api.com` through each proxy for geolocation + ISP
3. **Proxy Speed** — uses `httpx` with native SOCKS/HTTP proxy to test speed via Cloudflare Speed Test endpoints
4. **Results** — displayed in a sortable table; rows color-coded by status

## Limitations

- Testing is sequential; many proxies will take time
- Some proxies block speed test servers
- `ip-api.com` free tier has rate limits (45 req/min)
- Requires an active internet connection

## License

This project is provided as-is for educational and testing purposes.
