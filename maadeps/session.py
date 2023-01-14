
allow_modified_source = False
target: str
enable_tarball = False
extra_cmake_args = []


def parse_args(argv):
    import argparse
    import sys
    _this_module = sys.modules[__name__]
    parser = argparse.ArgumentParser()
    parser.add_argument("--target", default=None)
    parser.add_argument("--skip-src-update", action="store_true", default=False)
    parser.add_argument("--tarball", action="store_true", default=False)
    parser.add_argument("extra_cmake_args", nargs=argparse.ZERO_OR_MORE)  # '-- -DCMAKE_XXX ...'

    config = parser.parse_args(argv[1:])

    _this_module.target = config.target
    if _this_module.target is None:
        from .common import host_triplet
        _this_module.target = "maa-" + host_triplet
    _this_module.allow_modified_source = config.skip_src_update
    _this_module.enable_tarball = config.tarball
    _this_module.extra_cmake_args = config.extra_cmake_args
