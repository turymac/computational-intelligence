import random
import time
from copy import deepcopy
from math import sqrt, log
from util_cr import get_legal_moves

from mock_game import MockGame


class Node:
    def __init__(self, board, move, parent, to_move):
        self.board_state = board        # State of the game
        self.move = move                # Move
        self.parent = parent            # Parent Node
        self.N = 0                      # Number of visit to Node
        self.Q = 0                      # Cumulative sum of rewards
        self.children = {}              # Children nodes dict <Board>:<Node>
        self.to_move = to_move          # Id of player who has to move
        
    def __str__(self):
        return f"board_state: \n {self.board_state} \n move: {self.move} \n from: {repr(self.parent)} \n to_move: {self.to_move} \n {len(self.children)} children \n N: {self.N} \n Q: {self.Q}"

    def add_children(self, children: dict) -> None:
        for child in children:
            self.children[str(child.board_state)] = child    # <Board>:<Node>

    def value(self, explore: float = sqrt(2)):
        if self.N == 0:
            return 0 if explore == 0 else float('inf')
        else:
            return self.Q / self.N + explore * sqrt(log(self.parent.N) / self.N) # Balancing exploitation and exploration


class MCTS:
    def __init__(self, game=MockGame()):
        self.game = deepcopy(game)                              # Playground for simulating games
        self.root = Node(self.game.get_board(),None,None,None)  # Root node
        self.agent_id = -1                                      # Agent id
        self.sign = {-1: '_', 0:'\U0000274C', 1:'\U00002B55'}   # Just for nice print
        self.run_time = 0                                       # To compute statistics
        self.num_rollouts = 0                                   # To compute statistics

    def find_new_root(self, board, player_id): # Update the root state after every opponent move
        
        if len(self.root.children) and str(board) in self.root.children:
            print(self.sign[self.agent_id],"[CR] Thinking...")
            self.root = self.root.children[str(board)]
        
        else:   # First time we play
            self.root = Node(board, None, None, player_id)
            self.agent_id = player_id
            print("[CR] plays with",self.sign[self.agent_id])

    def select_node(self) -> tuple: # Select a node to start simulation from
        node = self.root

        while len(node.children) != 0:
            children = node.children.values()
            max_value = max(children, key=lambda n: n.value()).value()
            max_nodes = [n for n in children if n.value() == max_value]

            node = random.choice(max_nodes)

            if node.N == 0: # Every node will be explored at least one time
                return node

        if self.expand(node):
            node = random.choice(list(node.children.values()))
        return node

    def expand(self, parent: Node) -> bool:

        if self.game.check_terminal(parent.board_state) != -1:    # Cannot expand a terminal state
            return False


        # Generate all the children for the given node
        children = [Node(self.game.apply(deepcopy(parent.board_state), move, parent.to_move), move, parent, 1-parent.to_move) for move in get_legal_moves(deepcopy(parent.board_state), parent.to_move)] #WORK 

        parent.add_children(children)

        return True

    def roll_out(self, state, player_id) -> int:
        return self.game.simulate(state, player_id) # Random simulation srarting from selected node

    def back_propagate(self, node: Node, outcome: int) -> None:

        reward = 1 if outcome == self.agent_id else -1

        while node is not None: # Backpropagate the reward through the tree
            node.N += 1
            node.Q += reward
            node = node.parent

            reward = -1 * reward

    def search(self, time_limit: int, game):
        start_time = time.process_time()
        num_rollouts = 0
        player_id = game.get_current_player()
        board = game.get_board()
        self.find_new_root(board,player_id) # Update the root node

        while time.process_time() - start_time < time_limit:    # While we time to explore
            node = self.select_node()                                   # SELECT (and EXPAND)
            outcome = self.roll_out(node.board_state, node.to_move)     # SIMULATE
            self.back_propagate(node, outcome)                          # BACKPROPAGATE
            num_rollouts += 1

        run_time = time.process_time() - start_time
        self.run_time = run_time
        self.num_rollouts = num_rollouts

    def best_move(self):
        if self.game.check_terminal(self.root.board_state) != -1:
            return -1

        max_value = max(self.root.children.values(), key=lambda n: n.Q).Q
        max_nodes = [n for n in self.root.children.values() if n.Q == max_value]
        best_child = random.choice(max_nodes)   # Return the best move from the root state
        
        self.root = best_child  # Moves the root
        
        return best_child.move

    def statistics(self) -> tuple:
        return self.num_rollouts, self.run_time
