import io
p="/home/wennu/zkjh/Software/os/kernel/arch/mips/kernel/setup.c"
s=io.open(p,encoding="utf-8").read()
if "M2a" not in s:
    s=s.replace("\tarch_mem_addpart(PFN_DOWN(__pa_symbol(&_text)) << PAGE_SHIFT,",
"\tprom_putstr((char*)\"M2a:pre-addpart\\n\");\n\tarch_mem_addpart(PFN_DOWN(__pa_symbol(&_text)) << PAGE_SHIFT,",1)
    s=s.replace("\tpr_info(\"Determined physical RAM map:\\n\");\n\tprint_memory_map();",
"\tprom_putstr((char*)\"M2b:pre-memmap\\n\");\n\tpr_info(\"Determined physical RAM map:\\n\");\n\tprint_memory_map();\n\tprom_putstr((char*)\"M2c:post-memmap\\n\");",1)
    io.open(p,"w",encoding="utf-8").write(s); print("M2a/b/c patched")
else: print("already")
