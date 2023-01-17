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

    if not os.path.exists(os.path.join(root, "bootstrap_vcpkg.bat")):
        subprocess.check_call(["git", "submodule", "update", "--init", "vcpkg"], cwd=basedir)

    if os.name == "nt":
        script_name = "bootstrap-vcpkg.bat"
        executable_name = "vcpkg.exe"
    else:
        script_name = "bootstrap-vcpkg.sh"
        executable_name = "vcpkg"
    if not os.path.exists(os.path.join(root, executable_name)):
        subprocess.check_call([os.path.join(root, script_name), "-disableMetrics"], cwd=root)

def install(*ports, triplet=None):
    if triplet is None:
        triplet = _this_module.triplet
    cmd = [os.path.join(root, "vcpkg"), "install"]
    cmd.extend(port + ":" + triplet for port in ports)
    subprocess.check_call(cmd, cwd=root)

def install_manifest(manifest_root, triplet=None):
    if triplet is None:
        triplet = _this_module.triplet
    cmd = [os.path.join(root, "vcpkg"), "install", "--x-install-root=" + os.path.join(root, "installed"), "--triplet", triplet]
    subprocess.check_call(cmd, cwd=manifest_root)
