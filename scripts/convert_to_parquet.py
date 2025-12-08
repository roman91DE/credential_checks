#!/usr/bin/env python
"""Convert txt data files to parquet format for efficient storage and loading."""

import pandas as pd
from pathlib import Path

# Setup paths
project = Path.cwd()
data_dir = project / "data"
pw_dir = data_dir / "passwords"
user_dir = data_dir / "usernames"


def convert_txt_to_parquet(input_dir: Path, column_name: str) -> None:
    """
    Convert all txt files in a directory to parquet format.

    Args:
        input_dir: Directory containing txt files
        column_name: Name for the data column in the parquet file
    """
    txt_files = list(input_dir.glob("*.txt"))
    if not txt_files:
        print(f"No txt files found in {input_dir}")
        return

    print(f"Converting {len(txt_files)} files from {input_dir.name}...")

    for txt_file in txt_files:
        try:
            # Read the txt file
            df = pd.read_fwf(
                txt_file, header=None, names=[column_name], dtype_backend="pyarrow"
            ).drop_duplicates()

            # Write to parquet with the same name but .parquet extension
            parquet_file = txt_file.with_suffix(".parquet")
            df.to_parquet(parquet_file, compression="snappy", index=False)

            # Get file sizes
            txt_size = txt_file.stat().st_size / (1024 * 1024)  # MB
            parquet_size = parquet_file.stat().st_size / (1024 * 1024)  # MB
            ratio = (1 - parquet_size / txt_size) * 100

            print(f"  ✓ {txt_file.name}: {txt_size:.1f}MB → {parquet_size:.1f}MB ({ratio:.1f}% smaller)")

        except Exception as e:
            print(f"  ✗ Error converting {txt_file.name}: {e}")


if __name__ == "__main__":
    print("Converting data files to parquet format...\n")

    convert_txt_to_parquet(pw_dir, "password")
    convert_txt_to_parquet(user_dir, "username")

    print("\n✅ Conversion complete!")
    print("\nYou can now delete the txt files if desired:")
    print(f"  rm {pw_dir}/*.txt")
    print(f"  rm {user_dir}/*.txt")
