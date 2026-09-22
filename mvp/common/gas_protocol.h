#ifndef GAS_PROTOCOL_H
#define GAS_PROTOCOL_H
/*
 * JH-TG5110-M1-22 扩散式激光甲烷传感器模块 - 串口协议解析
 * 115200-8N1, 3.3V LVTTL, 主动上报定长 ASCII 帧(CR LF 结尾)
 * A +000.00 SP +21.4 SP 1001.01 SP +21.5 SP B+021.6 SP 00 SP 28 CR LF
 * 换算: 100%LEL=5%Vol -> 低报10%LEL=0.50%Vol 高报50%LEL=2.50%Vol
 */
#include <stdint.h>

#define GAS_FRAME_MAX       64u
#define GAS_LOW_ALARM_VOL   0.50f
#define GAS_HIGH_ALARM_VOL  2.50f

typedef struct {
    float conc_vol, temp1, pressure, temp2, temp3;
    uint8_t fault, checksum_ok, level;
} gas_frame_t;

int gas_parser_feed(uint8_t byte, gas_frame_t *out);
int gas_verify_checksum(const uint8_t *frame);
uint8_t gas_level(float conc_vol, float low_thr, float high_thr);
#endif