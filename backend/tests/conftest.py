import sys
from pathlib import Path

# Allow `import supervision`, `import db_config` when running pytest from anywhere.
BACKEND_DIR = Path(__file__).resolve().parent.parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))
