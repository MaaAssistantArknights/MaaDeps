#!/usr/bin/env python3
import os
import sys
sys.dont_write_bytecode = True
import subprocess
import glob
from pathlib import PurePath

from maadeps import basedir, resdir, host_triplet, BuildTree, session, vcpkg, runtime, gitutil, common

from maadeps.runner import task

@task
def vcpkg_bootstrap():
    if session.target is None:
        session.target = "maa-" + common.host_triplet
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
        dbg_tarball()


@task
def get_tarball_triplet():
    return vcpkg.triplet.removeprefix("maa-")

@task
def dbg_tarball():
    import tarfile
    os.chdir(basedir)
    dbgfiles = []
    tarball_triplet = get_tarball_triplet()

    if 'windows' in vcpkg.triplet:
        from maadeps import findpdb
        for file in glob.glob(f"./runtime/{vcpkg.triplet}/**/*", recursive=True):
            try:
                pdbfile = findpdb.find_pdb_file(file)
                try:
                    pdbfile = pdbfile.decode('utf-8')
                except UnicodeDecodeError:
                    pdbfile = pdbfile.decode('mbcs')
                pdbfile = PurePath(pdbfile)
                if pdbfile.is_relative_to(vcpkg.root):
                    print("found pdb for", file, "->", pdbfile)
                    dbgfiles.append((str(pdbfile), pdbfile.name))
            except:
                pass
    # TODO: collect debug file for other platforms

    if dbgfiles:
        with tarfile.TarFile.open(f"MaaDeps-{tarball_triplet}-dbg.tar.xz", 'w:xz') as dbgtar:
            for fsname, aname in dbgfiles:
                dbgtar.add(fsname, arcname=aname)

@task
def bin_tarball():
    import tarfile
    os.chdir(basedir)

    tarball_triplet = get_tarball_triplet()

    if 'windows' in session.target:
        def bin_filter(info: tarfile.TarInfo):
            if info.name.endswith(".pdb"):
                return None
            return info
    else:
        bin_filter = None
    with tarfile.TarFile.open(f"MaaDeps-{tarball_triplet}-sdk.tar.xz", 'w:xz') as bintar:
        bintar.add(f"./vcpkg/installed/{vcpkg.triplet}", filter=bin_filter)


if __name__ == "__main__":
    main()
