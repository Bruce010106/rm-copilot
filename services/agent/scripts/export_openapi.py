"""Write the FastAPI OpenAPI schema to apps/web/openapi.json (input for frontend type generation).

Usage (from services/agent):  python scripts/export_openapi.py
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.config import REPO_ROOT  # noqa: E402
from app.main import app  # noqa: E402

OUT = REPO_ROOT / "apps" / "web" / "openapi.json"

if __name__ == "__main__":
    OUT.write_text(
        json.dumps(app.openapi(), ensure_ascii=False, indent=2, sort_keys=True) + "\n", "utf-8"
    )
    print(f"wrote {OUT}")
