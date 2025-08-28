vcpkg_check_linkage(ONLY_DYNAMIC_LIBRARY)

vcpkg_download_distfile(ARCHIVE
    URLS "https://www.nuget.org/api/v2/package/Microsoft.AI.DirectML/${VERSION}"
    FILENAME "Microsoft.AI.DirectML.${VERSION}.nupkg"
    SHA512 fde767f56904abc90fd53f65d8729c918ab7f6e3c5e1ecdd479908fc02b4535cf2b0860f7ab2acb9b731d6cb809b72c3d5d4d02853fb8f5ea022a47bc44ef285
)

vcpkg_extract_source_archive(
    SOURCE_PATH
    ARCHIVE ${ARCHIVE}
    NO_REMOVE_ONE_LEVEL
)

file(MAKE_DIRECTORY
    ${CURRENT_PACKAGES_DIR}/include
    ${CURRENT_PACKAGES_DIR}/lib
    ${CURRENT_PACKAGES_DIR}/bin
    ${CURRENT_PACKAGES_DIR}/debug/lib
    ${CURRENT_PACKAGES_DIR}/debug/bin
)

file(COPY
    ${SOURCE_PATH}/include
    DESTINATION ${CURRENT_PACKAGES_DIR}
)

file(COPY ${SOURCE_PATH}/bin/${VCPKG_TARGET_ARCHITECTURE}-win/DirectML.dll
    DESTINATION ${CURRENT_PACKAGES_DIR}/bin)
file(COPY ${SOURCE_PATH}/bin/${VCPKG_TARGET_ARCHITECTURE}-win/DirectML.pdb
    DESTINATION ${CURRENT_PACKAGES_DIR}/bin)
file(COPY ${SOURCE_PATH}/bin/${VCPKG_TARGET_ARCHITECTURE}-win/DirectML.lib
    DESTINATION ${CURRENT_PACKAGES_DIR}/lib)

file(COPY ${SOURCE_PATH}/bin/${VCPKG_TARGET_ARCHITECTURE}-win/DirectML.dll
    DESTINATION ${CURRENT_PACKAGES_DIR}/debug/bin)
file(COPY ${SOURCE_PATH}/bin/${VCPKG_TARGET_ARCHITECTURE}-win/DirectML.pdb
    DESTINATION ${CURRENT_PACKAGES_DIR}/debug/bin)
file(COPY ${SOURCE_PATH}/bin/${VCPKG_TARGET_ARCHITECTURE}-win/DirectML.lib
    DESTINATION ${CURRENT_PACKAGES_DIR}/debug/lib)

# file(COPY ${SOURCE_PATH}/bin/${VCPKG_TARGET_ARCHITECTURE}-win/DirectML.Debug.dll
# DESTINATION ${CURRENT_PACKAGES_DIR}/debug/bin)
# file(COPY ${SOURCE_PATH}/bin/${VCPKG_TARGET_ARCHITECTURE}-win/DirectML.Debug.pdb
# DESTINATION ${CURRENT_PACKAGES_DIR}/debug/bin)

# # Handle copyright
file(INSTALL ${SOURCE_PATH}/LICENSE.txt DESTINATION ${CURRENT_PACKAGES_DIR}/share/${PORT} RENAME copyright)
