cmake_minimum_required(VERSION 3.15)
project(raptor)

if(WIN32)
    set(PREMAKE_BIN "binaries/premake/premake5-windows.exe")
    set(PREMAKE_DEST "premake5.exe")
elseif(APPLE)
    if(CMAKE_SYSTEM_PROCESSOR MATCHES "arm64")
        set(PREMAKE_BIN "binaries/premake/premake5-macosx")
    else()
        set(PREMAKE_BIN "binaries/premake/premake5-macosx-x64")
    endif()
    set(PREMAKE_DEST "premake5")
else()
    set(PREMAKE_BIN "binaries/premake/premake5-linux")
    set(PREMAKE_DEST "premake5")
endif()

install(
    PROGRAMS "${CMAKE_SOURCE_DIR}/${PREMAKE_BIN}"
    DESTINATION "src/raptor/bin"
    RENAME "${PREMAKE_DEST}"
)
