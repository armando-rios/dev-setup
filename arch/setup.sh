#!/bin/bash

update_system() {
  echo "Updating system"
  sudo pacman -Syu --noconfirm
}
