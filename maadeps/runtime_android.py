import os
from pathlib import Path
import subprocess
import shutil
from .common import resdir
from . import runtime_linux as linux

exclude = [
    "*onnxruntime_providers_shared*",
]

def set_rpath(file, rpath):
    linux.set_rpath(file, rpath)

def split_debug(file, debug_file):
    temp_debug_file = Path(file).parent / Path(debug_file).name
    android_ndk = os.environ.get("ANDROID_NDK_HOME", "/opt/android-ndk")
    ndk_which = os.path.join(android_ndk, "ndk-which")
    objcopy = subprocess.check_output([ndk_which, "objcopy"]).decode().strip()
    objcopy = os.environ.get("OBJCOPY", objcopy)
    subprocess.check_call([objcopy, "--only-keep-debug", "--", file, temp_debug_file])
    subprocess.check_call([objcopy, "--strip-unneeded", "--add-gnu-debuglink=" + str(temp_debug_file), "--", file])
    shutil.move(temp_debug_file, debug_file)

def is_elf(file):
    return linux.is_elf(file)

def get_soname(file):
    return linux.get_soname(file)

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
