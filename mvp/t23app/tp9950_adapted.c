/*
 * tp9950.c
 *
 * Copyright (C) 2012 Ingenic Semiconductor Co., Ltd.
 *
 * This program is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License version 2 as
 * published by the Free Software Foundation.
 */
#define DEBUG

#include <linux/init.h>
#include <linux/module.h>
#include <linux/slab.h>
#include <linux/i2c.h>
#include <linux/delay.h>
#include <linux/gpio.h>
#include <linux/clk.h>
#include <linux/proc_fs.h>
#include <soc/gpio.h>

#include <tx-isp-common.h>
#include <sensor-common.h>

#define TP9950_CHIP_ID_H	(0x28)
#define TP9950_CHIP_ID_L	(0x60)
#define SENSOR_OUTPUT_MAX_FPS 25
#define SENSOR_OUTPUT_MIN_FPS 5
#define SENSOR_VERSION	"H20230304a"

static int reset_gpio = GPIO_PA(18);
static int pwdn_gpio = -1;
static int sensor_resolution = TX_SENSOR_RES_200;

static unsigned char tp_fmt, tp_fmt1 = 0;

//#define EVEN_ODD
#define PRE_SET_PIC


#ifdef EVEN_ODD
#define CVBS_TIME 2
#define P_BLACK 24
#define N_BLACK 24

#else
#define CVBS_TIME 1
#define P_BLACK 0
#define N_BLACK 0
#endif

#define SHARPNESS 0x59

struct regval_list {
	unsigned char reg_num;
	unsigned char value;
};

/*
 * the part of driver maybe modify about different sensor and different board.
 */
struct tx_isp_sensor_attribute tp9950_attr;

unsigned int tp9950_alloc_again(unsigned int isp_gain, unsigned char shift, unsigned int *sensor_again)
{
	return isp_gain;
}

unsigned int tp9950_alloc_dgain(unsigned int isp_gain, unsigned char shift, unsigned int *sensor_dgain)
{
	return 0;
}

struct tx_isp_mipi_bus tp9950_mipi_hda={
        .mode = SENSOR_MIPI_OTHER_MODE,
        .clk = 594,
        .lans = 2,
        .settle_time_apative_en = 0,
        .mipi_sc.sensor_csi_fmt = TX_SENSOR_YUV422,
        .mipi_sc.hcrop_diff_en = 0,
        .mipi_sc.mipi_vcomp_en = 0,
        .mipi_sc.mipi_hcomp_en = 0,
        .mipi_sc.line_sync_mode = 0,
        .image_twidth = 1280,
        .image_theight = 720,
        .mipi_sc.mipi_crop_start0x = 0,
        .mipi_sc.mipi_crop_start0y = 0,
        .mipi_sc.mipi_crop_start1x = 0,
        .mipi_sc.mipi_crop_start1y = 0,
        .mipi_sc.mipi_crop_start2x = 0,
        .mipi_sc.mipi_crop_start2y = 0,
        .mipi_sc.mipi_crop_start3x = 0,
        .mipi_sc.mipi_crop_start3y = 0,
        .mipi_sc.work_start_flag = 0,
        .mipi_sc.data_type_en = 0,
        .mipi_sc.data_type_value = YUV422_8BIT,
        .mipi_sc.del_start = 0,
        .mipi_sc.sensor_frame_mode = TX_SENSOR_DEFAULT_FRAME_MODE,
        .mipi_sc.sensor_fid_mode = 0,
        .mipi_sc.sensor_mode = TX_SENSOR_DEFAULT_MODE,
};

//????a720x576ꡧPAL??????720X480ꡧNTSC???

struct tx_isp_mipi_bus tp9950_mipi_cvbs={
        .mode = SENSOR_MIPI_OTHER_MODE,
        .clk = 594,
        .lans = 2,
        .settle_time_apative_en = 0,
        .mipi_sc.sensor_csi_fmt = TX_SENSOR_YUV422,
        .mipi_sc.hcrop_diff_en = 0,
        .mipi_sc.mipi_vcomp_en = 0,
        .mipi_sc.mipi_hcomp_en = 0,
        .mipi_sc.line_sync_mode = 0,
        .image_twidth = 720,
        .image_theight = 240*CVBS_TIME+P_BLACK,
        .mipi_sc.mipi_crop_start0x = 0,
        .mipi_sc.mipi_crop_start0y = 0,
        .mipi_sc.mipi_crop_start1x = 0,
        .mipi_sc.mipi_crop_start1y = 0,
        .mipi_sc.mipi_crop_start2x = 0,
        .mipi_sc.mipi_crop_start2y = 0,
        .mipi_sc.mipi_crop_start3x = 0,
        .mipi_sc.mipi_crop_start3y = 0,
        .mipi_sc.work_start_flag = 0,
        .mipi_sc.data_type_en = 0,
        .mipi_sc.data_type_value = YUV422_8BIT,
        .mipi_sc.del_start = 0,
        .mipi_sc.sensor_frame_mode = TX_SENSOR_DEFAULT_FRAME_MODE,
        .mipi_sc.sensor_fid_mode = 0,
        .mipi_sc.sensor_mode = TX_SENSOR_DEFAULT_MODE,
};


struct tx_isp_mipi_bus tp9950_mipi_cvbs_p={
        .mode = SENSOR_MIPI_OTHER_MODE,
        .clk = 594,
        .lans = 2,
        .settle_time_apative_en = 0,
        .mipi_sc.sensor_csi_fmt = TX_SENSOR_YUV422,
        .mipi_sc.hcrop_diff_en = 0,
        .mipi_sc.mipi_vcomp_en = 0,
        .mipi_sc.mipi_hcomp_en = 0,
        .mipi_sc.line_sync_mode = 0,
        .image_twidth = 720,
        .image_theight = 288*CVBS_TIME+N_BLACK,
        .mipi_sc.mipi_crop_start0x = 0,
        .mipi_sc.mipi_crop_start0y = 0,
        .mipi_sc.mipi_crop_start1x = 0,
        .mipi_sc.mipi_crop_start1y = 0,
        .mipi_sc.mipi_crop_start2x = 0,
        .mipi_sc.mipi_crop_start2y = 0,
        .mipi_sc.mipi_crop_start3x = 0,
        .mipi_sc.mipi_crop_start3y = 0,
        .mipi_sc.work_start_flag = 0,
        .mipi_sc.data_type_en = 0,
        .mipi_sc.data_type_value = YUV422_8BIT,
        .mipi_sc.del_start = 0,
        .mipi_sc.sensor_frame_mode = TX_SENSOR_DEFAULT_FRAME_MODE,
        .mipi_sc.sensor_fid_mode = 0,
        .mipi_sc.sensor_mode = TX_SENSOR_DEFAULT_MODE,
};


