# Quixo - Salvatore Latino s314872

## Strategy adopted

Given the very large number of states of the game (ca. 3^23) Monte Carlo Tree Search is implemented and two different Agents are proposed.

## Agents

### Agent_MCTS

Here, a simple but effective MCTS strategy is implemented, representing game states as node of a tree where the moving root is the current state of the game while the children of a node are the states reachable in one move.

#### Node data structure

Each node is defined as follows
```
self.board_state = board        # State of the game
self.move = move                # Move
self.parent = parent            # Parent Node
self.N = 0                      # Number of visit to Node
self.Q = 0                      # Cumulative sum of rewards
self.children = {}              # Children nodes dict <Board>:<Node>
self.to_move = to_move          # Id of player who has to move
```

##### Value function (*f1*)

To determine which node explore the following function is adopted, trying to balance exploitation (i.e. to have a value of that node more and more accurate) and exploration of different nodes (i.e. a little explored node will be valued a bit more in order to be picked)
```
def value(self, explore: float = sqrt(2)):
  if self.N == 0:
    return 0 if explore == 0 else float('inf')
  else:
    return self.Q / self.N + explore * sqrt(log(self.parent.N) / self.N)
```

Agent receive an arbitrary amount of time for each move and the algorithm starts:

```
 while time.process_time() - start_time < time_limit:                     # While we have time to explore
            node = self.select_node()                                     # SELECT (and EXPAND)
            outcome = self.roll_out(node.board_state, node.to_move)       # SIMULATE
            self.back_propagate(node, outcome)                            # BACKPROPAGATE
```

* SELECT: Starting from the root of the tree a node is selected according to *f1* and EXPANDED (i.e. all of the children nodes are generated and attached to it)

* SIMULATE: Starting from the selected node a random simulation is performed and the winner is retrieved

* BACKPROPAGATE: A reward is backpropagated back to the root node

#### MCTS Agent Files

* mcts.py: Implementation of the Monte Carlo Tree Search algorithm
* mock_game.py: Playground game instance for random simulations needed
* util_cr.py:
  - ACCEPTABLE: Representing tiles in (column,row) coordinates belonging to the border of the board, the only ones allowed to be taken or moved
  - SLIDE_FOR_TILE: Mapping between tiles in (column,row) coordinates and allowed moves for specific position on the board
  - get_legal_moves(board, agent_id): Function computing all the possible moves from the given board for the given player

#### Agent MCTS Results

Agent doesn't need a training and with just 5 seconds per move is able to obtain a 100% win rate against a random player

### Evolved Agent_MCTS (MyPlayer)

