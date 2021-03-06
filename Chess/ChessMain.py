#Todo:
# - King capture possible..
import pygame as p
import random
from Chess import ChessEngine

WIDTH = HEIGHT = 512
DIMENSION = 8
SQ_SIZE = HEIGHT // DIMENSION
MAX_FPS = 15 # Animations later on
IMAGES = {}
'''
Initialize a global dictionary of images. This will be called only ones
'''

def loadImages():
    pieces = ['wP', 'wR', 'wB', 'wN', 'wQ', 'wK','bP', 'bR', 'bB', 'bN', 'bQ', 'bK']
    for piece in pieces:
        IMAGES[piece] = p.transform.scale(p.image.load("images/" + piece + ".png"), (SQ_SIZE, SQ_SIZE))


'''
The main driver for our vode. This will handle user input and updatingthe grapics'''

def main():
    p.init()
    screen = p.display.set_mode((WIDTH, HEIGHT))
    clock = p.time.Clock()
    screen.fill(p.Color("white"))
    gs = ChessEngine.GameState()
    validMoves = gs.getValidMoves()
    moveMade = False #flag vaieable for when a move is made
    animate = False
    loadImages()
    running = True
    sqSelected = () #last click from user(row, col)
    playerClicks = [] #keep track  of player clicks (two tuples: [(6,4), (4,4)]
    gameOver = False
    while running:
        for e in p.event.get():
            if e.type == p.QUIT:
                running = False
            elif e.type == p.KEYDOWN:
                if e.key == p.K_z:
                    gs.undoMove()
                    moveMade = True
                    animate = False
                    gameOver = False
                if e.key == p.K_r:
                    gs = ChessEngine.GameState()
                    validMoves = gs.getValidMoves()
                    sqSelected = ()
                    playerClicks = []
                    moveMade = False
                    animate = False
                    gameOver = False
            elif not gs.whiteToMove:
                best_move = minimax(gs)
                if best_move in gs.getValidMoves():
                    gs.makeMove(best_move)
                    moveMade = True
                    animate = True
            elif e.type == p.MOUSEBUTTONDOWN:
                if not gameOver:
                    location = p.mouse.get_pos() #(x,y) location
                    col = location[0]//SQ_SIZE
                    row = location[1]//SQ_SIZE
                    if sqSelected == (row,col):
                        sqSelected = ()
                        playerClicks = []
                    else:
                        sqSelected = (row, col)
                        playerClicks.append(sqSelected)
                    if len(playerClicks) == 2:
                        move = ChessEngine.Move(playerClicks[0], playerClicks[1], gs.board)
                        for i in range(len(validMoves)):
                            if move == validMoves[i]:
                                gs.makeMove(validMoves[i])
                                moveMade = True
                                animate = True
                                sqSelected = ()
                                playerClicks = []
                            if not moveMade:
                                playerClicks = [sqSelected]
        if moveMade:
            if animate:
                animateMove(gs.moveLog[-1], screen, gs.board, clock)
            validMoves = gs.getValidMoves()
            moveMade = False
            animate = False
        drawGameState(screen, gs, validMoves, sqSelected)

        if gs.checkMate:
            gameOver = True
            if gs.whiteToMove:
                drawText(screen, 'Black wins by checkmate')
            else:
                drawText(screen, 'White wins by checkmate')
        elif gs.staleMate:
            gameOver = True
            drawText(screen, 'Stalemate')

        clock.tick(MAX_FPS)
        p.display.flip()


def minimax(state):
    best_score = 10000
    best_move = 0
    for move in state.getValidMoves():
        state.makeMove(move)
        min_value = maxValue(state, 0, -float("inf"), float("inf"))
        if min_value < best_score:
            best_score = min_value
            best_move = move
        state.undoMove()
    print(count)
    return best_move

def maxValue(state, depth, alpha, beta):
    if state.checkMate:
        if state.whiteToMove:
            return -10000
        else:
            return 10000
    elif depth == 2:
        return evalPos(state)
    else:
        best_score = -float("inf")
        for move in state.getValidMoves():
            state.makeMove(move)
            min_value = minValue(state, depth+1, alpha, beta)
            state.undoMove()
            if min_value > best_score:
                best_score = min_value
            if min_value >= beta:
                return min_value
            alpha = max(alpha, min_value)
    return best_score

