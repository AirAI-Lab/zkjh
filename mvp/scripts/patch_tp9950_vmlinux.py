#!/usr/bin/env python3
"""Patch the known-good TP9950 kernel layout without relinking it.

Background:
- Commit 9389b24's kernel reaches Root Shell and probes I2C0 correctly.
- Its inlined tp9950_g_chip_ident() still returns early when version reads NACK.
- Rebuilding with a source-only removal changed text layout/entry from
  0x803c6660 to 0x803c6620 and exposed an unrelated early reset on this board.
- Therefore keep the known-good linked layout and replace only the two
  read-failure branches with NOPs in the final vmlinux.

Run from WSL after building/checking out the 9389b24-equivalent object:
    python3 /mnt/d/github/zkjh/mvp/scripts/patch_tp9950_vmlinux.py
"""
from pathlib import Path
import sys

VMLINUX = Path("/home/wennu/zkjh/Software/os/kernel/vmlinux")
TEXT_VADDR = 0x80010000
TEXT_FILE_OFFSET = 0x1000  # readelf -SW .text offset

# tp9950_g_chip_ident = 0x801aad00 in the known-good layout.
PATCHES = {
    # fe-read failure: bltz v1, failure_path
    0x801AAE6C: 0x04600022,
    # ff-read failure: bltz s0, failure_path
    0x801AAEC8: 0x0600000F,
}


def file_offset(vaddr: int) -> int:
    return TEXT_FILE_OFFSET + (vaddr - TEXT_VADDR)


def main() -> int:
    data = bytearray(VMLINUX.read_bytes())
    changed = 0
    for vaddr, expected in PATCHES.items():
        off = file_offset(vaddr)
        old = int.from_bytes(data[off:off + 4], "little")
        if old == 0:
            print(f"{vaddr:#010x}: already NOP")
            continue
        if old != expected:
            raise RuntimeError(
                f"unexpected instruction at {vaddr:#x}: {old:#010x}, "
                f"expected {expected:#010x}; refusing to patch an unknown layout"
            )
        data[off:off + 4] = (0).to_bytes(4, "little")
        print(f"{vaddr:#010x}: {old:#010x} -> NOP")
        changed += 1

    VMLINUX.write_bytes(data)
    print(f"patched {changed} branch(s); vmlinux layout and entry point preserved")
    return 0


if __name__ == "__main__":
    sys.exit(main())
