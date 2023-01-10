#!/usr/bin/env python3
import os
import sys
sys.dont_write_bytecode = True

import subprocess
import glob
import argparse
from pathlib import PurePath

from host_triplet import detect_host_triplet

host_triplet = detect_host_triplet()

basedir = os.path.abspath(os.path.dirname(__file__))
vcpkg_overlay_triplets = os.path.join(basedir, "triplets")

class Vcpkg:
    def __init__(self, root: str, triplet: str):
        self.root = root
        self.triplet = triplet
        self.toolchain_file = os.path.join(root, "scripts", "buildsystems", "vcpkg.cmake")
        self.install_prefix = os.path.join(root, "installed", triplet)

    def bootstrap(self):
        if os.name == "nt":
            script_name = "bootstrap-vcpkg.bat"
            executable_name = "vcpkg.exe"
        else:
            script_name = "bootstrap-vcpkg.sh"
            executable_name = "vcpkg"
        if not os.path.exists(os.path.join(self.root, executable_name)):
            subprocess.check_call([os.path.join(self.root, script_name), "-disableMetrics"], cwd=self.root)

    def install(self, *ports, triplet=None):
        if triplet is None:
            triplet = self.triplet
        cmd = [os.path.join(self.root, "vcpkg"), "install"]
        cmd.extend(port + ":" + triplet for port in ports)
        subprocess.check_call(cmd, cwd=self.root)


class Dirs:
    src: str
    bin: str

def clone_git_repo(url, ref, dest, skip_update=False):
    if os.path.isdir(os.path.join(dest, ".git")):
        if skip_update:
            return
        subprocess.check_call(["git", "fetch", url, ref, "--depth", "1"], cwd=dest)
        subprocess.check_call(["git", "reset", "--hard", "FETCH_HEAD"], cwd=dest)
    else:
        os.makedirs(dest, exist_ok=True)
        subprocess.check_call(["git", "init"], cwd=dest)
        subprocess.check_call(["git", "fetch", url, ref, "--depth", "1"], cwd=dest)
        subprocess.check_call(["git", "reset", "--hard", "FETCH_HEAD"], cwd=dest)
    subprocess.check_call(["git", "submodule", "update", "--init", "--recursive", "--recommend-shallow", "--depth", "1"], cwd=dest)

def apply_patches(source_dir, patch_files: list[str]):
    for patch_file in patch_files:
        subprocess.check_call(["git", "apply", os.path.abspath(patch_file)], cwd=source_dir)

def bootstrap_vcpkg(target_triplet=None):
    if target_triplet is None:
        target_triplet = "maa-" + host_triplet
    print("host triplet for vcpkg:", host_triplet)
    print("target triplet for vcpkg:", target_triplet)

    os.environ["VCPKG_OVERLAY_TRIPLETS"] = vcpkg_overlay_triplets

    root = os.path.join(basedir, "vcpkg")
    if not os.path.exists(os.path.join(root, "bootstrap_vcpkg.bat")):
        subprocess.check_call(["git", "submodule", "update", "--init", "vcpkg"], cwd=basedir)
    result = Vcpkg(os.path.join(basedir, "vcpkg"), target_triplet)
    result.bootstrap()
    return result

def invoke_cmake_install(source_dir, binary_dir, *cmake_args):
    subprocess.check_call(["cmake", "-S", source_dir, "-B", binary_dir, "-GNinja", *cmake_args], cwd=basedir)
    subprocess.check_call(["cmake", "--build", binary_dir, "-t", "install"], cwd=basedir)

