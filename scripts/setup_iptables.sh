#!/bin/bash
# setup_iptables.sh — Redirect port 22 → 2222 and 23 → 2223 (Cowrie ports)
# Run as root/sudo on your Oracle Cloud VM

set -e

echo "=== Setting up iptables port redirection ==="

# Allow Cowrie ports
sudo iptables -A INPUT -p tcp --dport 2222 -j ACCEPT
sudo iptables -A INPUT -p tcp --dport 2223 -j ACCEPT
sudo iptables -A INPUT -p tcp --dport 5000 -j ACCEPT

# Redirect incoming port 22 → 2222, port 23 → 2223
sudo iptables -t nat -A PREROUTING -p tcp --dport 22 -j REDIRECT --to-port 2222
sudo iptables -t nat -A PREROUTING -p tcp --dport 23 -j REDIRECT --to-port 2223

# Persist rules across reboots
sudo apt install -y iptables-persistent
sudo netfilter-persistent save

echo "[+] iptables rules saved"
echo "[+] Port 22 → 2222 (SSH honeypot)"
echo "[+] Port 23 → 2223 (Telnet honeypot)"
echo ""
echo "Verify with: sudo iptables -t nat -L PREROUTING -n -v"
