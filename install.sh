#!/bin/bash
#
# Arch Linux Installer with Hyprland - Remote Installer
# Usage: curl -L https://raw.githubusercontent.com/YOUR_USER/YOUR_REPO/main/install.sh | bash
#

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
REPO_USER="armando-rios"  # Replace with your GitHub username
REPO_NAME="dev-setup"        # Replace with your repo name
BRANCH="main"
BASE_URL="https://raw.githubusercontent.com/${REPO_USER}/${REPO_NAME}/${BRANCH}"

echo -e "${BLUE}╔══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║               Arch Linux Installer with Hyprland            ║${NC}"
echo -e "${BLUE}║                     Remote Installer                        ║${NC}"
echo -e "${BLUE}╚══════════════════════════════════════════════════════════════╝${NC}"
echo

# Check if running as root
if [[ $EUID -eq 0 ]]; then
   echo -e "${RED}⚠️  This script should NOT be run as root!${NC}"
   echo -e "${YELLOW}   Run it as a normal user, it will ask for sudo when needed.${NC}"
   echo
   read -p "Continue anyway? (y/N): " -n 1 -r
   echo
   if [[ ! $REPLY =~ ^[Yy]$ ]]; then
       exit 1
   fi
fi

# Check for required tools
echo -e "${BLUE}🔍 Checking required tools...${NC}"
for tool in curl python3 sudo; do
    if ! command -v $tool &> /dev/null; then
        echo -e "${RED}❌ Missing required tool: $tool${NC}"
        exit 1
    fi
done
echo -e "${GREEN}✅ All required tools found${NC}"
echo

# Check internet connection
echo -e "${BLUE}🌐 Testing internet connection...${NC}"
if ! curl -s --connect-timeout 5 https://github.com &> /dev/null; then
    echo -e "${RED}❌ No internet connection or GitHub is unreachable${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Internet connection OK${NC}"
echo

# Check if we're in Arch Linux (optional warning)
if [[ -f /etc/arch-release ]]; then
    echo -e "${GREEN}✅ Running on Arch Linux${NC}"
else
    echo -e "${YELLOW}⚠️  Warning: This installer is designed for Arch Linux${NC}"
    echo -e "${YELLOW}   You may encounter issues on other distributions${NC}"
    echo
    read -p "Continue anyway? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Create temporary directory
TEMP_DIR=$(mktemp -d)
echo -e "${BLUE}📁 Using temporary directory: $TEMP_DIR${NC}"

# Function to download file
download_file() {
    local url="$1"
    local dest="$2"
    local desc="$3"
    
    echo -e "${BLUE}⬇️  Downloading $desc...${NC}"
    if curl -fsSL "$url" -o "$dest"; then
        echo -e "${GREEN}✅ Downloaded: $desc${NC}"
    else
        echo -e "${RED}❌ Failed to download: $desc${NC}"
        echo -e "${RED}   URL: $url${NC}"
        exit 1
    fi
}

# Download installer files
cd "$TEMP_DIR"

echo -e "${BLUE}📦 Downloading Arch Linux Installer...${NC}"

# Create directory structure
mkdir -p arch-installer/utils

# Download main files
download_file "${BASE_URL}/arch-installer/main.py" "arch-installer/main.py" "main installer"
download_file "${BASE_URL}/arch-installer/utils/__init__.py" "arch-installer/utils/__init__.py" "utils module"
download_file "${BASE_URL}/arch-installer/utils/system.py" "arch-installer/utils/system.py" "system utilities"
download_file "${BASE_URL}/arch-installer/utils/disk.py" "arch-installer/utils/disk.py" "disk utilities"
download_file "${BASE_URL}/arch-installer/utils/tui.py" "arch-installer/utils/tui.py" "TUI interface"

echo
echo -e "${GREEN}🎉 Download complete!${NC}"
echo

# Make main.py executable
chmod +x arch-installer/main.py

# Show final instructions
echo -e "${BLUE}╔══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║                        Ready to Install                     ║${NC}"
echo -e "${BLUE}╚══════════════════════════════════════════════════════════════╝${NC}"
echo
echo -e "${YELLOW}⚠️  WARNING: This will FORMAT your selected disk!${NC}"
echo -e "${YELLOW}   Make sure you have backups of important data.${NC}"
echo
echo -e "${BLUE}📍 Installer location: ${TEMP_DIR}/arch-installer${NC}"
echo

# Ask for confirmation
read -p "Start the Arch Linux installer now? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${GREEN}🚀 Starting installer...${NC}"
    echo
    cd arch-installer
    exec sudo python3 main.py
else
    echo -e "${YELLOW}📝 To run the installer later:${NC}"
    echo -e "${BLUE}   cd ${TEMP_DIR}/arch-installer${NC}"
    echo -e "${BLUE}   sudo python3 main.py${NC}"
    echo
    echo -e "${YELLOW}📝 To clean up temporary files:${NC}"
    echo -e "${BLUE}   rm -rf ${TEMP_DIR}${NC}"
fi
