import random
from game import Game, Move, Player

from mcts import MCTS
from mcts_ba import MCTS_BA

class RandomPlayer(Player):
    def __init__(self) -> None:
        super().__init__()

    def make_move(self, game: 'Game') -> tuple[tuple[int, int], Move]:
        from_pos = (random.randint(0, 4), random.randint(0, 4))
        move = random.choice([Move.TOP, Move.BOTTOM, Move.LEFT, Move.RIGHT])
        return from_pos, move


class Agent_MCTS(Player):
    def __init__(self) -> None:
        super().__init__()
        self.mcts = MCTS()

    def make_move(self, game: Game) -> tuple[int, Move]:
        self.mcts.search(5, game)
        num_rollouts, run_time = self.mcts.statistics()
        print("[CR] Statistics: ", num_rollouts, "rollouts in", run_time, "seconds")
        tile, slide = self.mcts.best_move()
        return tile, slide
    
class MyPlayer(Player):
    def __init__(self, seconds_to_search = 3) -> None:
        super().__init__()
        self.mcts = MCTS_BA()
        self.seconds = seconds_to_search
    
    def make_move(self, game: Game) -> tuple[int, Move]:
        self.mcts.search(self.seconds, game)   #100%vsRnd@3sec, 90%vsMCTSAgent@5sec, HumanLvl@30sec
        num_rollouts, run_time = self.mcts.statistics()
        print("[BA] Statistics: ", num_rollouts, "rollouts in", run_time, "seconds")
        tile, slide = self.mcts.best_move()
        return tile, slide

class HumanPlayer(Player):
    def __init__(self) -> None:
        super().__init__()
        self.move_dict = {'L' : Move.LEFT, 'R' : Move.RIGHT, 'T' : Move.TOP, 'B' : Move.BOTTOM}

    def make_move(self, game) -> tuple[int, Move]:
        move = input("Make a move <<column[0-4] row[0-4]>> <<slide[L,R,T,B]>>: ").split(sep=' ')
        col = int(move[0])
        row = int(move[1])
        slide = self.move_dict[move[2]]
        return (col,row), slide


if __name__ == '__main__':
    games_to_play = 5
    seconds_for_agent = 3
    
    wins_as_first = 0
    wins_as_second = 0

    for ngame in range(games_to_play):
        print("Game",ngame+1," (Agent starts first and play with X)")
        g = Game()
        g.print()
        player1 = MyPlayer(seconds_for_agent)
        player2 = RandomPlayer()
        winner = g.play(player1, player2)
        print("Final board:")
        g.print()
        print(f"Winner: Player {winner}")
        if not winner:
            wins_as_first += 1

    for ngame in range(games_to_play):
        print("Game",ngame+1," (Agent starts second and play with O)")
        g = Game()
        g.print()
        player1 = RandomPlayer()
        player2 = MyPlayer(seconds_for_agent)
        winner = g.play(player1, player2)
        print("Final board:")
        g.print()
        print(f"Winner: Player {winner}")
        if winner:
            wins_as_second += 1

    print(f"Agent won {wins_as_first/games_to_play*100}% of games as first and {wins_as_second/games_to_play*100}% of games as second!")
