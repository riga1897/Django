#!/usr/bin/env python
import subprocess
import sys


def run_command(cmd: list[str], description: str) -> bool:
    print(f"\n{'='*60}")
    print(f"  {description}")
    print(f"{'='*60}")
    result = subprocess.run(cmd, capture_output=False)
    return result.returncode == 0


def main() -> None:
    targets = ["apps/", "config/", "tests/"]
    
    steps = [
        (
            ["ruff", "check", "--fix"] + targets,
            "🔧 Ruff: проверка и автофикс кода"
        ),
        (
            ["isort"] + targets,
            "🔀 Isort: автоформатирование импортов"
        ),
        (
            ["ruff", "format"] + targets,
            "📝 Ruff: форматирование кода (кроме импортов)"
        ),
        (
            ["black", "--check"] + targets,
            "⚫ Black: проверка форматирования"
        ),
        (
            ["isort", "--check-only"] + targets,
            "✓ Isort: финальная проверка импортов"
        ),
        (
            ["flake8"] + targets,
            "🔍 Flake8: проверка стиля кода"
        ),
        (
            ["mypy", "."],
            "🎯 Mypy: проверка типов"
        ),
    ]
    
    all_passed = True
    for cmd, desc in steps:
        if not run_command(cmd, desc):
            all_passed = False
    
    print(f"\n{'='*60}")
    if all_passed:
        print("✅ Все проверки пройдены успешно!")
        print(f"{'='*60}\n")
        sys.exit(0)
    else:
        print("❌ Обнаружены проблемы в коде")
        print(f"{'='*60}\n")
        sys.exit(1)


if __name__ == "__main__":
    main()
