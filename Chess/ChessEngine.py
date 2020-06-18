
class GameState():

    def __init__(self):
        #Bpard is an 8x8 2d list, each element to character, 1 is color, 2 is the type.
        self.board = [
            ["bR", "bN", "bB", "bQ", "bK", "bB", "bN", "bR"],
            ["bP", "bP", "bP", "bP", "bP", "bP", "bP", "bP"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["wP", "wP", "wP", "wP", "wP", "wP", "wP", "wP"],
            ["wR", "wN", "wB", "wQ", "wK", "wB", "wN", "wR"]
        ]

        self.checkMate = False
        self.staleMate = False
        self.whiteToMove = True
        self.moveLog = []
        self.moveFunctions = {'P': self.getPawnMoves, 'R': self.getRockMoves, 'N': self.getNightMoves,
                              'B': self.getBishopMoves, 'Q': self.getQueenMoves, 'K': self.getKingMoves}
        self.wKLocation = (7,4)
        self.bKLocation = (0,4)
        self.inCheck = False
        self.enPassantPossible = () #coordinates for the square where en passant is possible
        self.pins = []
        self.checks = []
        self.currentCastlingRight = CastleRights(True, True, True, True)
        self.castleRightsLog = [CastleRights(self.currentCastlingRight.wks, self.currentCastlingRight.bks,
                                             self.currentCastlingRight.wqs, self.currentCastlingRight.bqs)]

    '''
    Takes a Move as a parameter eand exevutes it, doesnt work for edge cases
    '''
    def makeMove(self, move):
        self.board[move.startRow][move.startCol] = "--"
        self.board[move.endRow][move.endCol] = move.pieceMoved
        self.moveLog.append(move)
        self.whiteToMove = not self.whiteToMove
        if move.pieceMoved == "wK":
            self.wKLocation = (move.endRow,move.endCol)
        elif move.pieceMoved == "bK":
            self.bKLocation = (move.endRow,move.endCol)
        #Pawn promotion
        if move.isPawnPromotion:
            promotedPiece = input("promote to Q, R, B or N:")
            self.board[move.endRow][move.endCol] = move.pieceMoved[0]+promotedPiece
        #En passant
        if move.possibleEnpassant:
            self.enPassantPossible = ((move.startRow+move.endRow)//2, move.startCol)
        else:
            self.enPassantPossible = ()
        if move.isEnpassantMoved:
            self.board[move.startRow][move.endCol] = "--"
        #Castle move
        if move.isCastleMove:
            if move.endCol - move.startCol == 2: #Kingside
                self.board[move.endRow][move.endCol-1] = self.board[move.endRow][move.endCol +1]
                self.board[move.endRow][move.endCol+1] = '--'
            else: #Queenside
                self.board[move.endRow][move.endCol+1] = self.board[move.endRow][move.endCol -2]
                self.board[move.endRow][move.endCol -2] = '--'


        #update casteling rights - whenever it is rook or a king
        self.updateCastleRights(move)
        self.castleRightsLog.append(CastleRights(self.currentCastlingRight.wks, self.currentCastlingRight.bks,
                                             self.currentCastlingRight.wqs, self.currentCastlingRight.bqs))


    def undoMove(self):
        if len(self.moveLog) > 0:
            lastMove = self.moveLog.pop()
            if lastMove.isEnpassantMoved:
                self.board[lastMove.startRow][lastMove.endCol] = lastMove.pieceCaptured
                self.board[lastMove.endRow][lastMove.endCol] = "--"
                self.enPassantPossible = (lastMove.endRow, lastMove.endCol)
            else:
                self.board[lastMove.endRow][lastMove.endCol] = lastMove.pieceCaptured
            self.board[lastMove.startRow][lastMove.startCol] = lastMove.pieceMoved
            self.whiteToMove = not self.whiteToMove
            if lastMove.pieceMoved == "wK":
                self.wKLocation = (lastMove.startRow, lastMove.startCol)
            elif lastMove.pieceMoved == "bK":
                self.bKLocation = (lastMove.startRow, lastMove.startCol)
            self.castleRightsLog.pop()
            newRights = self.castleRightsLog[-1]
            self.currentCastlingRight = CastleRights(newRights.wks, newRights.bks, newRights.wqs, newRights.bqs)
            if lastMove.isCastleMove:
                if lastMove.endCol - lastMove.startCol == 2:
                    self.board[lastMove.endRow][lastMove.endCol +1] = self.board[lastMove.endRow][lastMove.endCol -1]
                    self.board[lastMove.endRow][lastMove.endCol -1] = '--'
                else:
                    self.board[lastMove.endRow][lastMove.endCol -2] = self.board[lastMove.endRow][lastMove.endCol +1]
                    self.board[lastMove.endRow][lastMove.endCol +1] = '--'
            self.checkMate = False
            self.staleMate = False
        else:
            print("No undo possible")

    def updateCastleRights(self, move):
        if move.pieceMoved == 'wK':
            self.currentCastlingRight.wks = False
            self.currentCastlingRight.wqs = False
        elif move.pieceMoved == 'bK':
            self.currentCastlingRight.bks = False
            self.currentCastlingRight.bqs = False
        elif move.pieceMoved == 'wR':
            if move.startRow == 7:
                if move.startCol == 0:
                    self.currentCastlingRight.wqs = False
                elif move.startCol == 7:
                    self.currentCastlingRight.wks = False
        elif move.pieceMoved == 'bR':
            if move.startRow == 0:
                if move.startCol == 0:
                    self.currentCastlingRight.bqs = False
                elif move.startCol == 7:
                    self.currentCastlingRight.bks = False
    '''
    All moves considering checks
    '''
    def getValidMoves(self):
        moves = []
        self.inCheck, self.pins, self.checks = self.checkForPinsAndChecks()
        if self.whiteToMove:
            kingRow = self.wKLocation[0]
            kingCol = self.wKLocation[1]
        else:
            kingRow = self.bKLocation[0]
            kingCol = self.bKLocation[1]
        if self.inCheck:
            if len(self.checks) == 1:
                moves = self.getAllPossibleMoves()
                check = self.checks[0]
                checkRow = check[0]
                checkCol = check[1]
                pieceChecking = self.board[checkRow][checkCol]
                validSquares = []
                if pieceChecking[1] == "N":
                    validSquares = [(checkRow, checkCol)]
                else:
                    for i in range(1, 8):
                        validSquare = (kingRow + check[2]*i, kingCol + check[3]*i)
                        validSquares.append(validSquare)
                        if checkRow == validSquare[0] and checkCol == validSquare[1]:
                            break
                for i in range(len(moves) -1, -1, -1):
                    if moves[i].pieceMoved[1] != "K":
                        if not (moves[i].endRow, moves[i].endCol) in validSquares:
                            moves.remove(moves[i])
            else: #Means King is in double check
                self.getKingMoves(kingRow, kingCol, moves)
            if len(moves) == 0:
                self.checkMate = True
        else:
            moves = self.getAllPossibleMoves()
            if len(moves) == 0:
                self.staleMate = True
            self.getCastleMoves(kingRow, kingCol, moves)
        return moves



    def checkForPinsAndChecks(self):
        pins = [] #Squares where the allied pinned piece is and direction pined from
        checks = [] #squares where enemy is applying a check
        inCheck = False
        if self.whiteToMove:
            enemyColor = "b"
            allyColor = "w"
            startRow = self.wKLocation[0]
            startCol = self.wKLocation[1]
        else:
            enemyColor = "w"
            allyColor = "b"
            startRow = self.bKLocation[0]
            startCol = self.bKLocation[1]
        #Check outward from king for pins and chekcs, keep track of pins
        directions = ((-1, 0), (0, -1), (1, 0), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1))
        for j in range(len(directions)):
            d = directions[j]
            possiblePin = ()
            for i in range (1,8):
                endRow = startRow + d[0]* i
                endCol = startCol + d[1]* i
                if 0 <= endRow < 8 and 0 <= endCol < 8:
                    endPiece = self.board[endRow][endCol]
                    if endPiece[0] == allyColor and endPiece[1] != "K":
                        if possiblePin == (): #first piece, which could be pinned
                            possiblePin = (endRow, endCol, d[0], d[1])
                        else:
                            break
                    elif endPiece[0] == enemyColor:
                        type = endPiece[1]
                        if (0 <= j <= 3 and type == "R") or \
                                (4 <= j <= 7 and type == "B") or \
                                (i == 1 and type == "P" and ((enemyColor == 'w' and 6 <= j <= 7) or (enemyColor == "b" and 4 <= j <= 5))) or \
                                (type == "Q") or (i==1 and type == "K"):
                            if possiblePin == ():
                                inCheck = True
                                checks.append((endRow, endCol, d[0], d[1]))
                                break
                            else:
                                pins.append(possiblePin)
                        else:
                            break
        knightMoves = ((-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1))
        for move in knightMoves:
            endRow = startRow + move[0]
            endCol = startRow + move[1]
            if 0 <= endRow < 8 and 0 <= endCol < 8:
                if self.board[endRow][startRow] == enemyColor+"N":
                    inCheck = True
                    checks.append((endRow, endCol, d[0], d[1]))
        return inCheck, pins, checks


    def squareUnderAttack(self, r, c):
        self.whiteToMove = not self.whiteToMove
        oppMoves = self.getAllPossibleMoves()
        self.whiteToMove = not self.whiteToMove
        for move in oppMoves:
            if move.endRow == r and move.endCol == c:
                return True
        return False

    '''
    All moves not considering checks
    '''
    def getAllPossibleMoves(self):
        possibleMoves = []
        for r in range(len(self.board)):
            for c in range(len(self.board[r])):
                if (self.board[r][c][0] == 'w' and self.whiteToMove) or (self.board[r][c][0] == 'b' and not self.whiteToMove):
                    piece = self.board[r][c][1]
                    self.moveFunctions[piece](r, c, possibleMoves)
        return possibleMoves

    def getPawnMoves(self, row, col, moves):
        piecePinned = False
        pinDirection = ()
        for i in range(len(self.pins) -1, -1, -1):
            if self.pins[i][0] == row and self.pins[i][1] == col:
                piecePinned = True
                pinDirection = (self.pins[i][2], self.pins[i][3])
                break
        piece = self.board[row][col]
        if piece[0] == 'w':
            if self.board[row-1][col] == "--":
                if not piecePinned or pinDirection == (-1, 0):
                    moves.append(Move((row,col),(row-1,col),self.board))
                    if row == 6 and self.board[row-2][col] == "--":
                        moves.append(Move((row,col), (row-2,col), self.board))
            if col < 7:
                if self.board[row-1][col+1][0] == 'b':
                    if not piecePinned or pinDirection == (-1, 1):
                        moves.append(Move((row,col),(row-1,col+1), self.board))
                if (row - 1, col + 1) == self.enPassantPossible:
                    moves.append(Move((row, col), self.enPassantPossible, self.board))
            if col > 0:
                if self.board[row-1][col-1][0] == 'b':
                    if not piecePinned or pinDirection == (-1, -1):
                        moves.append(Move((row,col),(row-1, col-1), self.board))
                if (row - 1, col - 1) == self.enPassantPossible:
                    moves.append(Move((row, col), self.enPassantPossible, self.board))
        if piece[0] == 'b':
            if self.board[row+1][col] == "--":
                if not piecePinned or pinDirection == (1, 0):
                    moves.append(Move((row,col), (row+1,col), self.board))
                    if row == 1 and self.board[row+2][col] == "--":
                        moves.append(Move((row,col), (row+2,col), self.board))
            if col < 7:
                if self.board[row+1][col+1][0] == 'w':
                    if not piecePinned or pinDirection == (1, 1):
                        moves.append(Move((row,col),(row+1,col+1), self.board))
                if (row + 1, col + 1) == self.enPassantPossible:
                    moves.append(Move((row, col), self.enPassantPossible, self.board))
            if col > 0:
                if self.board[row+1][col-1][0] == 'w':
                    if not piecePinned or pinDirection == (1, -1):
                        moves.append(Move((row,col),(row+1, col-1), self.board))
                if (row + 1, col - 1) == self.enPassantPossible:
                    moves.append(Move((row, col), self.enPassantPossible, self.board))
    def getRockMoves(self, row, col, moves):
        piecePinned = False
        pinDirection = ()
        for i in range(len(self.pins) -1, -1, -1):
            if self.pins[i][0] == row and self.pins[i][1] == col:
                piecePinned = True
                pinDirection = (self.pins[i][2], self.pins[i][3])
                if self.board[row][col][1] != 'Q':
                    self.pins.remove(self.pins[i])
                break
        up = True #See getBishopMoves
        down = True
        right = True
        left = True
        sSq = (row, col)
        var = "b" if self.whiteToMove else "w"
        for i in range(1, 8):
            if row + i < 8 and down:
                if not piecePinned or pinDirection == (1,0) or pinDirection == (-1, 0):
                    if self.board[row + i][col] == "--":
                        moves.append(Move(sSq, (row + i, col), self.board))
                    elif self.board[row + i][col][0] == var:
                        moves.append(Move(sSq, (row + i, col), self.board))
                        down = False
                    else:
                        down = False
            if row - i > -1 and up:
                if not piecePinned or pinDirection == (-1, 0) or pinDirection == (1, 0):
                    if self.board[row - i][col] == "--":
                        moves.append(Move(sSq, (row - i, col), self.board))
                    elif self.board[row - i][col][0] == var:
                        moves.append(Move(sSq, (row - i, col), self.board))
                        up = False
                    else:
                        up = False
            if col + i < 8 and right:
                if not piecePinned or pinDirection == (0, 1) or pinDirection == (0, -1):
                    if self.board[row][col + i] == "--":
                        moves.append(Move(sSq, (row, col + i), self.board))
                    elif self.board[row][col + i][0] == var:
                        moves.append(Move(sSq, (row, col + i), self.board))
                        right = False
                    else:
                        right = False
            if col - i > -1 and left:
                if not piecePinned or pinDirection == (0, -1) or pinDirection == (0, 1):
                    if self.board[row][col - i] == "--":
                        moves.append(Move(sSq, (row, col - i), self.board))
                    elif self.board[row][col - i][0] == var:
                        moves.append(Move(sSq, (row, col - i), self.board))
                        left = False
                    else:
                        left = False

    def getNightMoves(self, row, col, moves):
        piecePinned = False
        pinDirection = ()
        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == row and self.pins[i][1] == col:
                piecePinned = True
                self.pins.remove(self.pins[i])
                break
        posMoves = [(1, 2), (-1, 2), (-2, 1), (-2, -1), (-1, -2), (1, -2), (2, -1), (2, 1)]
        var = "b" if self.whiteToMove else "w"
        sSq = (row, col)
        for posMove in posMoves:
            if row + posMove[0] < 0 or row + posMove[0] > 7 or col + posMove[1] < 0 or col + posMove[1] > 7:
                continue
            else:
                if not piecePinned:
                    if self.board[row + posMove[0]][col + posMove[1]] == "--" or self.board[row + posMove[0]][col + posMove[1]][0] == var:
                        moves.append(Move(sSq, (row+posMove[0], col+posMove[1]), self.board))


    def getBishopMoves(self, row, col, moves):
        piecePinned = False
        pinDirection = ()
        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == row and self.pins[i][1] == col:
                piecePinned = True
                pinDirection = (self.pins[i][2], self.pins[i][3])
                self.pins.remove(self.pins[i])
                break
        upRight = True #Initianiting the values of the different directions a bishop could move.
        upLeft = True #When they mett an obstical they will be False
        downRight = True
        downLeft = True
        sSq = (row, col)
        var = "b" if self.whiteToMove else "w"
        for i in range(1, 8):
            if row - i > -1 and col + i < 8 and upRight:
                if not piecePinned or pinDirection == (-1, 1) or pinDirection == (1, -1):
                    if self.board[row - i][col + i] == "--":
                        moves.append(Move(sSq, (row - i, col + i), self.board))
                    elif self.board[row - i][col + i][0] == var:
                        moves.append(Move(sSq, (row - i, col + i), self.board))
                        upRight = False
                    else:
                        upRight = False
            if row - i > -1 and col - i > -1 and upLeft:
                if not piecePinned or pinDirection == (1, 1) or pinDirection == (-1, -1):
                    if self.board[row - i][col - i] == "--":
                        moves.append(Move(sSq, (row - i, col - i), self.board))
                    elif self.board[row - i][col - i][0] == var:
                        moves.append(Move(sSq, (row - i, col - i), self.board))
                        upLeft = False
                    else:
                        upLeft = False
            if row + i < 8 and col + i < 8 and downRight:
                if not piecePinned or pinDirection == (1, 1) or pinDirection == (-1, -1):
                    if self.board[row + i][col + i] == "--":
                        moves.append(Move(sSq, (row + i, col + i), self.board))
                    elif self.board[row + i][col + i][0] == var:
                        moves.append(Move(sSq, (row + i, col + i), self.board))
                        downRight = False
                    else:
                        downRight = False
            if row + i < 8 and col - i > -1 and downLeft:
                if not piecePinned or pinDirection == (-1, 1) or pinDirection == (1, -1):
                    if self.board[row + i][col - i] == "--":
                        moves.append(Move(sSq, (row + i, col - i), self.board))
                    elif self.board[row + i][col - i][0] == var:
                        moves.append(Move(sSq, (row + i, col - i), self.board))
                        downLeft = False
                    else:
                        downLeft = False

    def getQueenMoves(self, row, col, moves):
        self.getRockMoves(row, col, moves)
        self.getBishopMoves(row, col, moves)

    def getKingMoves(self, row, col, moves):
        rowMoves = (-1, -1, -1, 0, 0, 1, 1, 1)
        colMoves = (-1, 0, 1, -1, 1, -1, 0, 1)
        allyColor = "w" if self.whiteToMove else "b"
        for i in range(8):
            endRow = row + rowMoves[i]
            endCol = col + colMoves[i]
            if 0 <= endRow < 8 and 0 <= endCol < 8:
                endPiece = self.board[endRow][endCol]
                if endPiece[0] != allyColor:
                    if allyColor == 'w':
                        self.wKLocation = (endRow, endCol)
                    else:
                        self.bKLocation = (endRow, endCol)
                    inCheck, pins, checks = self.checkForPinsAndChecks()
                    if not inCheck:
                        moves.append(Move((row, col), (endRow, endCol), self.board))
                    if allyColor == "w":
                        self.wKLocation = (row, col)
                    else:
                        self.bKLocation = (row, col)


    '''
    Generate all valid castle moves for the king at (r, c) and add them to the list of moves
    '''

    def getCastleMoves(self, r, c, moves):
        if self.squareUnderAttack(r, c):
            return
        if (self.whiteToMove and self.currentCastlingRight.wks) or (not self.whiteToMove and self.currentCastlingRight.bks):
            self.getKingsideCastleMoves(r, c, moves)
        if (self.whiteToMove and self.currentCastlingRight.wqs) or (not self.whiteToMove and self.currentCastlingRight.bqs):
            self.getQueensideCastleMoves(r, c, moves)

    def getKingsideCastleMoves(self, r, c, moves):
        if self.board[r][c+1] == '--' and self.board[r][c+2] == '--':
            if not self.squareUnderAttack(r, c+1) and not self.squareUnderAttack(r, c+2):
                moves.append(Move((r, c), (r, c+2), self.board, isCastleMove = True))


    def getQueensideCastleMoves(self, r, c, moves):
        if self.board[r][c-1] == '--' and self.board[r][c-2] == '--' and self.board[r][c-3] == '--':
            if not self.squareUnderAttack(r, c-1) and not self.squareUnderAttack(r, c-2):
                moves.append(Move((r,c), (r,c-2), self.board, isCastleMove = True))



class CastleRights():
    def __init__(self, wks, bks, wqs, bqs):
        self.wks = wks
        self.bks = bks
        self.wqs = wqs
        self.bqs = bqs

class Move():
    #maps keys to values
    # key : value
    ranksToRows = {"1": 7, "2": 6, "3": 5, "4": 4,
                   "5": 3, "6": 2, "7": 1, "8": 0}
    rowsToRanks = {v : k for k,v in ranksToRows.items()}

    filesToCols = {"a": 0, "b": 1, "c": 2, "d": 3,
                   "e": 4, "f": 5, "g": 6, "h": 7}
    colsToFiles = {v: k for k,v in filesToCols.items()}


    def __init__(self, startSq, endSq, board, isCastleMove = False):
        self.startRow = startSq[0]
        self.startCol = startSq[1]
        self.endRow = endSq[0]
        self.endCol = endSq[1]
        self.pieceMoved = board[self.startRow][self.startCol]
        self.pieceCaptured = board[self.endRow][self.endCol]
        self.isPawnPromotion = False
        if (self.pieceMoved == "wP" and self.endRow == 0) or (self.pieceMoved == "bP" and self.endRow == 7):
            self.isPawnPromotion = True
        self.possibleEnpassant = False #Check wheter Enpassant will be possible the next move
        if self.pieceMoved[1] == "P" and abs(self.startRow - self.endRow) == 2:
            self.possibleEnpassant = True
        self.isEnpassantMoved = False #Indicating whether the move was an enpassant move
        if self.pieceMoved[1] == 'P' and self.startCol != self.endCol and self.pieceCaptured=="--": #Checking if there is an enpassant move
            capCol = "w" if self.pieceMoved[0] == "b" else "b"
            self.isEnpassantMoved = True
            self.pieceCaptured = capCol+"P"
        self.isCastleMove = isCastleMove
        self.moveId = self.startRow*1000 + self.startCol*100 + self.endRow*10 + self.endCol


    '''
    Overriding the equals method
    '''
    def __eq__(self, other):
        if isinstance(other, Move):
            return other.moveId == self.moveId
        return False

    def getChessNotation(self):
        #Could add more to this to make it more accurate
        return self.getRankFile(self.startRow, self.startCol) + self.getRankFile(self.endRow,self.endCol)

    def getRankFile(self, r, c):
        return self.colsToFiles[c] + self.rowsToRanks[r]

#Just another change

