#!/usr/bin/env python3
"""
=============================================================================
  Raspberry Pi 4B — 3.5" TFT LCD System Dashboard
=============================================================================
  Author   : karthikey-yadav
  GitHub   : https://github.com/karthikey-yadav/something-with-raspberry-pi-
  License  : MIT

  Description:
    Displays a live system statistics dashboard on the 3.5" TFT LCD screen
    connected via GPIO SPI. Shows CPU usage, RAM, disk, temperature, IP
    address, and current time — refreshed every 2 seconds.

  Requirements:
    - Raspberry Pi 4 Model B
    - 3.5" TFT LCD (Waveshare / KeDei / Generic SPI)
    - Python 3.7+
    - Packages: psutil, Pillow
      Install: pip3 install psutil pillow --break-system-packages

  Usage:
    python3 script.py

  Auto-start on boot (crontab):
    @reboot sleep 10 && python3 /home/pi/something-with-raspberry-pi-/script.py &
=============================================================================
"""

import os
import time
import socket
import datetime
import subprocess

try:
    import psutil
except ImportError:
    raise SystemExit(
        "[ERROR] psutil not found.\n"
        "Install with: pip3 install psutil --break-system-packages"
    )

try:
    from PIL import Image, ImageDraw, ImageFont
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
    print("[WARN] Pillow not found. Falling back to terminal output.")
    print("Install with: pip3 install pillow --break-system-packages\n")

# ─────────────────────────────────────────────────────────────────────────────
# CONFIGURATION
# ─────────────────────────────────────────────────────────────────────────────

REFRESH_INTERVAL = 2          # seconds between updates
LCD_WIDTH        = 480        # pixels (3.5" TFT)
LCD_HEIGHT       = 320        # pixels
FRAMEBUFFER      = "/dev/fb1" # framebuffer device for the LCD

# Colours (R, G, B)
BG_COLOR       = (10, 14, 28)    # deep navy
HEADER_COLOR   = (220, 50, 70)   # raspberry red
TEXT_COLOR     = (220, 230, 255) # soft white
LABEL_COLOR    = (120, 140, 180) # muted blue
ACCENT_COLOR   = (50, 200, 150)  # teal-green
WARN_COLOR     = (255, 180, 0)   # amber warning
CRIT_COLOR     = (255, 60, 60)   # red critical
BAR_BG_COLOR   = (30, 35, 55)    # bar background
BAR_FG_COLOR   = (50, 200, 150)  # bar fill

# Thresholds for colour warnings
CPU_WARN_THRESHOLD  = 70   # %
CPU_CRIT_THRESHOLD  = 90   # %
TEMP_WARN_THRESHOLD = 65   # °C
TEMP_CRIT_THRESHOLD = 80   # °C
RAM_WARN_THRESHOLD  = 75   # %


# ─────────────────────────────────────────────────────────────────────────────
# SYSTEM STATS COLLECTION
# ─────────────────────────────────────────────────────────────────────────────

def get_cpu_usage() -> float:
    """Return current CPU usage as a percentage (0–100)."""
    return psutil.cpu_percent(interval=None)


def get_cpu_temperature() -> float:
    """
    Read CPU temperature from the Raspberry Pi thermal zone.
    Returns temperature in °C, or -1.0 if unavailable.
    """
    temp_path = "/sys/class/thermal/thermal_zone0/temp"
    try:
        with open(temp_path, "r") as f:
            raw = int(f.read().strip())
        return raw / 1000.0
    except (FileNotFoundError, ValueError):
        # Fallback: try vcgencmd (RPi-specific)
        try:
            result = subprocess.run(
                ["vcgencmd", "measure_temp"],
                capture_output=True, text=True, timeout=2
            )
            temp_str = result.stdout.strip().replace("temp=", "").replace("'C", "")
            return float(temp_str)
        except Exception:
            return -1.0


def get_ram_stats() -> dict:
    """Return RAM usage statistics (bytes and percent)."""
    vm = psutil.virtual_memory()
    return {
        "total":   vm.total,
        "used":    vm.used,
        "free":    vm.available,
        "percent": vm.percent,
    }


def get_disk_stats(path: str = "/") -> dict:
    """Return disk usage statistics for the given path."""
    disk = psutil.disk_usage(path)
    return {
        "total":   disk.total,
        "used":    disk.used,
        "free":    disk.free,
        "percent": disk.percent,
    }


