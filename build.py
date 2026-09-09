#!/usr/bin/env python3
import os
import sys
sys.dont_write_bytecode = True
import subprocess
import glob
from pathlib import Path

from maadeps import basedir, resdir, host_triplet, BuildTree, session, vcpkg, runtime, gitutil

from maadeps.runner import task

@task
def vcpkg_bootstrap():
    vcpkg.bootstrap(session.target)

@task
def vcpkg_install():
    vcpkg.install_manifest(basedir)

def main():
    session.parse_args(sys.argv)

    vcpkg_bootstrap()
    clean()
    vcpkg_install()
    runtime.sdk_ready()
    runtime.install_runtime()

    if session.enable_tarball:
        bin_tarball()
        sdk_tarball()

@task
def clean():
    import shutil
    os.chdir(basedir)
    shutil.rmtree("runtime", ignore_errors=True)
    shutil.rmtree("debug", ignore_errors=True)
    shutil.rmtree("tarball", ignore_errors=True)
    shutil.rmtree("vcpkg/installed", ignore_errors=True)

@task
def get_tarball_triplet():
    return vcpkg.triplet.removeprefix("maa-")

from maadeps.tarutil import open_tar_xz

@task
def bin_tarball():
    os.chdir(basedir)
    os.makedirs("tarball", exist_ok=True)
    runtime_dir = Path(runtime.get_runtime_dir())
    debug_dir = Path(runtime.get_debug_dir())
    runtimefiles = [p for p in runtime_dir.glob("**/*") if p.is_file() or p.is_symlink()] if runtime_dir.exists() else []
    dbgfiles = [p for p in debug_dir.glob("**/*") if p.is_file() or p.is_symlink()] if debug_dir.exists() else []
    tarball_triplet = get_tarball_triplet()

    if runtimefiles:
        with open_tar_xz(f"tarball/MaaDeps-{tarball_triplet}-runtime.tar.xz") as runtimetar:
            for fspath in runtimefiles:
                runtimetar.add(fspath, arcname=fspath.relative_to(basedir))
    if dbgfiles:
        with open_tar_xz(f"tarball/MaaDeps-{tarball_triplet}-dbg.tar.xz") as dbgtar:
            for fspath in dbgfiles:
                dbgtar.add(fspath, arcname=fspath.relative_to(debug_dir))

@task
def sdk_tarball():
    import tarfile
    os.chdir(basedir)
    os.makedirs("tarball", exist_ok=True)

    tarball_triplet = get_tarball_triplet()

    extra_files = [
        *glob.glob("./msbuild/*"),
        *glob.glob("./vcpkg/scripts/buildsystems/msbuild/*"),
        "./vcpkg/scripts/buildsystems/vcpkg.cmake",
        "./maadeps.cmake",
    ]

    if 'linux' in session.target:
        extra_files += [
            *glob.glob("./cmake/*"),
            *glob.glob("./x-tools/*"),
            "linux-toolchain-download.py"
        ]

    if 'windows' in session.target:
        def sdk_filter(info: tarfile.TarInfo):
            if info.name.endswith(".pdb"):
                return None
            return info
    else:
        sdk_filter = None
    with open_tar_xz(f"tarball/MaaDeps-{tarball_triplet}-devel.tar.xz") as sdktar:
        sdktar.add(f"./vcpkg/installed/{vcpkg.triplet}", filter=sdk_filter)
        # sdktar.add(f"./vcpkg/installed/{vcpkg.triplet.removeprefix('maa-').replace('arm64', 'x64')}/tools")

        for f in extra_files:
            sdktar.add(f)


if __name__ == "__main__":
    main()
