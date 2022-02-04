# -*- coding: utf-8 -*-
import copy
from dataclasses import dataclass, field
 
unexplored = []
explored = [] 

@dataclass
class Node:
    board: list = field(default_factory=list) # String representation of board
    child_boards: list = field(default_factory=list) # All possible boards that can be generated from current board
    minmax_score: int = field(default_factory=int) # Score that min/max algorithm assigns to current node


def hexapawn(board, size, player, num_moves):
    """
    Summary: Executes the main logic of the program and calls all supporting
             functions

    Arguments: board, size, player, and num_moves (defined exactly as the promt 
               states)

    Returns: Best possible move found from the passed in arguments. The function
             will attempt to return a move that leads to a win, and if this is
             not possible, it will return the move that provides the best outcome
             for the player as determined using the static evaluation function
             that was defined in class
    """

    global unexplored
    global explored

    # Check if passed in board already contains a win
    if containsWin(board, player):
        print(f"Player '{player}' has already won the game. Exiting ...\n")
        return
    if containsWin(board, swapPlayer(player)):
        print(f"Player '{swapPlayer(player)}' has already won the game. Exiting ...\n")
        return

    # Establish the first node using the passed in board
    curr_level = 0
    curr_player = player
    curr_node = establishNode(board, generateMoves(copy.deepcopy(board), curr_player))
    if curr_node.child_boards == []:
        print(f"No possible moves for the player '{player}.' Exiting program ...\n")
        return
    curr_player = swapPlayer(curr_player)

    # Add next possible moves to the 'unexplored' list
    for child_board in curr_node.child_boards:
        unexplored.append(child_board)
    explored.append([curr_node])
    curr_level += 1

    # Generate all possible moves to the desired depth 
    while curr_level < num_moves:
        new_unexplored = []
        new_nodes = []

        for curr_board in unexplored:
            curr_node = establishNode(curr_board, generateMoves(copy.deepcopy(curr_board), curr_player))
            for child_board in curr_node.child_boards:
                new_unexplored.append(child_board)
            new_nodes.append(curr_node)

        unexplored = copy.deepcopy(new_unexplored)
        curr_level += 1
        curr_player = swapPlayer(curr_player)
        explored.append(copy.deepcopy(new_nodes))

    if num_moves % 2 == 0:
        level_type = 'min'
    else:
        level_type = 'max'

    # Apply the evaluation function to all nodes at the terminal level and propogate upwards one level
    curr_level -= 1
    curr_nodes = explored[curr_level]
    for node in curr_nodes:
        child_boards = node.child_boards
        if child_boards == []:
            node.minmax_score = evaluateBoard(copy.deepcopy(node.board), player, curr_player)
        else:
            eval_scores = []
            for child_board in child_boards:
                eval_scores.append(evaluateBoard(copy.deepcopy(child_board), player, curr_player))
            if level_type == 'max':
                node.minmax_score = max(eval_scores)
            else:
                node.minmax_score = min(eval_scores)

    curr_level -= 1
    level_type = swapLevel(level_type)
    curr_idx = 0

    while curr_level >= 0:
        curr_nodes = explored[curr_level]
        for node in curr_nodes:
            if node.minmax_score != float('inf'):
                continue

            num_children = len(node.child_boards)
            if num_children == 0:
                node.minmax_score = evaluateBoard(copy.deepcopy(node.board), player, curr_player)
                continue

            child_scores = []
            for i in range(num_children):
                child_scores.append(explored[curr_level+1][curr_idx-1].minmax_score)
                curr_idx += 1

            if level_type == 'max':
                node.minmax_score = max(child_scores)
            else:
                node.minmax_score = min(child_scores)

        curr_level -= 1
        level_type = swapLevel(level_type)
        curr_idx = 0

    # In the case of ties, try to chose a next move that results in a win
    possible_moves = []
    for i in range(len(explored[0][0].child_boards)):
        if num_moves == 1:
            if explored[0][0].minmax_score == evaluateBoard(copy.deepcopy(explored[0][0].child_boards[i]), player, curr_player):
                possible_moves.append(explored[0][0].child_boards[i])

        elif explored[1][i].minmax_score == explored[0][0].minmax_score:
            possible_moves.append(copy.deepcopy(explored[1][i].board))

    unexplored = []
    explored = []

    # If no moves result in a win, chose the next move that maximizes your number of players and minimizes opponents'
    best_remaining = []
    for move in possible_moves:
        if containsWin(move, player):
            return move
        else:
            best_remaining.append(calculateDiff(move, player))

    highest_score_idx = best_remaining.index(max(best_remaining))

    return possible_moves[highest_score_idx]


