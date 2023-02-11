from pathlib import Path
import subprocess

exclude = [
    "*onnxruntime_providers_shared*",
]


def set_rpath(file, rpath):
    subprocess.check_call(["install_name_tool", "-add_rpath", rpath, file])


def split_debug(file, debug_file):
    subprocess.check_call(["dsymutil", file, "-o", debug_file])


def is_macho(file):
    from macholib.MachO import MachO
    try:
        MachO(file)
        return True
    except Exception:
        return False


def get_soname(file):
    from macholib.dylib import dylib_info
    try:
        return dylib_info(file).get('name', None)
    except Exception:
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
        if is_macho(file):
            soname = get_soname(file)
            if soname is not None:
                target_path = target / soname
            else:
                target_path = target / file.name
            install_file(file, target_path)
            split_debug(target_path, Path(debug, target_path.name + '.dSYM'))
