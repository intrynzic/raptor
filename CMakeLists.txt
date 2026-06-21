cmake_minimum_required(VERSION 3.25)
project(raptor)

set(CMAKE_CXX_STANDARD 23)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# PyBind11
set(PYBIND11_FINDPYTHON ON)
find_package(pybind11 CONFIG REQUIRED)

# Raptor native
add_subdirectory(native)

if(WIN32)
    set(PREMAKE_BIN "binaries/premake5.exe")
    set(PREMAKE_DEST "premake5.exe")
elseif(APPLE)
    if(CMAKE_SYSTEM_PROCESSOR MATCHES "arm64")
        set(PREMAKE_BIN "binaries/premake5-macosx")
    else()
        set(PREMAKE_BIN "binaries/premake5-macosx-x64")
        set(PREMAKE_DEST "premake5")
    endif()
else()
    set(PREMAKE_BIN "binaries/premake5-linux")
    set(PREMAKE_DEST "premake5")
endif()

# Install selected Premake binary
install(
    PROGRAMS "${CMAKE_SOURCE_DIR}/${PREMAKE_BIN}"
    DESTINATION "raptor/bin"
    RENAME "${PREMAKE_DEST}"
)

# Install Raptor's Python source
install(
    DIRECTORY "${CMAKE_SOURCE_DIR}/python/raptor"
    DESTINATION "."
    PATTERN "__pycache__" EXCLUDE
    PATTERN "*.pyc" EXCLUDE
)

# Install raptor_native
install(TARGETS raptor_native
    LIBRARY DESTINATION raptor
)
