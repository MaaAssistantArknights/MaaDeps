import os
import subprocess

from .common import basedir, resdir
from . import gitutil

class BuildTree:
    def __init__(self, name):
        from . import vcpkg
        self.source_dir = os.path.join(basedir, "src", name)
        self.binary_dir = os.path.join(vcpkg.root, "buildtrees", name, vcpkg.triplet)
    
    def fetch_git_repo(self, origin, ref, submodules=True):
        gitutil.fetch_git_repo(origin, ref, self.source_dir, submodules)
    
    def apply_patches(self, *patch_files: str):
        for patch_file in patch_files:
            gitutil.apply_patch(self.source_dir, patch_file)

    def invoke_cmake_install(self, *cmake_args, relative_source_dir=None):
        source_dir = self.source_dir
        if relative_source_dir is not None:
            source_dir = os.path.join(source_dir, relative_source_dir)
        subprocess.check_call(["cmake", "-S", source_dir, "-B", self.binary_dir, "-GNinja", *cmake_args], cwd=basedir)
        subprocess.check_call(["cmake", "--build", self.binary_dir, "-t", "install"], cwd=basedir)