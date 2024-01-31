from copy import deepcopy
from bitarray import bitarray
from game import Move
from util_ba import GameMeta, tile2ba, row2ba, col2ba, diag2ba, get_legal_moves_ba
from math import floor
import random


class MockGameBa(object):
    def __init__(self) -> None:
        self._board = bitarray(64)
        self.current_player_idx = 1
        self.look_forward = 1           # For how many steps of certain simulations try to find a terminal state

    def get_board(self) -> bitarray:
        '''
        Returns the board
        '''
        return deepcopy(self._board)

    def set_board(self, board) -> None:
        self._board=deepcopy(board)

    def get_current_player(self) -> int:
        '''
        Returns the current player
        '''
        return deepcopy(self.current_player_idx)

    def check_terminal(self, board):
        self.set_board(board)
        return self.check_winner()

    def check_winner(self) -> int:
        '''Check the winner. Returns the player ID of the winner if any, otherwise returns -1'''
        # for each row
        for player_id in range(2):
            for idx in range(5):
                # if a player has completed an entire row
                if sum(row2ba(idx,player_id) & self._board) == 5:
                    # return the relative id
                    return player_id
            # for each column
            for idy in range(5):
                # if a player has completed an entire column
                if sum(col2ba(idy,player_id) & self._board) == 5:
                    # return the relative id
                    return player_id
            # if a player has completed the principal diagonal
            if sum(diag2ba(-1,player_id) & self._board) == 5:
                # return the relative id
                return player_id
            # if a player has completed the secondary diagonal
            if sum(diag2ba(+1,player_id) & self._board) == 5:
                # return the relative id
                return player_id
        return -1
    
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
        
        return winner, False

    def apply(self, board, move, agent_id): # Simulate a move from a given state and returns the resulting board
        self.set_board(board)
        from_pos, slide = move
        self.__move(from_pos, slide, agent_id)
        return self.get_board()

    def __move(self, tile: int, slide: Move, player_id: int) -> bool:
        '''Perform a move'''
        if self.__can_take(tile, player_id) and slide in GameMeta.SLIDE_FOR_TILE[tile]:
            self.__slide(tile, slide, player_id)
            return True
        return False
        
    def __can_take(self, tile: int, player_id: int) -> bool:
        '''Take piece'''
        if tile in GameMeta.ACCEPTABLE and not self.__owned(tile, 1-player_id):
            return True
        return False

    def __owned(self, tile: int, player_id: int):
        c = tile2ba(tile, player_id)
        return any(c & self._board)    

    def __slide(self, tile: int, slide: Move, player_id) -> bool:
            s = self.get_board()
            c = tile2ba(tile, player_id)
            b = bitarray(64)
            row_index = floor(tile/5)
            column_index = tile % 5
            if slide == Move.RIGHT:
                c = c >> 4 - column_index
                b[column_index:5] = 1
                b = ((b >> 7) | (b >> 39)) >> ((row_index<<2)+row_index) # 5 * row_index
                self._board = (((s & b) << 1) & b) | (s & ~b) | c
            if slide == Move.LEFT:
                c = c << column_index
                b[0:column_index+1] = 1
                b = ((b >> 7) | (b >> 39)) >> ((row_index<<2)+row_index) # 5 * row_index
                self._board = (((s & b) >> 1) & b) | (s & ~b) | c
            if slide == Move.BOTTOM:
                c = c >> 5 * (4 - row_index)
                b[tile:20+column_index+1:5] = 1
                b = (b >> 7) | (b >> 39)
                self._board = (((s & b) << 5) & b) | (s & ~b) | c
            if slide == Move.TOP:
                c = c << 5 * row_index
                b[column_index:tile+1:5] = 1
                b = (b >> 7)| (b >> 39)
                self._board = (((s & b) >> 5) & b) | (s & ~b) | c
            