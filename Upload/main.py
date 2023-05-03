import threading
from numpy import Infinity, empty
import pygame # this brings in the library that we will be using for the game aspect of the code
from pygame import *
pygame.init()
import os
import time
from select import select
import sqlite3
 
#Constants for the program:
height, width = 650,650
row, column = 8, 8 # row is horizontal, column is vertical
square_size = height/column # we do it this was round because it is how many rows will fit in the screen
# the following are the colours that will be used 
dark = (177,134,101)
light = (241,219,180)
white = (255,255,255)
red = (255,0,0)
yellow = (255,255,0)
 
class Button():
    def __init__(self, height, width, colour, x, y, text = ''):
        self.height = height # this and the width are the dimentions in pixels
        self.width = width
        self.colour = colour # this is which colour the button is going to be
        self.x = x # the top lefthand corner of the buttons x co-ordinate
        self.y = y # the top lefthand corner of the buttons y co-ordinate
        self.text = text # this is the text that will go inside of the button
         
    def draw(self, window): # this takes all of the information about the button, and puts it on the screen 
        self.window = window # this is the window that the button will go in
        pygame.draw.rect(self.window, self.colour, (self.x, self.y, self.width, self.height), 0)
        if self.text != '':
            font = pygame.font.SysFont('Calibri', 20)
            text = font.render(self.text, 1, (0,0,0))
            window.blit(text, (self.x + (self.width/2 - text.get_width()/2), self.y + (self.height/2 - text.get_height()/2)))# this centers the text in the button
  
