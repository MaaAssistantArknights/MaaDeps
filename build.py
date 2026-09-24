#!/usr/bin/env python3
import os
import sys
sys.dont_write_bytecode = True
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(line_buffering=True)
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
    if session.dry_run:
        vcpkg.dry_run_manifest(basedir, "vcpkg_dry_run.txt")
        return

    clean()
    vcpkg_install()
    runtime.sdk_ready()
    runtime.install_runtime()
    redirect_cmake_targets()

    if session.enable_tarball:
        full_tarball()
        dbg_tarball()

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
def dbg_tarball():
    os.chdir(basedir)
    os.makedirs("tarball", exist_ok=True)
    debug_dir = Path(runtime.get_debug_dir())
    dbgfiles = [p for p in debug_dir.glob("**/*") if p.is_file() or p.is_symlink()] if debug_dir.exists() else []
    tarball_triplet = get_tarball_triplet()
    if dbgfiles:
        with open_tar_xz(f"tarball/MaaDeps-{tarball_triplet}-dbg.tar.xz") as dbgtar:
            for fspath in dbgfiles:
                dbgtar.add(fspath, arcname=fspath.relative_to(debug_dir))

@task
def bin_tarball():
    os.chdir(basedir)
    os.makedirs("tarball", exist_ok=True)
    runtime_dir = Path(runtime.get_runtime_dir())
    runtimefiles = [p for p in runtime_dir.glob("**/*") if p.is_file() or p.is_symlink()] if runtime_dir.exists() else []
    tarball_triplet = get_tarball_triplet()

    if runtimefiles:
        with open_tar_xz(f"tarball/MaaDeps-{tarball_triplet}-runtime.tar.xz") as runtimetar:
            for fspath in runtimefiles:
                runtimetar.add(fspath, arcname=fspath.relative_to(basedir))
    dbg_tarball()

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

    import fnmatch

    lib_excludes = (
        "*SPIRV-Tools*.a", "*SPIRV-Tools*.lib",
        "*protoc*.a", "*protoc*.lib",
        "*protobuf*.a", "*protobuf*.lib",
        "*onnx.a", "*onnx.lib",
        "*onnx_proto*.a", "*onnx_proto*.lib",
        "*VulkanSafeStruct*.a", "*VulkanSafeStruct*.lib",
    )

    tool_excludes = (
        "tools/protobuf",
        "tools/flatbuffers",
        "tools/directx-dxc",
    )

    def sdk_filter(info: tarfile.TarInfo):
        if info.name.endswith(".pdb"):
            return None
        norm_name = info.name.replace("\\", "/")
        for t in tool_excludes:
            if f"/{t}/" in f"/{norm_name}/" or norm_name.endswith(f"/{t}"):
                return None
        filename = Path(norm_name).name
        for pat in lib_excludes:
            if fnmatch.fnmatch(filename, pat):
                return None
        return info
    with open_tar_xz(f"tarball/MaaDeps-{tarball_triplet}-devel.tar.xz") as sdktar:
        sdktar.add(f"./vcpkg/installed/{vcpkg.triplet}", filter=sdk_filter)
        # sdktar.add(f"./vcpkg/installed/{vcpkg.triplet.removeprefix('maa-').replace('arm64', 'x64')}/tools")

        for f in extra_files:
            sdktar.add(f)

@task
def redirect_cmake_targets():
    if 'windows' not in session.target:
        return
    lib_dir = Path(f"./vcpkg/installed/{vcpkg.triplet}/lib")
    dbg_lib_dir = Path(f"./vcpkg/installed/{vcpkg.triplet}/debug/lib")
    if (lib_dir / "zs.lib").exists() and not (lib_dir / "zlib.lib").exists():
        import shutil
        shutil.copy2(lib_dir / "zs.lib", lib_dir / "zlib.lib")
    if (dbg_lib_dir / "zsd.lib").exists() and not (dbg_lib_dir / "zlibd.lib").exists():
        import shutil
        shutil.copy2(dbg_lib_dir / "zsd.lib", dbg_lib_dir / "zlibd.lib")
    share_dir = Path(f"./vcpkg/installed/{vcpkg.triplet}/share")
    if not share_dir.exists():
        return
    import re
    print("redirecting Windows CMake targets from bin/ to runtime/...")
    target_triplet = vcpkg.triplet
    for cmake_file in share_dir.glob("**/*.cmake"):
        if not cmake_file.is_file():
            continue
        try:
            content = cmake_file.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        new_content = re.sub(
            r"\$\{_IMPORT_PREFIX\}/debug/bin(?=[/\"\'\s;\)])",
            f"${{_IMPORT_PREFIX}}/../../../runtime/{target_triplet}/msvc-debug",
            content,
        )
        new_content = re.sub(
            r"\$\{_IMPORT_PREFIX\}/bin(?=[/\"\'\s;\)])",
            f"${{_IMPORT_PREFIX}}/../../../runtime/{target_triplet}",
            new_content,
        )
        if new_content != content:
            print(f"redirected targets in {cmake_file}")
            cmake_file.write_text(new_content, encoding="utf-8")

@task
def full_tarball():
    import fnmatch
    import tarfile
    os.chdir(basedir)
    os.makedirs("tarball", exist_ok=True)

    redirect_cmake_targets()

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

    lib_excludes = (
        "*SPIRV-Tools*.a", "*SPIRV-Tools*.lib",
        "*protoc*.a", "*protoc*.lib",
        "*protobuf*.a", "*protobuf*.lib",
        "*onnx.a", "*onnx.lib",
        "*onnx_proto*.a", "*onnx_proto*.lib",
        "*VulkanSafeStruct*.a", "*VulkanSafeStruct*.lib",
    )

    tool_excludes = (
        "tools/protobuf",
        "tools/flatbuffers",
        "tools/directx-dxc",
    )

    omit_installed_bin = 'windows' in session.target

    def full_filter(info: tarfile.TarInfo):
        if info.name.endswith(".pdb"):
            return None
        norm_name = info.name.replace("\\", "/")
        if omit_installed_bin:
            rel_to_installed = norm_name.removeprefix("./").removeprefix(f"vcpkg/installed/{vcpkg.triplet}/")
            if rel_to_installed == "bin" or rel_to_installed.startswith("bin/") or \
               rel_to_installed == "debug/bin" or rel_to_installed.startswith("debug/bin/"):
                return None
        for t in tool_excludes:
            if f"/{t}/" in f"/{norm_name}/" or norm_name.endswith(f"/{t}"):
                return None
        filename = Path(norm_name).name
        for pat in lib_excludes:
            if fnmatch.fnmatch(filename, pat):
                return None
        return info

    runtime_dir = Path(runtime.get_runtime_dir())
    runtimefiles = [p for p in runtime_dir.glob("**/*") if p.is_file() or p.is_symlink()] if runtime_dir.exists() else []

    with open_tar_xz(f"tarball/MaaDeps-{tarball_triplet}.tar.xz") as fulltar:
        fulltar.add(f"./vcpkg/installed/{vcpkg.triplet}", filter=full_filter)
        for fspath in runtimefiles:
            fulltar.add(fspath, arcname=fspath.relative_to(basedir))
        for f in extra_files:
            fulltar.add(f)


if __name__ == "__main__":
    main()
