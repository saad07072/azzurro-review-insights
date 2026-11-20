import os
import sys
from pathlib import Path

# Add project root to sys.path so app modules are resolvable on Vercel
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from app.api import app
