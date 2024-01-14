from library import Race
from run_sc2 import run_sc2
from agents.basic_agent import BasicAgent
from agents.noop_agent import NoOpAgent
from config import MAPS
import sys

sys.path.append(".")  # Needed to find library if running from terminal

if __name__ == "__main__":
    run_sc2(
        bot1=BasicAgent(),
        race1=Race.Terran,
        maps=MAPS,
        maps=MAPS,
        real_time=False) 