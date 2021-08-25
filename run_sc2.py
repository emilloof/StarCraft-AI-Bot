from library import Coordinator, Race, create_participants, create_computer, Difficulty, IDABot
from config import SC2_PATH, DEBUG_LOGS
from typing import Optional
import os
import random


def run_sc2(bot1: Optional[IDABot] = None,
            race1: Race = Race.Random,
            difficulty1: Difficulty = Difficulty.Easy,
            bot2: Optional[IDABot] = None,
            race2: Race = Race.Random,
            difficulty2: Difficulty = Difficulty.Easy,
            maps: list[str] = None,
            real_time: bool = False
            ) -> tuple[Optional[IDABot], Optional[IDABot]]:
    """
    Runs a game of StarCraft II with two players.

    :param bot1: Player 1 bot. If no bot is sent in, player 1 will be played by the built in computer AI.
    :param race1: The race of player 1.
    :param difficulty1: The difficulty of player 1. Only applicable if player 1 is built in computer AI.
    :param bot2: Player 2 bot. If no bot is sent in, player 2 will be played by the built in computer AI.
    :param race2: The race of player 2.
    :param difficulty2: The difficulty of player 2. Only applicable if player 2 is built in computer AI.
    :param maps: A list of maps from which a map will be randomly chosen to play on.
    :param real_time: Sets whether the game should be played in real time or not.
    :return: Both bots, so that their internal variables can be accessed after the game ends.
    """
    if maps is None:
        maps = ["InterloperTest.SC2Map"]

    coordinator = Coordinator(SC2_PATH)

    participant_1 = create_participants(race1, bot1) if bot1 else create_computer(race1, difficulty1)
    participant_2 = create_participants(race2, bot2) if bot2 else create_computer(race2, difficulty2)

    coordinator.set_real_time(real_time)
    coordinator.set_participants([participant_1, participant_2])
    coordinator.launch_starcraft()

    path = os.path.join(os.getcwd(), "maps", random.choice(maps))
    coordinator.start_game(path)

    while coordinator.update():
        pass

    if bot1 and DEBUG_LOGS:
        bot1.logger.save()

    return bot1, bot2
