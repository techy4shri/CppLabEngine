"""
CppLabEngine - A dedicated C/C++ IDE for college students
"""

from setuptools import setup, find_packages

setup(
    name="cpplab-ide",
    version="1.0.0",
    description="A dedicated C/C++ IDE with graphics.h and OpenMP support",
    author="CppLab Team",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    package_data={
        "cpplab": ["ui/*.ui"],
    },
    install_requires=[
        "PyQt6>=6.6.0",
    ],
    entry_points={
        "console_scripts": [
            "cpplab=cpplab.main:main",
        ],
    },
    python_requires=">=3.13",
)
