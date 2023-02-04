import os
from pathlib import Path
import shutil

from maadeps.runner import task
from . import vcpkg
from .common import basedir

@task
def sdk_ready():
    return True

@task
def get_runtime_dir():
    return os.path.join(basedir, "runtime", vcpkg.triplet)

@task
def get_debug_dir():
    return os.path.join(basedir, "debug", vcpkg.triplet)

@task
def install_runtime():
    if not sdk_ready.completed:
        sdk_ready()
        raise Exception("sdk not prepared")

    target_dir = get_runtime_dir()
    debug_dir = get_debug_dir()

    os.makedirs(target_dir, exist_ok=True)
    os.makedirs(debug_dir, exist_ok=True)

    if "windows" in vcpkg.triplet:
        from .runtime_windows import install_runtime as impl
    elif "linux" in vcpkg.triplet:
        from .runtime_linux import install_runtime as impl
    elif "osx" in vcpkg.triplet:
        from .runtime_macos import install_runtime as impl
    elif 'android' in vcpkg.triplet:
        from .runtime_android import install_runtime as impl
    else:
        raise NotImplementedError()

    impl(target_dir, debug_dir)

def install_file(src, dst):
    if Path(dst).is_dir():
        dst = Path(dst) / Path(src).name
    print("installing", src, "->", dst)
    Path(dst).parent.mkdir(parents=True, exist_ok=True)
    shutil.copy(src, dst)

def match_patterns(path: Path, patterns):
    for pat in patterns:
        if path.match(pat):
            return True
    return False
