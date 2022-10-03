import sys
import time
import random
import copy

import numpy as np
import pygame

pygame.init()

BLACK = (10,10,10)
GREY = (20,20,20)
WHITE = (245,245,245)

RED = (255,0,0)
ORANGE = (255,165,0)
YELLOW = (255,255,0)
GREEN = (0,255,0)
BLUE = (0,0,255)
AQUA = (0, 255, 255)
MAGENTA = (255,0,255)

DEBUG_FONT = pygame.font.SysFont("Arial", 16)

class Window():
    def __init__(self, windowed_resolution = (800,600), max_fps = 60, is_fullscreen = False, caption = '___', windowed_flags = pygame.RESIZABLE | pygame.NOFRAME, fullscreen_flags = pygame.FULLSCREEN | pygame.NOFRAME):
        self.clock = pygame.time.Clock()
        self.monitor = pygame.display.Info()
        
        self.monitor_resolution = (self.monitor.current_w,self.monitor.current_h)
        self.windowed_resolution = windowed_resolution
        
        self.max_fps = max_fps
        self.is_fullscreen = is_fullscreen
        self.caption = caption
        self.windowed_flags = windowed_flags
        self.fullscreen_flags = fullscreen_flags
        
        self.screen = self.create_screen()
    
    def toggle_fullscreen(self):
        self.is_fullscreen = not self.is_fullscreen
        self.screen = self.create_screen()
    
    def create_screen(self):
        pygame.display.set_caption(self.caption)
        if self.is_fullscreen:
            return pygame.display.set_mode(self.monitor_resolution, self.fullscreen_flags)
        else:
            return pygame.display.set_mode(self.windowed_resolution, self.windowed_flags)
            