def main(argv: list[str]):
    parser = argparse.ArgumentParser()
    parser.add_argument("--target", default=None)
    parser.add_argument("--skip-src-update", action="store_true", default=False)
    parser.add_argument("--tarball", action="store_true", default=False)

    config = parser.parse_args(argv[1:])

    # TODO: sanity check
    vcpkg = bootstrap_vcpkg(config.target)

    try:
        extra_index = argv.index('--', 1)
        extra_cmake_args = argv[extra_index+1:]
    except ValueError:
        extra_cmake_args = []

    cross_compiling = host_triplet != vcpkg.triplet.removeprefix("maa-")


    vcpkg.install("opencv4[core,eigen,lapack,jpeg,png,tiff,world]", "opencv[core,eigen,lapack,jpeg,png,tiff,world]", "zlib", "protobuf")

    # for protoc
    vcpkg.install("protobuf", triplet=host_triplet)

    def src_bin_dirs(name):
        result = Dirs()
        result.src = os.path.join(vcpkg.root, "buildtrees", name, "src")
        result.bin = os.path.join(vcpkg.root, "buildtrees", name, vcpkg.triplet)
        return result

    common_cmake_args = [
        # "-DCMAKE_TOOLCHAIN_FILE:FILEPATH=" + vcpkg.toolchain_file,
        # "-DVCPKG_TARGET_TRIPLET=" + vcpkg.triplet.removeprefix("maa-"),
        # "-DVCPKG_OVERLAY_TRIPLETS:PATH=" + vcpkg_overlay_triplets,
        "-DCMAKE_BUILD_TYPE=RelWithDebInfo",
        "-DCMAKE_INSTALL_PREFIX:PATH=" + vcpkg.install_prefix,
        *extra_cmake_args
    ]
    
    if vcpkg.triplet == 'maa-arm64-windows':
        common_cmake_args.append("-DCMAKE_SYSTEM_PROCESSOR=ARM64")
    elif vcpkg.triplet == 'maa-x64-windows':
        common_cmake_args.append("-DCMAKE_SYSTEM_PROCESSOR=AMD64")

    if 'windows' in vcpkg.triplet:
        common_cmake_args.append("-DCMAKE_SHARED_LIBRARY_SUFFIX_CXX=_maa.dll")
        # TODO: suffix for other platforms

    protoc_dir = os.path.join(vcpkg.root, "installed", host_triplet, "tools", "protobuf")
    protoc_basename = "protoc.exe" if os.name == 'nt' else "protoc"
    protoc_path = os.path.join(protoc_dir, protoc_basename)

    # os.environ["PATH"] = protoc_path + os.pathsep + os.environ["PATH"]

    ort = src_bin_dirs("onnxruntime")
    clone_git_repo("https://github.com/microsoft/onnxruntime", "v1.12.1", ort.src, skip_update=config.skip_src_update)
    ort_cmake_args = [
        "-Donnxruntime_BUILD_SHARED_LIB=ON",
        "-Donnxruntime_BUILD_UNIT_TESTS=OFF",
        "-Donnxruntime_PREFER_SYSTEM_LIB=ON",
        "-DProtobuf_USE_STATIC_LIBS=ON",
        "-DONNX_CUSTOM_PROTOC_EXECUTABLE:FILEPATH=" + protoc_path,
    ]
    if cross_compiling:
        ort_cmake_args.append("-Donnxruntime_CROSS_COMPILING=ON")

    invoke_cmake_install(os.path.join(ort.src, "cmake"), ort.bin, *common_cmake_args, *ort_cmake_args)

    paddle2onnx = src_bin_dirs("paddle2onnx")
    clone_git_repo("https://github.com/MaaAssistantArknights/Paddle2ONNX", "8718eb81a6a21f13fbde7b79f3b8745c9aee0491", paddle2onnx.src, skip_update=config.skip_src_update)

    fastdeploy = src_bin_dirs("fastdeploy")
    clone_git_repo("https://github.com/MaaAssistantArknights/FastDeploy", "9cb37186b72c032e59ccaf61d55c7ba7e8bcadb0", fastdeploy.src, skip_update=config.skip_src_update)
    invoke_cmake_install(fastdeploy.src, fastdeploy.bin, *common_cmake_args, 
        "-DENABLE_VISION=ON",
        "-DENABLE_ORT_BACKEND=ON",
        "-DORT_DIRECTORY:PATH=" + vcpkg.install_prefix,
        "-DOPENCV_DIRECTORY:PATH=" + vcpkg.install_prefix,
        "-DPaddle2ONNX_SRC:PATH=" + paddle2onnx.src,
        "-DONNX_CUSTOM_PROTOC_PATH:FILEPATH=" + protoc_dir,
    )

    # tarball
    if config.tarball:
        import tarfile
        os.chdir(basedir)

        tarball_triplet = vcpkg.triplet.removeprefix("maa-")

        def bin_filter(info: tarfile.TarInfo):
            if info.name.endswith(".pdb"):
                return None
            return info
        with tarfile.TarFile.open(f"MaaDeps-{tarball_triplet}-bin.tar.xz", 'w:xz') as bintar:
            bintar.add(f"./vcpkg/installed/{vcpkg.triplet}", filter=bin_filter)

        dbgfiles = []
        if 'windows' in vcpkg.triplet:
            import findpdb
            pureroot = PurePath(vcpkg.root)
            for file in glob.glob(f"./vcpkg/installed/{vcpkg.triplet}/bin/**", recursive=True):
                try:
                    pdbfile = findpdb.find_pdb_file(file)
                    try:
                        pdbfile = pdbfile.decode('utf-8')
                    except UnicodeDecodeError:
                        pdbfile = pdbfile.decode('mbcs')
                    pdbfile = PurePath(pdbfile)
                    if pdbfile.is_relative_to(vcpkg.root):
                        print("found pdb for", file, "->", pdbfile)
                        dbgfiles.append((str(pdbfile), str(PurePath(file).with_name(pdbfile.name))))
                except:
                    pass
        # TODO: collect debug file for other platforms

        if dbgfiles:
            with tarfile.TarFile.open(f"MaaDeps-{tarball_triplet}-dbg.tar.xz", 'w:xz') as dbgtar:
                for fsname, aname in dbgfiles:
                    dbgtar.add(fsname, arcname=aname)

if __name__ == "__main__":
    main(sys.argv)
