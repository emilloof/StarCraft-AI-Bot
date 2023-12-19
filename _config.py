# The path to your SC2_x64 executable. This will be specific to your computer:
SC2_PATH = r"<path>\StarCraft II\Versions\Base<version_number>\SC2_x64.exe"
# Example : SC2_PATH = r"C:\Program Files (x86)\StarCraft II\Versions\Base84643\SC2_x64.exe"

MAPS = ["InterloperTest.SC2Map"]

# Give resources and allows fast building, good for testing
DEBUG_CHEATS = True
# Debug prints to console
DEBUG_CONSOLE = False
# Log information such as computation time per step
# Note: The game needs to end in order for the log file to be saved! You can surrender the game.
DEBUG_LOGS = False
# Text on screen showing build order and tasks
DEBUG_TEXT = False
# Units information displayed on screen
DEBUG_UNIT = False
# Enable visual debugger
DEBUG_VISUAL = False
# Enable scout debugger
DEBUG_SCOUT = True
# Enable Debug of David's Bayesian strategy
DEBUG_BAYESIAN = False
# Enable debugging (showing list of) enemies
DEBUG_ENEMIES = False

# How many frames between actions
FRAME_SKIP = 10

# Path to build order
BUILD_ORDER_PATH = "builds/labs_build_order"

# Use eriks chokepoints
USE_CHOKES = True
# Use Hannes pathfinding
USE_MOVE = False
# Use Vincent potential flow scouting
USE_PFSCOUT = True

# --- Scouting vars used by Vincent ---
TIME_KEEP_ENEMY = 200
TIME_KEEP_ENEMY_BUILDING = 600
FRAME_SKIP_SCOUT = 1 # How many frames between scout actions update
FRAME_CLEAR_CACHE = 10 # How many frames until we invalidate cache
OLD_ENEMIES_ENABLED = False
