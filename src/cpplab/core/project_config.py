# Project configuration data model and persistence.

import json
import os
from pathlib import Path
from dataclasses import dataclass, asdict, field
from typing import List, Dict, Literal


@dataclass
class ProjectFeatures:
    graphics: bool = False
    openmp: bool = False


@dataclass
class ProjectConfig:
    name: str
    path: str
    language: Literal["c", "cpp"] = "cpp"
    standard: str = "c++17"
    project_type: Literal["console", "graphics"] = "console"
    features: ProjectFeatures = field(default_factory=ProjectFeatures)
    files: List[str] = field(default_factory=list)
    main_file: str = ""

    @staticmethod
    def load(project_dir: str) -> "ProjectConfig":
        config_path = Path(project_dir) / ".cpplab.json"
        with open(config_path, "r") as f:
            data = json.load(f)
        features = ProjectFeatures(**data.get("features", {}))
        return ProjectConfig(
            name=data["name"],
            path=data["path"],
            language=data.get("language", "cpp"),
            standard=data.get("standard", "c++17"),
            project_type=data.get("project_type", "console"),
            features=features,
            files=data.get("files", []),
            main_file=data.get("main_file", "")
        )

    def save(self) -> None:
        config_path = Path(self.path) / ".cpplab.json"
        data = {
            "name": self.name,
            "path": self.path,
            "language": self.language,
            "standard": self.standard,
            "project_type": self.project_type,
            "features": asdict(self.features),
            "files": self.files,
            "main_file": self.main_file
        }
        with open(config_path, "w") as f:
            json.dump(data, f, indent=2)

    def get_output_executable(self) -> str:
        return str(Path(self.path) / "build" / f"{self.name}.exe")


def create_new_project(
    name: str,
    parent_dir: str,
    language: Literal["c", "cpp"],
    standard: str,
    project_type: Literal["console", "graphics"],
    enable_graphics: bool = False,
    enable_openmp: bool = False
) -> ProjectConfig:
    project_path = Path(parent_dir) / name
    project_path.mkdir(parents=True, exist_ok=True)
    
    src_dir = project_path / "src"
    src_dir.mkdir(exist_ok=True)
    
    build_dir = project_path / "build"
    build_dir.mkdir(exist_ok=True)
    
    if project_type == "graphics":
        enable_graphics = True
        enable_openmp = False
    
    if enable_graphics and project_type == "console":
        enable_openmp = False
    
    features = ProjectFeatures(graphics=enable_graphics, openmp=enable_openmp)
    
    ext = ".c" if language == "c" else ".cpp"
    main_file = f"src/main{ext}"
    main_path = project_path / main_file
    
    template = _generate_main_template(language, enable_graphics, enable_openmp)
    with open(main_path, "w") as f:
        f.write(template)
    
    config = ProjectConfig(
        name=name,
        path=str(project_path),
        language=language,
        standard=standard,
        project_type=project_type,
        features=features,
        files=[main_file],
        main_file=main_file
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
    initgraph(&gd, &gm, "");
    
    outtextxy(250, 200, "Hello from CppLab!");
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
    initgraph(&gd, &gm, "");
    
    outtextxy(250, 200, "Hello from CppLab!");
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
