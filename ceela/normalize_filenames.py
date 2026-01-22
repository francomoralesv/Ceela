#!/usr/bin/env python3
"""
Script para normalizar nombres de archivos de NFD (macOS) a NFC (Linux)
Convierte caracteres especiales descompuestos a su forma compuesta.
"""

import os
import unicodedata
from pathlib import Path


def normalize_filename(filename):
    """Normaliza un nombre de archivo de NFD a NFC"""
    return unicodedata.normalize('NFC', filename)


def rename_files_recursive(base_path, dry_run=True):
    """
    Renombra archivos y directorios recursivamente de NFD a NFC

    Args:
        base_path: Ruta base desde donde empezar
        dry_run: Si es True, solo muestra qué se haría sin realizar cambios
    """
    base_path = Path(base_path)
    changes = []

    # Recorrer desde lo más profundo hacia arriba para evitar problemas
    # con directorios que cambiarán de nombre
    for root, dirs, files in os.walk(base_path, topdown=False):
        root_path = Path(root)

        # Procesar archivos
        for filename in files:
            normalized = normalize_filename(filename)
            if normalized != filename:
                old_path = root_path / filename
                new_path = root_path / normalized
                changes.append((old_path, new_path))

                if not dry_run:
                    try:
                        old_path.rename(new_path)
                        print(f"✓ Renombrado: {old_path} -> {new_path}")
                    except Exception as e:
                        print(f"✗ Error renombrando {old_path}: {e}")
                else:
                    print(f"[DRY RUN] {old_path} -> {new_path}")

        # Procesar directorios
        for dirname in dirs:
            normalized = normalize_filename(dirname)
            if normalized != dirname:
                old_path = root_path / dirname
                new_path = root_path / normalized
                changes.append((old_path, new_path))

                if not dry_run:
                    try:
                        old_path.rename(new_path)
                        print(f"✓ Renombrado directorio: {old_path} -> {new_path}")
                    except Exception as e:
                        print(f"✗ Error renombrando directorio {old_path}: {e}")
                else:
                    print(f"[DRY RUN] {old_path} -> {new_path}")

    return changes


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description='Normaliza nombres de archivos de NFD (macOS) a NFC (Linux)'
    )
    parser.add_argument(
        'path',
        nargs='?',
        default='.',
        help='Ruta base a procesar (default: directorio actual)'
    )
    parser.add_argument(
        '--apply',
        action='store_true',
        help='Aplicar los cambios (sin esta opción solo muestra qué se haría)'
    )

    args = parser.parse_args()

    print(f"Analizando archivos en: {args.path}")
    print(f"Modo: {'APLICAR CAMBIOS' if args.apply else 'DRY RUN (solo mostrar)'}")
    print("-" * 80)

    changes = rename_files_recursive(args.path, dry_run=not args.apply)

    print("-" * 80)
    print(f"\nTotal de archivos/directorios a renombrar: {len(changes)}")

    if not args.apply and changes:
        print("\n⚠️  Para aplicar estos cambios, ejecuta el script con --apply")
        print(f"   python3 normalize_filenames.py {args.path} --apply")


if __name__ == '__main__':
    main()
