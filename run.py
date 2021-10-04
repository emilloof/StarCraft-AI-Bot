from library import Coordinator, Race, create_participants
from agents.basic_agent import BasicAgent
import  argparse

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--GamePort', type=int, nargs="?", help='Game port')

    args, unknown = parser.parse_known_args()

    coordinator = Coordinator("/root/StarCraftII/Versions/Base75689/SC2_x64")
    bot1 = BasicAgent() # Initialize the bot
    participant_1 = create_participants(Race.Terran, bot1)
    coordinator.set_real_time(False)
    coordinator.set_participants([participant_1])
    coordinator.connect(args.GamePort) # Connect to the game
    coordinator.join_game()

    while not coordinator.all_games_ended():  # The coordinator returns false even if the game is not finished
        coordinator.update()


if __name__ == "__main__":
   main()