class AI(threading.Thread):
    def __init__(self, colour, running_status):
        self.piece = Piece()
        self.queen_val = 975
        self.rook_val = 500
        self.bishop_val = 325
        self.knight_val = 325
        self.pawn_val = 100
        self.bishop_pair_bonus = 50
        self.knight_pair_penalty = -50
        self.doubled_pawn_penalty = -20 
        self.tripled_pawn_penalty = -45
        self.knight_positioning = [6,9,12,15,15,12,9,6,9,12,15,15,15,15,12,9,12,15,18,21,21,18,15,12,15,15,21,24,24,21,15,15,15,15,21,24,24,21,15,15,12,15,18,21,21,18,15,12,9,12,15,15,15,15,12,9,6,9,12,15,15,12,9,6] # each element corresponds to the same position in the board, and if there is a knight on a square, the corresponding value in this list will be the bonus
        self.king_positioning_white = [25,30,25,10,10,10,30,25,20,20,5,5,5,5,20,20,10,7,5,5,5,5,7,10,5,5,5,5,5,5,5,5,5,5,5,5,5,5,5,5,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,3,3,3,3,3,3,3,3] # these are similar to the knight one but with the white king 
        self.king_positioning_black = [3,3,3,3,3,3,3,3,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,5,5,5,5,5,5,5,5,5,5,5,5,5,5,5,5,10,7,5,5,5,5,7,10,20,20,5,5,5,5,20,20,25,30,15,10,10,20,30,25] # similar to the knight one but with the black king 
        self.no_king_attackers = [0,50,75,88,94,97,99] # this list will store the value for the penalty for the number of attackers attacking the kings zone
        self.king_attackers_constant = [0,10,20,20,40,80] # this stores how much penalty should be awarded when each peice is attacking, this is in the form [none, pawn, knight, bishop, rook, queen]
        self.evaluation_res = None # this will be accessed by the board object that this is running in, so that it can be displayed
        self.best_move = None # this will be a string that will show what the best move is
 
    def play_calculation(self): # this will be the piece of code that will be run when the user wants to play the ai
        connection = None
        try:
            connection = sqlite3.connect('calculation.db') # establishing a connection to the calculation database
        except:
            pass
        cursor = connection.cursor()
        aiboard = []
        book = True
        self.best_move = None # when this is something then the computer will play the move
        self.ai_board = []
        while board.running: # while the game is still going
            self.white_long_castle = board.white_long_castle
            self.black_long_castle = board.black_long_castle
            self.white_short_castle = board.white_short_castle
            self.black_short_castle = board.black_short_castle
            if board.ai_turn == True: # now the program knows that the AI neesd to find a move
                if book == False: # the program needs to calculate what the best move is
                    self.ai_board = []
                    self.best_move = None
                    aiboard = [] # setting up an empty board, so that we can put the board in there
                    for i in range(0,len(board.board)): # because we need to append each thing to the board
                        aiboard.append(board.board[i]) # appending that position of the board to the list
                        self.ai_board.append(board.board[i])
                    if board.move % 2 == 0:
                        colour = 'white'
                        max_player = True
                    else:
                        colour = 'black'
                        max_player = False
                    using = []
                    for i in range(0,len(aiboard)):
                        using.append(aiboard[i])
                    start = time.time()
                    final_eval = self.think_ahead(aiboard,4,max_player,board.white_long_castle,board.white_short_castle,board.black_long_castle,board.black_short_castle,None,True,-Infinity,Infinity)
                    end = time.time()
                    try:
                        self.evaluation_res = final_eval[0]
                        self.best_move = final_eval[1]
                        board.analyse_pos = False
                        self.analyse_change = False
                    except: # if the above doesn't work, then we have come out of the eval manually, and therefore we can press the analysis button again
                        pass # nothing is to happen if we come out of the above too early
                    board.ai_turn = False
                else: # the program can refer to the opening book for the best move
                    for i in range(0,len(board.board)): 
                            aiboard.append(board.board[i])
                            self.ai_board.append(board.board[i])
                    fen = pos_to_FEN(board.board)
                    cursor.execute(f'''
                    SELECT * FROM 'opening_book' WHERE FEN='{fen}'
                    ''')
                    temp = cursor.fetchall()
                    if temp == []:
                        book = False
                    else:
                        self.best_move = temp[0][2].split('-')
                        self.evaluation_res = temp[0][1]
                        board.analyse_pos = False
                        self.analyse_change = False
                        board.ai_turn = False # the AI has just found the best move
 
    def analysis_calculation(self):
        connection = None
        try:
            connection = sqlite3.connect('calculation.db') # establishing connection with the database that has the opening book in it
        except: # if the database isn't there for some reason, which shouldn't happen
            pass
        cursor = connection.cursor()
        aiboard = []
        book = True # this means that the program should look in the opening database to search for what the best move is 
        self.evaluation_res = None # this will be accessed by the board object that this is running in, so that it can be displayed
        self.best_move = None # this will be a string that will show what the best move is
        self.analyse_change = True # this means that the analyse button can be pressed and this should have effect
        self.ai_board = []
        while board.running: # as logn as the program is still running, and there has not yet been a checkmate 
            self.white_long_castle = board.white_long_castle
            self.black_long_castle = board.black_long_castle
            self.white_short_castle = board.white_short_castle
            self.black_short_castle = board.black_short_castle
            if board.board != aiboard: # this will mean that the position has changed from when the AI last looked at the board
                self.analyse_change = True
                while self.analyse_change == True:
                    temp = None
                    if book == False:
                        if board.analyse_pos == True:
                            self.ai_board = []
                            self.best_move = None
                            self.evaluation_res = None
                            aiboard = [] # setting up an empty board, so that we can put the board in there
                            for i in range(0,len(board.board)): # because we need to append each thing to the board
                                aiboard.append(board.board[i]) # appending that position of the board to the list
                                self.ai_board.append(board.board[i])
                            if board.move % 2 == 0:
                                colour = 'white'
                                max_player = True
                            else:
                                colour = 'black'
                                max_player = False
                            using = []
                            for i in range(0,len(aiboard)):
                                using.append(aiboard[i])
                            start = time.time()
                            final_eval = self.think_ahead(aiboard,3,max_player,board.white_long_castle,board.white_short_castle,board.black_long_castle,board.black_short_castle,None,False,-Infinity,Infinity)
                            end = time.time()
                            try:
                                self.evaluation_res = final_eval[0]
                                self.best_move = move_to_text(board.board,final_eval[1])
                                board.analyse_pos = False
                                self.analyse_change = False
                            except: # if the above doesn't work, then we have come out of the eval manually, and therefore we can press the analysis button again
                                pass # nothing is to happen if we come out of the above too early
                    else: # this means that we need to look into the book
                        for i in range(0,len(board.board)): 
                            aiboard.append(board.board[i])
                            self.ai_board.append(board.board[i])
                        fen = pos_to_FEN(board.board)
                        cursor.execute(f'''
                        SELECT * FROM 'opening_book' WHERE FEN='{fen}'
                        ''')
                        temp = cursor.fetchall()
                        if temp == []:
                            book = False
                        else:
                            self.best_move = temp[0][2].split('-')
                            self.evaluation_res = temp[0][1]
                            board.analyse_pos = False
                            self.analyse_change = False
 
    def get_move_as_text(self):
        try: # this will all run if there is a list that is passed in, which will be if it is a book move
            if self.best_move == None: # if we haven't done anything yet, or the computer is caculating
                return 'calculating'
            elif ord(self.best_move[0]) > 64: # if we need to see if there is a letter at the front
                return self.best_move
            else: # if none of this is true, then we need to turn it into text
                return move_to_text(self.ai_board,self.best_move)
        except:
            return move_to_text(self.ai_board,self.best_move)
 
    def get_eval_as_text(self):
        if self.evaluation_res == None:
            return 'calculating'
        else:
            return str(self.evaluation_res)
 
    def think_ahead(self,board1,depth,max_player,white_long_castle,white_short_castle,black_long_castle,black_short_castle,move,play,alpha,beta):
        top_move = []
        current_score = 0 # this will be changed when the static eval is returned
        # move will be in the format [startsquare,endsquare]
        if play == False:
            if board.analyse_pos == False:
                return
        if move == None: # this is the beggining of the calculation, which means that there is no move yet, and this is yet to be generated
            pass
        else: # now we need to make the move on the baord
            temp = self.move_handler(board1,move[0],move[1],white_long_castle,white_short_castle,black_long_castle,black_short_castle) # making the move and returning the board
            # we use temp above because the results will be given in a tuple
            board1 = temp[0] # resetting what everything is
            white_short_castle = temp[1]
            white_long_castle = temp[2]
            black_short_castle = temp[3]
            black_long_castle = temp[4]
        if depth == 0: # we have reached the bottom of the tree
            #self.count += 1
            return self.evaluation(board1),top_move # we then need to return the evaluation for that position because this is then how we will work up
        second_board = []
        if max_player == True: # now we know that it is the maximising player
            current_score = -Infinity
            legal_moves = self.find_legal_moves(board1,'white',None,white_long_castle,white_short_castle,black_long_castle,black_short_castle)
            legal_count = 0
            for move in legal_moves:
                if check_if_legal(move[0],move[1],'white',board1) == True:
                    legal_count += 1
            if legal_count == 0 and self.InCheck(board1,'white') == True:
                return -1000000000, top_move
            for move in legal_moves: # this will cycle through all of the legal moves
                if play == False:
                    if board.analyse_pos == False:
                        return
                second_board = []
                if check_if_legal(move[0],move[1],'white',board1) == True: # only if the move is allowed to be made
                    for i in range(0,len(board1)): # this needs to happen in this for loop because the board needs to reset for each time we need to make a move
                        second_board.append(board1[i]) # setting up the second board
                    store = self.think_ahead(second_board,depth-1,False,white_long_castle,white_short_castle,black_long_castle,black_short_castle,move,play,alpha,beta)
                    try:
                        score = store[0]
                        if score > current_score:
                            current_score = score
                            top_move = move
                        if top_move == []:
                            current_score = score
                            top_move = move
                        alpha = max(alpha,score) # if the score we found was better, then we want to use it
                        if beta <= alpha: # we know this is a branch we are never going down
                            break
                    except:
                        pass
 
        if max_player == False: # now we know that this is black
            current_score = Infinity # we use this absurdly high number because this means that the first time we look at the position, the position will be better than this
            legal_moves = self.find_legal_moves(board1,'black',None,white_long_castle,white_short_castle,black_long_castle,black_short_castle)
            legal_count = 0
            for move in legal_moves:
                if check_if_legal(move[0],move[1],'black',board1) == True:
                    legal_count += 1
            if legal_count == 0 and self.InCheck(board1,'black') == True:
                return 1000000000, top_move
            for move in legal_moves:
                if play == False:
                    if board.analyse_pos == False:
                        return
                second_board = []
                if check_if_legal(move[0],move[1],'black',board1) == True: 
                    for i in range(0,len(board1)): 
                        second_board.append(board1[i])
                    store = self.think_ahead(second_board,depth-1,True,white_long_castle,white_short_castle,black_long_castle,black_short_castle,move,play,alpha,beta)
                    try:
                        score = store[0]
                        if score < current_score:
                            current_score = score
                            top_move = move
                        if top_move == []:
                            current_score = score
                            top_move = move
                        beta  = min(beta,score) # this is a better route
                        if beta <= alpha: # we have a better option than this branch
                            break
                    except:
                        pass
        if play == False: # if we are doing the analysis
            if board.analyse_pos == False: # if the user has stopped the analysis, so that they can change the position
                return # we need to come out of the whole tree
        return current_score,top_move
                     
    def move_handler(self,board,startsquare,endsquare,white_long_castle,white_short_castle,black_long_castle,black_short_castle):
        board[endsquare] = board[startsquare] # moving the piece to the new square
        board[startsquare] = 0 # once the piece has been moved, there will no longer be anything on the original square
        # dealing with castling
        if board[endsquare] == 14: # we know that this is the white king moving, this means that it could be castling
            if white_long_castle == True: # it has the ablility to castle
                if startsquare == 4 and endsquare == 2: # this means that the king has castled
                    board[3] = 12 # moving the rook to the new square
                    board[0] = 0 # deleting the rook from where it was
            if white_short_castle == True: # if they have the ability to short castle
                if startsquare == 4 and endsquare == 6: # if they have short castled
                    board[5] = 12 # rook movement
                    board[7] = 0
            white_long_castle = False # because the white king has just moved, the king can no longer move
            white_short_castle = False
        elif board[endsquare] == 22:
            if black_long_castle == True:
                if startsquare == 60 and endsquare == 58: # king has castled long
                    board[59] = 20
                    board[56] = 0
            if black_short_castle == True:
                if startsquare == 60 and endsquare == 62:
                    board[61] = 20
                    board[63] = 0
            black_long_castle = False
            black_short_castle = False
        elif board[endsquare] == 12: # if the rook has moved then we need to change the castling again
            if startsquare == 0: # the rook from the left corner has moved
                white_long_castle = False
            elif startsquare == 7: # the rook from the right corner has moved
                white_short_castle = False
        elif board[endsquare] == 20: # dealing with the black rook
            if startsquare == 56:
                black_long_castle = False
            elif startsquare == [63]:
                black_short_castle = False
        if endsquare == 0: # the following four if statements are if a piece is moving to the squares of the rooks, and this will mean, if there is a change, that something has taken those rooks, which means taht the computer can no longer castle
            white_long_castle = False
        elif endsquare == 7:
            white_short_castle = False
        elif endsquare == 56:
            black_long_castle = False
        elif endsquare == 63:
            black_short_castle = False
         
        if board[4] != 14: # if the white king is not on its start square, then it can no longer castle 
            white_short_castle = False
            white_long_castle = False
        if board[60] != 22: # if the black king is not on its start square, then it can no longer castle 
            black_short_castle = False
            black_long_castle = False
        if board[56] != 20: # if the queenside rook has moved - black
            black_long_castle = False
        if board[63] != 20: # kingside rook has moved - black
            black_short_castle = False
        if board[0] != 12: # queenside rook has moved - white
            white_long_castle = False
        if board[7] != 12: # kingside rook has moved - white
            white_short_castle = False
        if (endsquare >= 56 and endsquare <= 63) and board[endsquare] == 9: # if the white pawn has reached the end of the board, then it becomes a queen
            board[endsquare] = 13
        if (endsquare >= 0 and endsquare <= 7) and board[endsquare] == 17: # if the black pawn has reached the end of the board, then it becomes a queen
            board[endsquare] = 21
        return board, white_short_castle,white_long_castle,black_short_castle,black_long_castle
 
    def find_legal_moves(self,board,colour,prev,white_long_castle,white_short_castle,black_long_castle,black_short_castle):
        legal_moves = [] # this will store all of the moves that we find as a 2D list, containing the start and end square of a piece
        pieces = [1,2,3,4,5,6] # this contains all of the possible values for pieces
        piece = Piece()
        if colour == 'white': # setting up what we need to take away from each piece
            subtract = 8
        else:
            subtract = 16   
 
        temp = [] # this is where all of the squares that a piece can move will go     
        for i in range(0,len(board)): # this will cycle over the board trying to find pieces that can move
            temp = []
            if (board[i] - subtract) in pieces: # now we know that we have found a piece that can move
                if (board[i]-subtract) == 1: # we know that we have found a pawn 
                    if colour == 'white': # white pawns move differently to black pawns
                        temp = piece.pawn_moves_white(i,board,None)
                    else:
                        temp = piece.pawn_moves_black(i,board,None)
                elif (board[i]-subtract) == 2: # knight
                    temp = piece.knight_moves(i,board)
                elif (board[i]-subtract) == 3: # bishop
                    temp = piece.diagonal_moves(i,board)
                elif (board[i]-subtract) == 4: # rook
                    temp = piece.horizontal_moves(i,board)
                elif (board[i]-subtract) == 5: # queen
                    temp = piece.queen_moves(i,board)
                elif (board[i]-subtract) == 6: # king
                    if colour == 'white': # we know that we need to find the moves for the white king
                        temp = piece.king_moves_white(i,board,white_long_castle,white_short_castle)
                    else:
                        temp = piece.king_moves_black(i,board,black_long_castle,black_short_castle)
            for j in range(0,len(temp)):
                legal_moves.append([i,temp[j]])
        return legal_moves
 
    def get_data(self,board,current_move,critical):
        self.board = board
        self.current_move = current_move
        self.critical = critical
 
    def evaluation(self,board): # this will run all of the evaluation functions on the board that is to be evaluated
        self.eval = 0 # this will then be changed when each eval function is called
        self.eval += self.evaluate_material(board) # this finds the material values
        self.eval += self.doubled_pawns(board,'white') # since the result of this is negative, adding it to the evaluation is the correct way to do it
        self.eval -= self.doubled_pawns(board,'black') # because the result is negative and we want thsi to make the score more positive, we need to subtract it
        self.eval += self.connected_pawns(board,'white')
        self.eval += self.pawn_chain(board,'white')
        self.eval += self.connected_pawns(board,'black') # the returned value will be negative because it is from the black side, which means that it must be added 
        self.eval -= self.pawn_chain(board,'black')
        self.eval += self.pawn_islands(board,'white') # again, the result is negative, so this makes it better for black, which is how it should be
        self.eval -= self.pawn_islands(board,'black') # making this better for white because of the negative output
        self.eval += self.isolated_pawns(board,'white') # negative
        self.eval -+ self.isolated_pawns(board,'black') # negative
        self.eval += self.backward_pawns_white(board) # negative
        self.eval -= self.backward_pawns_black(board) # negative
        self.eval -= self.central_pawns_black(board) # positive
        self.eval += self.central_pawns_white(board) # positive
        self.eval += self.evaluate_mobility(board,'white')
        self.eval -= self.evaluate_mobility(board,'black')
        self.eval += self.passed_pawns_white(board)
        self.eval -= self.passed_pawns_black(board)
        self.eval += self.controlling_enemy_squares_white(board)
        self.eval -= self.controlling_enemy_squares_black(board)
        self.eval += self.rook_on_open_file_white(board)
        self.eval -= self.rook_on_open_file_black(board)
        self.eval += self.rook_infiltration_white(board)
        self.eval -= self.rook_infiltration_black(board)
        self.eval += self.king_in_center_pen(board)
        self.eval += self.pawn_shield_and_storm_white(board)
        self.eval -= self.pawn_shield_and_storm_black(board)
        self.eval -= self.attackers_of_king_white(board)
        self.eval += self.attackers_of_king_black(board)
        self.eval /= 100
        self.eval = round(self.eval,2) # making it 2 d.p so that it will be able to compare quicker, and to make it not a really long number to be displayed for the user
        self.piece = Piece()
        return self.eval # so that we know what the score was
 
    def evaluate_material(self,board): # this goes over the board and finds the acctual material that is on the baord
        evaluation = 0
        white_bishop_count = 0 # these will show how many bishops we have found because we need to know if there are ar 2 of them for the bishop pair bonus
        black_bishop_count = 0 
        white_knight_count = 0 # we will need to know if we need to apply the knight pair penalty
        black_knight_count = 0
        for i in range(0,len(board)): # this will be what loops over the baord and finds all of the pieces to find the material eval
            if board[i] < 16 and board[i] > 0: # then the piece is white
                if board[i] == 9:
                    evaluation += self.pawn_val
                elif board[i] == 10:
                    evaluation += self.knight_val
                    white_knight_count += 1
                elif board[i] == 11:
                    evaluation += self.bishop_val
                    white_bishop_count += 1
                elif board[i] == 12:
                    evaluation += self.rook_val
                elif board[i] == 13:
                    evaluation += self.queen_val
            elif board[i] > 16:
                if board[i] == 17:
                    evaluation -= self.pawn_val
                elif board[i] == 18:
                    evaluation -= self.knight_val
                    black_knight_count += 1
                elif board[i] == 19:
                    evaluation -= self.bishop_val
                    black_bishop_count += 1
                elif board[i] == 20:
                    evaluation -= self.rook_val
                elif board[i] == 21:
                    evaluation -= self.queen_val
        if white_bishop_count >1:
            evaluation += self.bishop_pair_bonus
        if black_bishop_count > 1:
            evaluation -= self.bishop_pair_bonus
        if white_knight_count > 1:
            evaluation += self.knight_pair_penalty
        if black_knight_count > 1:
            evaluation -= self.knight_pair_penalty
        return evaluation
 
    def doubled_pawns(self,board,colour): # we need to put colour in here so that we can run this code twice, and save memory for the code, and we can find it for the correct colour
        penalty = 0 # this will store the total penalty for a side
        if colour == 'white':
            subtract = 8
        else:
            subtract = 16
        i = 0
        j = 0
        pawn_count = 0
        for i in range(0,8): # this will go along the ranks
            pawn_count = 0
            for j in range(1,8): # this will go up the file
                if board[i+(j*8)] - subtract == 1:
                    pawn_count += 1
            if pawn_count > 1:
                if pawn_count == 2:
                    penalty += self.doubled_pawn_penalty
                else:
                    penalty += self.tripled_pawn_penalty
        return penalty # this will be negative
 
    def connected_pawns(self,board,colour): # this means we are finding how many pawns are next to each other of the same colour 
        bonus = 0 # at the end of the subroutine, this will be returned, and it is the bonus that each side should recieve from their pawn chains
        count = 0 # this will keep track of how many pawns there are in a row
        start = False
        pawn_total = 0 # this will find how many pawns have been looked at, and will stop when it has looked at all pawns
        if colour == 'white':
            subtract = 8
        else:
            subtract = 16
        self.pawn_board = []
        for i in range(len(board)):
            if board[i] - subtract == 1:
                self.pawn_board.append(1)
            else:
                self.pawn_board.append(0)
         
        self.pawn_stop = self.pawn_board.count(1) # when pawn_total reaches this number, we know that we need to stop looking
        # now we have a board with a 1 where there is a white pawn
        current = 0
        for i in range(8,len(board)-8): # this will cycle through the pawn list and will find where there is a pawn, and if there is one, this will be handled inside this loop
            count = 0 # this will be reset after a pawn has been looked at (and therefore a pawn chain has been looked at)
            if self.pawn_board[i] == 1: # we have found a pawn and therefore we should start counting how many there are 
                pawn_total += 1
                self.pawn_board[i] = 0
                start = True
                count = 1
                current = i % 8 # this tells us which file we are on, and then this can be used to check that we are not at the end of the board
                while start == True: # this will find the number of pawns in a row, and as soon as the next square is not a pawn, this will be broken out of
                    current += 1 # we have moved along a file
                    if current == 7: # we will look at this last file, but no further if this is true
                        start = False # we can no longer look for any more pawns becuase we are at the right hand side of the baord
                    else:
                        if self.pawn_board[i+count] == 1:
                            pawn_total += 1
                            self.pawn_board[i+count] = 0
                            count += 1
                        else:
                            start = False
                        if pawn_total == self.pawn_stop:
                            start = False
                # now we have the length of a pawn chain
                if count > 1:
                    if colour == 'white': # we need to find the rank aswell and then find the bonus for that
                        bonus += count*10*((i//8)*0.5)
                    else:
                        bonus -= count*10*((7-(i//8))*0.5)
        return bonus
 
    def pawn_chain(self,board,colour): # this means we are finding the number of pawns that are connected diagonally, and there should also be a bonus for how far forward the highest pawn is on the pawn chain
        bonus = 0 
        count = 0
        start = False
        pawn_total = 0
        if colour == 'white':
            subtract = 8
        else:
            subtract = 16
        current = 0
        for i in range(8,len(board)-16):
            if board[i] - subtract == 1:
                self.pawn_board[i] = 1
        for i in range(8,len(board)-8): # this is going to cycle through the pawns
            count = 0
            if self.pawn_board[i] == 1:
                pawn_total += 1
                self.pawn_board[i] = 0
                start = True
                count = 1
                current = i % 8
                # going up and right
                while start == True:
                    current += 1
                    if current >= 7:
                        start = False
                    if self.pawn_board[i + (count*9)] == 1:
                        pawn_total += 1
                        self.pawn_board[i+(count*9)] = 0
                        count += 1
                    else:
                        start = False
                    if pawn_total == self.pawn_stop:
                        start = False
                if count > 1:
                    if colour == 'white':
                        bonus += count*10
                    else:
                        bonus -= count*10
                # now we need to do this for going up and left
                start = True
                count = 1
                current = i % 8
                while start == True:
                    current -= 1
                    if current <= 0:
                        start = False
                    else:
                        if self.pawn_board[i+(count*7)] == 1:
                            pawn_total += 1
                            self.pawn_board[i+(count*7)] = 0
                            count += 1
                        else:
                            start = False
                        if pawn_total == self.pawn_stop:
                            start = False
                if count > 1:
                    if colour == 'white':
                        bonus += count*10
                    else:
                        bonus -= count*10
            if pawn_total == self.pawn_stop:
                break
        return bonus
 
    def pawn_islands(self,board,colour):
        if colour == 'white':
            subtract = 8
        else:
            subtract = 16
        bonus = 0
        island_count = 0
        pawn_present = False
        self.pawn_board = [] # this is resetting it, because it will be changed multiple times anyway, so we might as well
        for i in range(0,8): # this will go along the files
            pawn_present = False
            for j in range(0,7): # this will change the ranks 
                if board[(j*8)+i] - subtract == 1:
                    pawn_present = True
                    break
            if pawn_present == True:
                self.pawn_board.append(1)
            else:
                self.pawn_board.append(0)
        start = False
        for i in range(0,8):
            if self.pawn_board[i] == 1: # we will now find how many gaps there are from position i
                for j in range(0,i):# this will remove all of the irrellevant gaps at the end which aren't going to contribute to the island count
                    del self.pawn_board[0]
                island_count = self.pawn_board.count(0) + 1
                break # after this is all done, we can break out of the for loop
        if island_count > 1: # now we need to find the penalty that is caused from all of these islands in the position
            if island_count == 2:
                bonus = -20
            elif island_count == 3:
                bonus = -50
            elif island_count == 4:
                bonus = -100
        return bonus
 
    def isolated_pawns(self,board,colour):
        if colour == 'white':
            subtract = 8
        else:
            subtract = 16
        bonus = 0
        pawn_present = False
        self.pawn_board = []
        for i in range(0,8):
            pawn_present = False
            for j in range(0,7): 
                if board[(j*8)+i] - subtract == 1:
                    pawn_present = True
                    break
            if pawn_present == True:
                self.pawn_board.append(1)
            else:
                self.pawn_board.append(0)
        pawn_present = False
        for i in range(0,8):
            # after the follwing if statement we will have found if there are any isolated pawns, after this is done, we will need to find how many there are on the file
            if self.pawn_board[i] == 1: # if there is a known pawn there, we need to find if there is a pawn on each side of that pawn, and then we can find how many pawns there are in that file afterwards
                if i == 0: # we know that this is on the edge of the board
                    if self.pawn_board[1] == 0:
                        pawn_present = True # this is a recycled variable, so that we don't have to waste any memory
                elif i == 7: # we also know that this is on the edge of the board
                    if self.pawn_board[6] == 0:
                        pawn_present = True
                else: # we know that the pawns have an adjacent file on either side and this can therefore be tracked
                    if self.pawn_board[i-1] == 0 and self.pawn_board[i+1] == 0:
                        pawn_present = True
                # the following if statement will find how many pawns there are on the file
                if pawn_present == True:
                    for j in range(1,7):
                        if board[i+j*8] - subtract == 1:
                            bonus -= 25
                pawn_present = False
        return bonus
 
    def backward_pawns_white(self,board):
        pawn_board = []
        for i in range(len(board)):
            if board[i] - 8 == 1:
                pawn_board.append(1)
            else:
                pawn_board.append(0)
        bonus = 0
        pawn_stop = pawn_board.count(1)
        pawn_total = 0
        poss = True
        position = 8
        ho = False # this stands for half open, which will be used to tell if the file that the backwards pawn is on is half open or not
        l = 0 # l stands for looking, and this will be the store of the square we are checking for pawns behind the pawn that has been found so that we can see if it is backwards or not
        while pawn_total < pawn_stop: # this will therefore run until we have looked at all of the pawns in the position
            poss = True # this means that every time, each one could be backwards
            if pawn_board[position] == 1: # we have found a pawn and therefor we need to find if there are any pawns that are behind it
                pawn_total += 1
                if position % 8 != 0: # it will run this piece of code if we are not on the edge of the baord
                    l = position - 1
                    while l > 7: # this will allow l to decrease until it reaches the bottom of the baord where there will be no pawns
                        if pawn_board[l] == 1: # we have found a pawn that is behind the pawn, therefore we can break out of this while loop
                            l = 6
                            poss = False
                        else:
                            l -= 8 # this is so that we are looking behind the pawn that we have just found, which means that we need to go down the baord, hence the minus sign instead of a plus sign that we might expect
                if position % 8 != 7 and poss == True: # if there is still the posibility that the pawn is backwards, and it isn't on the 8th rank
                    l = position + 1
                    while l > 7: # this will allow l to decrease until it reaches the bottom of the baord where there will be no pawns
                        if pawn_board[l] == 1: # we have found a pawn that is behind the pawn, therefore we can break out of this while loop
                            l = 6
                            poss = False
                        else:
                            l -= 8
                # we don't need to exclude isolated pawns because all isolated pawns will be backwards pawns, so I have therefore reduced the penalty of isolated pawns because they will be penaltied twice
                if poss == True:
                    bonus -= 25
                    #now we need to find if the backwards pawn is on a half-open file, and if it is, we need to find if there is a queen or rook that can therefore attack it and then apply a penalty
                    ho = True
                    temp = position + 8
                    while temp < 64:
                        if board[temp]-16 == 1:
                            ho = False
                        temp += 8
                    if ho == True:
                        for i in range(len(board)-1,-1,-1):
                            if board[i] == 20 or board[i] == 21:
                                bonus -= 25
                                break
            position += 1
        return bonus
     
    def backward_pawns_black(self,board):
        pawn_board = []
        for i in range(len(board)):
            if board[i] - 16 == 1:
                pawn_board.append(1)
            else:
                pawn_board.append(0)
        bonus = 0
        pawn_stop = pawn_board.count(1)
        pawn_total = 0
        poss = True
        position = 55
        ho = False # this stands for half open, which will be used to tell if the file that the backwards pawn is on is half open or not
        l = 0 # l stands for looking, and this will be the store of the square we are checking for pawns behind the pawn that has been found so that we can see if it is backwards or not
        while pawn_total < pawn_stop: # this will therefore run until we have looked at all of the pawns in the position
            poss = True # this means that every time, each one could be backwards
            if pawn_board[position] == 1: # we have found a pawn and therefor we need to find if there are any pawns that are behind it
                pawn_total += 1
                if position % 8 != 0: # it will run this piece of code if we are not on the edge of the baord
                    l = position - 1
                    while l < 56: # this will allow l to increase until we reach the 'top' of the baord, which will be the 56th position in the list
                        if pawn_board[l] == 1: # we have found a pawn that is behind the pawn, therefore we can break out of this while loop
                            l = 64
                            poss = False
                        else:
                            l += 8 # we are using a plus sign so that we can go up the baord and find if there are any pawns 'behind' the pawn that we have jsut found
                if position % 8 != 7 and poss == True:
                    l = position + 1
                    while l < 56:
                        if pawn_board[l] == 1: # we have found a pawn that is behind the pawn, therefore we can break out of this while loop
                            l = 64
                            poss = False
                        else:
                            l += 8
                # we don't need to exclude isolated pawns because all isolated pawns will be backwards pawns, so I have therefore reduced the penalty of isolated pawns because they will be penaltied twice
                if poss == True:
                    bonus -= 25
                    #now we need to find if the backwards pawn is on a half-open file, and if it is, we need to find if there is a queen or rook that can therefore attack it and then apply a penalty
                    ho = True
                    temp = position - 8
                    while temp > 7:
                        if board[temp]-8 == 1:
                            ho = False
                        temp -= 8
                    if ho == True:
                        for i in range(len(board)-1,-1,-1):
                            if board[i] == 12 or board[i] == 13:
                                bonus -= 25
                                break
            position -= 1
        return bonus
         
    def central_pawns_white(self,board): # this will find if there are any pawns in the center for white
        bonus = 0
        for i in range(26,30):
            if board[i] == 9: 
                bonus += 10
        for i in range(34,38):
            if board[i] == 9:
                bonus += 10
        for i in range(27,29):
            if board[i] == 9:
                bonus += 5
        for i in range(35,37):
            if board[i] == 9:
                bonus += 5
        return bonus # returning the bonus
 
    def central_pawns_black(self,board): # this will find if there are any pawns in the center for black
        bonus = 0
        for i in range(26,30):
            if board[i] == 17: 
                bonus += 10
        for i in range(34,38):
            if board[i] == 17:
                bonus += 10
        for i in range(27,29):
            if board[i] == 17:
                bonus += 5
        for i in range(35,37):
            if board[i] == 17:
                bonus += 5
        return bonus # returning the bonus
 
    def evaluate_mobility(self,board,colour): # it is better to have more mvoes than the opponent, because it usually means that you have more freedom than your opponent, and this is a good thing
        # we need to have the colour because it makes a difference to the pawn movement of the side, which is important in mobility
        bonus = 0 # this will be changed when we have the total number of moves that can be made
        total = 0 # this will be changed when we find pieces, and then the length of this will be found, which will be the basis for what the bonus is 
        temp = None
        p1 = Piece() # this is so that the mvoes list can be found for each peice that we find on the board
        if colour == 'white':
            subtract = 8
        else:
            subtract = 16
        for i in range(0,len(board)): # this will cycle through the board and find if there is a piece on that square, and then it can find the legal moves for that piece
            if board[i] != 0: # there is a piece on this square
                found = board[i] - subtract # this will stop us needing to find baord[i] - subtract multiple times, which should increase the efficiency of the program
                if found > 0 and found < 7: # this means that we have found a piece that is of the colour that we are trying to find
                    if found == 1:
                        if subtract == 8: # now we know that the pawn we have found is white, and that means that it has to move in a specific direction
                            temp = p1.pawn_moves_white(i,board,None)
                        else: # now we know that the pawn is black, so we have to call the relevant subroutine
                            temp = p1.pawn_moves_black(i,board,None)
                    elif found == 2: # we have found a knight 
                        #temp = p1.knight_moves(i,board)
                        total += self.knight_positioning[i]
                    elif found == 3: # we have found a bishop
                        temp = p1.diagonal_moves(i,board)
                    elif found == 4: # we have found a rook
                        temp = p1.horizontal_moves(i,board)
                    elif found == 5: # we have found a queen
                        temp = p1.queen_moves(i,board)
                    elif found == 6: # we have found a king
                        temp = p1.king_moves_base(i,board,colour)
                        if colour == 'white':
                            total += self.king_positioning_white[i]
                        else:
                            total += self.king_positioning_black[i]
                    try:
                        total += len(temp)
                    except:
                        pass
        bonus += total
        return bonus
 
    def passed_pawns_white(self,board):
        temp = None # this will be used to keep track of where we are searching for when looking for black pawns in front of the pawn that has just been found
        passed = True # this will be changed to False if we find that it shoudl be a passed pawn
        passed_board = [0,0,0,0,0,0,0,0]
        bonus = 0
        for i in range(8,56): # this will cycle over the board and find all of the pawns
            passed = True
            if board[i] == 9: # a pawn has been found
                temp = i+8
                while temp < 56: # when it gets over 55 it will be on the final rank, which means that it won't be a pawn any more
                    if board[temp] == 17:
                        passed = False
                    temp += 8
                if passed == True and i%8 !=0:
                    temp = i - 1
                    while temp < 56:
                        if board[temp] == 17:
                            passed = False
                        temp += 8 
                if passed == True and i%8 != 7:
                    temp = i + 1
                    while temp < 56:
                        if board[temp] == 17:
                            passed = False
                        temp += 8
                if passed == True:
                    passed_board[i%8] = 1
                    bonus += 25
                    if i%8 != 0: # if we aren't on the left edge of the board
                        if board[i-9] == 9:
                            bonus += 1 # if there is a pawn protecting this passed pawn, then we need to give it a bonus
                    if i%8 != 7: # if we aren't on the right side of the board
                        if board[i-7] == 9:
                            bonus += 10
                    bonus += (i//8)*0.5 # this adds a bonus for how progressed the passed pawn is
        passed = False # we are going to reuse this for finding when we have found our first passed pawn
        count = 0 # this will be used to find how many connected passed pawns there are
        for i in range(0,len(passed_board)):
            count = 0
            if passed_board[i] == 1:
                count += 1
                passed = True
                while passed == True and (i + count) < 8:
                    if passed_board[i+count] == 1:
                        passed_board[i+count] = 0
                        count += 1
                    else:
                        passed = False
                if count > 1: # now we know that we need to give an extra bonus for connected passed pawns
                    bonus += count*10 # this is so that when there are connected passed pawns, there is another bonus 
        return bonus
 
    def passed_pawns_black(self,board):
        temp = None # this will be used to keep track of where we are searching for when looking for black pawns in front of the pawn that has just been found
        passed = True
        passed_board = [0,0,0,0,0,0,0,0]
        bonus = 0
        for i in range(8,56): # this will cycle over the board and find all of the pawns
            if board[i] == 17: # a pawn has been found
                temp = i+8
                while temp > 7: # when this gets below 7, we have gone below where we need to search
                    if board[temp] == 9:
                        passed = False
                    temp -= 8
                if passed == True:
                    temp = i - 1
                    while temp > 7:
                        if board[temp] == 9:
                            passed = False
                        temp -= 8 
                if passed == True:
                    temp = i + 1
                    while temp < 56:
                        if board[temp] == 9:
                            passed = False
                        temp += 8
                if passed == True:
                    passed_board[i%8] = 1
                    bonus += 25
                    if i%8 != 0:
                        if board[i+7] == 17:
                            bonus += 1
                    if i%8 != 7:
                        if board[i+9] == 17:  
                            bonus += 10  
                    bonus += (8-(i//2))*0.5 
        passed = False # we are going to reuse this for finding when we have found our first passed pawn
        count = 0 # this will be used to find how many connected passed pawns there are
        for i in range(0,len(passed_board)):
            count = 0
            if passed_board[i] == 1:
                count += 1
                passed = True
                while passed == True and (i + count) < 8:
                    if passed_board[i+count] == 1:
                        passed_board[i+count] = 0
                        count += 1
                    else:
                        passed = False
                if count > 1: # now we know that we need to give an extra bonus for connected passed pawns
                    bonus += count*10
        return bonus
 
    def controlling_enemy_squares_white(self,board): # this will find how many of the enemy squares white controls, and this will be beneficial to them 
        bonus = 0
        attacked_squares = []
        for i in range(0,len(board)):
            attacked_squares.append(0)
        piece = Piece()
        attacked_squares = piece.find_attacked_squares(board,'white',attacked_squares)
        for i in range(32,len(board)): # this will loop over the whole of the black side and see where white attacks, then there will be a bom=nus given
            if attacked_squares[i] == 1:
                bonus += 20
        # now that we have attacked squares, this can be used to find any pieces that are not defended
        for i in range(0,len(board)):
            if board[i] > 8 and board[i] < 15: # this means that we have found one of the white pieces
                if attacked_squares[i] == 0:
                    bonus -= 30
        return bonus
 
    def controlling_enemy_squares_black(self,board): # this will find how many of the enemy squres black controls, and this will also be beneficial to them 
        bonus = 0
        attacked_squares = []
        for i in range(0,len(board)):
            attacked_squares.append(0)
        piece = Piece()
        attacked_squares = piece.find_attacked_squares(board,'black',attacked_squares)
        for i in range(32,-1,-1): # this will loop over the whole of the white side and see where white attacks, then there will be a bom=nus given
            if attacked_squares[i] == 1:
                bonus += 20
        #having attacked squares now lets us look at where our pieces are and find if there are any undefended pieces
        for i in range(0,len(board)):
            if board[i] > 16: # now we have found one of the black pieces
                if attacked_squares[i] == 0:
                    bonus -= 30
        return bonus
 
    def rook_on_open_file_white(self,board): # a rook is most powerful on an open file, and while this will be shown by controling more enemy squares, it would be useful to give a little extra encouragement to the computer 
        bonus = 0
        temp = None
        open_file = True
        doubled = False # this will turn true if there are doubled rooks, and then we know that there are two rooks on the open file if this ends up being true
        rook_count = 0
        for i in range(0,len(board)): # cycling over the whole baord
            open_file = True
            if board[i] == 12: # this shows we have found a rook
                rook_count += 1
                temp = i + 8
                while temp < 64:
                    if board[temp] == 9: # we have found one of our own pawns, which means we are not on an open file
                        temp = 70 # exits the loop, without a bonus 
                        open_file = False
                    elif board[temp] == 17:
                        open_file = False
                        bonus += 20
                        temp = 70
                    elif board[temp] == 12:
                        bonus += 30
                        rook_count += 1
                        doubled = True
                    temp += 8
                if open_file == True:
                    bonus += 40
                    if doubled == True:
                        bonus += 40
                if rook_count == 2:
                    break
        return bonus
 
    def rook_on_open_file_black(self,board):
        bonus = 0
        temp = None
        open_file = True
        doubled = False
        rook_count = 0
        for i in range(len(board)-1,-1,-1):
            open_file = True
            if board[i] == 20: # this shows we have found a rook
                rook_count += 1
                temp = i - 8
                while temp >= 0:
                    if board[temp] == 17: # we have found one of our own pawns, which means we are not on an open file
                        temp = -1 # exits the loop, without a bonus 
                        open_file = False
                    elif board[temp] == 9:
                        open_file = False
                        bonus += 20
                        temp = -1
                    elif board[temp] == 20:
                        bonus += 30
                        rook_count += 1
                        doubled = True
                    temp -= 8
                if open_file == True:
                    bonus += 40
                    if doubled == True:
                        bonus += 40
                if rook_count == 2:
                    break
        return bonus
 
    def rook_infiltration_white(self,board): # this will see if there is a white rook on the 7th rank, because this will be good for white, because infiltrations will allow them to target enemy pawns, and attack the king
        bonus = 0
        for i in range(48,56): # searching the 7th rank
            if board[i] == 12: # we have found a rook
                bonus += 40 # a bonus for having the rook on the seventh rank
        return bonus
 
    def rook_infiltration_black(self,board):
        bonus = 0
        for i in range(8,16):
            if board[i] == 20:
                bonus += 40
        return bonus
 
    def pawn_shield_and_storm_white(self,board): # this is refering to the pawns in front of the king, becuase when there are these pawns, this will provide the king with more safety
        # the pawn_storm is being done in this aswell, so that we don't have to find the king multiple times, which will make the program a lot more time efficient
        bonus = 0
        for i in range(0,len(board)):
            if board[i] == 14: # we have found the king, and now we need to see if there are any pawns in front of them
                try: # this is to keep any edge cases form occuring, because if for some reason the white king is at the top of the board, such as when promoting a pawn, then the program will crash, because this index will be out of range
                    if board[i+8] == 0 and board[i+16] == 0: # if there is a pawn directly in front of the king
                        bonus -= 30
                except: # if that cannot be done, then the king is at the top of the board, so nothing can be done
                    pass
                try: 
                    if i % 8 != 0: # this means that the king is not on the far left side of the board
                        if board[i+7] == 0 and board[i+15] == 0: 
                            bonus -= 30
                        if i%8 != 0:  
                            pass
                except: 
                    pass
                try: 
                    if i % 8 != 7: # this means that the king is not on the far right side of the board
                        if board[i+9] == 0 and board[i+17] == 0: 
                            bonus -= 30
                        if i%8 != 0:  
                            pass
                except: 
                    pass
                # now we need to find out if there is a pawn storm heading our way, this will be done by finding where the pawns from directly infront, and from either side are, and see how close these are. This will be key to the safety of the king
                # right in front
                temp = i + 8 # this will be changed while we search for pawns
                while temp < 56:
                    if board[temp] == 17: # we have found a pawn, and now we can put in the bonus based on how far away it is
                        bonus -= (7-(temp//8)) *0.2 # this will find which rank it is on, and then it will multiply this by 0.2 to find the bonus 
                        temp = 200 # this means that the while loop will be exited, this has been made 200, so now we can know that if temp is not equal to 208, there will not be a pawn, and will therefore be an semi-open file towards the king
                    temp += 8
                # finding out if there are any open or semi-open files towards the king
                if temp != 208: # we know there is not a pawn, which means there is a semi open file
                    bonus -= 130 #this is assuming this is a fully open file, this will then be reduced if we find a white pawn that is in fact blocking the open file
                    for j in range(8+(i%8),49+(i%8),8): # looking at the possible areas for a white pawn
                        if board[j] == 9: # we have found a white pawn on the file
                            bonus += 65 # now it is no longer a fully open file, which means there is less of an advantage to black
                # to the left
                if i%8 != 0:
                    temp = i - 1
                    while temp < 56:
                        if board[temp] == 17:
                            bonus -= (7-(temp//8)) *0.2
                            temp = 200 
                        temp += 8
                    if temp != 208:
                        bonus -= 130 
                        for j in range(8+(temp%8),49+(temp%8),8): 
                            if board[j] == 9: 
                                bonus += 65
                # to the right
                if i%8 != 7:
                    temp = i + 1
                    while temp < 56:
                        if board[temp] == 17:
                            bonus -= (7-(temp//8)) *0.2
                            temp = 200 
                        temp += 8
                    if temp != 208:
                        bonus -= 130 
                        for j in range(8+(temp%8),49+(temp%8),8):
                            if board[j] == 9: 
                                bonus += 65
                return bonus # this will then break out of the subroutine once everything that needs to happen is completed
 
    def pawn_shield_and_storm_black(self,board):
        bonus = 0
        for i in range(len(board)-1,-1,-1):
            if board[i] == 22: # we have found the king, and now we need to see if there are any pawns in front of them
                try: # this is to keep any edge cases form occuring, because if for some reason the white king is at the top of the board, such as when promoting a pawn, then the program will crash, because this index will be out of range
                    if board[i-8] == 0 and board[i-16] == 0: # if there is a pawn directly in front of the king
                        bonus -= 30
                except: # if that cannot be done, then the king is at the top of the board, so nothing can be done
                    pass
                try: 
                    if i % 8 != 0: # this means that the king is not on the far left side of the board
                        if board[i-7] == 0 and board[i-15] == 0: 
                            bonus -= 30
                        if i%8 != 0:  
                            pass
                except: 
                    pass
                try: 
                    if i % 8 != 7: # this means that the king is not on the far right side of the board
                        if board[i-9] == 0 and board[i-17] == 0: 
                            bonus -= 30
                        if i%8 != 0:  
                            pass
                except: 
                    pass
                # now we need to find out if there is a pawn storm heading our way, this will be done by finding where the pawns from directly infront, and from either side are, and see how close these are. This will be key to the safety of the king
                # right in front
                temp = i - 8 # this will be changed while we search for pawns
                while temp > 7:
                    if board[temp] == 9: # we have found a pawn, and now we can put in the bonus based on how far away it is
                        bonus -= (temp//8) *0.2 # this will find which rank it is on, and then it will multiply this by 0.2 to find the bonus 
                        temp = -200 # this means that the while loop will be exited, this has been made 200, so now we can know that if temp is not equal to 208, there will not be a pawn, and will therefore be an semi-open file towards the king
                    temp -= 8
                # finding out if there are any open or semi-open files towards the king
                if temp != -208: # we know there is not a pawn, which means there is a semi open file
                    bonus -= 130 #this is assuming this is a fully open file, this will then be reduced if we find a white pawn that is in fact blocking the open file
                    for j in range(49+(temp%8),8+(temp%8),-8): # looking at the possible areas for a white pawn
                        if board[j] == 17: # we have found a white pawn on the file
                            bonus += 65 # now it is no longer a fully open file, which means there is less of an advantage to black
                # to the left
                if i%8 != 0:
                    temp = i - 1
                    while temp > 7:
                        if board[temp] == 9:
                            bonus -= (temp//8) *0.2
                            temp = -200 
                        temp -= 8
                    if temp != -208:
                        bonus -= 130 
                        for j in range(49+(temp%8),8+(temp%8),-8): 
                            if board[j] == 17: 
                                bonus += 65
                # to the right
                if i%8 != 7:
                    temp = i + 1
                    while temp > 7:
                        if board[temp] == 9:
                            bonus -= (temp//8) *0.2
                            temp = -200 
                        temp -= 8
                    if temp != -208:
                        bonus -= 130 
                        for j in range(49+(temp%8),8+(temp%8),-8):
                            if board[j] == 17:
                                bonus += 65
                return bonus
 
    def attackers_of_king_white(self,board): # this will find how many pieces are directed at their king, because the more there are, the less safe the king is
        bonus = 0
        king_zone = [] # this will become a collection of squares that are around the king, and if these are found to be attacked, then we need to add the piece to the number of attackers
        for i in range(0,len(board)): # this will put the squares around the king into the king_zone list
            if board[i] == 14:
                if (i%8) != 0:
                    king_zone.append(i-1)
                    try:
                        king_zone.append(i+7)
                        king_zone.append(i+15)
                    except:
                        pass
                if (i%8) != 7:
                    king_zone.append(i+1)
                    try:
                        king_zone.append(i+9)
                        king_zone.append(i+17)
                    except:
                        pass
                try:
                    king_zone.append(i+8)
                    king_zone.append(i+16)
                except:
                    pass
        bonus = self.king_zone_attackers_white(board,king_zone)/100
        return bonus
     
    def attackers_of_king_black(self,board):
        bonus = 0
        king_zone = [] # this will become a collection of squares that are around the king, and if these are found to be attacked, then we need to add the piece to the number of attackers
        for i in range(len(board)-1,-1,-1): # this will put the squares around the king into the king_zone list
            if board[i] == 22:
                if (i%8) != 0:
                    king_zone.append(i-1)
                    try:
                        king_zone.append(i-9)
                        king_zone.append(i-17)
                    except:
                        pass
                if (i%8) != 7:
                    king_zone.append(i+1)
                    try:
                        king_zone.append(i-7)
                        king_zone.append(i-15)
                    except:
                        pass
                try:
                    king_zone.append(i-8)
                    king_zone.append(i-16)
                except:
                    pass
        bonus = self.king_zone_attackers_black(board,king_zone)/100
        return bonus
 
    def king_zone_attackers_black(self,board,king_zone):
        attack_weight = 0 # this will go up for each attacking piece, and this will be dependent on which piece it is that is attackeing the zone
        number_of_attackers = 0 # this will keep track of how many pieces are attacking the kings zone
        squares = 0 # this keeps track of how many squares inside the king zone a piece is attacking
        piece = Piece()
        store = [] # this will be where we store which squares are attacked
        increased = False # this will allow us to only increment the number of attackers once per attacker
        number_inside = 0 # this will keep track of how many squares the piece attacks into
        ref = None # this will let the program know which position to look for to make the penalty
        for i in range(0,len(board)):
            increased = False # reset for each piece
            number_inside = 0 # reset for each piece
            ref = 0
            store = []
            if board[i] > 16: # this isn't an enemy piece
                pass # we also already give a bonus for the pawns, so there isn't one needed for this
            elif board[i] == 10: # we have found a knight
                store = piece.knight_attacked_squares(i)
                ref = 2
            elif board[i] == 11: # bishop
                store = piece.diagonal_attacked_squares(i,board)
                ref = 3
            elif board[i] == 12: # rook
                store = piece.horizontal_attacked_squares(i,board)
                ref = 4
            elif board[i] == 13: # queen
                store = piece.queen_attacked_squares(i,board)
                ref = 5
            for j in range(0,len(store)): # cycling through the attacked squares
                if store[j] in king_zone: # if the square that is attacked is in the king zone
                    if increased == False: # if we have not already increased it for this piece yet
                        number_of_attackers += 1
                    increased = True # now this won't affect the number of attackers any more
                    number_inside += 1
            attack_weight += number_inside*self.king_attackers_constant[ref]
        if number_of_attackers > 7:
            number_of_attackers = 7 # because anything more than this is irrelevant
        return attack_weight*(self.no_king_attackers[number_of_attackers-1]) # this is the penalty for the king having attackers
 
    def king_in_center_pen(self,board): # this will find if either of the kings are on their origional start square, becuase this should receive and penalty
        bonus = 0
        if board[4] == 14: # this means that the white king is on the start square
            bonus -= 35
        if board[60] == 22:
            bonus += 35 
        return bonus
 
    def king_zone_attackers_white(self,board,king_zone):
        attack_weight = 0 # this will go up for each attacking piece, and this will be dependent on which piece it is that is attackeing the zone
        number_of_attackers = 0 # this will keep track of how many pieces are attacking the kings zone
        squares = 0 # this keeps track of how many squares inside the king zone a piece is attacking
        piece = Piece()
        store = [] # this will be where we store which squares are attacked
        increased = False # this will allow us to only increment the number of attackers once per attacker
        number_inside = 0 # this will keep track of how many squares the piece attacks into
        ref = None # this will let the program know which position to look for to make the penalty
        for i in range(0,len(board)):
            increased = False # reset for each piece
            number_inside = 0 # reset for each piece
            ref = 0
            store = []
            if board[i] < 18: # this isn't an enemy piece
                pass # we also already give a bonus for the pawns, so there isn't one needed for this
            elif board[i] == 18: # we have found a knight
                store = piece.knight_attacked_squares(i)
                ref = 2
            elif board[i] == 19: # bishop
                store = piece.diagonal_attacked_squares(i,board)
                ref = 3
            elif board[i] == 20: # rook
                store = piece.horizontal_attacked_squares(i,board)
                ref = 4
            elif board[i] == 21: # queen
                store = piece.queen_attacked_squares(i,board)
                ref = 5
            for j in range(0,len(store)): # cycling through the attacked squares
                if store[j] in king_zone: # if the square that is attacked is in the king zone
                    if increased == False: # if we have not already increased it for this piece yet
                        number_of_attackers += 1
                    increased = True # now this won't affect the number of attackers any more
                    number_inside += 1
            attack_weight += number_inside*self.king_attackers_constant[ref]
        if number_of_attackers > 7:
            number_of_attackers = 7 # because anything more than this is irrelevant
        return attack_weight*(self.no_king_attackers[number_of_attackers-1]) # this is the penalty for the king having attackers
 
    def development_eval(self,board):
        penalty = 0
        if board[0] == 12:
            penalty -= 10
        if board[1] == 10:
            penalty -= 20
        if board[2] == 12:
            penalty -= 20
        if board[3] == 13:
            penalty -= 20
        if board[5] == 11:
            penalty -= 20
        if board[6] == 10:
            penalty -= 20
        if board[7] == 12:
            penalty -= 10
        if board[56] == 20:
            penalty += 10
        if board[57] == 18:
            penalty += 20
         
 
    def InCheck(self,board,colour):
        attacked_board_template = []
        for i in range(0,len(board)):
            attacked_board_template.append(0)
        in_check = False
        king_store = None # this will store where the king is 
        if colour == 'white':
            subtract = 8
            other_colour = 'black'
        else:
            subtract = 16
            other_colour = 'white'
        for i in range(0,len(board)): # this will cycle over the whole board
            if board[i] - subtract == 6:
                king_store = i # now we have the position of the king of the colour we are looking for 
                break
        for i in range(0,len(board)): # thsi is to look over the whole board again, but to
            temp = self.piece.find_attacked_squares(board,other_colour,attacked_board_template)
            try:
                if temp[king_store] == 1:
                    return True
            except:
                pass
 
        return False
 
class Board(threading.Thread):
    def set(self, display_colour,move,ai_colour):
        self.running = True
        self.analysis = False # when this is first initialised, we need to have this so that it doesn't automatically go into analysis mode 
        self.ai_turn = False
        self.white_long_castle = True
        self.black_long_castle = True
        self.white_short_castle = True
        self.black_short_castle = True
        self.display_colour = display_colour
        self.move = move
        self.ai_colour = ai_colour
        self.white_pawn = pygame.image.load(os.path.join('Images','white pawn.png'))
        self.white_knight = pygame.image.load(os.path.join('Images','white knight.png'))
        self.white_bishop = pygame.image.load(os.path.join('Images','white bishop.png'))
        self.white_rook = pygame.image.load(os.path.join('Images','white rook.png'))
        self.white_queen = pygame.image.load(os.path.join('Images','white queen.png'))
        self.white_king = pygame.image.load(os.path.join('Images','white king.png'))
        self.black_pawn = pygame.image.load(os.path.join('Images','black pawn.png'))
        self.black_knight = pygame.image.load(os.path.join('Images','black knight.png'))
        self.black_bishop = pygame.image.load(os.path.join('Images','black bishop.png'))
        self.black_rook = pygame.image.load(os.path.join('Images','black rook.png'))
        self.black_queen = pygame.image.load(os.path.join('Images','black queen.png'))
        self.black_king = pygame.image.load(os.path.join('Images','black king.png'))
        self.pieces = [self.black_pawn, self.black_knight, self.black_bishop, self.black_rook, self.black_queen, self.black_king,
        self.white_pawn, self.white_knight, self.white_bishop, self.white_rook, self.white_queen, self.white_king]
  
    def get_data(self,move,colour):
        self.move = move
        self.colour = colour
 
    def FEN_to_position(self, FEN):
        self.characters = ['p','n','b','r','q','k','P','N','B','R','Q','K']
        self.values = [17,18,19,20,21,22,9,10,11,12,13,14]
        self.board = []
        self.fen = FEN
        self.fenl = self.fen.split('/')
        self.fenfl = [] # fl means full list, because it is when the fen is fully split and can be operated on
        self.fenl.reverse()
        for i in range(0,8):
            temp = list(self.fenl[i])
            for j in range(0,len(temp)):
                self.fenfl.append(temp[j])
        for i in range(0,len(self.fenfl)):
            if self.fenfl[i] in self.characters:
                self.board.append(self.values[self.characters.index(self.fenfl[i])])
            else:
                for i in range(0,int(self.fenfl[i])):
                    self.board.append(0)
        return self.board
    
    def draw_board(self, window):
        window.fill(dark)
        for i in range(0,row):
            if i%2 == 0: # the if statements here will determine if the drawing of the squares should start at the first square or on the second
                start = 0
            else:
                start = 1
            for j in range(start,row,2):
                pygame.draw.rect(window, light,[i*square_size, j*square_size, square_size, square_size])
        # highlighting self.piece_clicked_square
        if self.piece_clicked_square != None:
            if self.display_colour == 'white':
                y = 81*(7-((self.piece_clicked_square-(self.piece_clicked_square%8))/8)) # this is the y value
                x = (81*(self.piece_clicked_square%8)) # this is the x value
            else:
                y = 81*((self.piece_clicked_square-(self.piece_clicked_square%8))/8) # this is the y position for the piece
                x = 244+(325-(81*(self.piece_clicked_square%8))) # this is the x position for the piece
            highlight = Button(81.25,81.25,yellow,x,y,'')
            highlight.draw(window)
 
    def promotion_window(self,window):
        queen_select = Button(162.5,650,dark,0,0,'Queen')
        rook_select = Button(162.5,650,light,0,162.5,'Rook')
        bishop_select = Button(162.5,650,dark,0,325,'Bishop')
        knight_select = Button(162.5,650,light,0,487.5,'Knight')
        queen_select.draw(window)
        rook_select.draw(window)
        bishop_select.draw(window)
        knight_select.draw(window)
                 
    def display_pieces(self, window):
        if self.display_colour == 'white':
            for i in range(0,len(self.board)):
                if self.board[i] in self.values:
                    y = 81*(7-((i-(i%8))/8)) # this is the y value
                    x = (81*(i%8)) # this is the x value
                    window.blit(self.pieces[self.values.index(self.board[i])],(x,y))
                else:
                    pass
        else:
            for i in range(0,len(self.board)):
                if self.board[i] in self.values:
                    y = 81*((i-(i%8))/8) # this is the y position for the piece
                    x = 244+(325-(81*(i%8))) # this is the x position for the piece
                    window.blit(self.pieces[self.values.index(self.board[i])],(x,y))
                else:
                    pass
        try:
            self.eval_display.draw(window)
            if self.analyse_pos == False:
                self.analyse_button.draw(window)
            else:
                self.stop_analyse_button.draw(window)
            self.best_move_display.draw(window)
        except:
            pass
  
    def find_square_clicked(self,mouse_pos):
        self.mouse_pos = mouse_pos
        if self.display_colour == 'white':
            mouse_x = self.mouse_pos[0]
            mouse_y = self.mouse_pos[1]
            x,y = int(mouse_x//81.25), int(7 - (mouse_y//81.25))
        else:
            mouse_x = 650 - mouse_pos[0]
            mouse_y = 650 - mouse_pos[1]
            x,y = int(mouse_x//81.25), int(7 - (mouse_y//81.25))
        self.square_clicked = (8*y) + x
     
    def find_all_attacked_squares(self,board,colour): # not tested
        self.attacked_squares = []
        for i in range(0,len(board)):
            self.attacked_squares.append(0)
        piece = Piece()
        self.attacked_squares1 = piece.find_attacked_squares(board,colour,self.attacked_squares)
        return self.attacked_squares
 
    def check_if_legal(self,startsquare,endsquare,colour,board):
        king_store = None # this will be where we keep the location of the king that we want to see if they are in check
        legal_check = False
        attacked_colour = None
        king_check = None # this is so that we know which value we are looking for
        if colour == 'white':
            attacked_colour = 'black'
            king_check = 14
        else:
            attacked_colour = 'white'
            king_check = 22
        attacked_squares = []
        for i in range(0,len(board)):
            attacked_squares.append(0)
        temp_board = []
        for i in range(0,len(board)):
            temp_board.append(board[i])
        temp_board[endsquare] = temp_board[startsquare]
        temp_board[startsquare] = 0
        piece = Piece()
        attacked_squares = piece.find_attacked_squares(temp_board,attacked_colour,attacked_squares)
        #finding the location of the king
        i = 0
        king_store = temp_board.index(king_check)
        if attacked_squares[king_store] == 0:
            legal_check = True
        return legal_check
 
    def check_for_mate(self,colour,board):
        self.temp_board = []
        for i in range(0,len(board)):
            self.temp_board.append(board[i])
        mate = True # this will be changed if we find a legal move
        king_store = None
        ocolour = None
        moves = None
        subtract = 0
        attacked_squares = []
        for i in range(0,len(board)):
            attacked_squares.append(0)
        if colour == 'white':
            ocolour = 'black'
            subtract = 16
        else:
            ocolour = 'white'
            subtract = 8
        i = 0
        while i < len(board):
            if board[i]-subtract == 6:
                king_store = i
                i = len(board)
            i += 1
        piece = Piece()
        attacked_squares = piece.find_attacked_squares(board,colour,attacked_squares) # now we have found all of the attacked squares of the side that has just moved
        if attacked_squares[king_store] == 1:
            if ocolour == 'white':
                moves = piece.king_moves_white(king_store,board,None,None) # we make these none, because if the king is in check then it isn't allowed to castle
            else:
                moves = piece.king_moves_black(king_store,board,None,None)
            i = 0 # this will be used for cycling through the list moves
            while i < len(moves):
                if attacked_squares[moves[i]] == 0: # this means that there is a square the king can move to that isn't being attacked
                    i = len(moves)
                    mate = False
                i += 1
        else: # the king isn't in check so it isn't mate
            mate = False
        if mate == True: # this will be entered if there is no move for the king to make
            moves = [] # we are reusing the variable that was used earlier to store all of the legal moves that the king has
            moves = piece.find_legal_moves_in_check(board,ocolour,moves,self.prev_move) # now we have a list of all of the possible moves (excluding if they are legal or not)
            for i in range(0,len(moves)): # this will allow us to go through every peice that is able to move
                for j in range(0,len(moves[i][1])): # this will allow us to cycle through the legal moves that each peice can make
                    legal = self.check_if_legal(moves[i][0],moves[i][1][j],ocolour,board)
                    if legal == True:
                        mate = False
        return mate,attacked_squares
 
    def move_handler(self,startsquare,endsquare,prev,board):
        board[endsquare] = board[startsquare]
        board[startsquare] = 0
        if board[endsquare] == 9 and prev != None: # if the piece that has just moved is a white pawn and there is the possibility to en passent
            if endsquare == startsquare + 7 or endsquare == startsquare + 9: # if the pawn has just moved diagonally
                if endsquare == prev + 8:
                    board[prev] = 0
        elif board[endsquare] == 17 and prev != None: # if the piece that has just moved is a white pawn and there is the possibility to en passent
            if endsquare == startsquare - 7 or endsquare == startsquare - 9: # if the pawn has just moved diagonally
                if endsquare == prev - 8:
                    board[prev] = 0
        if self.ai_turn == False:
            if self.piece_clicked == 14: # if it is the white king that moved 
                if startsquare == 4 and endsquare == 6 and self.white_short_castle == True:
                    board[5] = board[7]
                    board[7] = 0
                if startsquare == 4 and endsquare == 2 and self.white_long_castle == True:
                    board[3] = board[0]
                    board[0] = 0
                self.white_short_castle = False # it cannot castle any more
                self.white_long_castle = False
            elif self.piece_clicked == 22: # if it is the black king that moved
                if startsquare == 60 and endsquare == 62 and self.black_short_castle == True:
                    board[61] = board[63]
                    board[63] = 0
                if startsquare == 60 and endsquare == 58 and self.black_long_castle == True:
                    board[59] = board[56]
                    board[56] = 0
                self.black_long_castle = False # it can no longer castle
                self.black_short_castle = False
         
        if self.ai_colour == 'white' and board[endsquare] == 14: # the white side has just moved, and it was the king, and the ai is white
            if startsquare == 4 and endsquare == 2 and board[endsquare] == 14:
                board[3] = 12
                board[0] = 0
                self.white_long_castle = False
                self.white_short_castle = False
            if startsquare == 4 and endsquare == 6 and board[endsquare] == 14:
                board[5] = 12
                board[7] = 0
                self.white_long_castle = False
                self.white_short_castle = False
        if self.ai_colour == 'black' and board[endsquare] == 22:
            if startsquare == 60 and endsquare == 62 and board[endsquare] == 22:
                board[61] = 20
                board[63] = 0
                self.black_long_castle = False
                self.black_short_castle = False
            if startsquare == 60 and endsquare == 58 and board[endsquare] == 22:
                board[59] = 20
                board[56] = 0
                self.black_long_castle = False
                self.black_short_castle = False
 
        if self.ai_turn == False: # the user has just made a move
            if endsquare >= 56 and endsquare <= 63 and board[endsquare] == 9: # these two are if the user is going to have to promote
                pass
            elif endsquare >= 0 and endsquare <= 7 and board[endsquare] == 17:
                pass
            else:
                self.ai_turn = True
        else: # it was the AI that just moved
            if endsquare >= 56 and endsquare <= 63 and board[endsquare] == 9:
                board[endsquare] = 13
            if endsquare >= 0 and endsquare <= 7 and board[endsquare] == 17:
                board[endsquare] = 21
            self.ai_turn = False
 
    def click_handle(self,jclicked):
        ended = False
        if self.move % 2 == 0:
            subtract = 8
            colour = 'white'
        else:
            subtract = 16
            colour = 'black'
        done = 0
        piece = Piece()
        self.jclicked = self.square_clicked
        # the following has an r after it because this is the reduced one, and this means that it is the one that is irrespective of colour when subtract is taken off it
        self.piecesr = [1,2,3,4,5,6] # we are using this instead of values because we want to use subtract at some point and make sure that the square we clicked is in this list
        if self.clicked == True:
            if self.jclicked == self.piece_clicked_square:
                self.clicked = False
            elif self.board[self.jclicked] > 16 and colour == 'black' or self.board[self.jclicked] < 16 and self.board[self.jclicked] > 0 and colour == 'white':
                self.piece_clicked = self.board[self.square_clicked]
                self.piece_clicked_square = self.square_clicked # this is so that we can use this as the startsquare when we call the moves code and the movement handler
                if self.piece_clicked - subtract in self.piecesr: # change this to be in self.pieces at some point when it allows movement of pieces
                    self.clicked = True
            else:
                if self.piece_clicked-subtract == 1:
                    if subtract == 8:
                        self.moves_list = piece.pawn_moves_white(self.piece_clicked_square,self.board,self.prev_move)
                    else:
                        self.moves_list = piece.pawn_moves_black(self.piece_clicked_square,self.board,self.prev_move)
                elif self.piece_clicked-subtract == 2:
                    self.moves_list = piece.knight_moves(self.piece_clicked_square,self.board)
                elif self.piece_clicked-subtract == 3:
                    self.moves_list = piece.diagonal_moves(self.piece_clicked_square,self.board)
                elif self.piece_clicked-subtract == 4:
                    self.moves_list = piece.horizontal_moves(self.piece_clicked_square,self.board)
                elif self.piece_clicked-subtract == 5:
                    self.moves_list = piece.queen_moves(self.piece_clicked_square,self.board)
                elif self.piece_clicked-subtract == 6:
                    if subtract == 8:
                        self.moves_list = piece.king_moves_white(self.piece_clicked_square,self.board,self.white_long_castle,self.white_short_castle)
                    else:
                        self.moves_list = piece.king_moves_black(self.piece_clicked_square,self.board,self.black_long_castle,self.black_short_castle)
                legal_check = self.check_if_legal(self.piece_clicked_square,self.jclicked,colour,self.board)
                if self.jclicked in self.moves_list and legal_check == True:
                    self.move_handler(self.piece_clicked_square,self.jclicked,self.prev_move,self.board)
                    self.move += 1
                    returned = self.check_for_mate(colour,self.board)
                    ended = returned[0]
                    attacked = returned[1]
                    if subtract == 8 and self.piece_clicked == 14: # if it is the white king that moved 
                        self.white_short_castle = False # it cannot castle any more
                        self.white_long_castle = False
                    elif subtract == 16 and self.piece_clicked == 22: # if it is the black king that moved
                        self.black_long_castle = False # it can no longer castle
                        self.black_short_castle = False
                    if subtract == 8 and self.jclicked == 2 and self.piece_clicked == 14 and self.white_long_castle == True: # if the white king castled then the rook will also move
                        self.move_handler(0,3,None,self.board)
                    elif subtract == 8 and self.jclicked == 6 and self.piece_clicked == 14 and self.white_short_castle == True:
                        self.move_handler(7,5,None,self.board)
                    elif subtract == 16 and self.jclicked == 58 and self.piece_clicked == 22 and self.black_long_castle == True:
                        self.move_handler(56,59,None,self.board)
                    elif subtract == 16 and self.jclicked == 62 and self.piece_clicked == 22 and self.black_short_castle == True:
                        self.move_handler(63,61,None,self.board)
                    elif self.piece_clicked == 12:
                        if self.piece_clicked_square == 0:
                            self.white_long_castle = False
                        elif self.piece_clicked_square == 7:
                            self.white_short_castle = False
                    elif self.piece_clicked == 20:
                        if self.piece_clicked_square == 56:
                            self.black_long_castle = False
                        elif self.piece_clicked_square == 63:
                            self.black_short_castle = False
                    if self.jclicked == 0:
                        self.white_long_castle = False
                    elif self.jclicked == 7:
                        self.white_short_castle = False
                    elif self.jclicked == 56:
                        self.black_long_castle = False
                    elif self.jclicked == 63:
                        self.black_short_castle = False
                    if self.piece_clicked == 9 and self.piece_clicked_square >= 8 and self.piece_clicked_square <= 15: # if it was a pawn that is white and started on the second rank
                        if self.jclicked >= 24 and self.jclicked <= 31: # if the move is up 2 squares
                            self.prev_move = self.jclicked # so we know that the previous move was a 2 upward pawn move and we know the end square
                    elif self.piece_clicked == 17 and self.piece_clicked_square >= 48 and self.piece_clicked_square <= 55: 
                        if self.jclicked >= 32 and self.jclicked <= 39:
                            self.prev_move = self.jclicked
                    else: # if the move wouldn't allow en passent next move
                        self.prev_move = None # now if the pawn moves look at it, there won't be the option for en passent
                    if self.piece_clicked == 9 and self.jclicked >= 56:
                        self.promoting = True
                    elif self.piece_clicked == 17 and self.jclicked <= 7:
                        self.promoting = True
                done = 1
        if self.clicked == False:
            self.piece_clicked = self.board[self.square_clicked]
            self.piece_clicked_square = self.square_clicked # this is so that we can use this as the startsquare when we call the moves code and the movement handler
            if self.piece_clicked - subtract in self.piecesr: # change this to be in self.pieces at some point when it allows movement of pieces
                self.clicked = True
            else:
                self.piece_clicked_square = None
        if done == 1:
            self.clicked = False
            self.piece_clicked_square = None
        if self.board[4] != 14:
            self.white_short_castle = False
            self.white_long_castle = False
        if self.board[60] != 22:
            self.black_short_castle = False
            self.black_long_castle = False
        return ended
 
    def promotion_click_handle(self,y):
        piece = None
        if y >= 0 and y < 162.5:
            piece = 5
        elif y >= 162.5 and y <= 325:
            piece = 4
        elif y >= 325 and y <= 487.5:
            piece = 3
        elif y >= 487.5 and y <650:
            piece = 2
        self.promoting = False
        if (self.move-1)%2 == 0: # since we have already incremented the move this will be it being white that just moved
            piece += 8
        else: # this is now blacks move
            piece += 16
        self.board[self.jclicked] = piece
        self.ai_turn = True
         
    def find_all_legal_moves(self,board,colour,moves,prev):
        if colour == 'white':
            subtract = 8
        else:
            subtract = 16
        piece = Piece()
        piece_values = [1,2,3,4,5,6]
        store = None # this will store the peice on the baord
        store2 = None # this will store the attacked squares of a piece 
        temp = [] # this will become a 2D list that will have the startsquare as the first element and then have the moves as the second element
        for i in range(0,len(board)):
            temp = [] # so it will be reset each time
            if board[i] == 0: # if there is no piece
                pass
            else:
                store = board[i] - subtract
                if store in piece_values: # if there is a piece of the colour being attacked
                    if store == 1:
                        if colour == 'white':
                            store2 = piece.pawn_moves_white(i,board,prev)
                        else:
                            store2 = piece.pawn_moves_black(i,board,prev)
                    elif store == 2:
                        store2 = piece.knight_moves(i,board)
                    elif store == 3:
                        store2 = piece.diagonal_moves(i,board)
                    elif store == 4:
                        store2 = piece.horizontal_moves(i,board)
                    elif store == 5:
                        store2 = piece.queen_moves(i,board)
                    elif store == 6:
                        if colour == 'white':
                            store2 = piece.king_moves_white(i,board,self.white_long_castle,self.white_short_castle)
                        else:
                            store2 = piece.king_moves_black(i,board,self.black_long_castle,self.black_short_castle)
                    if len(store2)!=0:
                        temp.append(i)
                        temp.append(store2)
                        moves.append(temp)
        return moves
     
    def analyse(self): # this is so that the user can play against the computer 
        self.analyse_button = Button(100,200,light,700,250,'ANALYSE')
        self.stop_analyse_button = Button(100,200,red,700,250,'STOP')
        self.width = 1000
        self.ai_turn = False
        if __name__=='__main__':
            self.analyse_pos = False # this will be initially set to flase, and when it becomes true, this will set off the computer to analyse the position
            self.clicked = False
            self.piece_clicked = None
            self.piece_clicked_square = None
            self.moves_list = []
            self.promoting = False
            self.prev_move = None
            window = pygame.display.set_mode((self.width, height))
            pygame.display.set_caption('CHESS')
            self.running = True
            t1 = threading.Thread(target = ai.analysis_calculation)
            t1.start()
            clock = pygame.time.Clock()
            while self.running:
                self.best_move_display = Button(100,200,light,700,450,ai.get_move_as_text())
                self.eval_display = Button(100,100,dark,750,50,ai.get_eval_as_text())
                clock.tick(60)
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        self.running = False
                    elif event.type == MOUSEBUTTONDOWN:
                        mouse_pos = pygame.mouse.get_pos()
                        if mouse_pos[0] > 650: # this means that we have clicked off the board, so we need to see if the analyse button has been pressed
                            if mouse_pos[0] >= 700 and mouse_pos[0] <= 900:
                                if mouse_pos[1] >= 250 and mouse_pos[1] <= 350:
                                    if ai.analyse_change == True:
                                        if self.analyse_pos == True:
                                            self.analyse_pos = False
                                        else:
                                            self.analyse_pos = True
                        else:
                            if self.analyse_pos == False:
                                if self.promoting == False:
                                    self.find_square_clicked(mouse_pos)
                                    finished = self.click_handle(self.clicked)
                                else: 
                                    self.promotion_click_handle(mouse_pos[1])
                                if finished == True:
                                    self.running = False
                            else:
                                pass
                if self.promoting == False:
                    self.draw_board(window)
                    self.display_pieces(window)
                     
                else:
                    self.promotion_window(window)
                pygame.display.update()
 
    def user_vs_ai(self):
        if __name__=='__main__':
            self.ai_turn = False
            self.clicked = False
            self.piece_clicked = None
            self.piece_clicked_square = None
            self.moves_list = []
            self.promoting = False
            self.prev_move = None
            window = pygame.display.set_mode((width, height))
            pygame.display.set_caption('CHESS')
            self.running = True
            t1 = threading.Thread(target = ai.play_calculation)
            t1.start()
            clock = pygame.time.Clock()
            if self.move == 0 and self.ai_colour == 'white':
                self.ai_turn = True
            while self.running:
                if self.board[4] != 14:
                    self.white_long_castle = False
                    self.white_short_castle = False
                if self.board[0] != 12:
                    self.white_long_castle = False
                if self.board[7] != 12:
                    self.white_short_castle = False
                if self.board[60] != 22:
                    self.black_long_castle = False
                    self.black_short_castle = False
                if self.board[56] != 20:
                    self.black_long_castle = False
                    if self.board[63] != 20:
                        self.black_short_castle = False
                clock.tick(60)
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        self.running = False
                    elif event.type == MOUSEBUTTONDOWN: 
                        mouse_pos = pygame.mouse.get_pos()
                        if self.ai_turn == False:
                            if self.promoting == False:
                                self.find_square_clicked(mouse_pos)
                                finished = self.click_handle(self.clicked)
                            else: 
                                self.promotion_click_handle(mouse_pos[1])
                            if finished == True:
                                self.running = False
                if ai.best_move != None: # this means that the AI has found the best move, and the program now needs to make that move
                    self.move_handler(int(ai.best_move[0]),int(ai.best_move[1]),None,self.board)
                    ai.best_move = None
                    self.ai_turn = False
                    self.move += 1
                if self.promoting == False:
                    self.draw_board(window)
                    self.display_pieces(window)
                else:
                    self.promotion_window(window)
                pygame.display.update()
 
class Piece():
    def __init__(self):
        pass
 
    def find_legal_moves_in_check(self,board,colour,moves,prev): # we have to use a different one because the king behaviour will be different when in check
        if colour == 'white':
            subtract = 8
        else:
            subtract = 16
        piece_values = [1,2,3,4,5,6]
        store = None # this will store the peice on the baord
        store2 = None # this will store the attacked squares of a piece 
        temp = [] # this will become a 2D list that will have the startsquare as the first element and then have the moves as the second element
        for i in range(0,len(board)):
            temp = [] # so it will be reset each time
            if board[i] == 0: # if there is no piece
                pass
            else:
                store = board[i] - subtract
                if store in piece_values: # if there is a piece of the colour being attacked
                    if store == 1:
                        if colour == 'white':
                            store2 = self.pawn_moves_white(i,board,prev)
                        else:
                            store2 = self.pawn_moves_black(i,board,prev)
                    elif store == 2:
                        store2 = self.knight_moves(i,board)
                    elif store == 3:
                        store2 = self.diagonal_moves(i,board)
                    elif store == 4:
                        store2 = self.horizontal_moves(i,board)
                    elif store == 5:
                        store2 = self.queen_moves(i,board)
                    elif store == 6:
                        if colour == 'white':
                            store2 = self.king_moves_white(i,board,None,None)
                        else:
                            store2 = self.king_moves_black(i,board,None,None)
                    if len(store2)!=0:
                        temp.append(i)
                        temp.append(store2)
                        moves.append(temp)
        return moves
 
    def find_attacked_squares(self,board,colour,attacked_board): # colour means the colour that we are trying to find the attacked squares for
        # this finds the attacked squares of all of the pieces of one of the colours (the one that is given)
        if colour == 'white':
            subtract = 8
        else:
            subtract = 16
        piece_values = [1,2,3,4,5,6]
        store = None # this will store the peice on the baord
        store2 = None # this will store the attacked squares of a piece 
        for i in range(0,len(board)):
            if board[i] == 0:
                pass
            else:
                store = board[i] - subtract
                if store in piece_values:
                    if store == 1:
                        if colour == 'white':
                            store2 = self.pawn_attacked_squares_white(i) # we know that the starting square of the piece is going to be the square we found it on, and that means i 
                        else:
                            store2 = self.pawn_attacked_squares_black(i)
                    elif store == 2:
                        store2 = self.knight_attacked_squares(i)
                    elif store == 3:
                        store2 = self.diagonal_attacked_squares(i,board)
                    elif store == 4:
                        store2 = self.horizontal_attacked_squares(i,board)
                    elif store == 5:
                        store2 = self.queen_attacked_squares(i,board)
                    elif store == 6:
                        store2 = self.king_attacked_squares(i)
                if store2 != None:
                    for j in range(0,len(store2)):
                        try:
                            attacked_board[store2[j]] = 1
                        except:
                            pass
        return attacked_board
 
    def pawn_moves_white(self,startsquare, board,prev):
        moves_list = []
        startsquare = startsquare # this is so that we know where the beggining square is
        board = board # this is so that we can see what else is on the baord, because that will determine where the peice can move to
        temp = startsquare + 8
        position = 0
        try:
            if board[temp] == 0:
                moves_list.append(temp)
                if startsquare >= 8 and startsquare<=15:
                    temp = startsquare + 16
                    position = 1
                    if board[temp] == 0:
                        moves_list.append(temp)
            position = 2
            if startsquare%8 != 0:
                temp = startsquare+7
                if board[temp] > 16:
                    moves_list.append(temp)
            position = 3
            if startsquare%8 != 7:
                temp = startsquare+9
                if board[temp]>16:
                    moves_list.append(temp)
            position = 4
            if prev != None: # if there is the possiblity for en passent
                if prev == startsquare - 1:
                    moves_list.append(startsquare + 7)
                elif prev == startsquare + 1:
                    moves_list.append(startsquare + 9)
            i = 0
            while i < len(moves_list):
                if moves_list[i] > 63:
                    del moves_list[i]
                else:
                    i += 1
            return moves_list
        except:
            pass
    
    def pawn_moves_black(self,startsquare,board,prev):
        moves_list = []
        temp = startsquare - 8
        if board[temp] == 0:
            moves_list.append(temp)
            if startsquare >= 48 and startsquare <=55:
                temp = startsquare - 16
                if board[temp] == 0:
                    moves_list.append(temp)
        if startsquare%8 != 0:
            temp = startsquare - 9
            if board[temp] < 16 and board[temp] > 0:
                moves_list.append(temp)
        if startsquare%8 != 7:
            temp = startsquare - 7
            if board[temp] < 16 and board[temp] > 0:
                moves_list.append(temp)
        if prev != None:
            if prev == startsquare - 1:
                moves_list.append(startsquare - 9)
            elif prev == startsquare + 1:
                moves_list.append(startsquare - 7)
        i = 0
        while i < len(moves_list):
            if moves_list[i] < 0:
                del moves_list[i]
            else:
                i += 1
        return moves_list
     
    def knight_moves(self,startsquare, board):
        colour = None
        temp_piece = [1,2,3,4,5,6]
        base = 0
        if board[startsquare]<16:
            colour = 'white'
            subtract = 8
        else:
            colour = 'black'
            subtract = 16
        temp = startsquare
        moves_list = []
        check = startsquare%8
        if check > 1:
            try:
                if board[temp+6]-subtract not in temp_piece:
                    moves_list.append(temp+6)
            except:
                pass
            try:
                if board[temp-10]-subtract not in temp_piece:
                    moves_list.append(temp-10)
            except:
                pass
        if check > 0:
            try:
                if board[temp+15]-subtract not in temp_piece:
                    moves_list.append(temp+15)
            except:
                pass
            try:
                if board[temp-17]-subtract not in temp_piece:
                    moves_list.append(temp-17)
            except:
                pass
        if check < 6:
            try:
                if board[temp+10]-subtract not in temp_piece:
                    moves_list.append(temp+10)
            except:
                pass
            try:
                if board[temp-6]-subtract not in temp_piece:
                    moves_list.append(temp-6)
            except:
                pass
        if check < 7:
            try:
                if board[temp+17]-subtract not in temp_piece:
                    moves_list.append(temp+17)
            except:
                pass
            try:
                if board[temp-15]-subtract not in temp_piece:
                    moves_list.append(temp-15)
            except:
                pass
        i = 0
        while i < len(moves_list):
            if moves_list[i] > 63:
                del moves_list[i]
            else:
                i += 1
        i = 0
        while i < len(moves_list):
            if moves_list[i] < 0:
                del moves_list[i]
            else:
                i += 1
        return moves_list
 
    def horizontal_moves(self,startsquare, board):
        if board[startsquare] >= 16:
            colour = 'black'
        else:
            colour = 'white'
        moves_list = []
        leftmob = startsquare%8
        rightmob = 7-leftmob
        # this is for going left
        temp = startsquare
        i = 0
        while i < leftmob:
            temp-=1
            if board[temp] == 0:
                moves_list.append(temp)
                i += 1
            else:
                if colour == 'white':
                    if board[temp] > 16:
                        moves_list.append(temp)
                    i = leftmob
                else:
                    if board[temp] < 16:
                        moves_list.append(temp)
                    i = leftmob
        # this is for going right  
        i = 0     
        temp = startsquare
        while i < rightmob:
            temp+=1
            if board[temp] == 0:
                moves_list.append(temp)
                i += 1
            else:
                if colour == 'white':
                    if board[temp] > 16:
                        moves_list.append(temp)
                    i = rightmob
                else:
                    if board[temp] < 16:
                        moves_list.append(temp)
                    i = rightmob
         
        # for going down 
        temp = startsquare
        while temp >= 8:
            temp -= 8
            if board[temp] == 0:
                moves_list.append(temp)
            else:
                if colour == 'white':
                    if board[temp] > 16:
                        moves_list.append(temp)
                else:
                    if board[temp] < 16:
                        moves_list.append(temp)
                temp = -1
        # for going up
        temp = startsquare
        while temp < 56:
            temp += 8
            if board[temp] == 0:
                moves_list.append(temp)
            else:
                if colour == 'white':
                    if board[temp] > 16:
                        moves_list.append(temp)
                else:
                    if board[temp] < 16:
                        moves_list.append(temp)
                temp = 65
        return moves_list
         
    def diagonal_moves(self,startsquare, board):
        moves_list = []
        temp = startsquare
        leftmob = startsquare%8
        rightmob = 7 - leftmob
        if board[startsquare] >= 16:
            colour = 'black'
        else:
            colour = 'white'
        # for going up and left
        temp = startsquare
        i = 0
        while i < leftmob:
            temp += 7 
            if temp > 63:
                i = leftmob
            else:
                if board[temp] == 0:
                    moves_list.append(temp)
                else:
                    if colour == 'white':
                        if board[temp] > 16:
                            moves_list.append(temp)
                    else:
                        if board[temp] < 16:
                            moves_list.append(temp)
                    i = leftmob
                i += 1
        # for going down and left
        temp = startsquare
        i = 0
        while i < leftmob:
            temp -= 9
            if temp < 0:
                i = leftmob
            else:
                if board[temp] == 0:
                    moves_list.append(temp)
                else:
                    if colour == 'white':
                        if board[temp] > 16:
                            moves_list.append(temp)
                    else:
                        if board[temp] < 16:
                            moves_list.append(temp)
                    i = leftmob
            i += 1
        # for going up and right
        temp = startsquare
        i = 0
        while temp%8 < 7:
            temp += 9 
            if temp > 63:
                temp = 7
            else:
                if board[temp] == 0:
                    moves_list.append(temp)
                else:
                    if colour == 'white':
                        if board[temp] > 16:
                            moves_list.append(temp)
                    else:
                        if board[temp] < 16:
                            moves_list.append(temp)
                    temp = 7
        # for going down and right
        temp = startsquare
        i = 0
        while temp%8 < 7:
            temp -= 7 
            if temp < 0:
                temp = 7
            else:
                if board[temp] == 0:
                    moves_list.append(temp)
                else:
                    if colour == 'white':
                        if board[temp] > 16:
                            moves_list.append(temp)
                    else:
                        if board[temp] < 16:
                            moves_list.append(temp)
                    temp = 7
        return moves_list
 
    def king_moves_base(self,startsquare,board,colour): # not tested
        attacked_list = []
        moves_list = []
        if startsquare < 56:
            if colour == 'white':
                if board[startsquare + 8] == 0 or board[startsquare + 8] > 15:
                    moves_list.append(startsquare + 8)
            else:
                if board[startsquare + 8] == 0 or board[startsquare + 8] < 16:
                    moves_list.append(startsquare + 8)
            if startsquare % 8 != 0:
                if colour == 'white':
                    if board[startsquare + 7] == 0 or board[startsquare + 7] > 15:
                        moves_list.append(startsquare + 7)
                else:
                    if board[startsquare + 7] == 0 or board[startsquare + 7] < 16:
                        moves_list.append(startsquare + 7)
            if startsquare % 8  != 7:
                if colour == 'white':
                    if board[startsquare + 9] == 0 or board[startsquare + 9] > 15:
                        moves_list.append(startsquare + 9)
                else:
                    if board[startsquare + 9] == 0 or board[startsquare + 9] < 16:
                        moves_list.append(startsquare + 9)
         
        if startsquare > 7:
            if colour == 'white':
                if board[startsquare - 8] == 0 or board[startsquare - 8] > 15:
                    moves_list.append(startsquare - 8)
            else:
                if board[startsquare - 8] == 0 or board[startsquare - 8] < 16:
                    moves_list.append(startsquare - 8)
            if startsquare % 8 != 0:
                if colour == 'white':
                    if board[startsquare - 9] == 0 or board[startsquare - 9] > 15:
                        moves_list.append(startsquare-9)
                else:
                    if board[startsquare - 9] == 0 or board[startsquare - 9] < 16:
                        moves_list.append(startsquare-9)
            if startsquare != 7:
                if colour == 'white':
                    if board[startsquare - 7] == 0 or board[startsquare - 7] > 15:
                        moves_list.append(startsquare-7)
                else:
                    if board[startsquare - 7] == 0 or board[startsquare - 7] < 16:
                        moves_list.append(startsquare - 7)
         
        if startsquare % 8 != 0:
            if colour == 'white':
                if board[startsquare - 1] == 0 or board[startsquare - 1] > 15:
                    moves_list.append(startsquare - 1)
            else:
                if board[startsquare - 1] == 0 or board[startsquare - 1] < 16:
                    moves_list.append(startsquare - 1)
        if startsquare % 8 != 7:
            if colour == 'white':
                if board[startsquare + 1] == 0 or board[startsquare + 1] > 15:
                    moves_list.append(startsquare + 1)
            else:
                try:
                    if board[startsquare + 1] == 0 or board[startsquare + 1] < 16:
                        moves_list.append(startsquare + 1)
                except:
                    pass
 
        return moves_list
 
    def king_moves_white(self,startsquare, board, long_castle, short_castle):
        # we need to have long and short castle so we can see if it is allowed
        attacked_squares = []
        for i in range(0,len(board)):
            attacked_squares.append(0)
        moves_list = self.king_moves_base(startsquare,board,'white')
        if short_castle == True: # now we need to check that all of the squares in between are cleared and that they aren't on the attacked squares of the opponenet
            # checking that the king isn't in check
            if board[5] == 0 and board[6] == 0: # then we move onto the next phase of finding if it's legal. This bit makes sure that the coast is clear for the king to go through and that no peices are there 
                attacked_squares = self.find_attacked_squares(board,'black',attacked_squares) # this finds all of the attacked squares from black
                if attacked_squares[4] == 0 and attacked_squares[5] == 0 and attacked_squares[6] == 0: # this makes sure the king is not in check and that the king will not go through check when it castles
                    moves_list.append(6)
 
        if long_castle == True:
            if board[1] == 0 and board[2] == 0 and board[3] == 0:
                attacked_squares = self.find_attacked_squares(board,'black',attacked_squares)
                if attacked_squares[2] == 0 and attacked_squares[3] == 0 and attacked_squares[4] == 0:
                    moves_list.append(2)
         
        return moves_list
 
    def king_moves_black(self,startsquare, board, long_castle, short_castle): # not tested
        attacked_squares = []
        for i in range(0,len(board)):
            attacked_squares.append(0)
        moves_list = self.king_moves_base(startsquare,board,'black')
        if short_castle == True:
            if board[61] == 0 and board[62] == 0: 
                attacked_squares = self.find_attacked_squares(board,'white',attacked_squares)
                if attacked_squares[60] == 0 and attacked_squares[61] == 0 and attacked_squares[62] == 0:
                    moves_list.append(62)
 
        if long_castle == True:
            if board[57] == 0 and board[58] == 0 and board[59] == 0:
                attacked_squares = self.find_attacked_squares(board,'white',attacked_squares)
                if attacked_squares[58] == 0 and attacked_squares[59] == 0 and attacked_squares[60] == 0:
                    moves_list.append(58)
         
        return moves_list
 
    def queen_moves(self,startsquare,board):
        moves_list = []
        temp = self.horizontal_moves(startsquare,board)
        for i in range(0,len(temp)):
            moves_list.append(temp[i])
        temp = self.diagonal_moves(startsquare,board)
        for i in range(0,len(temp)):
            moves_list.append(temp[i])
        return moves_list
 
    def pawn_attacked_squares_white(self,startsquare):
        attacked_squares = []
        pfile = startsquare%8
        if startsquare <= 55:
            if pfile != 0:
                attacked_squares.append(startsquare+7)
            if pfile != 7:
                attacked_squares.append(startsquare+9)
        return attacked_squares
 
    def pawn_attacked_squares_black(self,startsquare):
        attacked_squares = []
        pfile = startsquare%8
        if startsquare >= 8:
            if pfile != 0:
                attacked_squares.append(startsquare-9)
            if pfile != 7:
                attacked_squares.append(startsquare-7)
        return attacked_squares
 
    def knight_attacked_squares(self,startsquare):
        temp = startsquare
        attacked_squares = []
        check = startsquare%8
        if check > 1:
            attacked_squares.append(temp+6)
            attacked_squares.append(temp-10)
            if check > 0:
                attacked_squares.append(temp+15)
                attacked_squares.append(temp-17)
        if check < 6:
            attacked_squares.append(temp+10)
            attacked_squares.append(temp-6)
            if check < 7:
                attacked_squares.append(temp+17)
                attacked_squares.append(temp-15)
        i = 0
        while i < len(attacked_squares):
            if attacked_squares[i] > 63:
                del attacked_squares[i]
            else:
                i += 1
        i = 0
        while i < len(attacked_squares):
            if attacked_squares[i] < 0:
                del attacked_squares[i]
            else:
                i += 1
        return attacked_squares
 
    def horizontal_attacked_squares(self,startsquare,board):
        attacked_squares = []
        leftmob = startsquare%8
        rightmob = 7-leftmob
        # this is for going left
        temp = startsquare
        i = 0
        while i < leftmob:
            temp-=1
            if board[temp] == 0:
                attacked_squares.append(temp)
                i += 1
            else:
                attacked_squares.append(temp)
                i = leftmob
        # this is for going right  
        i = 0     
        temp = startsquare
        while i < rightmob:
            temp+=1
            if board[temp] == 0:
                attacked_squares.append(temp)
                i += 1
            else:
                attacked_squares.append(temp)
                i = rightmob
         
        # for going down 
        temp = startsquare
        while temp >= 8:
            temp -= 8
            if board[temp] == 0:
                attacked_squares.append(temp)
            else:
                attacked_squares.append(temp)
                temp = -1
         
        # for going up
        temp = startsquare
        while temp < 56:
            temp += 8
            if board[temp] == 0:
                attacked_squares.append(temp)
            else:
                attacked_squares.append(temp)
                temp = 65
        return attacked_squares
         
    def diagonal_attacked_squares(self,startsquare,board):
        attacked_squares = []
        temp = startsquare
        leftmob = startsquare%8
        rightmob = 7 - leftmob
        if board[startsquare] >= 16:
            colour = 'black'
        else:
            colour = 'white'
        # for going up and left
        i = 0
        while i < leftmob:
            temp += 7 
            if temp > 63:
                i = leftmob
            else:
                if board[temp] == 0:
                    attacked_squares.append(temp)
                else:
                    attacked_squares.append(temp)
                    i = leftmob
                i += 1
        # for going down and left
        temp = startsquare
        i = 0
        while i < leftmob:
            temp -= 9
            if temp < 0:
                i = leftmob
            else:
                if board[temp] == 0:
                    attacked_squares.append(temp)
                else:
                    attacked_squares.append(temp)
                    i = leftmob
                i += 1
        # for going up and right
        temp = startsquare
        i = 0
        while temp%8 < 7:
            temp += 9 
            if temp > 63:
                i = rightmob
            else:
                if board[temp] == 0:
                    attacked_squares.append(temp)
                else:
                    attacked_squares.append(temp)
                    temp = 7
        # for going down and right
        temp = startsquare
        i = 0
        while temp%8 < 7:
            temp -= 7 
            if temp < 0:
                i = rightmob
            else:
                if board[temp] == 0:
                    attacked_squares.append(temp)
                else:
                    attacked_squares.append(temp)
                    temp = 7
        return attacked_squares
 
    def queen_attacked_squares(self,startsquare,board):
        attacked_squares = []
        temp = self.horizontal_attacked_squares(startsquare,board)
        for i in range(0,len(temp)):
            attacked_squares.append(temp[i])
        temp = self.diagonal_attacked_squares(startsquare,board)
        for i in range(0,len(temp)):
            attacked_squares.append(temp[i])
        return attacked_squares
 
    def king_attacked_squares(self,startsquare):
        attacked_squares = []
        if startsquare < 56:
            attacked_squares.append(startsquare+8)
            if startsquare % 8 != 0:
                attacked_squares.append(startsquare + 7)
            if startsquare != 7:
                attacked_squares.append(startsquare + 9)
         
        if startsquare > 7:
            attacked_squares.append(startsquare-8)
            if startsquare % 8 != 0:
                attacked_squares.append(startsquare - 9)
            if startsquare != 7:
                attacked_squares.append(startsquare - 7)
         
        if startsquare % 8 != 0:
                attacked_squares.append(startsquare - 1)
        if startsquare != 7:
            attacked_squares.append(startsquare + 1)
 
        return attacked_squares
 
def check_if_legal(startsquare,endsquare,colour,board):
    king_store = None # this will be where we keep the location of the king that we want to see if they are in check
    legal_check = False
    attacked_colour = None
    king_check = None # this is so that we know which value we are looking for
    if colour == 'white':
        attacked_colour = 'black'
        king_check = 14
    else:
        attacked_colour = 'white'
        king_check = 22
    attacked_squares = []
    for i in range(0,len(board)):
        attacked_squares.append(0)
    temp_board = []
    for i in range(0,len(board)):
        temp_board.append(board[i])
    temp_board[endsquare] = temp_board[startsquare]
    temp_board[startsquare] = 0
    piece = Piece()
    attacked_squares = piece.find_attacked_squares(temp_board,attacked_colour,attacked_squares)
    #finding the location of the king
    i = 0
    try:
        king_store = temp_board.index(king_check)
    except:
        quit()
    if attacked_squares[king_store] == 0:
        legal_check = True
    return legal_check
 
def move_to_text(board_used,move): # this will turn a move suggestion into text that the user can understand
    text = ''
    letter = {0:'a',1:'b',2:'c',3:'d',4:'e',5:'f',6:'g',7:'h'} # when we do a mod operation we will get a value, and now we need to turn this into a letter
    num_to_piece = {9:'P',10:'N',11:'B',12:'R',13:'Q',14:'K',17:'P',18:'N',19:'B',20:'R',21:'Q',22:'K'}
    if board_used[int(move[0])] == 0:
        pass
    else:
        text += num_to_piece[board_used[int(move[0])]]
    text += letter[int(move[1])%8]
    text += str((int(move[1])//8)+1)
    return text
 
def pos_to_FEN(board):
    num_to_piece = {9:'P',10:'N',11:'B',12:'R',13:'Q',14:'K',17:'p',18:'n',19:'b',20:'r',21:'q',22:'k'} # this is a dictionary that stores what each number means
    empty_count = 0 # this will store how many empty spaces there are in a row
    fen = '' # this will be added to as we go
    fen_list = [None,None,None,None,None,None,None,None] # this will store the fen for each rank in each position so that we can flip it at the end
    started = False # this will be true when we need to find how many empty squares there are in a row
    pos = 0
    while pos < 64: # this will loop over the whole board, we are using a while loop so that we can skip concurrent gaps
        empty_count = 0 # we need to reset this after each go
        if board[pos] != 0: # if there is a piece on the square
            fen += num_to_piece[board[pos]]
            pos += 1
        else: # if there is an empty square then we need to find how many there are in a row
            started = True
            empty_count = 1
            while started == True: # while there are still empty squars to be checked
                if (pos + empty_count) % 8 == 0: # we have now gone on to the next line, which means that we need to stop this search
                    started = False
                else: # we are not yet on the next line, which means that we can keep going
                    if board[pos+empty_count] == 0:
                        empty_count += 1
                    else:
                        started = False
            fen += str(empty_count)
            pos += empty_count
        if pos%8 == 0: # this means that we have moved on to the next row and we need to come out of it
            fen += '/'
            fen_list[(pos//8)-1] = fen
            fen = ''
 
    for i in range(len(fen_list)-1,-1,-1): # goes from the start to the end
        fen += fen_list[i]
    fen = fen[:-1]
    return fen
     
def keep_button_menu(window, button1, button2, button3, button4):
    window.fill(light)
    button1.draw(window)
    button2.draw(window)
    button3.draw(window)
    button4.draw(window)          
  
def keep_button_borl(window, button1, button2):
    window.fill(light)
    button1.draw(window)
    button2.draw(window)
  
def start_screen():
    window = pygame.display.set_mode((height, width)) # this and the next line are being done inside this subroutine because it means that the whole thing can be called when it is ready, and there is no need for weird while loops that aren't necessary
    pygame.display.set_caption('CHESS')
    running = True
    analysis = False
    clock = pygame.time.Clock()
    while running:
        clock.tick(60)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == MOUSEBUTTONDOWN: # this is when a mouse button is pressed on the screen
                mouse_pos = pygame.mouse.get_pos() # this will get the position of the mouse on the screen
                if mouse_pos[0] >= 25 and mouse_pos[0] <= 300 and mouse_pos[1] >= 25 and mouse_pos[1] <= 300:
                    #user vs computer: custom
                    FEN = ''
                    stage = 0 # if this is 0 then this tells the program that we dealing with user vs computer
                    FEN_REQ = 1
                    running = False
                elif mouse_pos[0] >= 350 and mouse_pos[0] <= 625 and mouse_pos[1] >= 25 and mouse_pos[1] <= 300:
                    #user vs computer: start
                    stage = 0
                    FEN_REQ = 0
                    running = False
                if mouse_pos[0] >= 25 and mouse_pos[0] <= 300 and mouse_pos[1] >= 350 and mouse_pos[1] <= 625:
                    #analysis:custom
                    FEN = ''
                    stage = 1 # this tells the program that we are dealing with analysis
                    FEN_REQ = 1
                    running = False
                    analysis = True
                elif mouse_pos[0] >= 350 and mouse_pos[0] <= 625 and mouse_pos[1] >= 350 and mouse_pos[1] <= 625:
                    #analysis: start
                    stage = 1
                    FEN_REQ = 0
                    running = False
                    analysis = True
        button1 = Button(275,275,dark,25,25,'USER VS COMPUTER: CUSTOM')
        button2 = Button(275,275,dark,350,25,'USER VS COMPUTER: START')
        button3 = Button(275,275,dark,25,350,'ANALYSIS: CUSTOM')
        button4 = Button(275,275,dark,350,350,'ANALYSIS: START')
        keep_button_menu(window, button1, button2, button3, button4)
        pygame.display.update()
    return stage, FEN_REQ, analysis
  
def b_or_l(): # this will get which colour the user wants to play as
    window = pygame.display.set_mode((height, width)) # this and the next line are being done inside this subroutine because it means that the whole thing can be called when it is ready, and there is no need for weird while loops that aren't necessary
    pygame.display.set_caption('CHESS')
    running = True
    clock = pygame.time.Clock()
    while running:
        clock.tick(60)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == MOUSEBUTTONDOWN: # this is when a mouse button is pressed on the screen
                mouse_pos = pygame.mouse.get_pos() # this will get the position of the mouse on the screen
                if mouse_pos[0] >= 25 and mouse_pos[0] <= 300 and mouse_pos[1] >= 25 and mouse_pos[1] <= 625: # the 'white' button has been pressed
                    colour = 'white'
                    running = False # as soon as one of the buttons is clicked, then we should move onto the next screen
                elif mouse_pos[0] >= 350 and mouse_pos[0] <= 625 and mouse_pos[1] >= 25 and mouse_pos[1] <= 625: # the 'black' button has been pressed
                    colour = 'black'
                    running = False
        button1 = Button(600,275,dark,25,25,'White') # this button will be clicked if the user wants to play as white
        button2 = Button(600,275,dark,350,25,'Black') # this will be clicked if the user wants to play as black
        keep_button_borl(window, button1, button2)
        pygame.display.update()
    return colour
  
def check_fen(fen):
    legal = True # this will be changed if we find anything bad about it
    w_king = False
    b_king = False
    fen_list = fen.split('/')
    approved = ['p','n','b','r','q','k','P','N','B','R','Q','K','1','2','3','4','5','6','7','8']
    if len(fen_list)!= 8:
        legal = False
    else:
        for i in range(0,8): # this will go through each line
            temp2 = list(fen_list[i])
            count = 0
            for j in range(0,len(temp2)):
                if temp2[j] not in approved:
                    legal = False
                if ord(temp2[j]) >= 65:
                    count += 1
                    if temp2[j] == 'K':
                        if w_king == True:
                            legal = False
                        w_king = True
                    elif temp2[j] == 'k':
                        if b_king == True:
                            legal = False
                        b_king = True
                else:
                    count += int(temp2[j])
            if count != 8:
                legal = False
    
    if b_king == True and w_king == True:
        pass
    else:
        legal = False
    try:
        temp = list(fen_list[0])
        if 'p' in temp or 'P' in temp:
            legal = False
        temp = list(fen_list[7])
        if 'p' in temp or 'P' in temp:
            legal = False
    except:
        legal = False
    return legal
          
def input_fen():
    fen = ''
    legal = True
    window = pygame.display.set_mode((1000, width)) # this and the next line are being done inside this subroutine because it means that the whole thing can be called when it is ready, and there is no need for weird while loops that aren't necessary
    pygame.display.set_caption('CHESS')
    running = True
    clock = pygame.time.Clock()
    while running:
        clock.tick(60)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_BACKSPACE:
                    fen = fen[:-1]
                else:
                    fen += event.unicode
            if event.type == MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                if mouse_pos[0]>=400 and mouse_pos[0]<=600 and mouse_pos[1]>=450 and mouse_pos[1]<= 650:
                    legal = check_fen(fen)
                    if legal == True:
                        running = False
                        return fen
        info = Button(100,100,light,450,0,'Please input your FEN below and click enter when done')
        input_box = Button(100,100,light,450,150,fen)
        enter = Button(200,200,dark,400,450,'ENTER')
        valid = Button(100,300,red,350,300,'INVALID: RE-ENTER FEN')
        keep_display_fen(window, info, input_box, enter, valid,legal)
        pygame.display.update()
  
def keep_display_fen(window, info, input_box, enter, valid, legal):
    window.fill(light)
    info.draw(window)
    input_box.draw(window)
    enter.draw(window)
    if legal == False:
        valid.draw(window)
  
def setup():
    start_pos = True
    analysis = False
    fen = 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR'
    start_info = start_screen()
    stage = start_info[0] # stage = 0 means we are playing against the computer, and stage = 1 means we are analysing
    FEN_REQ = start_info[1]
    analysis = start_info[2]
    colour = b_or_l() # 'white' means white is at the bottom of the screen and 'black' means black is
    if FEN_REQ == 1:
        fen = input_fen()
        start_pos = False
    return fen, stage, colour,analysis,start_pos
  
    pygame.quit()
 
# THE GAME
 
move = None
temp = setup()
fen = temp[0]
stage = temp[1]
colour = temp[2]
analysis = temp[3]
start_pos = temp[4]
ai_colour = None
 
if start_pos == True:
    move = 0
    if colour == 'white':
        ai_colour = 'black'
    else:
        ai_colour = 'white'
else:
    if colour == 'white':
        ai_colour = 'black'
        move = 0
    else:
        ai_colour = 'white'
        move = 1
board = Board()
board.set(colour, move, ai_colour)
boards = board.FEN_to_position(fen)
white_king_pos = boards.index(14)
black_king_pos = boards.index(22)
ai = AI(None,None)
if analysis == True:
    board.analyse()
else:
    board.get_data(move,colour)
    ai = AI(ai_colour,board.running)
    ai.get_data(board.board,None,None)
    board.user_vs_ai()