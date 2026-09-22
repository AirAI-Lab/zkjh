#include "zk_protocol.h"
#include <string.h>

uint16_t zk_crc16(const uint8_t *data, uint16_t len){
    uint16_t crc=0xFFFF;
    for(uint16_t i=0;i<len;i++){
        crc ^= data[i];
        for(uint8_t b=0;b<8;b++) crc = (crc&1) ? (crc>>1)^0xA001 : (crc>>1);
    }
    return crc;
}

uint16_t zk_pack(uint8_t cmd,const uint8_t *pl,uint16_t n,uint8_t *out){
    uint16_t i=0;
    out[i++]=ZK_HEAD0; out[i++]=ZK_HEAD1;
    out[i++]=(uint8_t)(n+1); out[i++]=cmd;
    if(n) memcpy(&out[i],pl,n);
    i+=n;
    uint16_t crc=zk_crc16(out,i);
    out[i++]=crc&0xFF; out[i++]=crc>>8;
    return i;
}

typedef struct { uint8_t st,buf[ZK_MAX_PAYLOAD+8]; uint16_t n,len; } zk_ctx_t;
static zk_ctx_t g;

int16_t zk_parse_feed(uint8_t byte,uint8_t *cmd,uint8_t *pl,uint16_t pl_max){
    switch(g.st){
    case 0: if(byte==ZK_HEAD0) g.st=1; break;
    case 1: if(byte==ZK_HEAD1) g.st=2; else g.st=0; break;
    case 2:
        g.len=byte; g.n=0;
        if(g.len<1||g.len>ZK_MAX_PAYLOAD+1){ g.st=0; break; }
        g.st=3; break;
    case 3:
        g.buf[g.n++]=byte;
        if(g.n==g.len) g.st=4;
        break;
    case 4:
        g.buf[g.n++]=byte;
        if(g.n==g.len+2){
            g.st=0;
            uint16_t crc=zk_crc16(g.buf,g.len);
            uint16_t rx=(uint16_t)(g.buf[g.len]|(g.buf[g.len+1]<<8));
            if(crc!=rx) return -2;
            uint16_t plen=g.len-1;
            if(plen>pl_max) return -3;
            memcpy(pl,&g.buf[1],plen);
            *cmd=g.buf[0];
            return (int16_t)plen;
        }
        break;
    }
    return -1;
}