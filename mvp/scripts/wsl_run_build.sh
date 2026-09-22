#!/bin/bash
set -e
sudo apt-get install -y cpio >/dev/null 2>&1 || sudo apt-get install -y cpio
command -v cpio
# crc32 shim (SDK 仅用于打印校验值)
if ! command -v crc32 >/dev/null 2>&1; then
  sudo tee /usr/local/bin/crc32 >/dev/null <<'EOF'
#!/usr/bin/env python3
import sys, zlib
for f in sys.argv[1:]:
    with open(f,'rb') as fp: print("%08x" % (zlib.crc32(fp.read()) & 0xffffffff), f)
EOF
  sudo chmod +x /usr/local/bin/crc32
fi
crc32 /etc/hostname
cd /home/wennu/zkjh/Software
set -a; source .env; set +a
export PATH=/home/wennu/zkjh/toolchain/bin-gnu:$PATH
rm -f out/camera/rootfs_camera.cpio out/camera/rootfs_camera.cpio.jzlzma
./build/build_camera_all.sh > /tmp/zk_build7.log 2>&1
RC=$?
echo "ALL EXIT=$RC $(date)"
tail -6 /tmp/zk_build7.log
echo "=== out ==="; ls -la out/camera/ | grep -v ^d; ls -la out/*.bin