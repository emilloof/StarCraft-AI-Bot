# The path to your SC2_x64 executable. This will be specific to your computer:
SC2_PATH = r"<path>\StarCraft II\Versions\Base<version_number>\SC2_x64.exe"
# Example : SC2_PATH = r"C:\Program Files (x86)\StarCraft II\Versions\Base84643\SC2_x64.exe"

MAPS = ["InterloperTest.SC2Map"]

# Give resources and allows fast building, good for testing
DEBUG_CHEATS = False
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
DEBUG_VISUAL = True

# How many frames between actions
FRAME_SKIP = 10

# Path to build order
BUILD_ORDER_PATH = "builds/labs_build_order"
