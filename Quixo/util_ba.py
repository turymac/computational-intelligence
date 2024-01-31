from bitarray import bitarray
import numpy as np
from game import Move

    # Tile
    ## ## ## ## ##
#    0  1  2  3  4
#    5  6  7  8  9
#   10 11 12 13 14
#   15 16 17 18 19
#   20 21 22 23 24

class GameMeta:

    ACCEPTABLE = set([0,1,2,3,4,5,9,10,14,15,19,20,21,22,23,24])

    SLIDE_FOR_TILE = {
        0  : [Move.BOTTOM, Move.RIGHT],                 # TOP LEFT CORNER
        1  : [Move.BOTTOM, Move.LEFT, Move.RIGHT],      # TOP SIDE
        2  : [Move.BOTTOM, Move.LEFT, Move.RIGHT],      # TOP SIDE
        3  : [Move.BOTTOM, Move.LEFT, Move.RIGHT],      # TOP SIDE
        4  : [Move.BOTTOM, Move.LEFT],                  # TOP RIGHT CORNER
        5  : [Move.BOTTOM, Move.TOP, Move.RIGHT],       # LEFT SIDE
        10 : [Move.BOTTOM, Move.TOP, Move.RIGHT],       # LEFT SIDE
        15 : [Move.BOTTOM, Move.TOP, Move.RIGHT],       # LEFT SIDE
        9  : [Move.BOTTOM, Move.TOP, Move.LEFT],        # RIGHT SIDE
        14 : [Move.BOTTOM, Move.TOP, Move.LEFT],        # RIGHT SIDE
        19 : [Move.BOTTOM, Move.TOP, Move.LEFT],        # RIGHT SIDE
        20 : [Move.TOP, Move.RIGHT],                    # LOW LEFT CORNER
        21 : [Move.TOP, Move.LEFT, Move.RIGHT],         # LOW SIDE
        22 : [Move.TOP, Move.LEFT, Move.RIGHT],         # LOW SIDE
        23 : [Move.TOP, Move.LEFT, Move.RIGHT],         # LOW SIDE
        24 : [Move.TOP, Move.LEFT]                      # LOW RIGHT CORNER
    }

    TILE2YX = {
        0   :   (0,0),
        1   :   (1,0),
        2   :   (2,0),
        3   :   (3,0),
        4   :   (4,0),
        5   :   (0,1),
        9   :   (4,1),
        10  :   (0,2),
        14  :   (4,2),
        15  :   (0,3),
        19  :   (4,3),
        20  :   (0,4),
        21  :   (1,4),
        22  :   (2,4),
        23  :   (3,4),
        24  :   (4,4)
    }

def __get_tiles_ba(board, agent_id):                # Get the tiles the given player could move/take
    tiles = [board[7:32],board[39:64]]
    obtainable = set()
    for tile in range(25):
        if tile in GameMeta.ACCEPTABLE:
            if tiles[agent_id][tile] and not tiles[1-agent_id][tile]:
                obtainable.add(tile)
            elif not tiles[agent_id][tile] and not tiles[1-agent_id][tile]:
                obtainable.add(tile)
    return obtainable

def get_legal_moves_ba(board, agent_id):            # Get all the possible moves from the given board for the given player
    playable_tiles = __get_tiles_ba(board,agent_id)
    playable_moves = []

    for t in playable_tiles:
        possible = GameMeta.SLIDE_FOR_TILE[t]
        for s in possible:
            playable_moves.append((t,s))
    
    return playable_moves

def ba2rc(ba_move):                         # Convert (tile,slide) to ((c,r),slide)
    tile, move = ba_move
    return GameMeta.TILE2YX[tile], move

# Computing bitarray representing TAKEN TILE
# U:unusued; X:space_for_X_player; O:space_for_O_player
# 0-----6------------------------3------3------------------------6
#                                1      8                        3
# UUUUUUUXXXXXXXXXXXXXXXXXXXXXXXXXUUUUUUUOOOOOOOOOOOOOOOOOOOOOOOOO  
def tile2ba(tile: int, player_id: int):     # Convert tile to corresponding bitarray for given player
        ba = bitarray(64)
        if(not player_id):
            ba[tile+7] = 1
        else:
            ba[tile+39] = 1
        return ba

def row2ba(row_index: int, player_id):      # Covert row index to corresponding bitarray
    ba = bitarray(64)
    if(not player_id):
        ba[0:5]=1
        ba = ba >> 7
        ba = ba >> row_index * 5
    else:
        ba[0:5]=1
        ba = ba >> 39
        ba = ba >> row_index * 5
    return ba

def col2ba(col_index: int, player_id):      # Covert col index to corresponding bitarray
    ba = bitarray(64)
    if(not player_id):
        ba[7+col_index:32:5] = 1
    else:
        ba[39+col_index:64:5] = 1
    return ba

# -1 -> principal diagonal; 1 -> secondary diagonal
def diag2ba(diag_index: int, player_id):    # Covert diag index to corresponding bitarray
    ba = bitarray(64)
    if diag_index == -1:
        ba[0:25:6] = 1
    elif diag_index == 1:
        ba[4:21:4] = 1
    if not player_id:
            ba = ba >> 7
    else:
            ba = ba >> 39
    return ba

def ba2board(ba: bitarray):                 # Convert bitarray corresponding to a state of the board to the (r,c) version
    board = np.ones((5, 5), dtype=np.uint8) * -1
    X = ba[7:31+1]  #X tiles
    O = ba[39:63+1] #O tiles
    for r in range(5):
        for c in range(5):
            if X[5*r+c]:
                board[r][c] = 0 # X player = 0 on board
                assert not O[5*r+c]
            if O[5*r+c]:
                board[r][c] = 1 # O player = 1 on board
                assert not X[5*r+c]
    return board

def board2ba(board):                        # Convert (r,c) board to corresponding bitarray
    ba = bitarray(64)
    for r in range(5):
        for c in range(5):
            if board[r][c] == 0:
                    ba[7+5*r+c]= 1
            elif board[r][c] == 1:
                    ba[39+5*r+c]= 1
    return ba            