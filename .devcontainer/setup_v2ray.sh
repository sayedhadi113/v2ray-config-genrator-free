#!/bin/bash
set -e

echo "Updating system..."
apt-get update && apt-get install -y curl wget unzip jq

echo "Installing V2Ray..."
bash <(curl -L https://raw.githubusercontent.com/v2fly/fhs-install-v2ray/master/install-release.sh)

# استفاده از UUID که از بیرون (ربات) می‌آید، یا تولید تصادفی
UUID=${V2RAY_UUID:-$(cat /proc/sys/kernel/random/uuid)}
echo "Using UUID: $UUID"

# نوشتن کانفیگ V2Ray (VMess+WebSocket روی پورت 443)
cat > /usr/local/etc/v2ray/config.json << EOF
{
  "inbounds": [{
    "port": 443,
    "protocol": "vmess",
    "settings": {
      "clients": [{"id": "$UUID"}]
    },
    "streamSettings": {
      "network": "ws",
      "wsSettings": {
        "path": "/"
      }
    }
  }],
  "outbounds": [{
    "protocol": "freedom",
    "settings": {}
  }]
}
EOF

# فعال کردن و شروع V2Ray
systemctl enable v2ray
systemctl start v2ray

# گرفتن IP عمومی Codespace
IP=$(curl -s ifconfig.me)

# ذخیره IP و UUID در یک فایل ساده (بعداً ربات آن را می‌خواند)
echo "$IP|$UUID" > /tmp/v2ray_info.txt

# همچنین اجازه می‌دهیم که ربات از طریق API گیت‌هاب این فایل را بخواند (نیاز به توکن)
# برای سادگی، فایل را در مسیری که ربات بتواند از طریق GitHub API دانلود کند می‌گذاریم:
# ما آن را به عنوان یک artifact ذخیره نمی‌کنیم؛ ربات از طریق دستور `gh codespace ...` بعداً IP را می‌گیرد.

echo "V2Ray started on $IP with UUID $UUID"
