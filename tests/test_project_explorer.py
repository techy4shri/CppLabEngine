import unittest
import tempfile
from pathlib import Path
from PyQt6.QtWidgets import QApplication

from src.cpplab.widgets.project_explorer import ProjectExplorer
from src.cpplab.core.project_config import ProjectConfig


class TestProjectExplorer(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Ensure a QApplication exists for widget creation
        cls._app = QApplication.instance() or QApplication([])

    def test_double_click_emits_full_path(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td) / "proj"
            (root / "src").mkdir(parents=True)

            rel = Path("src") / "main.cpp"
            full = root / rel
            full.write_text('int main() { return 0; }')

            pc = ProjectConfig(
                name="proj",
                root_path=root,
                language="cpp",
                standard="c++17",
                project_type="console",
                features={},
                files=[rel],
                main_file=rel,
                toolchain_preference="auto"
            )

            explorer = ProjectExplorer()
            captured = []
            explorer.file_double_clicked.connect(lambda s: captured.append(s))

            explorer.load_project(pc)

            root_item = explorer.topLevelItem(0)
            self.assertIsNotNone(root_item)
            file_item = root_item.child(0)
            self.assertIsNotNone(file_item)

            # Call handler directly
            explorer._on_item_double_clicked(file_item, 0)

            self.assertEqual(len(captured), 1)
            self.assertEqual(captured[0], str(full))


if __name__ == "__main__":
    unittest.main()
