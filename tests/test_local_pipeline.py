import os
import py_compile
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

import main as pipeline_main


def test_phase_directories_exist():
    expected = [
        "0_Dataset",
        "1_Veri_Manipülasyonu",
        "2_Ozellik_Muhendisligi_ve_Secimi",
        "3_Model_Egitimi_ve_Degerlendirme",
    ]
    for folder in expected:
        assert os.path.isdir(os.path.join(BASE_DIR, folder)), f"Missing folder: {folder}"


def test_sorted_scripts_discovery():
    p1 = os.path.join(BASE_DIR, "1_Veri_Manipülasyonu", "Python_Kodlari")
    scripts = pipeline_main.get_sorted_scripts(p1)
    assert len(scripts) > 0, "Phase 1 should contain Python scripts"


def test_all_python_files_compile():
    errors = []
    for root, dirs, files in os.walk(BASE_DIR):
        dirs[:] = [d for d in dirs if d not in {".git", "__pycache__", ".venv", "tests"}]
        for f in files:
            if f.endswith(".py"):
                fp = os.path.join(root, f)
                try:
                    py_compile.compile(fp, doraise=True)
                except Exception as exc:
                    errors.append(f"{fp}: {exc}")
    assert not errors, f"Syntax errors found: {errors}"
