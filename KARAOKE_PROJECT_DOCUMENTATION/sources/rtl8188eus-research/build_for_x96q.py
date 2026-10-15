"""Build only: never install/load modules or change networking."""
import argparse
import gzip
import hashlib
import os
from pathlib import Path
import platform
import shutil
import subprocess
import tarfile
import tempfile
import urllib.request

RELEASE = "6.6.44-current-sunxi64"
CONFIG_HASH = "ebc09f1d3dba1ebc61323b0c91cbb95e1ec34f3000a0fbf88bffb724f2083123"
INPUTS = [
    ("linux.tar.gz", "https://codeload.github.com/gregkh/linux/tar.gz/refs/tags/v6.6.44",
     "83f258ff86d40ee6c4d67ff78002309bbb824a5d7e0ad1fa793a1e00a7707cd3", "linux-6.6.44"),
    ("armbian.tar.gz", "https://codeload.github.com/sicXnull/armbian-build/tar.gz/de1a1959827c3a274d5b7d52c474e4dd373ae3ef",
     "3a7ca94c7fcb365fc22e80bfef29245c2d1e0037d37a1bcab918d0f54449a6b0", "armbian-build-de1a1959827c3a274d5b7d52c474e4dd373ae3ef"),
    ("driver.tar.gz", "https://codeload.github.com/aircrack-ng/rtl8188eus/tar.gz/af3bf004458f76b7aec33e9ba552cd382ed1f5c3",
     "7789a8d6e5f212e31a92bee1c9da41ceab1173e910503591d02762a0e95e7349", "rtl8188eus-af3bf004458f76b7aec33e9ba552cd382ed1f5c3"),
]


def sha(path):
    with Path(path).open("rb") as f:
        return hashlib.file_digest(f, "sha256").hexdigest()


