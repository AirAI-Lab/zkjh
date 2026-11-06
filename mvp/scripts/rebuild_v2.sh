cd /home/wennu/zkjh/Software
source .env
export PATH=/home/wennu/zkjh/toolchain/bin-gnu:$PATH
rm -f out/camera/tag.bin
./build/build_camera_all.sh > /tmp/build_v2.log 2>&1
echo BUILD_EXIT=$?
ls -la out/*.bin 2>/dev/null