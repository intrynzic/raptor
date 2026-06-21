cmake_minimum_required(VERSION 3.25)
project(raptor)

set(CMAKE_CXX_STANDARD 23)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Find the right Python environment
#
# Priority:
#   1. Already set by scikit-build-core (temp build env) — leave it alone
#   2. Project .venv exists — use it directly, no subprocess needed
#   3. Ask uv — works when .venv doesn't exist yet but uv is on PATH
#   4. Fall back to whatever CMake finds on PATH
if(NOT DEFINED Python3_EXECUTABLE)
    # Check for .venv in the project root first
    if(WIN32)
        set(_venv_python "${CMAKE_SOURCE_DIR}/.venv/Scripts/python.exe")
    else()
        set(_venv_python "${CMAKE_SOURCE_DIR}/.venv/bin/python")
    endif()

    if(EXISTS "${_venv_python}")
        set(Python3_EXECUTABLE "${_venv_python}" CACHE FILEPATH "Python from project .venv" FORCE)
        message(STATUS "Python (from .venv): ${Python3_EXECUTABLE}")
    else()
        execute_process(
            COMMAND uv run python -c "import sys; print(sys.executable)"
            WORKING_DIRECTORY "${CMAKE_SOURCE_DIR}"
            OUTPUT_VARIABLE _uv_python
            OUTPUT_STRIP_TRAILING_WHITESPACE
            RESULT_VARIABLE _uv_result
        )
        if(_uv_result EQUAL 0)
            set(Python3_EXECUTABLE "${_uv_python}" CACHE FILEPATH "Python from uv" FORCE)
            message(STATUS "Python (from uv): ${Python3_EXECUTABLE}")
        else()
            message(WARNING "uv not found and no .venv present — CMake will search PATH")
        endif()
    endif()
endif()

find_package(Python3 REQUIRED COMPONENTS Interpreter Development.Module)

# Configure PyBind11
#
# Prefer the pybind11 installed in the active Python environment so that
# standalone CMake and scikit-build-core both find the same copy.
if(NOT DEFINED pybind11_DIR)
    execute_process(
        COMMAND "${Python3_EXECUTABLE}" -c
                "import pybind11; print(pybind11.get_cmake_dir())"
        OUTPUT_VARIABLE _pybind11_cmake_dir
        OUTPUT_STRIP_TRAILING_WHITESPACE
        RESULT_VARIABLE _pybind11_result
    )
    if(NOT _pybind11_result EQUAL 0)
        message(FATAL_ERROR
            "pybind11 not found in Python environment: ${Python3_EXECUTABLE}\n"
            "Run: uv sync  (pybind11 must be under [build-system] requires in pyproject.toml)"
        )
    endif()
    set(pybind11_DIR "${_pybind11_cmake_dir}")
    message(STATUS "pybind11 cmake dir: ${pybind11_DIR}")
endif()

set(PYBIND11_FINDPYTHON ON)
find_package(pybind11 CONFIG REQUIRED)

# Subdirectories
add_subdirectory(native)

# TODO: Remove Premake binary selection
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