struct tx_isp_sensor_attribute tp9950_attr={
	.name = "tp9950",
	.chip_id = 0x2860,
	.cbus_type = TX_SENSOR_CONTROL_INTERFACE_I2C,
	.cbus_mask = V4L2_SBUS_MASK_SAMPLE_8BITS | V4L2_SBUS_MASK_ADDR_8BITS,
	/* i2c */
	.cbus_device = 0x44,
	/* mipi */
	.dbus_type = TX_SENSOR_DATA_INTERFACE_MIPI,
    .mipi = {
                .mode = SENSOR_MIPI_OTHER_MODE,
                .clk = 594,
                .lans = 2,
                .settle_time_apative_en = 0,
                .mipi_sc.sensor_csi_fmt = TX_SENSOR_YUV422,
                .mipi_sc.hcrop_diff_en = 0,
                .mipi_sc.mipi_vcomp_en = 0,
                .mipi_sc.mipi_hcomp_en = 0,
                .mipi_sc.line_sync_mode = 0,
                .image_twidth = 1920,
                .image_theight = 1080,
                .mipi_sc.mipi_crop_start0x = 0,
                .mipi_sc.mipi_crop_start0y = 0,
                .mipi_sc.mipi_crop_start1x = 0,
                .mipi_sc.mipi_crop_start1y = 0,
                .mipi_sc.mipi_crop_start2x = 0,
                .mipi_sc.mipi_crop_start2y = 0,
                .mipi_sc.mipi_crop_start3x = 0,
                .mipi_sc.mipi_crop_start3y = 0,
                .mipi_sc.work_start_flag = 0,
                .mipi_sc.data_type_en = 0,
                .mipi_sc.data_type_value = YUV422_8BIT,
                .mipi_sc.del_start = 0,
                .mipi_sc.sensor_frame_mode = TX_SENSOR_DEFAULT_FRAME_MODE,
                .mipi_sc.sensor_fid_mode = 0,
                .mipi_sc.sensor_mode = TX_SENSOR_DEFAULT_MODE,
        },
	.data_type = TX_SENSOR_DATA_TYPE_LINEAR,
	.max_integration_time_native = 1080,
	.integration_time_limit = 1080,
	.total_width = 1920,
	.total_height = 1080,
	.max_integration_time = 1080,
	.sensor_ctrl.alloc_again = tp9950_alloc_again,
	.sensor_ctrl.alloc_dgain = tp9950_alloc_dgain,
};

static struct regval_list tp9950_init_regs_1920_1080_25fps_mipi[] = {
};

static struct regval_list tp9950_init_regs_1280_720_25fps_mipi[] = {
};

static struct regval_list tp9950_init_regs_720_240_25fps_mipi_cvbs[] = {
};
/*
 * the order of the jxf23_win_sizes is [full_resolution, preview_resolution].
 */
static struct tx_isp_sensor_win_setting tp9950_win_sizes[] = {
	/* 1920*1080 @ max 25fps mipi*/
	{
		.width		= 1920,
		.height		= 1080,
		.fps		= 25 << 16 | 1,
		.mbus_code	= V4L2_MBUS_FMT_YUYV8_1X16,
		.colorspace	= V4L2_COLORSPACE_SRGB,
		.regs 		= tp9950_init_regs_1920_1080_25fps_mipi,
	},
	{
		.width		= 1280,
		.height		= 720,
		.fps		= 25 << 16 | 1,
		.mbus_code	= V4L2_MBUS_FMT_YUYV8_1X16,
		.colorspace	= V4L2_COLORSPACE_SRGB,
		.regs 		= tp9950_init_regs_1280_720_25fps_mipi,
	},
	{
		.width		= 720,
		.height		= 240*CVBS_TIME+N_BLACK,
		.fps		= 25 << 16 | 1,
		.mbus_code	= V4L2_MBUS_FMT_YUYV8_1X16,
		.colorspace	= V4L2_COLORSPACE_SRGB,
		.regs 		= tp9950_init_regs_720_240_25fps_mipi_cvbs,
	},
	{
		.width		= 1920,
		.height		= 1080,
		.fps		= 30 << 16 | 1,
		.mbus_code	= V4L2_MBUS_FMT_YUYV8_1X16,
		.colorspace	= V4L2_COLORSPACE_SRGB,
		.regs 		= tp9950_init_regs_1920_1080_25fps_mipi,
	},
	{
		.width		= 1280,
		.height		= 720,
		.fps		= 30 << 16 | 1,
		.mbus_code	= V4L2_MBUS_FMT_YUYV8_1X16,
		.colorspace	= V4L2_COLORSPACE_SRGB,
		.regs 		= tp9950_init_regs_1280_720_25fps_mipi,

	},	
	{
		.width		= 720,
		.height		= 288*CVBS_TIME+P_BLACK,
		.fps		= 25 << 16 | 1,
		.mbus_code	= V4L2_MBUS_FMT_YUYV8_1X16,
		.colorspace	= V4L2_COLORSPACE_SRGB,
		.regs 		= tp9950_init_regs_720_240_25fps_mipi_cvbs,
	},	
};
struct tx_isp_sensor_win_setting *wsize = &tp9950_win_sizes[0];

int tp9950_read(struct tx_isp_subdev *sd, unsigned char reg,
		unsigned char *value)
{
	struct i2c_client *client = tx_isp_get_subdevdata(sd);
	struct i2c_msg msg[2] = {
		[0] = {
			.addr	= client->addr,
			.flags	= 0,
			.len	= 1,
			.buf	= &reg,
		},
		[1] = {
			.addr	= client->addr,
			.flags	= I2C_M_RD,
			.len	= 1,
			.buf	= value,
		}
	};
	int ret;
	ret = private_i2c_transfer(client->adapter, msg, 2);
	if (ret > 0)
		ret = 0;

	return ret;
}

int tp9950_write(struct tx_isp_subdev *sd, unsigned char reg,
		 unsigned char value)
{
	struct i2c_client *client = tx_isp_get_subdevdata(sd);
	unsigned char buf[2] = {reg, value};
	struct i2c_msg msg = {
		.addr	= client->addr,
		.flags	= 0,
		.len	= 2,
		.buf	= buf,
	};
	int ret;
	ret = private_i2c_transfer(client->adapter, &msg, 1);
	if (ret > 0)
		ret = 0;

	return ret;
}

int tp9950_read_iic(struct i2c_client *client, unsigned char reg,
		unsigned char *value)
{
	struct i2c_msg msg[2] = {
		[0] = {
			.addr	= client->addr,
			.flags	= 0,
			.len	= 1,
			.buf	= &reg,
		},
		[1] = {
			.addr	= client->addr,
			.flags	= I2C_M_RD,
			.len	= 1,
			.buf	= value,
		}
	};
	int ret;
	ret = private_i2c_transfer(client->adapter, msg, 2);
	if (ret > 0)
		ret = 0;

	return ret;
}


int tp9950_write_iic(struct i2c_client *client, unsigned char reg,
		 unsigned char value)
{
	unsigned char buf[2] = {reg, value};
	struct i2c_msg msg = {
		.addr	= client->addr,
		.flags	= 0,
		.len	= 2,
		.buf	= buf,
	};
	int ret;
	ret = private_i2c_transfer(client->adapter, &msg, 1);
	if (ret > 0)
		ret = 0;

	return ret;
}

#if 0
static int tp9950_read_array(struct tx_isp_subdev *sd, struct regval_list *vals)
{
	int ret;
	unsigned char val;
	while (vals->reg_num != TP9950_REG_END) {
		if (vals->reg_num == TP9950_REG_DELAY) {
			private_msleep(vals->value);
		} else {
			ret = tp9950_read(sd, vals->reg_num, &val);
			if (ret < 0)
				return ret;
		}
		vals++;
	}
	return 0;
}

static int tp9950_write_array(struct tx_isp_subdev *sd, struct regval_list *vals,unsigned char cnt)
{
	int ret;
//	unsigned char val;
	while(cnt--){
		ret = tp9950_write(sd, vals->reg_num, vals->value);
//		ret = tp9950_read(sd, vals->reg_num, &val);
//		printk("	{0x%x,0x%x}\n",vals->reg_num, vals->value);
		if (ret < 0)
			return ret;
		vals++;
	}
	return 0;
}
#endif

