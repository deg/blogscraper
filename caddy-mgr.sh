#!/bin/bash

ACTION="${1:?Usage: $0 <start|stop|disable|remove|restart|status> <service-name> [domain] [port]}"
SERVICE="${2:?Missing service name}"
DOMAIN="${3:-}"
PORT="${4:-}"
USER_NAME="ubuntu"
WORK_DIR="$(pwd)"
UNIT_FILE="/etc/systemd/system/${SERVICE}.service"

start_or_install() {
  if [[ ! -f "$UNIT_FILE" ]]; then
    if [[ -z "$DOMAIN" || -z "$PORT" ]]; then
      echo "❌ Missing DOMAIN or PORT for install."
      echo "Usage: $0 start <service-name> <domain> <port>"
      exit 1
    fi
    echo "📦 Installing new proxy for $DOMAIN → localhost:$PORT"

    sudo tee "$UNIT_FILE" > /dev/null <<EOF
[Unit]
Description=Caddy reverse proxy for $DOMAIN
After=network.target

[Service]
ExecStart=/usr/bin/caddy reverse-proxy --from $DOMAIN --to :$PORT
WorkingDirectory=$WORK_DIR
Restart=always
User=$USER_NAME

[Install]
WantedBy=multi-user.target
EOF

    sudo systemctl daemon-reload
    sudo systemctl enable "$SERVICE"
  else
    echo "🔁 Restarting existing service: $SERVICE"
  fi

  sudo systemctl restart "$SERVICE"
  echo "✅ $SERVICE is running"
}

case "$ACTION" in
  start)
    start_or_install
    ;;
  stop)
    sudo systemctl stop "$SERVICE"
    ;;
  disable)
    sudo systemctl disable "$SERVICE"
    ;;
  restart)
    sudo systemctl restart "$SERVICE"
    ;;
  status)
    sudo systemctl status "$SERVICE"
    ;;
  remove)
    sudo systemctl stop "$SERVICE"
    sudo systemctl disable "$SERVICE"
    sudo rm -f "$UNIT_FILE"
    sudo systemctl daemon-reload
    echo "🧹 Removed $SERVICE"
    ;;
  *)
    echo "❌ Unknown action: $ACTION"
    echo "Usage: $0 <start|stop|disable|remove|restart|status> <service-name> [domain] [port]"
    exit 1
    ;;
esac
