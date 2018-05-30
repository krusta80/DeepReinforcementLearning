from agent import Agent
from game import Game

number_of_games = 1000
agents = []
outcomes = []
stats = {}
winner = -1

for i in range(0, 2):
    agents.append(Agent("Player " + str(i+1)))

game = Game(agents)

while number_of_games > 0:
    if number_of_games % 1000 == 1:
        print("==== NEW GAME ====")
        print(number_of_games)

    game.reset()
    outcomes.append(game.play_until_end())
    winner = game.get_winner()
    if not winner in stats:
        stats[winner] = 0
    stats[winner] += 1
    number_of_games -= 1

print(outcomes)
print(stats)
