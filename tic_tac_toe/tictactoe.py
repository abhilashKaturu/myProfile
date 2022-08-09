"""
Tic Tac Toe Player
"""

from cmath import inf
import math
import copy
import random

X = "X"
O = "O"
EMPTY = None


def initial_state():
    """
    Returns starting state of the board.
    """
    return [[EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY]]


def player(board):
    """
    Returns player who has the next turn on a board.
    """
    if isBoardEmpty(board):
        return X
    xcount = 0
    ocount = 0
    for i in board:
        for k in i:
            if k == X:
                xcount += 1
            if k == O:
                ocount += 1
    if xcount > ocount:
        return O
    elif ocount == xcount:
        return X


def isBoardEmpty(board):
    """
    Return if board is empty
    """
    for i in board:
        for k in i:
            if k is not EMPTY:
                return False
    return True


def actions(board):
    """
    Returns set of all possible actions (i, j) available on the board.
    """
    posactions = []
    for i in range(len(board)):
        for k in range(len(board[i])):
            if board[i][k] == EMPTY:
                posactions.append((i,k))
    return posactions


def result(board, action):
    """
    Returns the board that results from making move (i, j) on the board.
    """
    playing = player(board)
    mylist = copy.deepcopy(board)
    if mylist[action[0]][action[1]] is EMPTY:

        try:
            mylist[action[0]][action[1]] = playing
        except IndexError:
            raise Exception('Invalid move')
    else:
        raise Exception('Invalid Move')
    return mylist



def winner(board):
    """
    Returns the winner of the game, if there is one.
    """
    
    for i in board:
        #horizontals
        if (i[0] == i[1] == i[2]) and (i[0] is not EMPTY):
            return i[0]
    
    #verticals
    for i in range(3):
        if board[0][i] == board[1][i] == board[2][i]:
            return board[0][i]
    
    #diagonals
    if board[0][0] == board[1][1] == board[2][2]:
        return board[0][0]
    if board[0][2] == board[1][1] == board[2][0]:
        return board[2][0]
    
    return None


    


def terminal(board):
    """
    Returns True if game is over, False otherwise.
    """
    # try:
    if (winner(board) == X) or (winner(board) == O):
        return True
    
    #No tie and game didn't end
    for i in board:
        for k in i:
            if k is EMPTY:
                return False
    #If game ended in a tie
    return True


def utility(board):
    """
    Returns 1 if X has won the game, -1 if O has won, 0 otherwise.
    """
    i = winner(board)
    if i == X:
        return 1
    if i == O:
        return -1
    return 0

def isBoardEmpty(board):
    
    for i in board:
        for k in i:
            if k is not EMPTY:
                return False


    return True


def minimax(board):
    """
    Returns the optimal action for the current player on the board.
    """
    if terminal(board):
        return None


    if isBoardEmpty(board):
        i = random.randint(0, 2)
        k = random.randint(0, 2)
        return (i, k)
    
    counter = 0
    for i in board:
        for k in i:
            if k is not EMPTY:
                counter += 1
    if counter == 1:
        if board[1][1] == X:
            r = random.randint(0, 1)
            if r == 0:
                return (0, 0)
            else: return (2, 2)
        else:
            return (1, 1)


    curplayer = player(board)

    #Maximizing player
    def maxPlayer(board):
        best_action = ()
        if terminal(board):
            return utility(board), best_action
        v = -100
        
        for action in actions(board):
            if v != max(v, minPlayer(result(board, action))[0]):
                best_action = action
            v = max(v, minPlayer(result(board, action))[0])
        return v, best_action

    #Minimizing player

    def minPlayer(board):
        best_action = ()
        if terminal(board):
            return utility(board), best_action
        v = 100
        
        for action in actions(board):
            if v != min(v, maxPlayer(result(board, action))[0]):
                best_action = action
            v = min(v, maxPlayer(result(board, action))[0])
        return v, best_action
    
    if curplayer == X:
        
        return maxPlayer(board)[1]

    if curplayer == O:
        
        return minPlayer(board)[1]
        