class GameManager():
    '''Gamelogic and instancing tetrominoes'''
    game_speeds = [500,490,480,430,380,330,280,230,180,180,170,150,140,130,120,110,100,90,80,70] #ms
    game_over = False
    lines = 0
    level = 0
    score = 0
    speed = game_speeds[0]
    scoring = [40,100,300,1200]
    place_score = 10
    soft_drop_score = 1 #per grid square
    hard_drop_score = 2 #per grid square
    
    def __init__(self,position,board_size,square_size):
        self.position = position
        self.board_size = board_size
        self.square_size = square_size       
        
        self.prev_time = pygame.time.get_ticks()
        self.rect = pygame.Rect(self.position,(board_size[0] * square_size, board_size[1] * square_size))
        
        self.board = self.create_board() #stores every placed square in the grid
        
        offset = int((self.board_size[0]/2)-2)
        self.pieces = [[[1+offset,1],[Square([0+offset,1],self.square_size,MAGENTA),Square([1+offset,1],self.square_size,MAGENTA),Square([2+offset,1],self.square_size,MAGENTA),Square([1+offset,0],self.square_size,MAGENTA)]], #t
                       [[1.5+offset,0.5],[Square([1+offset,0],self.square_size,YELLOW),Square([2+offset,0],self.square_size,YELLOW),Square([2+offset,1],self.square_size,YELLOW),Square([1+offset,1],self.square_size,YELLOW)]], #o
                       [[1+offset,1],[Square([0+offset,0],self.square_size,BLUE),Square([0+offset,1],self.square_size,BLUE),Square([1+offset,1],self.square_size,BLUE),Square([2+offset,1],self.square_size,BLUE)]], #j
                       [[1+offset,1],[Square([0+offset,1],self.square_size,ORANGE),Square([1+offset,1],self.square_size,ORANGE),Square([2+offset,1],self.square_size,ORANGE),Square([2+offset,0],self.square_size,ORANGE)]], #l
                       [[1.5+offset,0.5],[Square([0+offset,0],self.square_size,AQUA),Square([1+offset,0],self.square_size,AQUA),Square([2+offset,0],self.square_size,AQUA),Square([3+offset,0],self.square_size,AQUA)]], #i
                       [[1+offset,1],[Square([0+offset,0],self.square_size,RED),Square([1+offset,0],self.square_size,RED),Square([1+offset,1],self.square_size,RED),Square([2+offset,1],self.square_size,RED)]], #z
                       [[1+offset,1],[Square([0+offset,1],self.square_size,GREEN),Square([1+offset,1],self.square_size,GREEN),Square([1+offset,0],self.square_size,GREEN),Square([2+offset,0],self.square_size,GREEN)]]] #s
        self.all_pieces = [0,1,2,3,4,5,6]
        
        self.cleared_rows = []
        self.optional_pieces = copy.deepcopy(self.all_pieces)
        self.stored_tetromino = self.new_piece()
        self.current_tetromino = self.new_piece()
        
    def create_board(self):
        matrix = []
        for y in range(self.board_size[1]):
            row = []
            for x in range(self.board_size[0]):
                row.append(None)
            matrix.append(row) 
        
        return matrix
    
    def placed_piece(self):
        self.current_tetromino = self.stored_tetromino
        self.stored_tetromino = self.new_piece()
    
    def new_piece(self):
        self.check_rows()
        self.update_speed()

        index = random.choice(self.optional_pieces)
        self.optional_pieces.remove(index)
        piece = copy.deepcopy(self.pieces[index])

        if len(self.optional_pieces) == 0:
            self.optional_pieces = copy.deepcopy(self.all_pieces)
        
        return Tetromino(piece[0],piece[1])
    
    def update(self,move_direction,rotate,hard_drop):
        manual = True
        if self.game_over is not True:
            self.current_tetromino.update()
            
            now = pygame.time.get_ticks()
            if now - self.prev_time >= self.speed:
                self.prev_time = pygame.time.get_ticks()
                
                #try to move down current block
                move_direction[1] = 1
                manual = False
                
            if hard_drop:
                self.current_tetromino.hard_drop(self)
                
            self.current_tetromino.move(self,move_direction,manual)
            
            if rotate:
                self.current_tetromino.rotate(self)
        
    
    def draw(self,screen):
        pygame.draw.rect(screen,BLACK,self.rect)
        
        #highlight
        for square in self.current_tetromino.squares:
            pygame.draw.rect(screen,GREY,(square.position[0]*self.square_size,0,self.square_size,self.board_size[1]*self.square_size))
        
        self.current_tetromino.draw(screen)

        #static squares
        for row in self.board:
            for square in row:
                if square is not None:
                    square.draw(screen)
        
        for cleared in self.cleared_rows:
            pygame.draw.rect(screen,WHITE,cleared[1])
        
        for i in range(len(self.cleared_rows)):
            if pygame.time.get_ticks() - self.cleared_rows[0][0] > 100:
                self.cleared_rows.pop(0)
        
        pygame.draw.rect(screen,WHITE,self.rect,2)
            

    def check_rows(self):
        frame_time = pygame.time.get_ticks()
        row = 0
        combo = 0
        while row < self.board_size[1]:
            if None not in self.board[row]: #full row
                combo +=1
                self.lines +=1
                cleared_row = pygame.Rect((0,row*self.square_size),(self.board_size[0]*self.square_size,self.square_size))
                self.cleared_rows.append([frame_time,cleared_row])
                #print('clear row')
                temp = copy.deepcopy(self.board)
                for y in range(row):
                    for x in range(self.board_size[0]):
                        if y+1 < self.board_size[1]:
                            temp[y+1][x] = self.board[y][x]
                            if self.board[y][x] is not None:
                                temp[y+1][x].position[1] +=1
                                temp[y+1][x].update()
                        
                self.board = copy.deepcopy(temp)
            row +=1
        
        #add score
        if combo > 0:
            self.score += self.scoring[combo-1] * (self.level+1)
    
    def update_speed(self):
        self.level = min(int(self.lines/10),19)
        self.speed = self.game_speeds[self.level]
        pass
                            

