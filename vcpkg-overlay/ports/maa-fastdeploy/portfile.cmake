vcpkg_from_github(
    OUT_SOURCE_PATH SOURCE_PATH
    REPO MaaAssistantArknights/FastDeploy
    REF 2279e19c150c4fc371a9be291f16f3d52633703d
    SHA512 380151fdafe81db1ec5c0bcc3e798664d2ff0a10916b8718a194a78074704fab9205821ee51f0ec9b050f3f810d49dc985d95d453718dc592d2076b205a2258a
    HEAD_REF maadeps
    PATCHES
        000-fix-rpath.patch
)

vcpkg_cmake_configure(
    SOURCE_PATH "${SOURCE_PATH}"
)

vcpkg_cmake_install()

file(INSTALL "${SOURCE_PATH}/LICENSE" DESTINATION "${CURRENT_PACKAGES_DIR}/share/${PORT}" RENAME copyright)
file(REMOVE_RECURSE "${CURRENT_PACKAGES_DIR}/debug/include")
file(REMOVE_RECURSE "${CURRENT_PACKAGES_DIR}/debug/share")