static int tp9950_reset(struct tx_isp_subdev *sd, int val)
{
	return 0;
}

static int tp9950_detect(struct tx_isp_subdev *sd, unsigned int *ident)
{
	unsigned char v;
	int ret;
	ret = tp9950_read(sd, 0xfe, &v);
	ISP_WARNING("-----%s: %d ret = %d, v = 0x%02x\n", __func__, __LINE__, ret,v);
	if (ret < 0)
		return ret;
	if (v != TP9950_CHIP_ID_H)
		return -ENODEV;
	ret = tp9950_read(sd, 0xff, &v);
	ISP_WARNING("-----%s: %d ret = %d, v = 0x%02x\n", __func__, __LINE__, ret,v);
	if (ret < 0)
		return ret;
	/* JKD-621-T23: 兼容 TP9950(0x2850) 与参考 TP9951(0x2860), 上板后按实测固定 */
	if (v != 0x50 && v != 0x60)
		return -ENODEV;
	printk("tp995x chip id = 0x28%02x (%s)\n", v, (v == 0x50 ? "TP9950" : "TP9951"));
	*ident = (*ident << 8) | v;

	return 0;
}

enum{
	VIN1=0,
    VIN2=1,
    VIN3=2,
    VIN4=3,
};

enum{
    STD_TVI,
    STD_HDA, //AHD
};

enum{
    PAL,
    NTSC,
    HD25,
    HD30,
    HD275,	//720p27.5
    FHD25,
    FHD30,
    FHD275,	//1080p27.5
    FHD28,
    UVGA25,  //1280x960p25, must use with MIPI_4CH4LANE_445M
    UVGA30,  //1280x960p30, must use with MIPI_4CH4LANE_445M
    F_UVGA30,  //FH 1280x960p30, 1800x1000
};

enum{
    MIPI_2LANE,
    MIPI_1LANE,
};

print_reg(struct tx_isp_subdev *sd)
{
	int i=0;
	int ret = 0;
	unsigned char data = 0;

	

	tp9950_write(sd,  0x40, 0x00);  //select decoder page
	for(i=0;i<0xff;i++)
	{	
		ret = tp9950_read(sd, i, &data);
		printk("decoder reg=%02x,data=%02x \n",i,data);
	}

	tp9950_write(sd,  0x40, 0x08); //select MIPI page
	for(i=0;i<0xff;i++)
	{	
		ret = tp9950_read(sd, i, &data);
		printk("mipi reg=%02x,data=%02x \n",i,data);
	}


}


void TP9950_mipi_out(struct tx_isp_subdev *sd, unsigned char fmt, unsigned char std, unsigned char lane)
{
	//mipi setting
	tp9950_write(sd,  0x40, 0x08); //select MIPI page
	tp9950_write(sd,  0x02, 0x79);
	tp9950_write(sd,  0x03, 0x71);
	tp9950_write(sd,  0x04, 0x71);

	tp9950_write(sd,  0x20, 0x00);
	
	if(MIPI_1LANE == lane)
	    tp9950_write(sd,  0x21, 0x11);
	else
	    tp9950_write(sd,  0x21, 0x12);
	
	tp9950_write(sd,  0x23, 0x9e);
	
	if(FHD30 == fmt || FHD25 == fmt || FHD275 == fmt || FHD28 == fmt)
	{
		tp9950_write(sd,  0x12, 0x54);
		tp9950_write(sd,  0x13, 0xef);
		
	    if(MIPI_1LANE == lane)
	    		tp9950_write(sd,  0x14, 0x00);
			else
			    tp9950_write(sd,  0x14, 0x41);
			
		tp9950_write(sd,  0x15, 0x02);

		tp9950_write(sd,  0x2a, 0x08);
		tp9950_write(sd,  0x2b, 0x04);
		tp9950_write(sd,  0x2c, 0x0c);
		tp9950_write(sd,  0x2e, 0x02);
	}else if(HD30 == fmt || HD25 == fmt || HD275 == fmt)
	{
		tp9950_write(sd, 0x12, 0x54);			
		tp9950_write(sd, 0x13, 0xef);	
		
	    if(MIPI_1LANE == lane)
	    		tp9950_write(sd, 0x14, 0x00);	
			else
			    tp9950_write(sd, 0x14, 0x41);
			    
			tp9950_write(sd, 0x15, 0x12);			
			
		tp9950_write(sd, 0x2a, 0x08);
		tp9950_write(sd, 0x2b, 0x01);
		tp9950_write(sd, 0x2c, 0x0e);
		tp9950_write(sd, 0x2e, 0x02);					
	}else if(NTSC == fmt || PAL == fmt){
		tp9950_write(sd,  0x12, 0x54);
		tp9950_write(sd,  0x13, 0xef);
		
	    if(MIPI_1LANE == lane)
	    		tp9950_write(sd,  0x14, 0x51);
			else
			    tp9950_write(sd,  0x14, 0x62);
			    
		tp9950_write(sd,  0x15, 0x07);
			
		tp9950_write(sd,  0x2a, 0x08);
		tp9950_write(sd,  0x2b, 0x01);
		tp9950_write(sd,  0x2c, 0x0e);
		tp9950_write(sd,  0x2e, 0x02);
		tp9950_write(sd,  0x22, 0x01);//jjz
		
	}

	tp9950_write(sd,  0x10, 0xa0);
	tp9950_write(sd,  0x10, 0x20);
	/* Enable MIPI CSI2 output */
	tp9950_write(sd,  0x28, 0x02);	 //stream off 
	tp9950_write(sd,  0x28, 0x00);	 //stream on
	tp9950_write(sd,  0x40, 0x00); //back to decoder page
}

