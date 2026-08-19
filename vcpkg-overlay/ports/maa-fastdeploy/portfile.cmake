vcpkg_from_github(
    OUT_SOURCE_PATH SOURCE_PATH
    REPO MaaXYZ/FastDeploy
    REF e3233f2f1e5f723bb11af3b061d0e6027db5c331
    SHA512 3f3d94059d7ace0d389afc4fb654ebac936c62beb51ac5cc47ea23927cf6606c7f91c4cba40db6d86fdceed48393eb3984b0008367aebf4df50f9311d146e426
    PATCHES
        fix-float16-libcxx-no-specializations.patch
)

vcpkg_cmake_configure(
    SOURCE_PATH "${SOURCE_PATH}"
)

vcpkg_cmake_install()
vcpkg_cmake_config_fixup(PACKAGE_NAME fastdeploy_ppocr CONFIG_PATH share/fastdeploy_ppocr)

file(INSTALL "${SOURCE_PATH}/LICENSE" DESTINATION "${CURRENT_PACKAGES_DIR}/share/${PORT}" RENAME copyright)
file(REMOVE_RECURSE "${CURRENT_PACKAGES_DIR}/debug/include")
file(REMOVE_RECURSE "${CURRENT_PACKAGES_DIR}/debug/share")
