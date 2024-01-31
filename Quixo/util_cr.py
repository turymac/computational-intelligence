from game import Move

class GameMeta:

    ACCEPTABLE = set([(0,0),(1,0),(2,0),(3,0),(4,0),(0,1),(4,1),(0,2),
                      (4,2),(0,3),(4,3),(0,4),(1,4),(2,4),(3,4),(4,4)])

    SLIDE_FOR_TILE = {
        (0,0)  : [Move.BOTTOM, Move.RIGHT],                 # TOP LEFT CORNER
        (1,0)  : [Move.BOTTOM, Move.LEFT, Move.RIGHT],      # TOP SIDE
        (2,0)  : [Move.BOTTOM, Move.LEFT, Move.RIGHT],      # TOP SIDE
        (3,0)  : [Move.BOTTOM, Move.LEFT, Move.RIGHT],      # TOP SIDE
        (4,0)  : [Move.BOTTOM, Move.LEFT],                  # TOP RIGHT CORNER
        (0,1)  : [Move.BOTTOM, Move.TOP, Move.RIGHT],       # LEFT SIDE
        (0,2) : [Move.BOTTOM, Move.TOP, Move.RIGHT],        # LEFT SIDE
        (0,3) : [Move.BOTTOM, Move.TOP, Move.RIGHT],        # LEFT SIDE
        (4,1)  : [Move.BOTTOM, Move.TOP, Move.LEFT],        # RIGHT SIDE
        (4,2) : [Move.BOTTOM, Move.TOP, Move.LEFT],         # RIGHT SIDE
        (4,3) : [Move.BOTTOM, Move.TOP, Move.LEFT],         # RIGHT SIDE
        (0,4) : [Move.TOP, Move.RIGHT],                     # LOW LEFT CORNER
        (1,4) : [Move.TOP, Move.LEFT, Move.RIGHT],          # LOW SIDE
        (2,4) : [Move.TOP, Move.LEFT, Move.RIGHT],          # LOW SIDE
        (3,4) : [Move.TOP, Move.LEFT, Move.RIGHT],          # LOW SIDE
        (4,4) : [Move.TOP, Move.LEFT]                       # LOW RIGHT CORNER
    }


def __get_tiles(board, agent_id):       # Get the tiles the given player could move/take
    obtainable = set()

    for x in range(5):
        for y in range(5):
            if (board[x][y] == agent_id or board[x][y] == -1) and (x,y) in GameMeta.ACCEPTABLE:
                obtainable.add((y,x))   # Game as input wants (y,x)

    return obtainable

def get_legal_moves(board, agent_id):   # Get all the possible moves from the given board for the given player
    playable_tiles = __get_tiles(board,agent_id)
    playable_moves = [(t,s) for t in playable_tiles for s in GameMeta.SLIDE_FOR_TILE[t]]
    return playable_moves