def containsWin(board, curr_player):
    """
    Summary: Checks if the passed in board contains a win for the passed in player

    Arguments: board (current board) and curr_player (player whose turn it is to move)

    Returns: 1 if board contains win, 0 otherwise
    """

    if curr_player == 'w':
        for symbol in board[-1]:
            if symbol == 'w': # Check if white reached end of board
                return 1

        for row in board: # Check for no more black pieces
            for symbol in row:
                if symbol == 'b':
                    return 0
        return 1

    else:
        for symbol in board[0]:
            if symbol == 'b': # Check if black reached end of board
                return 1

        for row in board: # Check for no more white pieces
            for symbol in row:
                if symbol == 'w':
                    return 0
        return 1


def moveWhite(board):
    """
    Summary: Generates all possible moves for white pieces when it is white's turn

    Arguments: board

    Returns: List containing string representations of all possible moves generated
             from the passed in board
    """

    new_boards = []
    board_copy = copy.deepcopy(board)

    for i in range(len(board) - 1):
        for j in range(len(board[0])):

            # Check for white piece
            if board[i][j] != 'w':
                continue

            # Forward
            if board[i+1][j] == '-':
                board[i] = list(board[i])
                board[i][j] = '-'
                board[i] = ''.join(board[i])

                board[i+1] = list(board[i+1])
                board[i+1][j] = 'w'
                board[i+1] = ''.join(board[i+1])

                if board not in new_boards:
                    new_boards.append(board)
                board = copy.deepcopy(board_copy)

            # Diagonal right
            if j != len(board) - 1 and board[i+1][j+1] == 'b':
                board[i] = list(board[i])
                board[i][j] = '-'
                board[i] = ''.join(board[i])

                board[i+1] = list(board[i+1])
                board[i+1][j+1] = 'w'
                board[i+1] = ''.join(board[i+1])

                if board not in new_boards:
                    new_boards.append(board)
                board = copy.deepcopy(board_copy)

            # Diagonal left
            if j != 0 and board[i+1][j-1] == 'b':
                board[i] = list(board[i])
                board[i][j] = '-'
                board[i] = ''.join(board[i])

                board[i+1] = list(board[i+1])
                board[i+1][j-1] = 'w'
                board[i+1] = ''.join(board[i+1])

                if board not in new_boards:
                    new_boards.append(board)
                board = copy.deepcopy(board_copy)

    return new_boards


def moveBlack(board):
    """
    Summary: Generates all possible moves for black pieces when it is blacks's turn

    Arguments: board

    Returns: List containing string representations of all possible moves generated
             from the passed in board
    """

    new_boards = []
    board_copy = copy.deepcopy(board)

    for i in range(len(board) - 1, 0, -1):
        for j in range(len(board[0])):

            # Check for black piece
            if board[i][j] != 'b':
                continue

            # Forward
            if board[i-1][j] == '-':
                board[i] = list(board[i])
                board[i][j] = '-'
                board[i] = ''.join(board[i])

                board[i-1] = list(board[i-1])
                board[i-1][j] = 'b'
                board[i-1] = ''.join(board[i-1])

                if board not in new_boards:
                    new_boards.append(board)
                board = copy.deepcopy(board_copy)

            # Diagonal right
            if j != len(board) - 1 and board[i-1][j+1] == 'w':
                board[i] = list(board[i])
                board[i][j] = '-'
                board[i] = ''.join(board[i])

                board[i-1] = list(board[i-1])
                board[i-1][j+1] = 'b'
                board[i-1] = ''.join(board[i-1])

                if board not in new_boards:
                    new_boards.append(board)
                board = copy.deepcopy(board_copy)

            # Diagonal left
            if j != 0 and board[i-1][j-1] == 'w':
                board[i] = list(board[i])
                board[i][j] = '-'
                board[i] = ''.join(board[i])

                board[i-1] = list(board[i-1])
                board[i-1][j-1] = 'b'
                board[i-1] = ''.join(board[i-1])

                if board not in new_boards:
                    new_boards.append(board)
                board = copy.deepcopy(board_copy)

    return new_boards


