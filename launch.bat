@echo off
REM Launcher script for CppLab IDE
REM Ensure the local `src` directory is on PYTHONPATH so `cpplab` can be imported
set PYTHONPATH=%CD%\src;%PYTHONPATH%
python -m cpplab.main
