from library import Race, Difficulty
from run_sc2 import run_sc2
from agents.basic_agent import BasicAgent
from agents.noop_agent import NoOpAgent
from config import MAPS
import sys

sys.path.append(".")  # Needed to find library if running from terminal

if __name__ == "__main__":
    bot2 = BasicAgent()
    bot2.use_scout = False
    run_sc2(
        bot1=BasicAgent(),
        race1=Race.Terran,
        race2=Race.Protoss,
        difficulty1=Difficulty.CheatVision,
        maps=MAPS,
        real_time=False)

 
 