Taking inspiration from "Quixo is solved" [https://arxiv.org/abs/2007.15895] an alternative data structure is proposed for the personal Game instance of the agent used for the simulated games.
Each state of the game is represented over a 64-bit array (Thanks to BitArray library [https://pypi.org/project/bitarray/] which is ***mandatory*** to run the agent. Just type `pip install bitarray`.

#### BitArray (ba) representation of the game

##### Board of the game (s)

Given the fact that board is composed of 25 tiles and that Quixo is a 2-player games 50 bit would be enough to represent a signle state of the game (i.e. which tile belongs to which player). However a 64-bit array is used for alignment in memory reasons

* [00-06]bits: Unusued
* [07-31]bits: Set to 1 if the corresponding tile (0-24) belongs to X player
* [32-38]bits: Unusued
* [39-63]bits: Set to 1 if the corresponding tile (0-24) belongs to O player
```
# U:unusued; X:space_for_X_player; O:space_for_O_player
# 0-----6------------------------3------3------------------------6
#                                1      8                        3
# UUUUUUUXXXXXXXXXXXXXXXXXXXXXXXXXUUUUUUUOOOOOOOOOOOOOOOOOOOOOOOOO  
```

##### Checking the existence of a given line of Xs or Os:

`ones_in(s & A) == 5` with a different A for each pair of line and symbol

##### Performe a move

`Left-pushing move (((s & B) << 1) & B | (s & ~B) | C)` where B is a 64-bit array representing the row of the tile to move and C a 64-bit array having only the bit corresponding to the tile to move for the moving player set to 1

`Right-pushing move (((s & B) >> 1) & B | (s & ~B) | C)` where B is a 64-bit array representing the row of the tile to move and C a 64-bit array having only the bit corresponding to the tile to move for the moving player set to 1

`Down-pushing move (((s & B) >> 5) & B | (s & ~B) | C)` where B is a 64-bit array representing the column of the tile to move and C a 64-bit array having only the bit corresponding to the tile to move for the moving player set to 1

`Left-pushing move (((s & B) << 5) & B | (s & ~B) | C)` where B is a 64-bit array representing the column of the tile to move and C a 64-bit array having only the bit corresponding to the tile to move for the moving player set to 1

#### Improvements

The compact representation based on bitarray instead of matrices allows the Evolved Agent to perform ***twice*** the amount of rollouts (a single repetition of SELECT,EXPAND,SIMULATE,BACKPROPAGATE) with respect to Agent_MCTS in the same timespan, resulting in a more wide exploration of the game states. 

#### Better simulations

Another simple yet effective functionality is implemented: the ability to forecast if starting from a node is possible to win in some moves for one of the player.

In a standard simulation, all the move performed are picked random until a terminal state, then the winner and the corresponding reward are backpropagated through the root of the tree. Although randomness it is a valid approximation in the early stages of the game, it becomes increasingly less accurate as the match progress. If our agent assumes that our opponent plays randomly, it won't defend enough and will tend to prefer states where it has more tiles in a row rather than preventing the opponent from getting 5.

But checking for every state of the game every possible move, applying it and checking if it is a terminal one is very computational intensive, so the following strategy is adppted:

* Only state situated within a certain distance from the root are checked to be near-terminal 

```
def roll_out(self, state, to_move, deepness) -> int:
        if to_move==1-self.agent_id and deepness <= 3:
            return self.game.simulate(deepcopy(state), to_move, self.agent_id)  # Simulation will care about winning move for <<game.look_forward>> steps
        else:
            return self.game.simulate(deepcopy(state), to_move)                 # Simulation will be random for every move
``` 

```
    def simulate(self, state, to_move, agent_id = None):    # Simulate a match from a given state
        self.set_board(state)
        self.current_player_idx = to_move

        winner = -1       
        cnt = 0

        while winner < 0:
            ok = False
            while not ok:
                cnt += 1
                if agent_id is not None and cnt <= self.look_forward:
                    early = self.win_in_one(agent_id)       # Finds out if to_move player can end the game
                    if early != -1:
                        return early, True
                from_pos = (random.randint(0, 25))
                slide = random.choice([Move.TOP, Move.BOTTOM, Move.LEFT, Move.RIGHT])
                ok = self.__move(from_pos, slide, self.current_player_idx)
            self.current_player_idx = 1 - self.current_player_idx
            winner = self.check_winner()
```
* If our opponent from a state in wich has to move can win in a move model will assume he will do it and a negative reward is assigned 

```
    def win_in_one(self, agent_id):
        board = self.get_board()
        children = [self.apply(deepcopy(board), move, self.current_player_idx) for move in get_legal_moves_ba(deepcopy(board), self.current_player_idx)] 
        terminal = -1
        for child in children:
            winner = self.check_terminal(child)
            if winner == 1-agent_id:    
                return winner           # Oppo can win in a move
            elif winner == agent_id:
                terminal = agent_id     # If there is a winning move for Hero and not for Oppo
        return terminal
```

#### Pros and Cons

Providing a more complex model for simulations allows the Agent to be better suited for competitive opponents, but at the same time it slow down the rollouts procedure.

With early winner check Evolved Agent performs still more rollouts wrt Agent_MCTS in the same timespan, but from 2x it goes down to +30%, still remarkable but more less impressive. 

Nonetheless its style of playing improves a lot, by not making the opponent left with four tiles in a row after playing move, unless opponent will not be able to fill the line at his next turn or if it impossible for Agent to block the Opponent.

#### Evolved Agent_MCTS (MyPlayer) Files

* mcts_ba.py: Implementation of the Monte Carlo Tree Search algorithm
* mock_game_ba.py: Playground game instance for simulations needed with early winner prediction mechanism and purely random 
* util_ba.py:
  - ACCEPTABLE: Representing tiles belonging to the border of the board, the only ones allowed to be taken or moved
  - SLIDE_FOR_TILE: Mapping between tiles and allowed moves for specific position on the board
  - TILE2XY: Mapping between tiles and tiles in (r,c) coordinates, the one the official Game accept
  - get_legal_moves_ba(board, agent_id): Function computing all the possible moves from the given board for the given player
  - ba2rc(ba_move): Convert (tile,slide) move in ((r,c),slide) move
  - tile2ba(tile, player_id): Calculate C for performing move in mock_game_ba
  - row2ba(row_index, player_id): Calculate B for performing left/right-pushing move and for checking winning row
  - col2ba(col_index, player_id): Calculate B for performing top/bottom-pushing move and for checking winning column
  - diag2ba(diag_index, player_id): Calculate bit-array representing a diagonal for checking winning diagonal

#### Evolved Agent_MCTS (MyPlayer) Results

Evolved Agent doesn't need a training and:
  * with just 3 seconds per move is able to obtain a 100% win rate against a random player.
  * with 5 seconds per move is able to obtain a 90% win rate against Agent_MCTS.
  * with 30 seconds per move is able to obtain human-level performance.




