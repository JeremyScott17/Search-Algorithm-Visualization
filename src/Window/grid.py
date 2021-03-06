import pygame
import time
from .constants import *


class Grid:
    def __init__(self, win):
        self.win = win  
        self._init()
    
    def _init(self):
        self.grid = [[True for _ in range(COLS)] for _ in range(ROWS)]  # False = visited | True = not visited
        self.start_point = None  # (row, col)
        self.end_point = None  # (row, col)
        self.walls = []  # [(row, col)]
        self.shortest_path = []  # [(row, col)]
    
    def _draw_squares(self):
        r = 0
        for row in self.grid:
            c = 0
            for sq in row:
                if (r, c) == self.start_point:
                    pygame.draw.rect(self.win, BLUE, (c * SQUARE_SIZE, r * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))
                    pygame.draw.rect(self.win, BLACK, (c * SQUARE_SIZE, r * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE), 2)
                elif (r, c) == self.end_point:
                    pygame.draw.rect(self.win, RED, (c * SQUARE_SIZE, r * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))
                    pygame.draw.rect(self.win, BLACK, (c * SQUARE_SIZE, r * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE), 2)
                elif (r, c) in self.walls:
                    pygame.draw.rect(self.win, BROWN, (c * SQUARE_SIZE, r * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))
                    pygame.draw.rect(self.win, BLACK, (c * SQUARE_SIZE, r * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE), 2)
                elif (r, c) in self.shortest_path:
                    pygame.draw.rect(self.win, YELLOW, (c * SQUARE_SIZE, r * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))
                    pygame.draw.rect(self.win, BLACK, (c * SQUARE_SIZE, r * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE), 2)
                elif not sq:  # visited square that isn't the start, end, a wall or in the shortest path
                    pygame.draw.rect(self.win, GREEN, (c * SQUARE_SIZE, r * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))
                    pygame.draw.rect(self.win, BLACK, (c * SQUARE_SIZE, r * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE), 2)
                else:
                    pygame.draw.rect(self.win, BLACK, (c * SQUARE_SIZE, r * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE), 2)
                c += 1
            r += 1
    
    def _get_row_col(self, x, y):
        row = y // SQUARE_SIZE
        col = x // SQUARE_SIZE
        return row, col

    def _get_child_nodes(self, parent):
        children = []
        parent_row, parent_col = parent

        if parent_row != 0 and (parent_row - 1, parent_col) not in self.walls:
            children.append((parent_row - 1, parent_col))
        
        if parent_col != COLS - 1 and (parent_row, parent_col + 1) not in self.walls:
            children.append((parent_row, parent_col + 1))

        if parent_row != ROWS - 1 and (parent_row + 1, parent_col) not in self.walls:
            children.append((parent_row + 1, parent_col))
        
        if parent_col != 0 and (parent_row, parent_col - 1) not in self.walls:
            children.append((parent_row, parent_col - 1))
        
        return children
    
    def draw(self):
        pygame.draw.rect(self.win, WHITE, (0, 0, GRID_WIDTH, GRID_HEIGHT))  # fill the grid area white
        pygame.draw.rect(self.win, BLACK, (0, 0, GRID_WIDTH, GRID_HEIGHT), 2)  # draw a black outline around the grid
        self._draw_squares()

    def ready(self):
        if self.start_point and self.end_point:
            return True
        else:
            return False
    
    def select_start(self, mouse_pos):
        mouse_x, mouse_y = mouse_pos
        chosen_row, chosen_col = self._get_row_col(mouse_x, mouse_y)
        if (chosen_row, chosen_col) == self.end_point or (chosen_row, chosen_col) in self.walls:
            return False
        else:
            if self.start_point:
                self.grid[self.start_point[0]][self.start_point[1]] = True
            
            self.start_point = (chosen_row, chosen_col)
            self.grid[chosen_row][chosen_col] = False
            return True
    
    def select_end(self, mouse_pos):
        mouse_x, mouse_y = mouse_pos
        chosen_row, chosen_col = self._get_row_col(mouse_x, mouse_y)
        if (chosen_row, chosen_col) == self.start_point or (chosen_row, chosen_col) in self.walls:
            return False
        else:
            if self.end_point:
                self.grid[self.end_point[0]][self.end_point[1]] = True
            
            self.end_point = (chosen_row, chosen_col)
            return True
    
    def select_wall(self, mouse_pos):
        mouse_x, mouse_y = mouse_pos
        chosen_row, chosen_col = self._get_row_col(mouse_x, mouse_y)
        if (chosen_row, chosen_col) == self.start_point or (chosen_row, chosen_col) == self.end_point or (chosen_row, chosen_col) in self.walls:
            return False
        else:
            self.walls.append((chosen_row, chosen_col))
            self.grid[chosen_row][chosen_col] = False
            return True
    
    def remove(self, mouse_pos):
        mouse_x, mouse_y = mouse_pos
        row, col = self._get_row_col(mouse_x, mouse_y)

        if (row, col) == self.start_point:
            self.start_point = None
        elif (row, col) == self.end_point:
            self.end_point = None
        elif (row, col) in self.walls:
            self.walls.remove((row, col))
        
        self.grid[row][col] = True

    
    def reset(self):
        self._init()
        
    def run_bfs(self):
        # breadth first search
        paths = [[None for _ in range(COLS)] for _ in range(ROWS)]
        paths[self.start_point[0]][self.start_point[1]] = 0
        
        frontier = [self.start_point]
        while True:
            time.sleep(SLEEP_TIME)
            if len(frontier) == 0:
                return False
            node = frontier.pop(0)
            self.grid[node[0]][node[1]] = False
            child_nodes = self._get_child_nodes(node)
            for child in child_nodes:
                if self.grid[child[0]][child[1]] and child not in frontier:
                    paths[child[0]][child[1]] = node
                    if child == self.end_point:
                        prev_node = paths[child[0]][child[1]]
                        self.run_dijkstra(None, None, False)
                        return True
                    else:
                        frontier.append(child)
            self.update()
    
    def run_dfs(self, start, paths=[[None for _ in range(COLS)] for _ in range(ROWS)]):
        # depth first search
        time.sleep(SLEEP_TIME)
        children = self._get_child_nodes(start)
        if len(children) == 0:
            return False
        else:
            for next_node in children:
                curr_x, curr_y = next_node
                if next_node == self.end_point:  # found the end point
                    self.run_dijkstra(None, None, False)
                    self.update()
                    return True
                elif self.grid[curr_x][curr_y]:  # square hasn't been visited and isn't end point
                    paths[curr_x][curr_y] = start
                    self.grid[curr_x][curr_y] = False
                    self.update()
                    succ = self.run_dfs(next_node)

                    if succ:  # found end point therefore no need to continue searching
                        return succ
                else:  # current child node has already been visited by a different branch
                    continue
    
    def run_dijkstra(self, start_node=None, end_node=None, highlight=True):
        if start_node == None:
            start_node = self.start_point
        if end_node == None:
            end_node = self.end_point

        unvisited = set()
        for row in range(ROWS):
            for col in range(COLS):
                if (row, col) in self.walls:
                    continue
                else:
                    unvisited.add((row, col))

        distance = [[0 for _ in range(COLS)] for _ in range(ROWS)]

        # assign distance from start for each square
        start_row, start_col = start_node
        for row in range(ROWS):
            for col in range(COLS):
                if (row, col) == start_node:
                    continue
                elif (row, col) in self.walls:
                    distance[row][col] = -1
                else:
                    distance[row][col] = float('inf')
        current_node = start_node

        found = False
        while not found:
            if highlight:
                time.sleep(SLEEP_TIME)
            curr_x, curr_y = current_node
            # filter child nodes that have been visited
            children = list(filter(lambda x: x in unvisited, self._get_child_nodes(current_node)))
            
            for child in children:
                child_x, child_y = child

                dist = distance[curr_x][curr_y] + 1
                distance[child_x][child_y] = min(distance[child_x][child_y], dist)

                if child == end_node:
                    self.shortest_path.append(current_node)
                    found = True  # end search
            
            if highlight:
                self.grid[curr_x][curr_y] = False
            self.update()
            unvisited.remove(current_node)

            # get next current node
            min_dist = float('inf')
            for node in unvisited:
                row, col = node
                if distance[row][col] <= min_dist:
                    min_dist = distance[row][col]
                    current_node = node
        
        node = self.shortest_path[0]
        while True:
            children = self._get_child_nodes(node)

            min_dist = float('inf')
            next_node = None
            for child in children:
                child_x, child_y = child
                
                if distance[child_x][child_y] < min_dist:
                    min_dist = distance[child_x][child_y]
                    next_node = child
            
            if next_node == start_node:
                break
            else:
                self.shortest_path.append(next_node)
                node = next_node
    
    def update(self):
        self.draw()
        pygame.event.pump()
        pygame.display.update()