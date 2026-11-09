#include <linux/module.h>
#include <linux/kernel.h>
#include <linux/init.h>
#include <linux/proc_fs.h>
#include <linux/uaccess.h>
#include <linux/kallsyms.h>
#include <asm/cacheflush.h>
#include <linux/errno.h>

/*
 * JKD-621-T23 ISP bring-up aid.
 *
 * The known-good 9389b24 kernel reaches Root Shell, but tp9950_g_chip_ident()
 * returns -5 when the board-specific TP995x version registers NACK.  This
 * module patches only the two inlined failure branches at runtime, preserving
 * the validated linked image.  A user-space write to /proc/isp_reprobe then
 * re-invokes tx_isp_init() so the failure point can be isolated interactively.
 */

typedef unsigned long (*kallsyms_lookup_name_t)(const char *name);
typedef int (*tx_isp_init_t)(void);

static kallsyms_lookup_name_t lookup_symbol;
static tx_isp_init_t tx_isp_init_ptr;
static unsigned long g_chip_ident_addr;
static int patch_applied;
static int last_reprobe_result = -ENOENT;

struct patch_def {
	unsigned long offset;
	unsigned int expected;
	const char *name;
};

static struct patch_def patches[] = {
	{ 0x16c, 0x04600022, "0xfe read failure branch" },
	{ 0x1c8, 0x0600000f, "0xff read failure branch" },
};

static int write_nop(unsigned long address, unsigned int expected)
{
	unsigned int old;
	unsigned int nop = 0;
	int ret;

	old = *(volatile unsigned int *)address;
	if (old == nop) {
		printk(KERN_INFO "isp_reprobe: %px already NOP\n", (void *)address);
		return 0;
	}
	if (old != expected) {
		printk(KERN_ERR "isp_reprobe: %px unexpected instruction %08x (expected %08x)\n",
		       (void *)address, old, expected);
		return -EINVAL;
	}

	ret = probe_kernel_write((void *)address, &nop, sizeof(nop));
	if (ret) {
		printk(KERN_ERR "isp_reprobe: write %px failed: %d\n", (void *)address, ret);
		return ret;
	}
	flush_icache_all();
	printk(KERN_INFO "isp_reprobe: %px %08x -> NOP (%s)\n",
	       (void *)address, expected, "version-read failure");
	return 0;
}

static int apply_patches(void)
{
	unsigned int i;
	int ret;

	if (!g_chip_ident_addr)
		return -ENOENT;

	for (i = 0; i < ARRAY_SIZE(patches); i++) {
		ret = write_nop(g_chip_ident_addr + patches[i].offset,
				patches[i].expected);
		if (ret)
			return ret;
	}
	patch_applied = 1;
	return 0;
}

static int reprobe_isp(void)
{
	int ret;

	if (!patch_applied || !tx_isp_init_ptr)
		return -ENOENT;

	printk(KERN_INFO "isp_reprobe: calling tx_isp_init at %px\n",
	       (void *)tx_isp_init_ptr);
	ret = tx_isp_init_ptr();
	last_reprobe_result = ret;
	printk(KERN_INFO "isp_reprobe: tx_isp_init returned %d\n", ret);
	return ret;
}

static ssize_t isp_reprobe_read(struct file *file, char __user *buf,
				size_t count, loff_t *ppos)
{
	char text[96];
	int len;

	if (*ppos)
		return 0;
	len = scnprintf(text, sizeof(text),
			"patch=%d tx_isp_init=%px last=%d\n",
			patch_applied, (void *)tx_isp_init_ptr,
			last_reprobe_result);
	if (copy_to_user(buf, text, len))
		return -EFAULT;
	*ppos = len;
	return len;
}

static ssize_t isp_reprobe_write(struct file *file, const char __user *buf,
				 size_t count, loff_t *ppos)
{
	char command;
	int ret;

	if (!count)
		return -EINVAL;
	if (copy_from_user(&command, buf, 1))
		return -EFAULT;
	if (command != '1')
		return -EINVAL;

	ret = reprobe_isp();
	return ret ? ret : count;
}

static const struct file_operations isp_reprobe_fops = {
	.owner = THIS_MODULE,
	.read = isp_reprobe_read,
	.write = isp_reprobe_write,
};

static int __init isp_reprobe_init(void)
{
	lookup_symbol = (kallsyms_lookup_name_t)kallsyms_lookup_name;
	if (!lookup_symbol)
		return -ENOENT;

	g_chip_ident_addr = lookup_symbol("tp9950_g_chip_ident");
	tx_isp_init_ptr = (tx_isp_init_t)lookup_symbol("tx_isp_init");
	if (!g_chip_ident_addr || !tx_isp_init_ptr) {
		printk(KERN_ERR "isp_reprobe: symbols not found: chip=%px init=%px\n",
		       (void *)g_chip_ident_addr, (void *)tx_isp_init_ptr);
		return -ENOENT;
	}

	printk(KERN_INFO "isp_reprobe: tp9950_g_chip_ident=%px tx_isp_init=%px\n",
	       (void *)g_chip_ident_addr, (void *)tx_isp_init_ptr);

	if (!proc_create("isp_reprobe", 0600, NULL, &isp_reprobe_fops))
		return -ENOMEM;

	return apply_patches();
}

static void __exit isp_reprobe_exit(void)
{
	remove_proc_entry("isp_reprobe", NULL);
}

module_init(isp_reprobe_init);
module_exit(isp_reprobe_exit);
MODULE_LICENSE("GPL");
MODULE_DESCRIPTION("JKD-621-T23 ISP interactive reprobe aid");
