# Project configuration: metadata, persistence, and project creation.

import json
from pathlib import Path
from dataclasses import dataclass, field
from typing import Literal


@dataclass
class ProjectConfig: #normalization for this to always be path bug fixed
    name: str
    root_path: Path
    language: Literal["c", "cpp"]
    standard: str
    project_type: Literal["console", "graphics"]
    features: dict[str, bool]
    files: list[Path]
    main_file: Path
    toolchain_preference: str = "auto"  # "auto", "mingw64", "mingw32"
    
    @property
    def graphics(self) -> bool:
        """Convenience property for graphics feature."""
        return self.features.get("graphics", False)
    
    @property
    def openmp(self) -> bool:
        """Convenience property for OpenMP feature."""
        return self.features.get("openmp", False)
    
    def get_main_file_path(self) -> Path:
        return self.root_path / self.main_file
    
    def get_config_file_path(self) -> Path:
        return self.root_path / ".cpplab.json"
    
    def get_output_executable(self) -> Path:
        return self.root_path / "build" / f"{self.name}.exe"
    
    @staticmethod
    def load(project_dir: Path | str) -> "ProjectConfig":
        root = Path(project_dir)
        config_path = root / ".cpplab.json"
        
        with open(config_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        return ProjectConfig(
            name=data["name"],
            root_path=root,
            language=data.get("language", "cpp"),
            standard=data.get("standard", "c++17"),
            project_type=data.get("project_type", "console"),
            features=data.get("features", {}),
            files=[Path(p) for p in data.get("files", [])],
            main_file=Path(data.get("main_file", "src/main.cpp")),
            toolchain_preference=data.get("toolchain_preference", "auto")
        )
    
    def save(self) -> None:
        config_path = self.get_config_file_path()
        
        data = {
            "name": self.name,
            "language": self.language,
            "standard": self.standard,
            "project_type": self.project_type,
            "features": self.features,
            "files": [str(p) for p in self.files],
            "main_file": str(self.main_file),
            "toolchain_preference": self.toolchain_preference
        }
        
        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)


def create_new_project(
    name: str,
    parent_dir: Path | str,
    language: Literal["c", "cpp"],
    standard: str,
    project_type: Literal["console", "graphics"],
    enable_graphics: bool = False,
    enable_openmp: bool = False
) -> ProjectConfig:
    root_path = Path(parent_dir) / name
    root_path.mkdir(parents=True, exist_ok=True)
    
    src_dir = root_path / "src"
    src_dir.mkdir(exist_ok=True)
    
    build_dir = root_path / "build"
    build_dir.mkdir(exist_ok=True)
    
    if project_type == "graphics":
        enable_graphics = True
        enable_openmp = False
    
    if enable_graphics and project_type == "console":
        enable_openmp = False
    
    features = {
        "graphics": enable_graphics,
        "openmp": enable_openmp
    }
    
    ext = ".c" if language == "c" else ".cpp"
    main_file = Path(f"src/main{ext}")
    main_file_path = root_path / main_file
    
    template = _generate_main_template(language, enable_graphics, enable_openmp)
    with open(main_file_path, "w", encoding="utf-8") as f:
        f.write(template)
    
    config = ProjectConfig(
        name=name,
        root_path=root_path,
        language=language,
        standard=standard,
        project_type=project_type,
        features=features,
        files=[main_file],
        main_file=main_file,
        toolchain_preference="auto"
    )
    
    config.save()
    return config


def _generate_main_template(language: str, graphics: bool, openmp: bool) -> str:
    if language == "c":
        if graphics:
            return """#include <graphics.h>
#include <stdio.h>

int main() {
    int gd = DETECT, gm;
    initgraph(&gd, &gm, (char*)"");
    
    outtextxy(250, 200, (char*)"Hello from CppLab!");
    circle(300, 250, 50);
    
    getch();
    closegraph();
    return 0;
}
"""
        elif openmp:
            return """#include <stdio.h>
#include <omp.h>

int main() {
    printf("Hello from CppLab!\\n");
    
    #pragma omp parallel
    {
        int tid = omp_get_thread_num();
        printf("Thread %d says hi!\\n", tid);
    }
    
    return 0;
}
"""
        else:
            return """#include <stdio.h>

int main() {
    printf("Hello from CppLab!\\n");
    return 0;
}
"""
    else:
        if graphics:
            return """#include <graphics.h>
#include <iostream>

int main() {
    int gd = DETECT, gm;
    initgraph(&gd, &gm, (char*)"");
    
    outtextxy(250, 200, (char*)"Hello from CppLab!");
    circle(300, 250, 50);
    
    getch();
    closegraph();
    return 0;
}
"""
        elif openmp:
            return """#include <iostream>
#include <omp.h>

int main() {
    std::cout << "Hello from CppLab!" << std::endl;
    
    #pragma omp parallel
    {
        int tid = omp_get_thread_num();
        #pragma omp critical
        std::cout << "Thread " << tid << " says hi!" << std::endl;
    }
    
    return 0;
}
"""
        else:
            return """#include <iostream>

int main() {
    std::cout << "Hello from CppLab!" << std::endl;
    return 0;
}
"""