class Tetromino():
    '''Stores the group of squares'''
    def __init__(self,pivot,squares):
        self.pivot = pivot
        self.squares = squares
    
    def update(self):
        for square in self.squares:
            square.update()
    
    def draw(self,screen):
        for square in self.squares:
            square.draw(screen)
    
    def display(self,screen,position):
        for square in self.squares:
            square.display(screen,position)
    
    def hard_drop(self,game):
        #check y
        valid_y = True
        count = 0
        while valid_y:
            for square in self.squares:
                new_y = square.position[1] + count
                
                #outside bounds
                if new_y < 0 or new_y > game.board_size[1]-1:
                    valid_y = False
                
                #collided with piece on y
                elif game.board[new_y][square.position[0]] is not None:
                    valid_y = False
            if valid_y:
                count+=1

        #if free move down x amount of times
        if count > 0:
            game.score += count * game.hard_drop_score
            game.prev_time = pygame.time.get_ticks()
            for square in self.squares:
                square.position[1] += count -1
            self.pivot[1] += count -1
            
            self.update()
            
            for square in self.squares:
                game.board[square.position[1]][square.position[0]] = square
            game.placed_piece()
            
            if self.pivot[1] <= 1.5:
                game.game_over = True
    
    def move(self,game,direction,manual = False):
        
        #check x
        valid_x = True
        for square in self.squares:
            new_x = square.position[0] + direction[0]
            
            #outside bounds
            if new_x < 0 or new_x > game.board_size[0]-1:
                valid_x = False
            
            #collided with piece on x
            elif game.board[square.position[1]][new_x] is not None:
                valid_x = False
            
        #if free move x
        if valid_x:
            for square in self.squares:
                square.position[0] += direction[0]
            self.pivot[0] += direction[0]
            
        #check y
        valid_y = True
        for square in self.squares:
            new_y = square.position[1] + direction[1]
            
            #outside bounds
            if new_y < 0 or new_y > game.board_size[1]-1:
                valid_y = False
            
            #collided with piece on y
            elif game.board[new_y][square.position[0]] is not None:
                valid_y = False
                
        #if free move y
        if valid_y:
            if direction[1] > 0:
                if manual == True:
                    game.score += direction[1] * game.soft_drop_score
                game.prev_time = pygame.time.get_ticks()
                for square in self.squares:
                    square.position[1] += direction[1]
                self.pivot[1] += direction[1]
                
        #if not new block
        if not valid_y:
            
            self.update()
            
            for square in self.squares:
                game.board[square.position[1]][square.position[0]] = square
            game.placed_piece()
            if self.pivot[1] <= 1.5:
                game.game_over = True
            return
                    
    def rotate(self,game):
        
        valid = True
        push_x = 0 #store the addition x wall kick
        push_y = 0 #store the addition y wall kick
        
        #check the rotation
        for square in self.squares:
            new_x = int(-(square.position[1] - self.pivot[1]) + self.pivot[0]) + push_x
            new_y = int((square.position[0] - self.pivot[0]) + self.pivot[1]) + push_y
            
            while new_x < 0:
                new_x +=1
                push_x += 1
            
            while new_x > game.board_size[0]-1:
                new_x -=1
                push_x -= 1
            
            while new_y < 0:
                new_y +=1
                push_y += 1
            
            if game.board[new_y][new_x] is not None:
                valid = False
        
        #move the piece
        if valid:
            for square in self.squares:
                x = int(-(square.position[1] - self.pivot[1]) + self.pivot[0]) + push_x
                y = int((square.position[0] - self.pivot[0]) + self.pivot[1]) + push_y
                square.position = [x,y]
            self.pivot = [self.pivot[0] + push_x,self.pivot[1] + push_y]
        
