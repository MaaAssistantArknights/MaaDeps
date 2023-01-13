#!/usr/bin/env python3
import os
import sys
sys.dont_write_bytecode = True
import subprocess
import glob
from pathlib import PurePath

from maadeps import basedir, resdir, host_triplet, BuildTree, session, vcpkg, runtime, gitutil

from maadeps.runner import task

@task
def vcpkg_bootstrap():
    vcpkg.bootstrap(session.target)

@task
def vcpkg_install():
    vcpkg.install("opencv4[core,eigen,lapack,jpeg,png,tiff,world]", "re2", "boost-config", "boost-mp11", "protobuf", "flatbuffers")

def main():
    session.parse_args(sys.argv)

    vcpkg_bootstrap()
    vcpkg_install()
    build_extra_packages()
    runtime.sdk_ready()
    runtime.install_runtime()

    if session.enable_tarball:
        bin_tarball()
        dbg_tarball()


@task
def build_extra_packages():
    common_cmake_args = [
        # "-DCMAKE_TOOLCHAIN_FILE:FILEPATH=" + vcpkg.toolchain_file,
        # "-DVCPKG_TARGET_TRIPLET=" + vcpkg.triplet.removeprefix("maa-"),
        "-DCMAKE_BUILD_TYPE=Release",
        "-DCMAKE_INSTALL_PREFIX:PATH=" + vcpkg.install_prefix,
        *session.extra_cmake_args
    ]
    
    if vcpkg.triplet == 'maa-arm64-windows':
        common_cmake_args.append("-DCMAKE_TOOLCHAIN_FILE:FILEPATH=" + os.path.join(resdir, "toolchains", "toolchain-msvc-arm64.cmake"))
    elif vcpkg.triplet == 'maa-x64-windows':
        common_cmake_args.append("-DCMAKE_TOOLCHAIN_FILE:FILEPATH=" + os.path.join(resdir, "toolchains", "toolchain-msvc-x64.cmake"))

    if 'windows' in vcpkg.triplet:
        common_cmake_args.append("-DCMAKE_SHARED_LIBRARY_SUFFIX_CXX=_maa.dll")
        # TODO: suffix for other platforms

    vcpkg.install("protobuf", triplet=host_triplet)
    protoc_dir = os.path.join(vcpkg.root, "installed", host_triplet, "tools", "protobuf")
    exe_suffix = ".exe" if os.name == 'nt' else ""
    protoc_path = os.path.join(protoc_dir, "protoc" + exe_suffix)
    flatc = os.path.join(vcpkg.root, "installed", host_triplet, "tools", "flatbuffers", "flatc" + exe_suffix)
    eigen_path = os.path.join(vcpkg.root, "installed", vcpkg.triplet, "include", "eigen3")

    # os.environ["PATH"] = protoc_path + os.pathsep + os.environ["PATH"]

    ort = BuildTree("onnxruntime")
    ort.fetch_git_repo("https://github.com/microsoft/onnxruntime", "v1.12.1", submodules=False)
    submodules = ["onnx", "SafeInt", "tensorboard", "dlpack", "cxxopts", "pytorch_cpuinfo", "date", "json"]
    if 'windows' in vcpkg.triplet:
        submodules.append("wil")
    elif "linux" in vcpkg.triplet:
        submodules.append("nsync")

    for mod in submodules:
        gitutil.update_sumbodule(ort.source_dir, f"cmake/external/{mod}")
    subprocess.check_call([sys.executable, "compile_schema.py", "--flatc", flatc], cwd=os.path.join(ort.source_dir, "onnxruntime/core/flatbuffers/schema"))
    ort_cmake_args = [
        "-Donnxruntime_BUILD_SHARED_LIB=ON",
        "-Donnxruntime_BUILD_UNIT_TESTS=OFF",
        "-Donnxruntime_ENABLE_LTO=ON",
        "-DCMAKE_INTERPROCEDURAL_OPTIMIZATION=ON",
        "-Donnxruntime_PREFER_SYSTEM_LIB=ON",
        "-DProtobuf_USE_STATIC_LIBS=ON",
        "-Donnxruntime_USE_PREINSTALLED_EIGEN=ON",
        "-Deigen_SOURCE_PATH:PATH=" + eigen_path,
        "-DFLATBUFFERS_BUILD_FLATC=OFF",
        "-DONNX_CUSTOM_PROTOC_EXECUTABLE:FILEPATH=" + protoc_path,
    ]
    if vcpkg.cross_compiling:
        ort_cmake_args.append("-Donnxruntime_CROSS_COMPILING=ON")

    ort.invoke_cmake_install(*common_cmake_args, *ort_cmake_args, relative_source_dir="cmake")

    paddle2onnx = BuildTree("paddle2onnx")
    paddle2onnx.fetch_git_repo("https://github.com/MaaAssistantArknights/Paddle2ONNX", "37d6736cfc13857789a36dc263baa17c4defb784")

    fastdeploy = BuildTree("fastdeploy")
    fastdeploy.fetch_git_repo("https://github.com/MaaAssistantArknights/FastDeploy", "9cb37186b72c032e59ccaf61d55c7ba7e8bcadb0")
    fastdeploy.invoke_cmake_install(*common_cmake_args, 
        "-DENABLE_VISION=ON",
        "-DENABLE_ORT_BACKEND=ON",
        "-DORT_DIRECTORY:PATH=" + vcpkg.install_prefix,
        "-DOPENCV_DIRECTORY:PATH=" + vcpkg.install_prefix,
        "-DPaddle2ONNX_SRC:PATH=" + paddle2onnx.source_dir,
        "-DCMAKE_INTERPROCEDURAL_OPTIMIZATION=ON",
        "-DONNX_CUSTOM_PROTOC_PATH:FILEPATH=" + protoc_dir,
    )

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
        for file in glob.glob(f"./vcpkg/installed/{vcpkg.triplet}/bin/**/*", recursive=True):
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

    tarball_triplet = vcpkg.triplet.removeprefix("maa-")

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
