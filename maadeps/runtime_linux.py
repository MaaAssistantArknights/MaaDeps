import os
from pathlib import Path
import subprocess

from .common import resdir

exclude = [
    "*onnxruntime_providers_shared*",
]

def set_rpath(file, rpath):
    subprocess.check_call(["patchelf", "--set-rpath", rpath, file])

def is_elf(file):
    with open(file, "rb") as f:
        return f.read(4) == b"\x7fELF"

def get_soname(file):
    from elftools.elf.elffile import ELFFile
    from elftools.elf.dynamic import DynamicSection, DynamicSegment
    with open(file, "rb") as f:
        elffile = ELFFile(f)
        for section in elffile.iter_sections():
            if not isinstance(section, DynamicSection):
                continue
            padding = 20 + (8 if elffile.elfclass == 32 else 0)
            for tag in section.iter_tags():
                if tag.entry.d_tag == 'DT_SONAME':
                    return tag.soname
    return None

def rename_to_soname(file):
    soname = get_soname(file)
    if soname is not None:
        p = Path(file)
        if p.name != soname:
            print("rename", p, "to", soname)
            p.rename(p.with_name(soname))

def install_runtime(target):
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
            target_path = target / file.name
            install_file(file, target_path)
            set_rpath(target_path, '$ORIGIN')
            rename_to_soname(target_path)
