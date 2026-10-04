"""Vercel adapter using the same Atlas source as local runs."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "atlas-ai"))
from atlas_backend.http import handler
