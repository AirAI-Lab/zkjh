#include <stdio.h>
#include <stdlib.h>
#include <fcntl.h>
#include <unistd.h>
#include <string.h>
#include <errno.h>
#include <sys/ioctl.h>
#include <linux/i2c-dev.h>

static int parse_u8(const char *text, unsigned char *value)
{
    char *end = NULL;
    unsigned long result;

    errno = 0;
    result = strtoul(text, &end, 0);
    if (errno || !end || *end || result > 0xff)
        return -1;
    *value = (unsigned char)result;
    return 0;
}

int main(int argc, char **argv)
{
    unsigned char addr, reg, val;
    char path[32];
    int fd, ret;

    if (argc != 4 && argc != 5) {
        fprintf(stderr, "usage: %s BUS ADDR REG [VALUE]\n", argv[0]);
        return 2;
    }

    snprintf(path, sizeof(path), "/dev/i2c-%d", atoi(argv[1]));
    if (parse_u8(argv[2], &addr) || parse_u8(argv[3], &reg)) {
        fprintf(stderr, "bad address/register\n");
        return 2;
    }

    fd = open(path, O_RDWR);
    if (fd < 0) {
        perror(path);
        return 1;
    }
    if (ioctl(fd, I2C_SLAVE, addr) < 0) {
        perror("I2C_SLAVE");
        close(fd);
        return 1;
    }

    if (argc == 5) {
        if (parse_u8(argv[4], &val)) {
            fprintf(stderr, "bad value\n");
            close(fd);
            return 2;
        }
        unsigned char buf[2] = { reg, val };
        ret = write(fd, buf, 2);
        if (ret != 2) {
            fprintf(stderr, "write reg 0x%02x: ret=%d errno=%d\n", reg, ret, errno);
            close(fd);
            return 1;
        }
        printf("W bus=%d addr=0x%02x reg=0x%02x val=0x%02x\n",
               atoi(argv[1]), addr, reg, val);
    } else {
        ret = write(fd, &reg, 1);
        if (ret != 1) {
            fprintf(stderr, "select reg 0x%02x: ret=%d errno=%d\n", reg, ret, errno);
            close(fd);
            return 1;
        }
        ret = read(fd, &val, 1);
        if (ret != 1) {
            fprintf(stderr, "read reg 0x%02x: ret=%d errno=%d\n", reg, ret, errno);
            close(fd);
            return 1;
        }
        printf("R bus=%d addr=0x%02x reg=0x%02x val=0x%02x\n",
               atoi(argv[1]), addr, reg, val);
    }

    close(fd);
    return 0;
}
