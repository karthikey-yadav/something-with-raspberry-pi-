# 🍓 Raspberry Pi 4B — 3.5" TFT LCD Display Project

> A complete, production-ready setup guide for running a **3.5-inch SPI TFT LCD** on **Raspberry Pi 4 Model B** — including headless SSH access, remote desktop via VNC, and a live system stats dashboard script.

---

## 📋 Table of Contents

- [Project Overview](#-project-overview)
- [Hardware Requirements](#-hardware-requirements)
- [Block Diagram](#-block-diagram)
- [Step 1 — Flash OS with Raspberry Pi Imager](#-step-1--flash-os-with-raspberry-pi-imager)
- [Step 2 — First Boot & SSH via PuTTY](#-step-2--first-boot--ssh-via-putty)
- [Step 3 — Remote Desktop via RealVNC Viewer](#-step-3--remote-desktop-via-realvnc-viewer)
- [Step 4 — Hardware Assembly](#-step-4--hardware-assembly)
- [Step 5 — LCD Driver Installation](#-step-5--lcd-driver-installation)
- [Step 6 — Running the Dashboard Script](#-step-6--running-the-dashboard-script)
- [Project Script](#-project-script)
- [Troubleshooting](#-troubleshooting)
- [License](#-license)

---

## 📌 Project Overview

This project sets up a **3.5-inch TFT LCD touchscreen** directly connected to the GPIO header of a Raspberry Pi 4B. The display acts as a compact, standalone monitor — showing a live system dashboard (CPU usage, RAM, temperature, IP address) rendered right on the screen without needing an HDMI monitor.

**Use Cases:**
- Portable mini-computer display
- IoT device status panel
- Embedded system HMI (Human-Machine Interface)
- Learning platform for SPI, GPIO, and Linux display systems

---

## 🛠️ Hardware Requirements

| Component | Specification |
|---|---|
| Raspberry Pi | 4 Model B (2GB / 4GB / 8GB RAM) |
| Display | 3.5" TFT LCD (SPI-based — Waveshare / KeDei / Generic) |
| MicroSD Card | 16GB+ (Class 10 / U1 recommended) |
| Power Supply | 5V / 3A USB-C |
| USB Keyboard & Mouse | For initial local setup (optional) |
| Host Computer | Windows / macOS / Linux (for flashing & SSH) |

**Software Tools (on host machine):**
- [Raspberry Pi Imager](https://www.raspberrypi.com/software/) — OS flashing
- [PuTTY](https://www.putty.org/) — SSH terminal access
- [RealVNC Viewer](https://www.realvnc.com/en/connect/download/viewer/) — Remote desktop

---

## 🔷 Block Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                     HOST COMPUTER (Windows/Mac/Linux)           │
│                                                                 │
│  ┌──────────────────┐  ┌──────────────┐  ┌───────────────────┐ │
│  │  RPi Imager      │  │   PuTTY      │  │  RealVNC Viewer   │ │
│  │  (Flash SD Card) │  │  (SSH :22)   │  │  (VNC :5900)      │ │
│  └────────┬─────────┘  └──────┬───────┘  └────────┬──────────┘ │
└───────────┼────────────────── │ ─────────────────  │ ───────────┘
            │  MicroSD           │  Wi-Fi/LAN         │  Wi-Fi/LAN
            ▼                   ▼                    ▼
┌───────────────────────────────────────────────────────────────┐
│                  RASPBERRY PI 4 MODEL B                       │
│                                                               │
│   ┌──────────────────┐      ┌──────────────────────────────┐  │
│   │   MicroSD Slot   │      │   GPIO 40-Pin Header         │  │
│   │  (Raspberry Pi   │      │                              │  │
│   │   OS Bookworm)   │      │  VCC  → Pin 1  (3.3V)        │  │
│   └──────────────────┘      │  GND  → Pin 6  (GND)         │  │
│                             │  MOSI → Pin 19 (SPI0 MOSI)   │  │
│   ┌──────────────────┐      │  MISO → Pin 21 (SPI0 MISO)   │  │
│   │  CPU: BCM2711    │      │  SCLK → Pin 23 (SPI0 SCLK)   │  │
│   │  Quad-Core A72   │      │  CS   → Pin 24 (SPI0 CE0)    │  │
│   │  1.8 GHz         │      │  DC   → Pin 18 (GPIO 24)     │  │
│   └──────────────────┘      │  RST  → Pin 22 (GPIO 25)     │  │
│                             │  LED  → Pin 12 (GPIO 18)     │  │
│   ┌──────────────────┐      └──────────────┬───────────────┘  │
│   │  RAM: LPDDR4     │                     │  SPI Bus          │
│   │  2/4/8 GB        │                     │                   │
│   └──────────────────┘                     ▼                   │
│                             ┌──────────────────────────────┐   │
│   ┌──────────────────┐      │   3.5" TFT LCD Display       │   │
│   │  Wi-Fi / BT 5.0  │      │   (ILI9486 / XPT2046)        │   │
│   │  (SSH + VNC)     │      │   Resolution: 480 × 320      │   │
│   └──────────────────┘      │   Interface: SPI              │   │
│                             │   Touch: XPT2046              │   │
└─────────────────────────────┴──────────────────────────────┘   
```

---

## ⚡ Step 1 — Flash OS with Raspberry Pi Imager

1. **Download** [Raspberry Pi Imager](https://www.raspberrypi.com/software/) and install it on your computer.

2. **Insert** your MicroSD card into your computer (via card reader).

3. **Open Raspberry Pi Imager** and configure:
   - **Device:** Raspberry Pi 4
   - **OS:** Raspberry Pi OS (64-bit) — *Bookworm recommended*
   - **Storage:** Your MicroSD card

4. **Click the ⚙️ gear icon** (Advanced Options) before flashing — this is critical for headless setup:
   - ✅ **Set hostname:** `raspberrypi.local`
   - ✅ **Enable SSH** → Use password authentication
   - ✅ **Set username:** `pi` | **Password:** `your_secure_password`
   - ✅ **Configure Wi-Fi:** Enter your SSID and password
   - ✅ **Set locale / timezone**

5. Click **Save → Write** and wait for flashing + verification to complete (~5–10 min).

6. **Eject** the MicroSD card safely and insert it into the Raspberry Pi.

---

## 🖥️ Step 2 — First Boot & SSH via PuTTY

> No HDMI monitor needed — SSH over Wi-Fi from the start!

1. **Power on** the Raspberry Pi (USB-C, 5V/3A).

2. Wait ~60 seconds for the first boot to complete.

3. **Find the Pi's IP address** using one of:
   - Your router's DHCP client list (look for `raspberrypi`)
   - Run `ping raspberrypi.local` in your terminal / Command Prompt
   - Use a network scanner like [Advanced IP Scanner](https://www.advanced-ip-scanner.com/)

4. **Open PuTTY:**
   - Host Name: `raspberrypi.local` *or* the IP address (e.g. `192.168.1.45`)
   - Port: `22`
   - Connection type: `SSH`
   - Click **Open**

5. **Login** with your credentials:
   ```
   login as: pi
   pi@raspberrypi.local's password: your_secure_password
   ```

6. **Update the system:**
   ```bash
   sudo apt update && sudo apt full-upgrade -y
   sudo reboot
   ```

---

## 🖱️ Step 3 — Remote Desktop via RealVNC Viewer

1. **Enable VNC on the Pi** (via SSH after reboot):
   ```bash
   sudo raspi-config
   ```
   Navigate to: `Interface Options → VNC → Enable → Finish`

2. **Set a VNC password** (optional but recommended):
   ```bash
   vncpasswd
   ```

3. **Download** [RealVNC Viewer](https://www.realvnc.com/en/connect/download/viewer/) on your host machine and install it.

4. **Open RealVNC Viewer:**
   - Enter: `raspberrypi.local` or the Pi's IP address
   - Press Enter / Connect
   - Enter the VNC password when prompted

5. You now have a **full graphical desktop** of your Raspberry Pi remotely! 🎉

> 💡 **Tip:** For best performance, in VNC Viewer go to `Properties → Expert` and set `ColorLevel` to `pal8` for low-bandwidth connections.

---

## 🔌 Step 4 — Hardware Assembly

> ⚠️ Always **power off** the Raspberry Pi before attaching or detaching GPIO hardware.

```bash
sudo shutdown -h now
```

1. Wait until the Pi's green LED stops flashing and the red LED goes off.
2. **Align the 3.5" LCD** with the 40-pin GPIO header. Pin 1 (marked on the PCB) goes to the top-left corner of the GPIO block.
3. **Press down firmly** and evenly until all pins are fully seated.
4. Verify no pins are bent or offset.
5. **Power the Pi back on.**

> On first power-on with the LCD attached, you will likely see a **white or blank screen** — this is expected until drivers are installed.

---

## 📦 Step 5 — LCD Driver Installation

SSH into your Pi and run the following:

```bash
# Update & install dependencies
sudo apt update && sudo apt install -y git cmake curl

# Clone the Waveshare LCD driver repository
git clone https://github.com/waveshare/LCD-show.git
cd LCD-show

# Make driver scripts executable
chmod +x LCD35-show LCD-hdmi

# Install the 3.5" LCD driver (this will reboot automatically)
sudo ./LCD35-show
```

> The Pi will **reboot automatically** after installation. On reboot, the 3.5" display should show the desktop or console.

**Switching back to HDMI output:**
```bash
cd ~/LCD-show
sudo ./LCD-hdmi
```

**Rotating the display:**
```bash
# 90 degrees
sudo ./LCD35-show 90

# 180 degrees
sudo ./LCD35-show 180

# 270 degrees
sudo ./LCD35-show 270
```

---

## 🚀 Step 6 — Running the Dashboard Script

```bash
# Install Python dependencies
pip3 install psutil pillow --break-system-packages

# Clone this repository
git clone https://github.com/karthikey-yadav/something-with-raspberry-pi-.git
cd something-with-raspberry-pi-

# Run the dashboard
python3 script.py
```

**Run on boot (optional):**
```bash
# Open crontab
crontab -e

# Add this line at the bottom:
@reboot sleep 10 && python3 /home/pi/something-with-raspberry-pi-/script.py &
```

---

## 📜 Project Script

The `script.py` monitors and displays live system stats on the 3.5" LCD. See the full annotated source in [`script.py`](./script.py).

**What it displays:**
- 🌡️ CPU temperature
- 📊 CPU usage (%)
- 💾 RAM usage (used / total)
- 💿 Disk usage (used / total)
- 🌐 Local IP address
- 🕐 Current time & date

---

## 🔧 Troubleshooting

| Issue | Solution |
|---|---|
| White/blank LCD screen | Driver not installed — run `sudo ./LCD35-show` |
| Cannot SSH (connection refused) | Ensure SSH was enabled in Imager advanced settings; check IP address |
| `raspberrypi.local` not found | Use IP address directly; install Bonjour on Windows |
| VNC shows "Cannot connect" | Ensure VNC is enabled via `raspi-config` |
| Script fails with import error | Run `pip3 install psutil pillow --break-system-packages` |
| LCD shows wrong orientation | Run `sudo ./LCD35-show 90` (or 180/270) |
| No Wi-Fi on first boot | Re-flash with correct SSID/password in Imager advanced settings |
| Touchscreen not working | Check `/boot/config.txt` for `dtoverlay=waveshare35a` line |

---

## 📁 Repository Structure

```
something-with-raspberry-pi-/
│
├── README.md          # This file — complete setup guide
├── script.py          # Live system dashboard Python script
├── block_diagram.svg  # Hardware & software block diagram
└── rpi.jpg            # Project photo
```

---

## 🧾 License

This project is open-source under the [MIT License](https://opensource.org/licenses/MIT).  
Feel free to fork, modify, and build upon it. Attribution appreciated! 🙏

---

<p align="center">
  Made with ❤️ by <a href="https://github.com/karthikey-yadav">karthikey-yadav</a>
</p>
