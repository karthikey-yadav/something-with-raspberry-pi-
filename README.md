# something-with-raspberry-pi-


# 📟 Raspberry Pi 4B with 3.5" LCD Screen Setup

This guide walks you through setting up a **3.5-inch TFT LCD display** on a **Raspberry Pi 4 Model B**.  
The instructions cover hardware connections, driver installation, and configuration for both console and desktop GUI output.

---

## 🛠️ Hardware Requirements
- Raspberry Pi 4 Model B (any RAM variant)  
- 3.5" TFT LCD Screen (SPI-based, e.g., Waveshare, KeDei, or generic clones)  
- MicroSD card with Raspberry Pi OS installed  
- Power supply (5V, 3A recommended)  
- HDMI cable + monitor (optional, for first-time setup)  
- USB keyboard and mouse  

---

## 🔌 Hardware Setup
1. **Shut down** your Raspberry Pi before attaching the LCD.  
2. Connect the **3.5" LCD** directly to the GPIO header (pins should align perfectly).  
3. Ensure the LCD is firmly seated on the GPIO pins.  
4. Power on the Raspberry Pi — you may initially see a white screen until drivers are configured.  

---

## 💻 Software Setup

## 💻 Base System Prep
```bash
# Update OS
sudo apt update && sudo apt upgrade -y

# Essentials
sudo apt install -y git cmake curl

---

## now for installing lcd 

# Install LCD Driver 
# Get the driver helper scripts
git clone https://github.com/waveshare/LCD-show.git
cd LCD-show

# Make scripts executable
chmod +x LCD35-show LCD-hdmi


# Default orientation (0°)
./LCD35-show







