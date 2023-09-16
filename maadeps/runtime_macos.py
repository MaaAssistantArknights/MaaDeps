from pathlib import Path
import subprocess

exclude = [
    "*onnxruntime_providers_shared*",
]


def set_rpath(file, rpath):
    subprocess.check_call(["install_name_tool", "-add_rpath", rpath, file])


def split_debug(file, debug_file):
    subprocess.check_call(["dsymutil", file, "-o", debug_file])
    subprocess.check_call(["strip", "-x", "-S", file])


def is_macho(file):
    result = subprocess.run(["file", file], capture_output=True)
    text = result.stdout.decode()
    if text.startswith(f"{file}: Mach-O"):
        return True
    return False


def get_soname(file):
    result = subprocess.run(["otool", "-l", file], capture_output=True)
    cmds = result.stdout.decode().splitlines()
    for i, cmd in enumerate(cmds):
        if cmd.endswith("LC_ID_DYLIB"):
            name_line = cmds[i + 2]
            name_path = Path(name_line.split()[1])
            return name_path.name
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