class Square():
    '''Each individual square'''
    def __init__(self,position,size,colour):
        self.position = position
        self.size = size
        self.colour = colour
        self.update()
    
    def update(self):
        self.rect = pygame.Rect((self.position[0]*self.size,self.position[1]*self.size),(self.size,self.size))
    
    def draw(self,screen):
        pygame.draw.rect(screen,self.colour,self.rect)
        pygame.draw.rect(screen,BLACK,self.rect,1) #outline
    
    def display(self,screen,position):
        display_rect = pygame.Rect((self.position[0]*self.size + position[0],self.position[1]*self.size+ position[1]),(self.size,self.size))
        pygame.draw.rect(screen,self.colour,display_rect)
        pygame.draw.rect(screen,BLACK,display_rect,1) #outline
        pass
        
    
def quit_application():
    pygame.quit()
    sys.exit()
    
def debug_text(text,colour):
    return DEBUG_FONT.render(text, True, colour)

def debug(variable, title = None, *args):
    text = ''
    if title is not None: text += str(title) + ': '
    text += str(variable)
    for var in args: text += ' / ' + str(var) 
    return debug_text(text,WHITE)
    
window = Window(windowed_resolution=(320,400),max_fps=60)

def main(window,screen):
    game = GameManager((0,0),(10,20),20)
    prev_time = time.perf_counter()
    hold_time = 150
    hold_move_delay = 50
    held_counter = pygame.time.get_ticks()
    move_counter = pygame.time.get_ticks()
    while True:
        dt = time.perf_counter() - prev_time
        prev_time = time.perf_counter()
        
        screen.fill(BLACK) 
        
        move_direction = [0,0]
        rotate = False
        hard_drop = False
        
        # INPUT
        for event in pygame.event.get():
            if event.type == pygame.QUIT: 
                quit_application()
            if event.type == pygame.KEYDOWN: 
                if event.key == pygame.K_ESCAPE:
                    quit_application()
                if event.key == pygame.K_f:
                    window.toggle_fullscreen()
                
                if event.key == pygame.K_UP or event.key == pygame.K_w:
                    rotate = True
                if event.key == pygame.K_LEFT or event.key == pygame.K_a:
                    move_direction[0] -= 1
                    move_counter = pygame.time.get_ticks() + hold_time
                if event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                    move_direction[0] += 1
                    move_counter = pygame.time.get_ticks() + hold_time
                if event.key == pygame.K_DOWN or event.key == pygame.K_s:
                    move_direction[1] = 1
                    held_counter = pygame.time.get_ticks() + hold_time
                
                if event.key == pygame.K_SPACE:
                    hard_drop = True
                    
                if event.key == pygame.K_r:
                    main(window,screen)
            
            if event.type == pygame.VIDEORESIZE: 
                if not window.is_fullscreen:
                    window.windowed_resolution = (pygame.display.get_window_size())
                    print('RESOLUTION :', window.windowed_resolution)

             
        keys = pygame.key.get_pressed()
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            if pygame.time.get_ticks() - held_counter > hold_move_delay:
                move_direction[1] = 1
                held_counter = pygame.time.get_ticks()
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            if pygame.time.get_ticks() - move_counter > hold_move_delay:
                move_direction[0] += 1
                move_counter = pygame.time.get_ticks()
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            if pygame.time.get_ticks() - move_counter > hold_move_delay:
                move_direction[0] -= 1
                move_counter = pygame.time.get_ticks()
                
        game.update(move_direction,rotate,hard_drop)
        
        game.draw(screen)
        screen.blit(debug('lines'), (220,80))
        screen.blit(debug(game.lines), (220,95))
        screen.blit(debug('score'), (220,120))
        screen.blit(debug(game.score), (220,135))
        screen.blit(debug('level'), (220,160))
        screen.blit(debug(game.level), (220,175))

        game.stored_tetromino.display(screen,(160,20))
        # screen.blit(debug(int(window.clock.get_fps()),'FPS',window.max_fps), (0,2))
        # screen.blit(debug(dt), (0,15))
        
        pygame.display.update() 
        window.clock.tick(window.max_fps)
        
main(window, window.screen)