void TP9950_sensor_init(struct tx_isp_subdev *sd, unsigned char ch,unsigned char fmt,unsigned char std, unsigned char lane)
{

	tp9950_write(sd,  0x40, 0x00);  //select decoder page
	tp9950_write(sd,  0x06, 0x12);  //default value	
	tp9950_write(sd,  0x42, 0x00);  //common setting for all format	
	tp9950_write(sd,  0x4e, 0x00);  //common setting for MIPI output
	tp9950_write(sd,  0x54, 0x00);  //common setting for MIPI output
	tp9950_write(sd,  0x41, ch);   //video MUX select

#ifdef 	PRE_SET_PIC
	tp9950_write(sd,  0x10, 0);	//brightness	
	tp9950_write(sd,  0x11, 64);   //contrast
	tp9950_write(sd,  0x12, 64);	//saturation		
#endif

	printk("TP9950_sensor_init %d %d \n",fmt,std);

	if(NTSC == fmt) {

// CVBS_960H
		// tp9950_write(sd, 0x02, 0x47);
		// tp9950_write(sd, 0x0c, 0x13);
		// tp9950_write(sd, 0x0d, 0x51);

		// tp9950_write(sd, 0x15, 0x13);
		// tp9950_write(sd, 0x16, 0x76);
		// tp9950_write(sd, 0x17, 0x80);
		// tp9950_write(sd, 0x18, 0x17);
		// tp9950_write(sd, 0x19, 0x20);
		// tp9950_write(sd, 0x1a, 0x17);
		// tp9950_write(sd, 0x1c, 0x09);
		// tp9950_write(sd, 0x1d, 0x48);
	
		// tp9950_write(sd, 0x20, 0x48);
		// tp9950_write(sd, 0x21, 0x84);
		// tp9950_write(sd, 0x22, 0x37);
		// tp9950_write(sd, 0x23, 0x3f);

		// tp9950_write(sd, 0x2b, 0x70);
		// tp9950_write(sd, 0x2c, 0x2a);
		// tp9950_write(sd, 0x2d, 0x64);
		// tp9950_write(sd, 0x2e, 0x56);

		// tp9950_write(sd, 0x30, 0x7a);
		// tp9950_write(sd, 0x31, 0x4a);
		// tp9950_write(sd, 0x32, 0x4d);
		// tp9950_write(sd, 0x33, 0xf0);
		
		// tp9950_write(sd, 0x35, 0x65);
		// tp9950_write(sd, 0x38, 0x00);
		// tp9950_write(sd, 0x39, 0x04);
			
	//PAL 720H
#if 1
		tp9950_write(sd,0x02, 0x47);
		tp9950_write(sd,0x0c, 0x13); 
		tp9950_write(sd,0x0d, 0x50);  

		tp9950_write(sd,0x15, 0x03);
		tp9950_write(sd,0x16, 0xd6); 
		tp9950_write(sd,0x17, 0xa0); 
		tp9950_write(sd,0x18, 0x12);
		tp9950_write(sd,0x19, 0xf0);
		tp9950_write(sd,0x1a, 0x05);				
		tp9950_write(sd,0x1c, 0x06);
		tp9950_write(sd,0x1d, 0xb4);
	
		tp9950_write(sd,0x20, 0x40);  
		tp9950_write(sd,0x21, 0x84); 
		tp9950_write(sd,0x22, 0x36);
		tp9950_write(sd,0x23, 0x3c);

		tp9950_write(sd,0x2b, 0x70);  
		tp9950_write(sd,0x2c, 0x2a); 
		tp9950_write(sd,0x2d, 0x4b);
		tp9950_write(sd,0x2e, 0x57);

		tp9950_write(sd,0x30, 0x62);  
		tp9950_write(sd,0x31, 0xbb); 
		tp9950_write(sd,0x32, 0x96);
		tp9950_write(sd,0x33, 0xcb);
		
		tp9950_write(sd,0x35, 0x65); 
		tp9950_write(sd,0x38, 0x00);			
		tp9950_write(sd,0x39, 0x04); 

#else


		tp9950_write(sd, 0x02, 0x47);
		tp9950_write(sd, 0x06, 0x32);
		tp9950_write(sd, 0x0c, 0x13);
		tp9950_write(sd, 0x0d, 0x51);

		tp9950_write(sd, 0x15, 0x03);
		tp9950_write(sd, 0x16, 0xf0); 
		tp9950_write(sd, 0x17, 0xa0); 
		tp9950_write(sd, 0x18, 0x17);
		tp9950_write(sd, 0x19, 0x20);
		tp9950_write(sd, 0x1a, 0x15);
		tp9950_write(sd, 0x1c, 0x06);
		tp9950_write(sd, 0x1d, 0xc0);
	
		tp9950_write(sd, 0x20, 0x48);
		tp9950_write(sd, 0x21, 0x84);
		tp9950_write(sd, 0x22, 0x37);
		tp9950_write(sd, 0x23, 0x3f);

		tp9950_write(sd, 0x2b, 0x70);
		tp9950_write(sd, 0x2c, 0x2a);
		tp9950_write(sd, 0x2d, 0x4b);
		tp9950_write(sd, 0x2e, 0x56);

		tp9950_write(sd, 0x30, 0x7a);
		tp9950_write(sd, 0x31, 0x4a);
		tp9950_write(sd, 0x32, 0x4d);
		tp9950_write(sd, 0x33, 0xfb);
		
		tp9950_write(sd, 0x35, 0x65);
		tp9950_write(sd, 0x38, 0x00);
		tp9950_write(sd, 0x39, 0x04);
#endif

	}else if(PAL== fmt) {

#if 0
		tp9950_write(sd,0x02, 0x47);
		tp9950_write(sd,0x0c, 0x13); 
		tp9950_write(sd,0x0d, 0x50);  

		tp9950_write(sd,0x15, 0x03);
		tp9950_write(sd,0x16, 0xd6); 
		tp9950_write(sd,0x17, 0xa0); 
		tp9950_write(sd,0x18, 0x12);
		tp9950_write(sd,0x19, 0xf0);
		tp9950_write(sd,0x1a, 0x05);				
		tp9950_write(sd,0x1c, 0x06);
		tp9950_write(sd,0x1d, 0xb4);
	
		tp9950_write(sd,0x20, 0x40);  
		tp9950_write(sd,0x21, 0x84); 
		tp9950_write(sd,0x22, 0x36);
		tp9950_write(sd,0x23, 0x3c);

		tp9950_write(sd,0x2b, 0x70);  
		tp9950_write(sd,0x2c, 0x2a); 
		tp9950_write(sd,0x2d, 0x4b);
		tp9950_write(sd,0x2e, 0x57);

		tp9950_write(sd,0x30, 0x62);  
		tp9950_write(sd,0x31, 0xbb); 
		tp9950_write(sd,0x32, 0x96);
		tp9950_write(sd,0x33, 0xcb);
		
		tp9950_write(sd,0x35, 0x65); 
		tp9950_write(sd,0x38, 0x00);			
		tp9950_write(sd,0x39, 0x04); 

#else


		tp9950_write(sd, 0x02, 0x47);
		tp9950_write(sd, 0x06, 0x32);
		tp9950_write(sd, 0x0c, 0x13);
		tp9950_write(sd, 0x0d, 0x51);

		tp9950_write(sd, 0x15, 0x03);
		tp9950_write(sd, 0x16, 0xf0); 
		tp9950_write(sd, 0x17, 0xa0); 
		tp9950_write(sd, 0x18, 0x17);
		tp9950_write(sd, 0x19, 0x20);
		tp9950_write(sd, 0x1a, 0x15);
		tp9950_write(sd, 0x1c, 0x06);
		tp9950_write(sd, 0x1d, 0xc0);
	
		tp9950_write(sd, 0x20, 0x48);
		tp9950_write(sd, 0x21, 0x84);
		tp9950_write(sd, 0x22, 0x37);
		tp9950_write(sd, 0x23, 0x3f);

		tp9950_write(sd, 0x2b, 0x70);
		tp9950_write(sd, 0x2c, 0x2a);
		tp9950_write(sd, 0x2d, 0x4b);
		tp9950_write(sd, 0x2e, 0x56);

		tp9950_write(sd, 0x30, 0x7a);
		tp9950_write(sd, 0x31, 0x4a);
		tp9950_write(sd, 0x32, 0x4d);
		tp9950_write(sd, 0x33, 0xfb);
		
		tp9950_write(sd, 0x35, 0x65);
		tp9950_write(sd, 0x38, 0x00);
		tp9950_write(sd, 0x39, 0x04);
#endif

	}
	
	else if(FHD30 == fmt)
	{	
			tp9950_write(sd, 0x02, 0x40);
			tp9950_write(sd, 0x07, 0xc0); 
			tp9950_write(sd, 0x0b, 0xc0);		
			tp9950_write(sd, 0x0c, 0x03); 
			tp9950_write(sd, 0x0d, 0x50);  

			tp9950_write(sd, 0x15, 0x03);
			tp9950_write(sd, 0x16, 0xd2); 
			tp9950_write(sd, 0x17, 0x80); 
			tp9950_write(sd, 0x18, 0x29);
			tp9950_write(sd, 0x19, 0x38);
			tp9950_write(sd, 0x1a, 0x47);				
			tp9950_write(sd, 0x1c, 0x08);  //1920*1080, 30fps
			tp9950_write(sd, 0x1d, 0x98);  //
	
			tp9950_write(sd, 0x20, 0x30);  
			tp9950_write(sd, 0x21, 0x84); 
			tp9950_write(sd, 0x22, 0x36);
			tp9950_write(sd, 0x23, 0x3c);

			tp9950_write(sd, 0x2b, 0x60);  
			tp9950_write(sd, 0x2c, 0x2a); 
			tp9950_write(sd, 0x2d, 0x30);
			tp9950_write(sd, 0x2e, 0x70);

			tp9950_write(sd, 0x30, 0x48);  
			tp9950_write(sd, 0x31, 0xbb); 
			tp9950_write(sd, 0x32, 0x2e);
			tp9950_write(sd, 0x33, 0x90);
			
			tp9950_write(sd, 0x35, 0x05);
			tp9950_write(sd, 0x38, 0x00); 
			tp9950_write(sd, 0x39, 0x1C);	
	
			if(STD_HDA == std) //AHD1080p30 extra
			{
				tp9950_write(sd,  0x02, 0x44);
				
				tp9950_write(sd,  0x0d, 0x72);
				
				tp9950_write(sd,  0x15, 0x01);
				tp9950_write(sd,  0x16, 0xf0);
				tp9950_write(sd,  0x18, 0x2a);
							
				tp9950_write(sd,  0x20, 0x38);
				tp9950_write(sd,  0x21, 0x46);
				
				tp9950_write(sd,  0x25, 0xfe);
				tp9950_write(sd,  0x26, 0x0d);
				
				tp9950_write(sd,  0x2c, 0x3a);
				tp9950_write(sd,  0x2d, 0x54);
				tp9950_write(sd,  0x2e, 0x40);
				
				tp9950_write(sd,  0x30, 0xa5);
				tp9950_write(sd,  0x31, 0x95);
				tp9950_write(sd,  0x32, 0xe0);
				tp9950_write(sd,  0x33, 0x60);				
			}
		}
	

	else if(FHD25 == fmt) {
			tp9950_write(sd, 0x02, 0x40);
			tp9950_write(sd, 0x07, 0xc0); 
			tp9950_write(sd, 0x0b, 0xc0); 
			tp9950_write(sd, 0x0c, 0x03); 
			tp9950_write(sd, 0x0d, 0x50);  
  		
			tp9950_write(sd, 0x15, 0x03);
			tp9950_write(sd, 0x16, 0xd2); 
			tp9950_write(sd, 0x17, 0x80); 
			tp9950_write(sd, 0x18, 0x29);
			tp9950_write(sd, 0x19, 0x38);
			tp9950_write(sd, 0x1a, 0x47);
  		
			tp9950_write(sd, 0x1c, 0x0a);  //1920*1080, 25fps
			tp9950_write(sd, 0x1d, 0x50);  //
			
			tp9950_write(sd, 0x20, 0x30);  
			tp9950_write(sd, 0x21, 0x84); 
			tp9950_write(sd, 0x22, 0x36);
			tp9950_write(sd, 0x23, 0x3c);
  		
			tp9950_write(sd, 0x2b, 0x60);  
			tp9950_write(sd, 0x2c, 0x2a); 
			tp9950_write(sd, 0x2d, 0x30);
			tp9950_write(sd, 0x2e, 0x70);
  		
			tp9950_write(sd, 0x30, 0x48);  
			tp9950_write(sd, 0x31, 0xbb); 
			tp9950_write(sd, 0x32, 0x2e);
			tp9950_write(sd, 0x33, 0x90);
					
			tp9950_write(sd, 0x35, 0x05);
			tp9950_write(sd, 0x38, 0x00); 
			tp9950_write(sd, 0x39, 0x1C); 	

			if(STD_HDA == std)  //AHD1080p25 extra
			{                                     
   			tp9950_write(sd,  0x02, 0x44);
   			
   			tp9950_write(sd,  0x0d, 0x73);
   			
   			tp9950_write(sd,  0x15, 0x01);
   			tp9950_write(sd,  0x16, 0xf0);
   			tp9950_write(sd,  0x18, 0x2a);
   			   			
   			tp9950_write(sd,  0x20, 0x3c);
   			tp9950_write(sd,  0x21, 0x46);
   			
   			tp9950_write(sd,  0x25, 0xfe);
   			tp9950_write(sd,  0x26, 0x0d);
   			
   			tp9950_write(sd,  0x2c, 0x3a);
   			tp9950_write(sd,  0x2d, 0x54);
   			tp9950_write(sd,  0x2e, 0x40);
   			
   			tp9950_write(sd,  0x30, 0xa5);
   			tp9950_write(sd,  0x31, 0x86);
   			tp9950_write(sd,  0x32, 0xfb);
   			tp9950_write(sd,  0x33, 0x60);
			}
	}
	else if(HD30 == fmt)
	{
		tp9950_write(sd, 0x02, 0x42);
		tp9950_write(sd, 0x07, 0xc0); 
		tp9950_write(sd, 0x0b, 0xc0);  		
		tp9950_write(sd, 0x0c, 0x13); 
		tp9950_write(sd, 0x0d, 0x50);  

		tp9950_write(sd, 0x15, 0x13);
		tp9950_write(sd, 0x16, 0x15); 
		tp9950_write(sd, 0x17, 0x00); 
		tp9950_write(sd, 0x18, 0x19);
		tp9950_write(sd, 0x19, 0xd0);
		tp9950_write(sd, 0x1a, 0x25);			
		tp9950_write(sd, 0x1c, 0x06);  //1280*720, 30fps
		tp9950_write(sd, 0x1d, 0x72);  //1280*720, 30fps

		tp9950_write(sd, 0x20, 0x30);  
		tp9950_write(sd, 0x21, 0x84); 
		tp9950_write(sd, 0x22, 0x36);
		tp9950_write(sd, 0x23, 0x3c);

		tp9950_write(sd, 0x2b, 0x60);  
		tp9950_write(sd, 0x2c, 0x2a); 
		tp9950_write(sd, 0x2d, 0x30);
		tp9950_write(sd, 0x2e, 0x70);

		tp9950_write(sd, 0x30, 0x48);  
		tp9950_write(sd, 0x31, 0xbb); 
		tp9950_write(sd, 0x32, 0x2e);
		tp9950_write(sd, 0x33, 0x90);
		
		tp9950_write(sd, 0x35, 0x25); 
		tp9950_write(sd, 0x38, 0x00);	
		tp9950_write(sd, 0x39, 0x18); 

		if(STD_HDA == std) //AHD720p30 extra
		{
    			tp9950_write(sd,  0x02, 0x46);

    			tp9950_write(sd,  0x0d, 0x70);
    			
    			tp9950_write(sd,  0x18, 0x1b);
    			
    			tp9950_write(sd,  0x20, 0x40);
    			tp9950_write(sd,  0x21, 0x46);

    			tp9950_write(sd,  0x25, 0xfe);
    			tp9950_write(sd,  0x26, 0x01);

    			tp9950_write(sd,  0x2c, 0x3a);
    			tp9950_write(sd,  0x2d, 0x5a);
    			tp9950_write(sd,  0x2e, 0x40);

    			tp9950_write(sd,  0x30, 0x9d);
    			tp9950_write(sd,  0x31, 0xca);
    			tp9950_write(sd,  0x32, 0x01);
    			tp9950_write(sd,  0x33, 0xd0);
		}	
	}
	else if(HD25 == fmt) 
	{
		tp9950_write(sd, 0x02, 0x42);
		tp9950_write(sd, 0x07, 0xc0); 
		tp9950_write(sd, 0x0b, 0xc0);  		
		tp9950_write(sd, 0x0c, 0x13); 
		tp9950_write(sd, 0x0d, 0x50);  

		tp9950_write(sd, 0x15, 0x13);
		tp9950_write(sd, 0x16, 0x15); 
		tp9950_write(sd, 0x17, 0x00); 
		tp9950_write(sd, 0x18, 0x19);
		tp9950_write(sd, 0x19, 0xd0);
		tp9950_write(sd, 0x1a, 0x25);			
		tp9950_write(sd, 0x1c, 0x07);  //1280*720, 25fps
		tp9950_write(sd, 0x1d, 0xbc);  //1280*720, 25fps

		tp9950_write(sd, 0x20, 0x30);  
		tp9950_write(sd, 0x21, 0x84); 
		tp9950_write(sd, 0x22, 0x36);
		tp9950_write(sd, 0x23, 0x3c);

		tp9950_write(sd, 0x2b, 0x60);  
		tp9950_write(sd, 0x2c, 0x2a); 
		tp9950_write(sd, 0x2d, 0x30);
		tp9950_write(sd, 0x2e, 0x70);

		tp9950_write(sd, 0x30, 0x48);  
		tp9950_write(sd, 0x31, 0xbb); 
		tp9950_write(sd, 0x32, 0x2e);
		tp9950_write(sd, 0x33, 0x90);
		
		tp9950_write(sd, 0x35, 0x25); 
		tp9950_write(sd, 0x38, 0x00);	
		tp9950_write(sd, 0x39, 0x18); 

		if(STD_HDA == std)  //AHD720p25 extra
		{
				tp9950_write(sd,  0x02, 0x46);

				tp9950_write(sd,  0x0d, 0x71);

				tp9950_write(sd,  0x18, 0x1b);

				tp9950_write(sd,  0x20, 0x40);
				tp9950_write(sd,  0x21, 0x46);

				tp9950_write(sd,  0x25, 0xfe);
				tp9950_write(sd,  0x26, 0x01);

				tp9950_write(sd,  0x2c, 0x3a);
				tp9950_write(sd,  0x2d, 0x5a);
				tp9950_write(sd,  0x2e, 0x40);

				tp9950_write(sd,  0x30, 0x9e);
				tp9950_write(sd,  0x31, 0x20);
				tp9950_write(sd,  0x32, 0x10);
				tp9950_write(sd,  0x33, 0x90);
		}
	}

	TP9950_mipi_out(sd, fmt, std, lane);

#if 0	
	printk("start read 9951 reg \n");

	private_msleep(3000);

	print_reg(sd);
#endif	
}

