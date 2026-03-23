#!/usr/bin/env python
"""
PyXplore Desktop - Launch Script
Run with conda RAG environment
"""

import subprocess
import sys
import os
from pathlib import Path

def main():
    # Get the directory of this script
    script_dir = Path(__file__).parent
    main_py = script_dir / "main.py"

    # Check if main.py exists
    if not main_py.exists():
        print(f"Error: main.py not found at {main_py}")
        sys.exit(1)

    # Run with conda RAG environment
    print("Starting PyXplore Desktop with RAG environment...")
    print()

    cmd = ["conda", "run", "-n", "RAG", "python", str(main_py)]

    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error running application: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nApplication closed.")
        sys.exit(0)

if __name__ == "__main__":
    main()
