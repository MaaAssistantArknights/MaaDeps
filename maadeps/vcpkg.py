import sys
import os
from .common import basedir, host_triplet
import subprocess
from maadeps.runner import task

_this_module = sys.modules[__name__]


root = os.path.join(basedir, "vcpkg")
install_prefix: str
triplet: str
cross_compiling = False

@task
def bootstrap(target_triplet=None):
    if target_triplet is None:
        target_triplet = "maa-" + host_triplet
    print("host triplet for vcpkg:", host_triplet)
    print("target triplet for vcpkg:", target_triplet)

    global triplet, cross_compiling, install_prefix
    triplet = target_triplet
    cross_compiling = host_triplet != target_triplet.removeprefix("maa-")
    install_prefix = os.path.join(root, "installed", target_triplet)

    os.environ["VCPKG_OVERLAY_TRIPLETS"] = os.path.join(basedir, "vcpkg-overlay", "triplets")
    os.environ["VCPKG_OVERLAY_PORTS"] = os.path.join(basedir, "vcpkg-overlay", "ports")

    archives_dir = os.path.join(root, "archives")
    if os.path.exists(archives_dir) and "VCPKG_DEFAULT_BINARY_CACHE" not in os.environ:
        os.environ["VCPKG_DEFAULT_BINARY_CACHE"] = archives_dir

    ccache_vars = "CMAKE_C_COMPILER_LAUNCHER;CMAKE_CXX_COMPILER_LAUNCHER;CCACHE_DIR;CCACHE_BASEDIR;CCACHE_COMPILERCHECK;ANDROID_CCACHE;NDK_CCACHE"
    if "VCPKG_KEEP_ENV_VARS" in os.environ:
        if "CMAKE_C_COMPILER_LAUNCHER" not in os.environ["VCPKG_KEEP_ENV_VARS"]:
            os.environ["VCPKG_KEEP_ENV_VARS"] += f";{ccache_vars}"
    else:
        os.environ["VCPKG_KEEP_ENV_VARS"] = ccache_vars

    import shutil
    from pathlib import Path
    ccache_bin = shutil.which("ccache")
    if not ccache_bin and os.environ.get("ccache_symlinks_path"):
        cand = Path(os.environ["ccache_symlinks_path"]) / ("ccache.exe" if sys.platform == "win32" else "ccache")
        if cand.is_file():
            ccache_bin = str(cand)
    if ccache_bin and Path(ccache_bin).is_file():
        os.environ.setdefault("CMAKE_C_COMPILER_LAUNCHER", ccache_bin)
        os.environ.setdefault("CMAKE_CXX_COMPILER_LAUNCHER", ccache_bin)
        os.environ.setdefault("ANDROID_CCACHE", ccache_bin)
        os.environ.setdefault("NDK_CCACHE", ccache_bin)

    if os.name == "nt":
        script_name = "bootstrap-vcpkg.bat"
        executable_name = "vcpkg.exe"
    else:
        script_name = "bootstrap-vcpkg.sh"
        executable_name = "vcpkg"

    if not os.path.exists(os.path.join(root, script_name)):
            subprocess.check_call(["git", "submodule", "update", "--init", "--recommend-shallow", "vcpkg"], cwd=basedir)

    if not os.path.exists(os.path.join(root, executable_name)):
        subprocess.check_call([os.path.join(root, script_name), "-disableMetrics"], cwd=root)

def _get_host_triplet(target_triplet):
    if sys.platform.startswith("linux"):
        return host_triplet
    if cross_compiling or (host_triplet != target_triplet.removeprefix("maa-")):
        return host_triplet
    return target_triplet

def install(*ports, triplet=None):
    if triplet is None:
        triplet = _this_module.triplet
    cmd = [
        os.path.join(root, "vcpkg"),
        "install",
        "--host-triplet",
        _get_host_triplet(triplet),
    ]
    cmd.extend(port + ":" + triplet for port in ports)
    subprocess.check_call(cmd, cwd=root)

def install_manifest(manifest_root, triplet=None):
    if triplet is None:
        triplet = _this_module.triplet
    cmd = [
        os.path.join(root, "vcpkg"),
        "install",
        "--x-install-root=" + os.path.join(root, "installed"),
        "--triplet",
        triplet,
        "--host-triplet",
        _get_host_triplet(triplet),
    ]
    if sys.platform == "win32":
        cmd.append("--clean-buildtrees-after-build")
    subprocess.check_call(cmd, cwd=manifest_root)
