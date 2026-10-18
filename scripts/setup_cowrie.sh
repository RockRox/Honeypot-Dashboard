#!/bin/bash
# setup_cowrie.sh — Install and configure Cowrie on Ubuntu 22.04
# Run as ubuntu user on your Oracle Cloud VM:
#   chmod +x setup_cowrie.sh && ./setup_cowrie.sh

set -e

echo "=== Honeypot Setup: Cowrie on Ubuntu 22.04 ==="

# 1. System updates
sudo apt update && sudo apt upgrade -y
sudo apt install -y git python3-venv python3-pip libssl-dev libffi-dev \
    build-essential libpython3-dev authbind

# 2. Create dedicated cowrie user
if ! id -u cowrie &>/dev/null; then
    sudo adduser --disabled-password --gecos "" cowrie
    echo "[+] Created cowrie user"
fi

# 3. Clone Cowrie
sudo su - cowrie -c "
    if [ ! -d ~/cowrie ]; then
        git clone https://github.com/cowrie/cowrie.git ~/cowrie
    fi
    cd ~/cowrie
    python3 -m venv cowrie-env
    source cowrie-env/bin/activate
    pip install --upgrade pip
    pip install -r requirements.txt
    echo '[+] Cowrie installed'
"

# 4. Configure Cowrie
sudo su - cowrie -c "
    cd ~/cowrie
    cp etc/cowrie.cfg.dist etc/cowrie.cfg
    sed -i 's/^#hostname = svr04/hostname = webserver01/' etc/cowrie.cfg
    sed -i 's/^#listen_endpoints = .*/listen_endpoints = tcp:2222:interface=0.0.0.0/' etc/cowrie.cfg
    sed -i 's/^enabled = false/enabled = true/' etc/cowrie.cfg
    echo '[+] Cowrie configured'
"

# 5. systemd service
sudo tee /etc/systemd/system/cowrie.service > /dev/null <<'EOF'
[Unit]
Description=Cowrie SSH/Telnet Honeypot
After=network.target

[Service]
Type=forking
User=cowrie
ExecStart=/home/cowrie/cowrie/bin/cowrie start
ExecStop=/home/cowrie/cowrie/bin/cowrie stop
Restart=always
Environment=VIRTUAL_ENV=/home/cowrie/cowrie/cowrie-env
Environment=PATH=/home/cowrie/cowrie/cowrie-env/bin:/usr/bin:/bin
PIDFile=/home/cowrie/cowrie/var/run/cowrie.pid

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable cowrie
sudo systemctl start cowrie

echo ""
echo "=== Setup complete ==="
echo "Cowrie status: $(sudo systemctl is-active cowrie)"
echo "Log file:      /home/cowrie/cowrie/var/log/cowrie/cowrie.json"
echo ""
echo "Next step: run scripts/setup_iptables.sh to redirect ports 22 → 2222"
