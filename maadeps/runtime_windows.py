import shutil
from pathlib import Path


exclude = [
    "bin/onnxruntime_providers_shared_maa.dll",
    "*.pdb",
    # mingw gcc-libs
    "bin/libatomic-1.dll",
    "bin/libgcc_s_seh-1.dll",
    "bin/libgomp-1.dll",
    "bin/libquadmath-0.dll",
    "bin/libssp-0.dll",
    "bin/libstdc++-6.dll",
]

def match_patterns(path: Path, patterns):
    for pat in patterns:
        if path.match(pat):
            return True
    return False

def install_runtime(target_dir):
    from . import vcpkg
    prefix = Path(vcpkg.install_prefix)
    target = Path(target_dir)
    from .runtime import install_file
    for file in prefix.glob("bin/**/*"):
        if (match_patterns(file, exclude)):
            continue
        if file.is_file():
            target_path = target / file.relative_to(prefix / "bin")
            install_file(file, target_path)
