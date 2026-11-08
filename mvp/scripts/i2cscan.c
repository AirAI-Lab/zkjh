#include <stdio.h>
#include <stdlib.h>
#include <fcntl.h>
#include <string.h>
#include <sys/ioctl.h>
#include <linux/i2c-dev.h>
#include <unistd.h>

int main(int argc, char *argv[]) {
    int bus = argc > 1 ? atoi(argv[1]) : 0;
    char path[32];
    sprintf(path, "/dev/i2c-%d", bus);
    int fd = open(path, O_RDWR);
    if (fd < 0) { printf("ERR: cannot open %s\n", path); return 1; }
    
    printf("I2C bus %d scan (03-77):\n", bus);
    int found = 0;
    for (int addr = 0x03; addr <= 0x77; addr++) {
        if (ioctl(fd, I2C_SLAVE, addr) < 0) continue;
        unsigned char cmd = 0, buf[1];
        // Write 0 then read 1 = device ACK check
        if (write(fd, &cmd, 1) >= 0 || read(fd, buf, 1) >= 0) {
            printf("  0x%02x (%d) ACK\n", addr, addr);
            found++;
        }
    }
    if (!found) printf("  No devices found\n");
    printf("Total: %d devices\n", found);
    close(fd);
    return 0;
}
