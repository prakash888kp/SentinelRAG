#!/usr/bin/env bash
# SentinelRAG Azure Ubuntu VM bootstrap — Docker + Compose
# Run once on the VM as a sudo-capable user (e.g. azureuser).
set -euo pipefail

echo "==> Updating apt"
sudo apt-get update -y
sudo DEBIAN_FRONTEND=noninteractive apt-get upgrade -y

echo "==> Installing prerequisites"
sudo apt-get install -y ca-certificates curl gnupg lsb-release git

echo "==> Installing Docker Engine + Compose plugin"
sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
sudo chmod a+r /etc/apt/keyrings/docker.gpg
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  $(. /etc/os-release && echo \"$VERSION_CODENAME\") stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt-get update -y
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

echo "==> Allowing current user to run docker"
sudo usermod -aG docker "$USER"

echo "==> Docker versions"
sudo docker --version
sudo docker compose version

echo "==> Done. Log out/in (or newgrp docker), then:"
echo "    cd ~/sentinelrag && docker compose up -d"
echo "    curl -s http://127.0.0.1:8000/health"
