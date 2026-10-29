#!/usr/bin/env python3
"""Container entry point: dispatch.py <venture|hospitality|career> ENVELOPE [crew args...]"""
import runpy
import sys
from pathlib import Path

CREWS = {"venture", "hospitality", "career"}

if len(sys.argv) < 2 or sys.argv[1] not in CREWS:
    print(f"usage: dispatch.py <{'|'.join(sorted(CREWS))}> ENVELOPE.json [--out DIR] "
          "[--input-dir DIR] [--dry-run]", file=sys.stderr)
    sys.exit(2)
crew = sys.argv.pop(1)
script = Path(__file__).resolve().parent / f"{crew}.py"
sys.argv[0] = str(script)
sys.path.insert(0, str(script.parent))
runpy.run_path(str(script), run_name="__main__")
