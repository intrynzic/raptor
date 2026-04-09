cmake_minimum_required(VERSION 3.15)
project(raptor)

if(WIN32)
    set(PREMAKE_BIN "bin/premake5.exe")
    set(PREMAKE_DEST "premake5.exe")
else()
    set(PREMAKE_BIN "bin/premake5")
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
    DIRECTORY "${CMAKE_SOURCE_DIR}/src/raptor"
    DESTINATION "."
    PATTERN "__pycache__" EXCLUDE
    PATTERN "*.pyc" EXCLUDE
)
