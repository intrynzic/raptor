@echo off

echo Running pybind11-stubgen...
uv run pybind11-stubgen raptor.native -o python
echo.