def get_ip_address() -> str:
    """Return the local IP address of this device, or 'N/A' if offline."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.settimeout(1)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "N/A"


def get_uptime() -> str:
    """Return system uptime as a human-readable string."""
    try:
        boot_time = psutil.boot_time()
        uptime_seconds = time.time() - boot_time
        hours, rem = divmod(int(uptime_seconds), 3600)
        minutes, seconds = divmod(rem, 60)
        return f"{hours:02d}h {minutes:02d}m {seconds:02d}s"
    except Exception:
        return "N/A"


def bytes_to_human(n: int) -> str:
    """Convert bytes to a human-readable string (KB, MB, GB)."""
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if n < 1024.0:
            return f"{n:.1f} {unit}"
        n /= 1024.0
    return f"{n:.1f} PB"


def threshold_color(value: float, warn: float, crit: float) -> tuple:
    """Return colour based on value thresholds."""
    if value >= crit:
        return CRIT_COLOR
    elif value >= warn:
        return WARN_COLOR
    return ACCENT_COLOR


# ─────────────────────────────────────────────────────────────────────────────
# TERMINAL RENDERER (fallback without Pillow / LCD)
# ─────────────────────────────────────────────────────────────────────────────

def render_terminal(stats: dict) -> None:
    """Print a formatted dashboard to the terminal."""
    os.system("clear")
    now = datetime.datetime.now().strftime("%Y-%m-%d  %H:%M:%S")
    sep = "─" * 48

    print(f"\033[1;31m{'🍓  RASPBERRY PI SYSTEM DASHBOARD':^48}\033[0m")
    print(f"\033[90m{sep}\033[0m")
    print(f"  \033[90mTime :\033[0m  {now}")
    print(f"  \033[90mIP   :\033[0m  {stats['ip']}")
    print(f"  \033[90mUptime:\033[0m {stats['uptime']}")
    print(f"\033[90m{sep}\033[0m")

    # CPU
    cpu_c = "\033[91m" if stats['cpu'] >= CPU_CRIT_THRESHOLD else \
            "\033[93m" if stats['cpu'] >= CPU_WARN_THRESHOLD else "\033[92m"
    print(f"  \033[90mCPU  :\033[0m  {cpu_c}{stats['cpu']:5.1f}%\033[0m  {_bar(stats['cpu'])}")

    # Temperature
    temp = stats['temp']
    temp_str = f"{temp:.1f}°C" if temp >= 0 else "N/A"
    t_c = "\033[91m" if temp >= TEMP_CRIT_THRESHOLD else \
          "\033[93m" if temp >= TEMP_WARN_THRESHOLD else "\033[92m"
    print(f"  \033[90mTemp :\033[0m  {t_c}{temp_str:>7}\033[0m")

    # RAM
    ram_c = "\033[93m" if stats['ram']['percent'] >= RAM_WARN_THRESHOLD else "\033[92m"
    print(f"  \033[90mRAM  :\033[0m  {ram_c}{stats['ram']['percent']:5.1f}%\033[0m  "
          f"\033[90m{bytes_to_human(stats['ram']['used'])} / {bytes_to_human(stats['ram']['total'])}\033[0m"
          f"  {_bar(stats['ram']['percent'])}")

    # Disk
    print(f"  \033[90mDisk :\033[0m  \033[92m{stats['disk']['percent']:5.1f}%\033[0m  "
          f"\033[90m{bytes_to_human(stats['disk']['used'])} / {bytes_to_human(stats['disk']['total'])}\033[0m"
          f"  {_bar(stats['disk']['percent'])}")

    print(f"\033[90m{sep}\033[0m")
    print(f"\033[90m  Refresh every {REFRESH_INTERVAL}s  |  Ctrl+C to exit\033[0m")


def _bar(percent: float, width: int = 14) -> str:
    """Render an ASCII progress bar."""
    filled = int(width * percent / 100)
    return f"[\033[96m{'█' * filled}\033[90m{'░' * (width - filled)}\033[0m]"


# ─────────────────────────────────────────────────────────────────────────────
# LCD RENDERER (Pillow → framebuffer)
# ─────────────────────────────────────────────────────────────────────────────

def draw_bar(draw: "ImageDraw", x: int, y: int, width: int, height: int,
             percent: float, color: tuple) -> None:
    """Draw a filled progress bar on the image."""
    draw.rectangle([x, y, x + width, y + height], fill=BAR_BG_COLOR)
    filled_w = int(width * percent / 100)
    if filled_w > 0:
        draw.rectangle([x, y, x + filled_w, y + height], fill=color)


def render_lcd(stats: dict) -> None:
    """Render the stats dashboard to the 3.5" TFT LCD via framebuffer."""
    img  = Image.new("RGB", (LCD_WIDTH, LCD_HEIGHT), BG_COLOR)
    draw = ImageDraw.Draw(img)

    # Try loading fonts; fall back to default if not found
    try:
        font_lg  = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf", 22)
        font_md  = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf", 16)
        font_sm  = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf", 13)
    except IOError:
        font_lg = font_md = font_sm = ImageFont.load_default()

    # ── Header bar ──────────────────────────────────────────────────────────
    draw.rectangle([0, 0, LCD_WIDTH, 38], fill=HEADER_COLOR)
    draw.text((12, 8),  "🍓  RASPBERRY PI DASHBOARD", font=font_lg, fill=(255, 255, 255))

    now = datetime.datetime.now().strftime("%H:%M:%S")
    draw.text((LCD_WIDTH - 90, 12), now, font=font_md, fill=(255, 230, 230))

    # ── Row layout ──────────────────────────────────────────────────────────
    row_start = 50
    row_h     = 52
    pad_l     = 16
    bar_x     = 160
    bar_w     = 270
    bar_h     = 14

    rows = [
        {
            "label":   "CPU",
            "value":   f"{stats['cpu']:5.1f}%",
            "percent": stats['cpu'],
            "color":   threshold_color(stats['cpu'], CPU_WARN_THRESHOLD, CPU_CRIT_THRESHOLD),
            "sub":     f"Uptime: {stats['uptime']}",
        },
        {
            "label":   "TEMP",
            "value":   f"{stats['temp']:.1f}°C" if stats['temp'] >= 0 else " N/A",
            "percent": min(stats['temp'], 100) if stats['temp'] >= 0 else 0,
            "color":   threshold_color(stats['temp'], TEMP_WARN_THRESHOLD, TEMP_CRIT_THRESHOLD),
            "sub":     "CPU Core Temperature",
        },
        {
            "label":   "RAM",
            "value":   f"{stats['ram']['percent']:5.1f}%",
            "percent": stats['ram']['percent'],
            "color":   threshold_color(stats['ram']['percent'], RAM_WARN_THRESHOLD, 95),
            "sub":     f"{bytes_to_human(stats['ram']['used'])} / {bytes_to_human(stats['ram']['total'])}",
        },
        {
            "label":   "DISK",
            "value":   f"{stats['disk']['percent']:5.1f}%",
            "percent": stats['disk']['percent'],
            "color":   threshold_color(stats['disk']['percent'], 70, 90),
            "sub":     f"{bytes_to_human(stats['disk']['used'])} / {bytes_to_human(stats['disk']['total'])}",
        },
    ]

    for i, row in enumerate(rows):
        y = row_start + i * row_h
        # Alternating row background
        if i % 2 == 0:
            draw.rectangle([0, y, LCD_WIDTH, y + row_h - 2], fill=(15, 20, 38))

        draw.text((pad_l, y + 6),  row["label"], font=font_md, fill=LABEL_COLOR)
        draw.text((pad_l + 70, y + 4), row["value"], font=font_lg, fill=row["color"])
        draw_bar(draw, bar_x, y + 8,  bar_w, bar_h, row["percent"], row["color"])
        draw.text((bar_x, y + 26), row["sub"], font=font_sm, fill=(100, 115, 150))

    # ── Footer ──────────────────────────────────────────────────────────────
    footer_y = LCD_HEIGHT - 28
    draw.rectangle([0, footer_y, LCD_WIDTH, LCD_HEIGHT], fill=(15, 18, 35))
    draw.text((pad_l, footer_y + 7), f"IP: {stats['ip']}", font=font_sm, fill=LABEL_COLOR)

    date_str = datetime.datetime.now().strftime("%d %b %Y")
    draw.text((LCD_WIDTH - 110, footer_y + 7), date_str, font=font_sm, fill=LABEL_COLOR)

    # ── Write to framebuffer ─────────────────────────────────────────────────
    try:
        with open(FRAMEBUFFER, "wb") as fb:
            fb.write(img.tobytes())
    except (PermissionError, FileNotFoundError):
        # Fall back to saving a PNG preview (useful for testing on desktop)
        img.save("/tmp/dashboard_preview.png")