static int tp9950_init(struct tx_isp_subdev *sd, int enable)
{
	struct tx_isp_sensor *sensor = sd_to_sensor_device(sd);
	int ret = 0;
	unsigned char reg = 0;
	unsigned char v =0;

	if(!enable)
		return ISP_SUCCESS;

#if 0
	tp9950_write_iic(tx_isp_get_subdevdata(sd), 0x40, 0x00);

	//i2c_smbus_write_byte_data(client,0x40, 0x00);


	tp9950_read_iic(tx_isp_get_subdevdata(sd), 0x03, &reg);

	//reg = i2c_smbus_read_byte_data(client, 0x03);
	printk("reg 0x03=%x\n",reg);


	tp9950_write_iic(tx_isp_get_subdevdata(sd),0x2f, 0x09);
	private_msleep(50);
	
	reg = tp9950_read_iic(tx_isp_get_subdevdata(sd), 0x04, &reg);
	
	printk("reg 0x04=%x\n",reg);


	private_msleep(300);

	reg = tp9950_read_iic(tx_isp_get_subdevdata(sd), 0x01, &reg);

	printk("reg 0x01=%x\n",reg);


	ret = tp9950_write(sd,0x40, 0x00);


	ret = tp9950_read(sd, 0x03, &v);
	ISP_WARNING("-----%s: %d ret = %d, v = 0x%02x\n", __func__, __LINE__, ret,v);
#endif
	printk("wsize->width =%d wsize->height=%d \n",wsize->width,wsize->height);

	sensor->video.mbus.width = wsize->width;
	sensor->video.mbus.height = wsize->height;
	sensor->video.mbus.code = wsize->mbus_code;
	sensor->video.mbus.field = V4L2_FIELD_NONE;
	sensor->video.mbus.colorspace = wsize->colorspace;
	sensor->video.fps = wsize->fps;

		TP9950_sensor_init(sd, VIN1, tp_fmt, tp_fmt1, MIPI_2LANE);
	if (ret)
		return ret;
	ret = tx_isp_call_subdev_notify(sd, TX_ISP_EVENT_SYNC_SENSOR_ATTR, &sensor->video);
	sensor->priv = wsize;

	return 0;
}

