# Server setup

This document captures the full setup for provisioning a lightweight, responsive,
single-instance AWS environment suitable for Dockerized FastAPI + React + MongoDB
apps, using EBS and Ubuntu. Updated: 2025-03-27.


## Image deployment

We are using a **single EC2 instance**. This should be enough to run docker compose with:
- FastAPI backend
- Vite + React frontend
- MongoDB (local, dockerized)
- Static storage on attached EBS

This instance is designed for **very low use**, with high idle time but responsive behavior.

## 🔧 EC2 Instance Configuration

https://console.aws.amazon.com/ec2/home#LaunchInstanceWizard


### Instance Type
- **Ubuntu 22.04 LTS (arm64)**
- **Type:** `t4g.small` (2 vCPUs, 2 GiB RAM)
- **Alternative (x86):** `t3.small`
- **Why:** ARM-based Graviton2 instance is cheaper and works well with containers,
  especially on an M2 Mac dev environment

n### Storage
- **Root volume:** 50 GiB `gp3`
  - Format: `ext4` (default)
- **Reason for gp3:** Faster, cheaper, and more configurable than gp2

### Networking and Access

Use deg-office security group and DEG-Amazon-key.pem

## 🐧 Linux Setup

- SSH into the instance
- Install Docker.  See https://docs.docker.com/engine/install/ubuntu/
- Install caddy. See https://caddyserver.com/docs/install#debian-ubuntu-raspbian
- Install other tools:

```bash
sudo apt install emacs make unzip zip
sudo apt update && sudo apt upgrade && sudo apt autoremove
```

- Allocate and attach an AWS Elastic IP address
- Setup an `A` DNS record on godaddy.command


## App setup

- Use sftp to copy `.ssh/config` and `.ssh/id_rsa_github`


## Start and stop

```
make server-up
...
make server-down
```