def config_values(path):
    values = {}
    for line in Path(path).read_text().splitlines():
        if line.startswith("CONFIG_"):
            key, value = line.split("=", 1)
            values[key] = value
        elif line.startswith("# CONFIG_") and line.endswith(" is not set"):
            values[line.split()[1]] = "n"
    return values


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default=f"/boot/config-{RELEASE}")
    parser.add_argument("--work-parent", default="/root")
    parser.add_argument("--cache")
    parser.add_argument("--cross-prefix")
    parser.add_argument("--cc")
    args = parser.parse_args()
    args.work_parent = str(Path(args.work_parent).resolve())
    args.config = str(Path(args.config).resolve())
    if not args.cross_prefix and (platform.machine() != "aarch64" or platform.release() != RELEASE):
        raise RuntimeError("This script targets X96Q ARM64 kernel " + RELEASE)
    if sha(args.config) != CONFIG_HASH:
        raise RuntimeError("Kernel configuration differs; no build attempted")
    if shutil.disk_usage(args.work_parent).free < 2_800_000_000:
        raise RuntimeError("Need at least 2.8 GB free in the build directory")
    for tool in ("make", "gcc", "flex", "bison", "bc", "patch", "tar"):
        if not shutil.which(tool):
            raise RuntimeError("Missing build tool: " + tool)
    lab = Path(tempfile.mkdtemp(prefix="rtl8188eus-build-", dir=args.work_parent))
    lab.chmod(0o700)
    print("Build directory:", lab, flush=True)
    log = (lab / "build.log").open("w")

    def run(command, cwd=lab):
        log.write("\nCOMMAND: " + repr(command) + "\n")
        log.flush()
        subprocess.run(command, cwd=cwd, stdout=log, stderr=subprocess.STDOUT, check=True)

    for filename, url, digest, prefix in INPUTS:
        archive = lab / filename
        cached = Path(args.cache) / filename if args.cache else None
        print("Preparing", filename, flush=True)
        if cached and cached.is_file():
            shutil.copyfile(cached, archive)
        else:
            with urllib.request.urlopen(url, timeout=120) as response, archive.open("xb") as target:
                shutil.copyfileobj(response, target)
        if sha(archive) != digest:
            raise RuntimeError("Archive checksum mismatch: " + filename)
        # Check paths before invoking tar; the pinned archives are HTTPS downloads.
        with tarfile.open(archive) as tf:
            for member in tf:
                path = Path(member.name)
                if path.is_absolute() or ".." in path.parts or path.parts[0] != prefix:
                    raise RuntimeError("Unexpected archive path")
        run(["tar", "-xzf", str(archive)])

    kernel, armbian, driver = [lab / item[3] for item in INPUTS]
    patches = armbian / "patch/kernel/archive/sunxi-6.6"
    print("Applying the 424 Armbian patches", flush=True)
    count = 0
    for line in (patches / "series.conf").read_text().splitlines():
        name = line.strip()
        if not name or name.startswith(("#", "-")):
            continue
        run(["patch", "--batch", "--forward", "-p1", "-i", str(patches / name)], kernel)
        count += 1
    if count != 424:
        raise RuntimeError("Unexpected patch count")
    shutil.copyfile(args.config, kernel / ".config")
    flags = ["ARCH=arm64", "LOCALVERSION=-current-sunxi64", "KBUILD_MODPOST_WARN="]
    if args.cross_prefix:
        flags.append("CROSS_COMPILE=" + args.cross_prefix)
    if args.cc:
        flags.append("CC=" + args.cc)
    print("Preparing kernel build headers", flush=True)
    run(["make", "-j2", *flags, "olddefconfig", "modules_prepare"], kernel)
    original = config_values(args.config)
    prepared = config_values(kernel / ".config")
    compiler_values = {
        "CONFIG_CC_VERSION_TEXT", "CONFIG_GCC_VERSION", "CONFIG_CLANG_VERSION",
        "CONFIG_AS_VERSION", "CONFIG_LD_VERSION", "CONFIG_PAHOLE_VERSION",
        "CONFIG_GCC_ASM_GOTO_OUTPUT_WORKAROUND",
    }
    if args.cross_prefix:
        compiler_values.update({"CONFIG_CC_CAN_LINK", "CONFIG_BPFILTER_UMH"})
    changed = {key: (original[key], prepared[key])
               for key in original.keys() & prepared.keys()
               if original[key] != prepared[key] and key not in compiler_values}
    mandatory = """64BIT ARM64 SMP CPU_BIG_ENDIAN CPU_LITTLE_ENDIAN
        ARM64_PAGE_SHIFT ARM64_VA_BITS ARM64_PA_BITS HZ
        MODULES MODULE_UNLOAD MODVERSIONS MODULE_SIG MODULE_SIG_FORCE
        STACKPROTECTOR STACKPROTECTOR_STRONG STACKPROTECTOR_PER_TASK
        ARM64_PTR_AUTH_KERNEL ARM64_BTI_KERNEL SHADOW_CALL_STACK
        RANDSTRUCT RANDSTRUCT_NONE LTO LTO_NONE CFI_CLANG
        PREEMPT PREEMPT_RT PREEMPT_DYNAMIC PREEMPT_NONE""".split()
    for option in mandatory:
        key = "CONFIG_" + option
        before, after = original.get(key, "n"), prepared.get(key, "n")
        if before != after:
            changed[key] = (before, after)
    if changed:
        raise RuntimeError("Kernel settings changed; stopped for review: " + repr(changed))
    release = subprocess.check_output(["make", "-s", *flags, "kernelrelease"], cwd=kernel, text=True).strip()
    if release != RELEASE:
        raise RuntimeError("Unexpected kernel release: " + release)
    # Populated with verified export records from the reconstructed kernel.
    symbol_file = Path(__file__).with_name("driver-symbols.symvers.gz")
    symbol_hash = Path(__file__).with_name("driver-symbols.sha256").read_text().strip()
    if sha(symbol_file) != symbol_hash:
        raise RuntimeError("Symbol table checksum mismatch")
    (kernel / "Module.symvers").write_bytes(gzip.decompress(symbol_file.read_bytes()))
    print("Building 8188eu; no installation or loading", flush=True)
    run(["make", "-j2", *flags, "M=" + str(driver), "CONFIG_RTL8188EU=m",
         "CONFIG_TXPWR_BY_RATE_EN=y", "CONFIG_TXPWR_LIMIT_EN=y", "modules"], kernel)
    module = lab / "8188eu-test.ko"
    shutil.copyfile(driver / "8188eu.ko", module)
    module.chmod(0o600)
    print("BUILD COMPLETE:", module, flush=True)
    print("SHA256:", sha(module), flush=True)
    print("Not installed; networking unchanged. Log:", log.name, flush=True)


if __name__ == "__main__":
    main()
