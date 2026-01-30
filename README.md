# Proxy Speed Tester

A desktop application for testing and comparing proxy server performance metrics including download speed, upload speed, latency, and geolocation information.

![App Screenshot](screenshot.png)

## Features

- Test system bandwidth without proxy
- Test multiple proxy servers simultaneously
- Support for multiple proxy protocols (HTTP, HTTPS, SOCKS4, SOCKS5)
- Proxy authentication support (username/password)
- Display detailed metrics:
  - IP address
  - Country and city location
  - ISP information
  - Download speed (Mbps)
  - Upload speed (Mbps)
  - Latency (ms)
- Color-coded results (green for OK, red for failed/slow)
- Easy-to-use graphical interface

## Requirements

- Python 3.7+
- tkinter (usually included with Python)

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd prospeed-app
```

2. Create a virtual environment:
```bash
python -m venv .venv
```

3. Activate the virtual environment:

Windows:
```bash
.venv\Scripts\activate
```

Linux/Mac:
```bash
source .venv/bin/activate
```

4. Install dependencies:
```bash
pip install -r requirements.txt
```

Or use the provided script:
```bash
script\requirement.bat
```

5. Create environment configuration file:
```bash
cp .env.example .env.dev
```

Or on Windows:
```bash
copy .env.example .env.dev
```

The `.env.dev` file contains configuration settings for development mode. You can modify it as needed.

## Usage

### Running the Application

Windows:
```bash
script\serve.bat dev
```

Or directly:
```bash
python -m app.main
```

### Testing Proxies

1. Click "Test System Speed" to measure your baseline internet speed
2. Enter proxy addresses in the input field, one per line
3. Supported formats:
   - `protocol://ip:port`
   - `protocol://username:password@ip:port`

Examples:
```
http://192.168.1.1:8080
https://192.168.1.1:8443
socks5://192.168.1.1:1080
socks4://192.168.1.1:1080
http://user:pass@192.168.1.1:8080
socks5://user:pass@192.168.1.1:1080
```

4. Click "Test Proxies" to start testing
5. View results in the table below
6. Use "Stop" to halt testing or "Clear Results" to reset

## Project Structure

```
prospeed-app/
├── app/
│   ├── __init__.py
│   ├── main.py          # Application entry point
│   └── speed.py         # Proxy testing logic and UI
├── build/               # Build output directory
├── script/
│   ├── requirement.bat  # Install dependencies
│   ├── serve.bat        # Run the application
│   ├── build.bat        # Build executable
│   └── release.bat      # Release script
├── requirements.txt     # Python dependencies
├── .env.example         # Environment configuration template
└── README.md
```

## Dependencies

- **httpx**: Modern HTTP client with native SOCKS proxy support
- **socksio**: SOCKS proxy protocol support for httpx
- **PySocks**: SOCKS proxy library
- **speedtest-cli**: Network speed testing (system speed)
- **requests**: HTTP library for proxy info checking
- **Nuitka**: Python compiler for building standalone executables
- **zstandard**: Compression library used by Nuitka

## Building Executable

To build a standalone executable file:

1. Create production environment configuration:
```bash
copy .env.example .env.prod
```

2. Build the executable:
```bash
script\build.bat <version>
```

Example:
```bash
script\build.bat 1.0.0
```

This will create `prospeed-v1.0.0.exe` in the `build/` directory using Nuitka compiler.

**Requirements for building:**
- Nuitka installed (`pip install nuitka`)
- C compiler (Visual Studio Build Tools on Windows)

## How It Works

1. **System Speed Test**: Measures your direct internet connection speed using speedtest-cli
2. **Proxy Info Check**: Uses ip-api.com to retrieve geolocation and ISP information
3. **Proxy Speed Test**: Uses httpx client with native SOCKS/HTTP proxy support to test speed via speedtest.net servers
4. **Results Display**: Shows comprehensive metrics in an organized table view with color-coded status

## Limitations

- Speed testing can take time depending on the number of proxies
- Some proxies may block speedtest servers
- Requires active internet connection
- Free IP geolocation API has rate limits

## License

This project is provided as-is for educational and testing purposes.

## Contributing

Feel free to submit issues and enhancement requests.
