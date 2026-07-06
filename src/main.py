#!/usr/bin/env python3
"""Точка входа в программу"""

import sys
import click


def main():
    """Запуск программы"""
    # Если запуск с аргументами → CLI режим
    if len(sys.argv) > 1:
        from src.cli import cli
        cli()
    else:
        # Без аргументов → GUI (если не в Docker)
        try:
            from src.gui import main as gui_main
            gui_main()
        except ImportError:
            # Если нет графики → показываем help
            from src.cli import cli
            print("⚠️  Графический интерфейс недоступен, используйте CLI режим")
            print("Примеры:")
            print("  python -m src.main init")
            print("  python -m src.main add --login test --generate")
            print("  python -m src.main list")
            sys.exit(1)


if __name__ == '__main__':
    main()