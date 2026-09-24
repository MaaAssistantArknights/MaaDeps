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
    if "VCPKG_DEFAULT_BINARY_CACHE" not in os.environ:
        os.makedirs(archives_dir, exist_ok=True)
        os.environ["VCPKG_DEFAULT_BINARY_CACHE"] = archives_dir

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
    subprocess.check_call(cmd, cwd=manifest_root)

def dry_run_manifest(manifest_root, output_file="vcpkg_dry_run.txt", triplet=None):
    if triplet is None:
        triplet = _this_module.triplet
    if not os.path.isabs(output_file):
        output_file = os.path.join(basedir, output_file)
    import tempfile
    with tempfile.TemporaryDirectory() as temp_install_root:
        cmd = [
            os.path.join(root, "vcpkg"),
            "install",
            "--dry-run",
            "--x-install-root=" + temp_install_root,
            "--triplet",
            triplet,
            "--host-triplet",
            _get_host_triplet(triplet),
            f"--x-write-nuget-packages-config={output_file}",
        ]
        subprocess.check_call(cmd, cwd=manifest_root)

def prune_archives():
    from pathlib import Path
    import re
    status_file = Path(root) / "installed" / "vcpkg" / "status"
    archives_dir = Path(os.environ.get("VCPKG_DEFAULT_BINARY_CACHE", os.path.join(root, "archives")))
    if not status_file.is_file() or not archives_dir.is_dir():
        return
    active_abis = set(re.findall(r"Abi: ([0-9a-fA-F]+)", status_file.read_text(encoding="utf-8", errors="ignore")))
    if not active_abis:
        return
    pruned = 0
    kept = 0
    for p in archives_dir.glob("**/*.zip"):
        if p.stem not in active_abis:
            print("Pruning stale binary archive:", p.name)
            try:
                p.unlink()
                pruned += 1
            except OSError as e:
                print("Failed to delete stale archive:", p, e)
        else:
            kept += 1
    for d in sorted(archives_dir.glob("*"), reverse=True):
        if d.is_dir() and not any(d.iterdir()):
            try:
                d.rmdir()
            except OSError:
                pass
    print(f"vcpkg archives pruned: {pruned} removed, {kept} retained.")