def generateMoves(curr_board, player):
    """
    Summary: Generates moves for either white or black player according to the
             value of the 'player' argument that is passed in. If the passed in
             board already contains a win, then no new moves are generated from
             this board

    Arguments: curr_board (board you wish to generate moves from) and player (player
               whose turn it is)

    Returns: List containing string representations of all possible moves generated
             from the passed in board
    """

    if player == 'w':
        if containsWin(curr_board, 'w'):
            return []
        new_boards = moveWhite(curr_board)
        return new_boards

    else:
        if containsWin(curr_board, 'b'):
            return []
        new_boards = moveBlack(curr_board)
        return new_boards


def swapLevel(level_type):
    """
    Simple function used to alternate the value of the 'level_type' variable
    """

    if level_type == 'max':
        return 'min'
    else:
        return 'max'


def swapPlayer(curr_player):
    """
    Simple function used to alternate the value of the 'curr_player' variable.
    'curr_player' represents the player whose turn it is to move
    """

    if curr_player == 'w':
        return 'b'
    else:
        return 'w'


def calculateDiff(board, master_player):
    """
    Summary: Calculates the difference of the number of pieces that each player
             has on the board

    Arguments: board (current board) and master_player (value for the color of
               pawns that was originally passed to the hexapawn function)

    Returns: Number of master_player pieces minus number of opponent's pieces
    """
    num_white = 0
    num_black = 0

    for row in board:
        for symbol in row:
            if symbol == 'w':
                num_white += 1
            elif symbol == 'b':
                num_black += 1

    if master_player == 'w':
        return num_white - num_black
    else:
        return num_black - num_white


def evaluateBoard(curr_board, master_player, curr_player):
     """
     Summary: Uses the static evaluation function presented in lecture. Assigns
             score for board depending on the color assigned to the master_player
             variable. Wins are determined by either a piece making it to the end,
             a player running out of pieces, or a player having no possible moves

     Arguments: curr_board (board to be evaluated), master_player (color who we
                are attempting to generate the best possible next move for), and
                curr_player (player whose turn it is to move)

     Returns: Integer representing the evaluation score for the board
     """

     if master_player == 'w':
         if containsWin(curr_board, 'w'):
             return 10
         elif containsWin(curr_board, 'b'):
             return -10
         elif curr_player == 'b' and generateMoves(curr_board, 'b') == []:
             return 10
         elif curr_player == 'w' and generateMoves(curr_board, 'w') == []:
             return -10
         else:
             return calculateDiff(curr_board, master_player)

     else:
         if containsWin(curr_board, 'b'):
             return 10
         elif containsWin(curr_board, 'w'):
             return -10
         elif curr_player == 'w' and generateMoves(curr_board, 'w') == []:
             return 10
         elif curr_player == 'b' and generateMoves(curr_board, 'b') == []:
             return -10
         else:
             return calculateDiff(curr_board, master_player)


def establishNode(board, child_boards):
    """
    Simple function used to create a node object
    """

    curr_node = Node()

    curr_node.board = board
    curr_node.child_boards = child_boards
    curr_node.minmax_score = float('inf')

    return curr_node
