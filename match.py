from game import Game
from funcs import playMatchesBetweenVersions
import loggers as lg

env = Game()
playMatchesBetweenVersions(env, 1, -1, 33, 1, lg.logger_tourney, 0)
