import os
import sys
import shutil
import tarfile
import subprocess
from pathlib import Path
from contextlib import contextmanager


def find_xz_executable() -> str | None:
    candidates = []
    which_xz = shutil.which("xz")
    if which_xz:
        candidates.append(which_xz)
    if sys.platform == "win32":
        win_candidates = [
            Path(os.environ.get("ProgramFiles", r"C:\Program Files")) / "Git" / "usr" / "bin" / "xz.exe",
            Path(os.environ.get("ProgramFiles(x86)", r"C:\Program Files (x86)")) / "Git" / "usr" / "bin" / "xz.exe",
            Path(os.environ.get("LOCALAPPDATA", "")) / "Programs" / "Git" / "usr" / "bin" / "xz.exe",
            Path(os.environ.get("USERPROFILE", "")) / "scoop" / "apps" / "git" / "current" / "usr" / "bin" / "xz.exe",
        ]
        for c in win_candidates:
            if c.is_file():
                candidates.append(str(c))
    for exe in candidates:
        try:
            res = subprocess.run([exe, "-T0", "-V"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            if res.returncode == 0:
                return exe
        except Exception:
            continue
    return None


@contextmanager
def open_tar_xz(out_path):
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    xz_exe = find_xz_executable()
    if xz_exe:
        print(f"Compressing {out_path} using multi-threaded xz ({xz_exe} -T0)...")
        with open(out_path, "wb") as out_f:
            proc = subprocess.Popen(
                [xz_exe, "-T0"],
                stdin=subprocess.PIPE,
                stdout=out_f,
            )
            try:
                with tarfile.open(mode="w|", fileobj=proc.stdin) as tar:
                    yield tar
            except Exception:
                if proc.stdin and not proc.stdin.closed:
                    proc.stdin.close()
                proc.kill()
                if out_path.exists():
                    try:
                        out_path.unlink()
                    except OSError:
                        pass
                raise
            else:
                if proc.stdin and not proc.stdin.closed:
                    proc.stdin.close()
                proc.wait()
                if proc.returncode != 0:
                    raise RuntimeError(f"xz failed with returncode {proc.returncode}")
    else:
        print(f"Compressing {out_path} using built-in tarfile (single-threaded fallback)...")
        with tarfile.TarFile.open(out_path, "w:xz") as tar:
            yield tar
