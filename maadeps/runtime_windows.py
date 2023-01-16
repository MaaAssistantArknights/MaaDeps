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

def install_runtime(target_dir, debug_dir):
    from . import vcpkg
    prefix = Path(vcpkg.install_prefix)
    target = Path(target_dir)
    from .runtime import install_file, match_patterns
    for file in prefix.glob("bin/**/*"):
        if (match_patterns(file, exclude)):
            continue
        if file.is_file():
            target_path = target / file.relative_to(prefix / "bin")
            install_file(file, target_path)
            from maadeps import findpdb
            try:
                pdbfile = findpdb.find_pdb_file(file)
                try:
                    pdbfile = pdbfile.decode('utf-8')
                except UnicodeDecodeError:
                    pdbfile = pdbfile.decode('mbcs')
                pdbfile = Path(pdbfile)
                if pdbfile.is_relative_to(vcpkg.root):
                    print("found pdb for", file, "->", pdbfile)
                    install_file(pdbfile, debug_dir)
            except:
                pass
