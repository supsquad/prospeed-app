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
├── script/
│   ├── requirement.bat  # Install dependencies
│   └── serve.bat        # Run the application
├── requirements.txt     # Python dependencies
└── README.md
```

## Dependencies

- **requests**: HTTP library for API calls and proxy testing
- **speedtest-cli**: Network speed testing
- **PySocks**: SOCKS proxy support

## How It Works

1. System Speed Test: Measures your direct internet connection speed using speedtest-cli
2. Proxy Info Check: Uses ip-api.com to retrieve geolocation and ISP information
3. Proxy Speed Test: Routes speedtest-cli through the proxy using SOCKS/HTTP tunneling
4. Results Display: Shows comprehensive metrics in an organized table view

## Limitations

- Speed testing can take time depending on the number of proxies
- Some proxies may block speedtest servers
- Requires active internet connection
- Free IP geolocation API has rate limits

## License

This project is provided as-is for educational and testing purposes.

## Contributing

Feel free to submit issues and enhancement requests.
