#!/bin/bash
apt-get update
apt-get install -y curl wget unzip
bash <(curl -L https://raw.githubusercontent.com/v2fly/fhs-install-v2ray/master/install-release.sh)
# تنظیمات کانفیگ V2Ray
cat > /usr/local/etc/v2ray/config.json << EOF
{
  "inbounds": [{
    "port": 443,
    "protocol": "vmess",
    "settings": {
      "clients": [{"id": "$(cat /proc/sys/kernel/random/uuid)"}]
    },
    "streamSettings": {"network": "ws"}
  }],
  "outbounds": [{"protocol": "freedom"}]
}
EOF
systemctl start v2ray
