import sys
from pathlib import Path
import importlib.util
import pytest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


# Skip the entire suite when optional heavy dependencies are missing.
def _is_available(mod: str) -> bool:
    try:
        return importlib.util.find_spec(mod) is not None
    except ModuleNotFoundError:
        return False


# Historically the test-suite depended on Playwright which is quite heavy. The
# current tests do not require it so we avoid failing when the optional package
# is missing.
