from pathlib import Path

from tools.file_reader_tool import read_submission_files


def test_read_submission_files_returns_expected_dict():
    submissions_dir = Path("tests/temp_submissions")
    submissions_dir.mkdir(parents=True, exist_ok=True)

    try:
        # Valid files
        (submissions_dir / "STU001.txt").write_text(
            "This is student 1 submission.", encoding="utf-8"
        )
        (submissions_dir / "STU002.md").write_text(
            "# Essay\nStudent 2 answer content.", encoding="utf-8"
        )
        (submissions_dir / "STU003.py").write_text(
            "print('student 3 code submission')", encoding="utf-8"
        )

        # Ignored files
        (submissions_dir / "notes.csv").write_text("id,score", encoding="utf-8")
        (submissions_dir / "empty.txt").write_text("   ", encoding="utf-8")

        result = read_submission_files(str(submissions_dir))

        assert isinstance(result, dict)
        assert set(result.keys()) == {"STU001", "STU002", "STU003"}
        assert all(value.strip() for value in result.values())

        print("SUCCESS: File Reader tool returned expected student dictionary.")

    finally:
        for file_path in submissions_dir.glob("*"):
            if file_path.is_file():
                file_path.unlink()
        submissions_dir.rmdir()


if __name__ == "__main__":
    test_read_submission_files_returns_expected_dict()