static int tp9950_s_stream(struct tx_isp_subdev *sd, int enable)
{
	int ret = 0;

	if (enable) {
		printk("tp9950 stream on\n");
	} else {
		printk("tp9950 stream off\n");
	}

	return ret;
}


static int tp9950_set_mode(struct tx_isp_subdev *sd, int value)
{
	struct tx_isp_sensor *sensor = sd_to_sensor_device(sd);
	int ret = ISP_SUCCESS;

	if(wsize){
		sensor->video.mbus.width = wsize->width;
		sensor->video.mbus.height = wsize->height;
		sensor->video.mbus.code = wsize->mbus_code;
		sensor->video.mbus.field = V4L2_FIELD_NONE;
		sensor->video.mbus.colorspace = wsize->colorspace;
		sensor->video.fps = wsize->fps;
		ret = tx_isp_call_subdev_notify(sd, TX_ISP_EVENT_SYNC_SENSOR_ATTR, &sensor->video);
	}
	return ret;
}

static int tp9950_g_chip_ident(struct tx_isp_subdev *sd,
			       struct tx_isp_chip_ident *chip)
{
	struct i2c_client *client = tx_isp_get_subdevdata(sd);
	unsigned int ident = 0;
	int ret = ISP_SUCCESS;

	if(reset_gpio != -1){
		ret = private_gpio_request(reset_gpio,"tp9950_reset");
		if(!ret){
			private_gpio_direction_output(reset_gpio, 1);
			private_msleep(20);
			private_gpio_direction_output(reset_gpio, 0);
			private_msleep(20);
			private_gpio_direction_output(reset_gpio, 1);
			private_msleep(10);
		}else{
			ISP_ERROR("gpio requrest fail %d\n",reset_gpio);
		}
	}
	if(pwdn_gpio != -1){
		ret = private_gpio_request(pwdn_gpio,"tp9950_pwdn");
		if(!ret){
			private_gpio_direction_output(pwdn_gpio, 1);
			private_msleep(10);
			private_gpio_direction_output(pwdn_gpio, 0);
			private_msleep(10);
			private_gpio_direction_output(pwdn_gpio, 1);
			private_msleep(10);
		}else{
			ISP_ERROR("gpio requrest fail %d\n",pwdn_gpio);
		}
	}
	ret = tp9950_detect(sd, &ident);
	if (ret) {
		ISP_ERROR("chip found @ 0x%x (%s) is not an tp9950 chip.\n",
			  client->addr, client->adapter->name);
		return ret;
	}
	ISP_WARNING("tp9950 chip found @ 0x%02x (%s) version %s\n", client->addr, client->adapter->name, SENSOR_VERSION);
	if(chip){
		memcpy(chip->name, "tp9950", sizeof("tp9950"));
		chip->ident = ident;
		chip->revision = SENSOR_VERSION;
	}
	return 0;
}

