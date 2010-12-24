#include <linux/module.h>
#include <linux/vermagic.h>
#include <linux/compiler.h>

MODULE_INFO(vermagic, VERMAGIC_STRING);

struct module __this_module
__attribute__((section(".gnu.linkonce.this_module"))) = {
 .name = KBUILD_MODNAME,
 .init = init_module,
#ifdef CONFIG_MODULE_UNLOAD
 .exit = cleanup_module,
#endif
 .arch = MODULE_ARCH_INIT,
};

static const struct modversion_info ____versions[]
__used
__attribute__((section("__versions"))) = {
	{ 0x9d5b1f89, "module_layout" },
	{ 0x66c7693b, "blk_queue_merge_bvec" },
	{ 0xfd0e693, "blk_init_queue" },
	{ 0x12da5bb2, "__kmalloc" },
	{ 0x44962268, "alloc_disk" },
	{ 0x77ecac9f, "zlib_inflateEnd" },
	{ 0xe404e5ec, "blk_cleanup_queue" },
	{ 0xd6ee688f, "vmalloc" },
	{ 0xd0d8621b, "strlen" },
	{ 0xba4ed498, "blk_queue_max_hw_sectors" },
	{ 0xc8b57c27, "autoremove_wake_function" },
	{ 0xf97ee6d, "filp_close" },
	{ 0x999e8297, "vfree" },
	{ 0x3c2c5af5, "sprintf" },
	{ 0x8b2b568d, "invalidate_bdev" },
	{ 0xe174aa7, "__init_waitqueue_head" },
	{ 0x41344088, "param_get_charp" },
	{ 0x58366afb, "blk_queue_max_segments" },
	{ 0xe9755515, "vfs_read" },
	{ 0xeb4edb50, "set_device_ro" },
	{ 0x88941a06, "_raw_spin_unlock_irqrestore" },
	{ 0xa81eb26b, "current_task" },
	{ 0xb72397d5, "printk" },
	{ 0x4bd50a42, "kthread_stop" },
	{ 0xa1bc4adb, "del_gendisk" },
	{ 0x48fcb85b, "kunmap" },
	{ 0xc9c1c680, "blk_queue_segment_boundary" },
	{ 0x2da418b5, "copy_to_user" },
	{ 0xce5ac24f, "zlib_inflate_workspacesize" },
	{ 0x6f5427, "_raw_spin_unlock_irq" },
	{ 0x71a50dbc, "register_blkdev" },
	{ 0x7c458596, "fput" },
	{ 0x881039d0, "zlib_inflate" },
	{ 0xb5a459dc, "unregister_blkdev" },
	{ 0x1babe6ef, "kmap" },
	{ 0x108e8985, "param_get_uint" },
	{ 0x4292364c, "schedule" },
	{ 0xed299523, "put_disk" },
	{ 0xf333a2fb, "_raw_spin_lock_irq" },
	{ 0xa429c391, "blk_fetch_request" },
	{ 0xaca7218b, "wake_up_process" },
	{ 0x7c7d77df, "__blk_end_request_all" },
	{ 0x587c70d8, "_raw_spin_lock_irqsave" },
	{ 0x4211c3c1, "zlib_inflateInit2" },
	{ 0x6ad065f4, "param_set_charp" },
	{ 0xf09c7f68, "__wake_up" },
	{ 0xd2965f6f, "kthread_should_stop" },
	{ 0x37a0cba, "kfree" },
	{ 0x2c5caf8f, "kthread_create" },
	{ 0x3ed63055, "zlib_inflateReset" },
	{ 0xe75663a, "prepare_to_wait" },
	{ 0x3285cc48, "param_set_uint" },
	{ 0x9a183ed4, "add_disk" },
	{ 0xe8b507a8, "set_user_nice" },
	{ 0xd56b3f56, "fget" },
	{ 0xb00ccc33, "finish_wait" },
	{ 0xa8396164, "blk_queue_max_segment_size" },
	{ 0xa37fa399, "vfs_getattr" },
	{ 0x33d169c9, "_copy_from_user" },
	{ 0xa0d8b7cb, "filp_open" },
};

static const char __module_depends[]
__used
__attribute__((section(".modinfo"))) =
"depends=";

