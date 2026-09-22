#ifndef ZK_PROTOCOL_H
#define ZK_PROTOCOL_H
/* JKD-621-T23 HC32L136 <-> T23 UART0 协议 (ICD v0.1 ch2)
 * 115200-8N1; AA 55 | LEN | CMD | PAYLOAD | CRC16-MODBUS(lo,hi); LEN=CMD+PAYLOAD */
#include <stdint.h>

#define ZK_HEAD0 0xAA
#define ZK_HEAD1 0x55
#define ZK_MAX_PAYLOAD 200

enum {
    ZK_CMD_WAKE_NOTICE=0x01, ZK_CMD_STATUS_REQ=0x02, ZK_CMD_STATUS_RSP=0x03,
    ZK_CMD_GAS_REQ=0x04, ZK_CMD_GAS_RSP=0x05, ZK_CMD_SET_WAKE=0x10,
    ZK_CMD_SET_SENSOR=0x11, ZK_CMD_SLEEP=0x20, ZK_CMD_SLEEP_ACK=0x21,
    ZK_CMD_WDT_FEED=0x30, ZK_CMD_HEARTBEAT=0x7F,
};
enum {
    ZK_WAKE_RTC=1, ZK_WAKE_VIB=2, ZK_WAKE_TILT=3, ZK_WAKE_DISPLACE=4,
    ZK_WAKE_HALL=5, ZK_WAKE_GAS=6, ZK_WAKE_KEY=7, ZK_WAKE_WDT_RST=8,
};

uint16_t zk_crc16(const uint8_t *data, uint16_t len);
uint16_t zk_pack(uint8_t cmd, const uint8_t *pl, uint16_t n, uint8_t *out);
int16_t  zk_parse_feed(uint8_t byte, uint8_t *cmd, uint8_t *pl, uint16_t pl_max);
#endif