static int tp9950_sensor_ops_ioctl(struct tx_isp_subdev *sd, unsigned int cmd, void *arg)
{
	long ret = 0;
	if(IS_ERR_OR_NULL(sd)){
		ISP_ERROR("[%d]The pointer is invalid!\n", __LINE__);
		return -EINVAL;
	}
	switch(cmd){
	case TX_ISP_EVENT_SENSOR_RESIZE:
		if(arg)
			ret = tp9950_set_mode(sd, *(int*)arg);
		break;
	default:
		break;
	}

	return ret;
}

static int tp9950_g_register(struct tx_isp_subdev *sd, struct tx_isp_dbg_register *reg)
{
	unsigned char val = 0;
	int len = 0;
	int ret = 0;

	len = strlen(sd->chip.name);
	if(len && strncmp(sd->chip.name, reg->name, len)){
		return -EINVAL;
	}
	if (!private_capable(CAP_SYS_ADMIN))
		return -EPERM;
	ret = tp9950_read(sd, reg->reg & 0xffff, &val);
	reg->val = val;
	reg->size = 2;

	return ret;
}

static int tp9950_s_register(struct tx_isp_subdev *sd, const struct tx_isp_dbg_register *reg)
{
	int len = 0;

	len = strlen(sd->chip.name);
	if(len && strncmp(sd->chip.name, reg->name, len)){
		return -EINVAL;
	}
	if (!private_capable(CAP_SYS_ADMIN))
		return -EPERM;
	tp9950_write(sd, reg->reg & 0xffff, reg->val & 0xff);

	return 0;
}

static struct tx_isp_subdev_core_ops tp9950_core_ops = {
	.g_chip_ident = tp9950_g_chip_ident,
	.reset = tp9950_reset,
	.init = tp9950_init,
	/*.ioctl = tp9950_ops_ioctl,*/
	.g_register = tp9950_g_register,
	.s_register = tp9950_s_register,
};

static struct tx_isp_subdev_video_ops tp9950_video_ops = {
	.s_stream = tp9950_s_stream,
};

static struct tx_isp_subdev_sensor_ops	tp9950_sensor_ops = {
	.ioctl	= tp9950_sensor_ops_ioctl,
};

static struct tx_isp_subdev_ops tp9950_ops = {
	.core = &tp9950_core_ops,
	.video = &tp9950_video_ops,
	.sensor = &tp9950_sensor_ops,
};

/* It's the sensor device */
static u64 tx_isp_module_dma_mask = ~(u64)0;
struct platform_device sensor_platform_device = {
	.name = "tp9950",
	.id = -1,
	.dev = {
		.dma_mask = &tx_isp_module_dma_mask,
		.coherent_dma_mask = 0xffffffff,
		.platform_data = NULL,
	},
	.num_resources = 0,
};

static ssize_t tp9950_mode_get(struct device *dev,struct device_attribute *attr, char *buf)
{
	sprintf(buf,"%d",sensor_resolution);
	
	return strlen(buf);
}




//static DEVICE_ATTR(tp9950_mode,S_IRUGO|S_IWUSR|S_IRUSR, tp9950_mode_get,NULL);
static DEVICE_ATTR(tp9950_mode,0444, tp9950_mode_get,NULL);



