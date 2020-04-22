from ladder import run_ladder_game
from Paul import PaulBot
from sc2.player import Bot

dummy_bot = PaulBot()
race = dummy_bot.my_race
protoss_bot = Bot(race, dummy_bot)


def main():
    # Ladder game started by LadderManager
    print("Starting ladder game...")
    result, opponentid = run_ladder_game(protoss_bot)
    print(result, " against opponent ", opponentid)


if __name__ == '__main__':
    main()
