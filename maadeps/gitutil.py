import os
import subprocess
from .common import resdir

def fetch_git_repo(origin, ref, dest, submodules=True):
    env = {**os.environ, "XDG_CONFIG_HOME": os.path.join(resdir, "git-override")}
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
    if submodules:
        update_sumbodule(dest, recursive=True)

def update_sumbodule(repo, name=None, recursive=False):
    env = {**os.environ, "XDG_CONFIG_HOME": os.path.join(resdir, "git-override")}
    cmd = ["git", "submodule", "update", "--init", "--recommend-shallow", "--depth", "1"]
    if recursive:
        cmd.append("--recursive")
    if name is not None:
        cmd.append(name)
    subprocess.check_call(cmd, cwd=repo, env=env)

def apply_patch(srcdir, patch_file: str):
    subprocess.check_call(["git", "apply", os.path.abspath(patch_file)], cwd=srcdir)