static int tp9950_probe(struct i2c_client *client, const struct i2c_device_id *id)
{
	struct tx_isp_subdev *sd;
	struct tx_isp_video_in *video;
	struct tx_isp_sensor *sensor;
	int ret;
	unsigned long rate=0;
	unsigned char reg = 0;
    int trytimes = 0;
	unsigned char reg03 = 0;
    
	unsigned char reg04 = 0;
    int same_value_times = 0;


	sensor = (struct tx_isp_sensor *)kzalloc(sizeof(*sensor), GFP_KERNEL);
	if(!sensor){
		ISP_ERROR("Failed to allocate sensor subdev.\n");
		return -ENOMEM;
	}
	memset(sensor, 0 ,sizeof(*sensor));



	sensor->mclk = clk_get(NULL, "cgu_cim");
	if (IS_ERR(sensor->mclk)) {
		ISP_ERROR("Cannot get sensor input clock cgu_cim\n");
		goto err_get_mclk;
	}

	rate = clk_get_rate(clk_get_parent(sensor->mclk));

	if (((rate / 1000) % 27000) != 0) {
		struct clk *vpll;
		vpll = clk_get(NULL,"sclka");
		if (IS_ERR(vpll)) {
			pr_err("get vpll failed\n");
		} else {
			rate = clk_get_rate(vpll);
			if (((rate / 1000) % 27000) != 0) {
				clk_set_rate(vpll,10800000);
			}
			ret = clk_set_parent(sensor->mclk, vpll);
			if (ret < 0)
				pr_err("set mclk parent as epll err\n");
		}
	}

	private_clk_set_rate(sensor->mclk, 27000000);
	private_clk_enable(sensor->mclk);

	tp9950_write_iic(client, 0x40, 0x00);	

	tp9950_read_iic(client, 0x03, &reg);
	printk("reg1 0x03=%x\n",reg);

    /*
	tp9950_read_iic(client, 0x03, &reg);
	printk("reg1 0x03=%x\n",reg);
	private_msleep(300);
	reg03 = reg;
	tp9950_read_iic(client, 0x03, &reg);
	printk("reg1 0x03=%x\n",reg);*/

    while(trytimes++<20)
    {
        
        private_msleep(30);
    	tp9950_read_iic(client, 0x03, &reg);
    	printk("reg1 0x03=%x\n",reg);
        if(reg03 == reg)
        {
            same_value_times++;
        }
        else
        {
            same_value_times = 0;
        }

        if(same_value_times==3)
        {
            break;
        }
        
        reg03 = reg;
    }
    trytimes = 0;
    same_value_times =0;

	if((reg &0x07)==0x06)
	{
		tp9950_write_iic(client,0x2f, 0x09);
		private_msleep(100);

		ret = tp9950_read_iic(client, 0x04, &reg);
		printk("reg 0x04=%x\n",reg);
        reg04 = reg;


        while(trytimes++<20)
        {          
            
            ret = tp9950_read_iic(client, 0x04, &reg);
            printk("reg 0x04=%x\n",reg);

           
            if(reg==0x94 || reg==0x93)
            {
                break;
            }
            
        }


        
		if(reg == 0x94)
		{
			
			sensor_resolution = TX_SENSOR_RES_300;
				
			printk("============> Now is cvbs p jjz\n");

		}
		else
		{
		
			sensor_resolution = TX_SENSOR_RES_30;
				
			printk("============> Now is cvbs n jjz\n");			
		}
	}
	else if((reg &0x07)==0x03)
	{
		sensor_resolution = TX_SENSOR_RES_200;
		printk("============> Now is 1080p25 hda jjz\n");
		
	}
	else if((reg &0x07)==0x05)
	{
		sensor_resolution = TX_SENSOR_RES_100;
		
		printk("============> Now is 720p25 hda\n");
	}
	else if((reg &0x07)==0x02)
	{
		sensor_resolution = TX_SENSOR_RES_400;
		
		printk("============> Now is 1080p30 hda\n");
	}
	else if((reg &0x07)==0x04)
	{
		sensor_resolution = TX_SENSOR_RES_500;
		
		printk("============> Now is 720p30 hda\n");
	}	
/*
	tp9950_write_iic(client,0x2f, 0x09);
	private_msleep(300);
	
	ret = tp9950_read_iic(client, 0x04, &reg);
	printk("reg 0x04=%x\n",reg);

	private_msleep(300);
	ret = tp9950_read_iic(client, 0x01, &reg);
	printk("reg 0x01=%x\n",reg);*/



	if(sensor_resolution == TX_SENSOR_RES_200){
		wsize = &tp9950_win_sizes[0];
		tp_fmt = FHD25;
		tp_fmt1 = STD_HDA;//1;
		printk("============> Now is 1080p25 hda jjz\n");
	}
	else if(sensor_resolution == TX_SENSOR_RES_400){
		wsize = &tp9950_win_sizes[3];
		tp_fmt = FHD30;
		tp_fmt1 = STD_HDA;//1;
		printk("============> Now is 1080p30 hda jjz\n");
	}
	else if(sensor_resolution == TX_SENSOR_RES_500){
		wsize = &tp9950_win_sizes[4];
		memcpy(&(tp9950_attr.mipi), &tp9950_mipi_hda, sizeof(tp9950_mipi_hda));
		tp9950_attr.max_integration_time_native = 720;
		tp9950_attr.integration_time_limit = 720;
		tp9950_attr.total_width = 1280;
		tp9950_attr.total_height = 720;
		tp9950_attr.max_integration_time = 720;
		tp_fmt = HD30;
		tp_fmt1 = STD_HDA;
		printk("============> Now is 720p hda\n");

	}	
	else if(sensor_resolution == TX_SENSOR_RES_100){
			wsize = &tp9950_win_sizes[1];
			memcpy(&(tp9950_attr.mipi), &tp9950_mipi_hda, sizeof(tp9950_mipi_hda));
			tp9950_attr.max_integration_time_native = 720;
			tp9950_attr.integration_time_limit = 720;
			tp9950_attr.total_width = 1280;
			tp9950_attr.total_height = 720;
			tp9950_attr.max_integration_time = 720;
			tp_fmt = HD25;
			tp_fmt1 = STD_HDA;
			printk("============> Now is 720p hda\n");
	}else if(sensor_resolution == TX_SENSOR_RES_30){
			wsize = &tp9950_win_sizes[2];
			memcpy(&(tp9950_attr.mipi), &tp9950_mipi_cvbs, sizeof(tp9950_mipi_cvbs));
			tp9950_attr.max_integration_time_native = 240*CVBS_TIME+N_BLACK;
			tp9950_attr.integration_time_limit = 240*CVBS_TIME+N_BLACK;
			tp9950_attr.total_width = 720;
			tp9950_attr.total_height = 240*CVBS_TIME+N_BLACK;
			tp9950_attr.max_integration_time = 240*CVBS_TIME+N_BLACK;
			tp_fmt = NTSC;
			tp_fmt1 = 0;
			printk("============> Now is cvbs N jjz\n");
	}else if(sensor_resolution == TX_SENSOR_RES_300){
			wsize = &tp9950_win_sizes[5];
			memcpy(&(tp9950_attr.mipi), &tp9950_mipi_cvbs_p, sizeof(tp9950_mipi_cvbs_p));
			tp9950_attr.max_integration_time_native = 288*CVBS_TIME+P_BLACK;
			tp9950_attr.integration_time_limit = 288*CVBS_TIME+P_BLACK;
			tp9950_attr.total_width = 720;
			tp9950_attr.total_height = 288*CVBS_TIME+P_BLACK;
			tp9950_attr.max_integration_time = 288*CVBS_TIME+P_BLACK;
			tp_fmt = PAL;
			tp_fmt1 = 0;
			printk("============> Now is cvbs P jjz\n");
	}


	/*
	  convert sensor-gain into isp-gain,
	*/
	tp9950_attr.max_again = 1;
	tp9950_attr.max_dgain = 0;
	tp9950_attr.expo_fs = 0;
	sd = &sensor->sd;
	video = &sensor->video;
	sensor->video.attr = &tp9950_attr;
	sensor->video.vi_max_width = wsize->width;
	sensor->video.vi_max_height = wsize->height;
	sensor->video.mbus.width = wsize->width;
	sensor->video.mbus.height = wsize->height;
	sensor->video.mbus.code = wsize->mbus_code;
	sensor->video.mbus.field = V4L2_FIELD_NONE;
	sensor->video.mbus.colorspace = wsize->colorspace;
	sensor->video.fps = wsize->fps;
	tx_isp_subdev_init(&sensor_platform_device, sd, &tp9950_ops);
	tx_isp_set_subdevdata(sd, client);
	tx_isp_set_subdev_hostdata(sd, sensor);
	private_i2c_set_clientdata(client, sd);
	pr_debug("probe ok fps=%d,w=%d,h=%d\n",sensor->video.fps,wsize->width,wsize->height);


	ret = device_create_file(&client->dev, &dev_attr_tp9950_mode);

	
/*
	tp9950_write_iic(client, 0x40, 0x00);

	//i2c_smbus_write_byte_data(client,0x40, 0x00);


	tp9950_read_iic(client, 0x03, &reg);

	//reg = i2c_smbus_read_byte_data(client, 0x03);
	printk("reg2 0x03=%x\n",reg);


	tp9950_write_iic(client,0x2f, 0x09);
	private_msleep(300);
	
	reg = tp9950_read_iic(client, 0x04, &reg);
	
	printk("reg 0x04=%x\n",reg);


	private_msleep(300);

	reg = tp9950_read_iic(client, 0x01, &reg);

	printk("reg 0x01=%x\n",reg);
*/
	

	pr_debug("probe ok ------->tp9950 jjz\n");
	return 0;
err_get_mclk:
	kfree(sensor);

	return -1;
}

static int tp9950_remove(struct i2c_client *client)
{
	struct tx_isp_subdev *sd = private_i2c_get_clientdata(client);
	struct tx_isp_sensor *sensor = tx_isp_get_subdev_hostdata(sd);

	if(reset_gpio != -1)
		private_gpio_free(reset_gpio);
	if(pwdn_gpio != -1)
		private_gpio_free(pwdn_gpio);

	private_clk_disable(sensor->mclk);
	private_clk_put(sensor->mclk);
	tx_isp_subdev_deinit(sd);
	kfree(sensor);
	return 0;
}

static const struct i2c_device_id tp9950_id[] = {
	{ "tp9950", 0 },
	{ }
};
MODULE_DEVICE_TABLE(i2c, tp9950_id);

static struct i2c_driver tp9950_driver = {
	.driver = {
		.owner = NULL,
		.name	= "tp9950",
	},
	.probe		= tp9950_probe,
	.remove		= tp9950_remove,
	.id_table	= tp9950_id,
};

/* ===== Zeratul built-in sensor wrapper (提供 ISP 期望的导出符号) ===== */
char * get_sensor_name(void)
{
	return "tp9950";
}

int get_sensor_i2c_addr(void)
{
	return 0x44;   /* TP9950/TP9951 Techpoint 默认 7bit 地址, 上板用 i2cdetect 复核 */
}

int get_sensor_width(void)
{
	return tp9950_win_sizes->width;
}

int get_sensor_height(void)
{
	return tp9950_win_sizes->height;
}

int init_sensor(void)
{
	return private_i2c_add_driver(&tp9950_driver);
}

void exit_sensor(void)
{
	private_i2c_del_driver(&tp9950_driver);
}
