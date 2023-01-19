import os
from pathlib import Path
import subprocess
import shutil
from .common import resdir

exclude = [
    "*onnxruntime_providers_shared*",
]

def set_rpath(file, rpath):
    subprocess.check_call(["patchelf", "--set-rpath", rpath, file])

def split_debug(file, debug_file):
    temp_debug_file = Path(file).parent / Path(debug_file).name
    objcopy = os.environ.get("OBJCOPY", "objcopy")
    subprocess.check_call([objcopy, "--only-keep-debug", "--", file, temp_debug_file])
    subprocess.check_call([objcopy, "--strip-unneeded", "--add-gnu-debuglink=" + str(temp_debug_file), "--", file])
    shutil.move(temp_debug_file, debug_file)

def is_elf(file):
    with open(file, "rb") as f:
        return f.read(4) == b"\x7fELF"

def get_soname(file):
    from elftools.elf.elffile import ELFFile
    from elftools.elf.dynamic import DynamicSection
    with open(file, "rb") as f:
        elffile = ELFFile(f)
        for section in elffile.iter_sections():
            if not isinstance(section, DynamicSection):
                continue
            for tag in section.iter_tags():
                if tag.entry.d_tag == 'DT_SONAME':
                    return tag.soname
    return None

def install_runtime(target, debug):
    from . import vcpkg
    prefix = Path(vcpkg.install_prefix)
    target = Path(target)
    from .runtime import install_file, match_patterns
    for file in prefix.glob("lib/**/*"):
        if (match_patterns(file, exclude)):
            continue
        if file.is_symlink() or not file.is_file():
            continue
        if is_elf(file):
            soname = get_soname(file)
            if soname is not None:
                target_path = target / soname
            else:
                target_path = target / file.name
            install_file(file, target_path)
            set_rpath(target_path, '$ORIGIN')
            split_debug(target_path, Path(debug, target_path.name + '.debug'))
