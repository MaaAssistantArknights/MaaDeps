import os
import subprocess

from .common import basedir, resdir

class BuildTree:
    def __init__(self, name):
        from . import vcpkg
        self.source_dir = os.path.join(basedir, "src", name)
        self.binary_dir = os.path.join(vcpkg.root, "buildtrees", name, vcpkg.triplet)
    
    def fetch_git_repo(self, origin, ref):
        env = {**os.environ, "XDG_CONFIG_HOME": os.path.join(resdir, "git-override")}
        dest = self.source_dir
        if os.path.isdir(os.path.join(dest, ".git")):
            from . import session
            if session.allow_modified_source:
                return
            subprocess.check_call(["git", "fetch", origin, ref, "--depth", "1"], cwd=dest, env=env)
            subprocess.check_call(["git", "reset", "--hard", "FETCH_HEAD"], cwd=dest, env=env)
        else:
            os.makedirs(dest, exist_ok=True)
            subprocess.check_call(["git", "init"], cwd=dest, env=env)
            subprocess.check_call(["git", "fetch", origin, ref, "--depth", "1"], cwd=dest, env=env)
            subprocess.check_call(["git", "reset", "--hard", "FETCH_HEAD"], cwd=dest, env=env)
        subprocess.check_call(["git", "submodule", "update", "--init", "--recursive", "--recommend-shallow", "--depth", "1"], cwd=dest, env=env)
    
    def apply_patches(self, *patch_files: str):
        for patch_file in patch_files:
            subprocess.check_call(["git", "apply", os.path.abspath(patch_file)], cwd=self.source_dir)

    def invoke_cmake_install(self, *cmake_args, relative_source_dir=None):
        source_dir = self.source_dir
        if relative_source_dir is not None:
            source_dir = os.path.join(source_dir, relative_source_dir)
        subprocess.check_call(["cmake", "-S", source_dir, "-B", self.binary_dir, "-GNinja", *cmake_args], cwd=basedir)
        subprocess.check_call(["cmake", "--build", self.binary_dir, "-t", "install"], cwd=basedir)