"""Native 016 source contracts; never builds a player package."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools/art016'))
from verify import Native016