def minValue(state, depth, alpha, beta):
    if state.checkMate:
        if state.whiteToMove:
            return 10000
        else:
            return -10000
    elif depth == 2:
        return evalPos(state)
    else:
        best_score = float("inf")
        for move in state.getValidMoves():
            state.makeMove(move)
            max_value = maxValue(state, depth+1, alpha, beta)
            state.undoMove()
            if max_value < best_score:
                best_score = max_value
            if max_value <= alpha:
                return max_value
            beta = min(beta, max_value)
    return best_score

count=0
def evalPos(state):
    global count
    count += 1
    evaluation = {"bK": -900, "bQ": -90, "bR": -50, "bN": -30, "bB": -30, "bP": -10,
                  "wK": 900, "wQ": 90, "wR": 50, "wN": 30, "wB": 30, "wP": 10, "--": 0}
    score = 0
    for row in state.board:
        for square in row:
            score += evaluation[square] + random.random()
    return score
'''
Highligjt square selected and moves for piece selected
'''
def highlightSquares(screen, gs, validMoves, sqSelected):
    if sqSelected != ():
        r, c = sqSelected
        if gs.board[r][c][0] == ('w' if gs.whiteToMove else 'b'): #sqSelected is a piece that can be moved
            s = p.Surface((SQ_SIZE, SQ_SIZE))
            s.set_alpha(100) #Transperancy value
            s.fill(p.Color('blue'))
            screen.blit(s, (c*SQ_SIZE, r*SQ_SIZE))
            s.fill(p.Color('yellow'))
            for move in validMoves:
                if move.startRow == r and move.startCol == c:
                    screen.blit(s, (SQ_SIZE*move.endCol, SQ_SIZE*move.endRow))


"""
Responsable for the graphics within the currane game state."""
def drawGameState(screen, gs, validMoves, sqSelected):
    drawBoard(screen) #draw squares on the board
    highlightSquares(screen, gs, validMoves, sqSelected)
    drawPieces(screen, gs.board) #draw pieces on top of those squares

def drawBoard(screen):
    global colors
    colors = [p.Color("white"), p.Color("gray")]
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            color = colors[((r+c) % 2)]
            p.draw.rect(screen, color, p.Rect(c*SQ_SIZE, r*SQ_SIZE, SQ_SIZE, SQ_SIZE))

"""
Draw the pieces on the board using the urrent GameState.board
"""
def drawPieces(screen, board):
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            piece = board[r][c]
            if piece != "--":
                screen.blit(IMAGES[piece], p.Rect(c*SQ_SIZE, r*SQ_SIZE, SQ_SIZE, SQ_SIZE))


'''
Animating a move
'''

def animateMove(move, screen, board, clock):
    global colors
    dR = move.endRow - move.startRow
    dC = move.endCol - move.startCol
    framesPerSquare = 3
    frameCount = (abs(dR) + abs(dC)) * framesPerSquare
    for frame in range(frameCount + 1):
        r, c = (move.startRow + dR*frame/frameCount, move.startCol + dC*frame/frameCount)
        drawBoard(screen)
        drawPieces(screen, board)
        #erase the piece moved from its ending square
        color = colors[(move.endRow + move.endCol) % 2]
        endSquare = p.Rect(move.endCol*SQ_SIZE, move.endRow*SQ_SIZE, SQ_SIZE, SQ_SIZE)
        p.draw.rect(screen, color, endSquare)
        #draw captured piece onto recangel
        if move.pieceCaptured != '--':
            screen.blit(IMAGES[move.pieceCaptured], endSquare)
        screen.blit(IMAGES[move.pieceMoved], p.Rect(c*SQ_SIZE, r*SQ_SIZE, SQ_SIZE, SQ_SIZE))
        p.display.flip()
        clock.tick(60)


def drawText(screen, text):
    font = p.font.SysFont("Helvetica", 32, True, False)
    textObject = font.render(text, 0, p.Color('Gray'))
    textLocation = p.Rect(0, 0, WIDTH, HEIGHT).move(WIDTH/2 - textObject.get_width()/2, HEIGHT/2 - textObject.get_height()/2)
    screen.blit(textObject, textLocation)
    textObject = font.render(text, 0, p.Color("Black"))
    screen.blit(textObject, textLocation.move(2,2))

if __name__ == "__main__":
    main()

