from pathlib import Path

from evidencebench.cli import main


def make_inputs(tmp_path: Path) -> tuple[Path, Path, Path]:
    source = tmp_path / "source.md"
    source.write_text("# Guide\n\nThe item is blue.\n", encoding="utf-8")
    question = tmp_path / "question.txt"
    question.write_text("What color is the item?", encoding="utf-8")
    answer = tmp_path / "answer.txt"
    answer.write_text("The item is blue.", encoding="utf-8")
    return source, question, answer


def test_cli_evaluate_json_and_version(tmp_path: Path, capsys) -> None:
    source, question, answer = make_inputs(tmp_path)
    assert main(["version"]) == 0
    assert capsys.readouterr().out.strip() == "0.1.0"
    assert (
        main(
            [
                "evaluate",
                "--sources",
                str(source),
                "--question",
                str(question),
                "--answer",
                str(answer),
                "--format",
                "json",
            ]
        )
        == 0
    )
    assert '"SUPPORTED"' in capsys.readouterr().out


def test_cli_assert_returns_nonzero_for_failed_threshold(tmp_path: Path, capsys) -> None:
    source, question, answer = make_inputs(tmp_path)
    answer.write_text("The moon is made of cheese.", encoding="utf-8")
    code = main(
        [
            "assert",
            "--sources",
            str(source),
            "--question",
            str(question),
            "--answer",
            str(answer),
            "--minimum-evidence-coverage",
            "1.0",
        ]
    )
    assert code == 1
    assert "Threshold failures" in capsys.readouterr().err


def test_cli_missing_input_returns_two(tmp_path: Path, capsys) -> None:
    code = main(
        [
            "evaluate",
            "--sources",
            str(tmp_path),
            "--question",
            "missing",
            "--answer",
            "missing",
        ]
    )
    assert code == 2
    assert "No TXT" in capsys.readouterr().err