# ─────────────────────────────────────────────────────────────────────────────
# MAIN LOOP
# ─────────────────────────────────────────────────────────────────────────────

def collect_stats() -> dict:
    """Gather all system statistics into a single dictionary."""
    return {
        "cpu":    get_cpu_usage(),
        "temp":   get_cpu_temperature(),
        "ram":    get_ram_stats(),
        "disk":   get_disk_stats("/"),
        "ip":     get_ip_address(),
        "uptime": get_uptime(),
    }


def main() -> None:
    """Main entry point — collect stats and render in a loop."""
    lcd_available = PIL_AVAILABLE and os.path.exists(FRAMEBUFFER)

    if lcd_available:
        print("[INFO] LCD framebuffer found. Rendering to display.")
    else:
        print("[INFO] No LCD framebuffer — using terminal output.")
        if PIL_AVAILABLE:
            print(f"[INFO] Framebuffer '{FRAMEBUFFER}' not found. "
                  "Is the LCD driver installed? (see README)")

    print(f"[INFO] Refreshing every {REFRESH_INTERVAL}s.  Press Ctrl+C to quit.\n")

    # Prime psutil CPU measurement (first call always returns 0.0)
    psutil.cpu_percent(interval=0.1)

    try:
        while True:
            stats = collect_stats()

            if lcd_available:
                render_lcd(stats)
            else:
                render_terminal(stats)

            time.sleep(REFRESH_INTERVAL)

    except KeyboardInterrupt:
        print("\n[INFO] Dashboard stopped by user. Goodbye! 🍓")


if __name__ == "__main__":
    main()
