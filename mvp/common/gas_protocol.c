#include "gas_protocol.h"
#include <string.h>
#include <stdlib.h>
#include <stdio.h>

typedef struct { uint8_t buf[GAS_FRAME_MAX]; uint16_t len; } gas_ctx_t;
static gas_ctx_t g_ctx;

static float parse_num(const char *s, uint8_t n){
    char tmp[16]; uint8_t i=0;
    for(uint8_t k=0;k<n && i<15;k++){
        char c=s[k];
        if(c=='B') continue;
        if(c=='+'||c=='-'||c=='.'||(c>='0'&&c<='9')) tmp[i++]=c;
    }
    tmp[i]=0;
    return (float)strtof(tmp,NULL);
}

int gas_verify_checksum(const uint8_t *f){
    uint8_t x=0;
    for(int i=0;i<38;i++) x ^= f[i];
    char dec[8]; int n = snprintf(dec,sizeof(dec),"%d",(int)x);
    if(n<2) return 0;
    const char *tail = dec + (n-2);
    return (tail[0]==f[40] && tail[1]==f[41]) ? 1 : 0;
}

uint8_t gas_level(float v,float lo,float hi){
    if(v>=hi) return 2;
    if(v>=lo) return 1;
    return 0;
}

int gas_parser_feed(uint8_t byte, gas_frame_t *out){
    if(byte=='A') g_ctx.len=0;
    if(g_ctx.len < GAS_FRAME_MAX) g_ctx.buf[g_ctx.len++]=byte; else g_ctx.len=0;
    if(g_ctx.len>=4 && byte=='\n' && g_ctx.buf[g_ctx.len-2]=='\r'){
        const uint8_t *f=g_ctx.buf; uint16_t n=g_ctx.len;
        g_ctx.len=0;
        if(n<42) return 0;
        memset(out,0,sizeof(*out));
        out->conc_vol = parse_num((const char*)&f[1],7);
        out->temp1    = parse_num((const char*)&f[9],5);
        out->pressure = parse_num((const char*)&f[15],7);
        out->temp2    = parse_num((const char*)&f[23],5);
        out->temp3    = parse_num((const char*)&f[29],7);
        out->fault    = (uint8_t)((f[37]-'0')*10 + (f[38]-'0'));
        out->checksum_ok = gas_verify_checksum(f);
        out->level = gas_level(out->conc_vol, GAS_LOW_ALARM_VOL, GAS_HIGH_ALARM_VOL);
        return 1;
    }
    return 0;
}