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
    vcpkg.install("opencv4[core,eigen,lapack,jpeg,png,tiff,world]", "opencv[core,eigen,lapack,jpeg,png,tiff,world]", "maa-fastdeploy")

def main():
    session.parse_args(sys.argv)

    vcpkg_bootstrap()
    vcpkg_install()
    runtime.sdk_ready()
    runtime.install_runtime()

    if session.enable_tarball:
        bin_tarball()
        sdk_tarball()


@task
def get_tarball_triplet():
    return vcpkg.triplet.removeprefix("maa-")

@task
def bin_tarball():
    import tarfile
    os.chdir(basedir)
    os.makedirs("tarball", exist_ok=True)
    runtimefiles = Path(runtime.get_runtime_dir()).glob("**/*")
    dbgfiles = Path(runtime.get_debug_dir()).glob("**/*")
    tarball_triplet = get_tarball_triplet()


    if runtimefiles:
        with tarfile.TarFile.open(f"tarball/MaaDeps-{tarball_triplet}-runtime.tar.xz", 'w:xz') as runtimetar:
            for fspath in runtimefiles:
                runtimetar.add(fspath, arcname=fspath.relative_to(runtime.get_runtime_dir()))
    if dbgfiles:
        with tarfile.TarFile.open(f"tarball/MaaDeps-{tarball_triplet}-dbg.tar.xz", 'w:xz') as dbgtar:
            for fspath in dbgfiles:
                dbgtar.add(fspath, arcname=fspath.relative_to(runtime.get_debug_dir()))

@task
def sdk_tarball():
    import tarfile
    os.chdir(basedir)
    os.makedirs("tarball", exist_ok=True)

    tarball_triplet = get_tarball_triplet()

    if 'windows' in session.target:
        def bin_filter(info: tarfile.TarInfo):
            if info.name.endswith(".pdb"):
                return None
            return info
    else:
        bin_filter = None
    with tarfile.TarFile.open(f"tarball/MaaDeps-{tarball_triplet}-sdk.tar.xz", 'w:xz') as bintar:
        bintar.add(f"./vcpkg/installed/{vcpkg.triplet}", filter=bin_filter)


if __name__ == "__main__":
    main()
