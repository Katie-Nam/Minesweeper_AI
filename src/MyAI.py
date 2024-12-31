# ==============================CS-199==================================
# FILE:			MyAI.py
#
# AUTHOR: 		Justin Chung
#
# DESCRIPTION:	This file contains the MyAI class. You will implement your
#				agent in this file. You will write the 'getAction' function,
#				the constructor, and any additional helper functions.
#
# NOTES: 		- MyAI inherits from the abstract AI class in AI.py.
#
#				- DO NOT MAKE CHANGES TO THIS FILE.
# ==============================CS-199==================================

from AI import AI
from Action import Action
from collections import deque
import random



class MyAI(AI):

    def __init__(self, rowDimension, colDimension, totalMines, startX, startY):
        ########################################################################
        #                            YOUR CODE BEGINS                          #
        ########################################################################
        self.rowDimension = colDimension        # swap row and column (for expert)
        self.colDimension = rowDimension        # swap row and column (for expert)
        self.totalMines = totalMines
        self.startX = startX
        self.startY = startY

        self.uncovered = {}      # track uncovered cells (coordinates and numbers)
        self.flagged = set()        # track flagged cells
        self.flag_queue = deque()       # queue of flagged cells to flag next
        self.safe_queue = deque()           # queue of safe cells to uncover next
        self.initial_move = True    # true for initial uncover

        self.last_uncovered_x = startX      # variables to hold coordinates of last uncovered cell
        self.last_uncovered_y = startY

        ########################################################################
        #                            YOUR CODE ENDS                            #
        ########################################################################

    def get_neighbors(self, x, y):
        neighbors = []
        for dx in range(-1, 2):
            for dy in range(-1, 2):
                if dx == 0 and dy == 0:
                    continue
                nx, ny = x + dx, y + dy
                # check bounds to ensure neighbors are within the grid
                if 0 <= nx < self.rowDimension and 0 <= ny < self.colDimension:
                    neighbors.append((nx, ny))
        return neighbors

    def uncover_safe_queue(self):
        while self.safe_queue:
            x, y = self.safe_queue.popleft()
            if (x, y) not in self.uncovered:
                self.last_uncovered_x, self.last_uncovered_y = x, y
                return Action(AI.Action.UNCOVER, x, y)
        return None
    
    def uncover_flag_queue(self):
        while self.flag_queue:
            x, y = self.flag_queue.popleft()
            # self.last_uncovered_x, self.last_uncovered_y = x, y
            return Action(AI.Action.FLAG, x, y)
        return None

    def found_zero(self, current_cell):
        # Mark all neighbors of the current cell as safe and add them to the safe queue
        neighbors = self.get_neighbors(*current_cell)
        for cell in neighbors:
            if cell not in self.uncovered and cell not in self.flagged:
                self.safe_queue.append(cell)
        # Attempt to uncover all cells in the safe queue immediately
        return self.uncover_safe_queue()

    def hint_equal_to_covered_cells(self, current_cell, number):
        neighbors = self.get_neighbors(*current_cell)
        covered_neighbors = [cell for cell in neighbors if cell not in self.uncovered and cell not in self.flagged]
        flagged_neighbors = [cell for cell in neighbors if cell in self.flagged]
        
        # if covered neighbors equals number, but theres a flagged neighbor, skip this cell
        if len(covered_neighbors) == number and flagged_neighbors:
            return None
        # check if the number of covered neighbors equals the cell's number
        elif number > 0 and len(covered_neighbors) == number:
            for cell in covered_neighbors:
                self.flagged.add(cell)
                self.flag_queue.append(cell)
            return Action(AI.Action.FLAG, *cell)
        
        return None

    def hint_equal_to_flagged_cells(self, current_cell, number):
        neighbors = self.get_neighbors(*current_cell)
        flagged_neighbors = [cell for cell in neighbors if cell in self.flagged]

        # check if the number of flagged neighbors equals the cell's number
        if number == len(flagged_neighbors):
            for cell in neighbors:
                if cell not in self.uncovered and cell not in self.flagged:
                    self.safe_queue.append(cell)
            return True  # indicates that neighbors were added to the safe queue

        return False  # indicates that no neighbors were added

    def hint_minus_flagged_equals_covered_neighbors(self, current_cell, number):
        neighbors = self.get_neighbors(*current_cell)
        
        flagged_neighbors = [cell for cell in neighbors if cell in self.flagged]
        covered_neighbors = [cell for cell in neighbors if cell not in self.uncovered and cell not in self.flagged]
        
        # if number of covered neighbors == hint - flagged neighbors, flag all covered neighbors
        if len(covered_neighbors) == (number - len(flagged_neighbors)):
            for cell in covered_neighbors:
                if cell not in self.flagged: 
                    self.flagged.add(cell)
                    self.flag_queue.append(cell)
            return True  # indicates that new cells were added to the flag queue
        return None

    def detect_121_pattern(self, current_cell):
        x, y = current_cell

        # Ensure the current cell is uncovered and contains "2"
        if current_cell not in self.uncovered or self.uncovered[current_cell] != 2:
            return False

        # check for horizontal 1-2-1 pattern
        left_cell = (x - 1, y)
        right_cell = (x + 1, y) 

        # check for vertical 1-2-1 pattern
        above_cell = (x, y + 1)
        below_cell = (x, y - 1)

        # Ensure the left and right neighbors are uncovered "1" tiles
        if (
            left_cell in self.uncovered and self.uncovered[left_cell] == 1 and
            right_cell in self.uncovered and self.uncovered[right_cell] == 1
        ):
            # Check the three tiles below the left "1", "2", and right "1"
            below_left = (x - 1, y - 1)
            below_middle = (x, y - 1)
            below_right = (x + 1, y - 1)

            above_left = (x - 1, y + 1)
            above_middle = (x, y + 1)
            above_right = (x + 1, y + 1)

            # Ensure all three tiles below are uncovered
            if (
                below_left in self.uncovered and
                below_middle in self.uncovered and
                below_right in self.uncovered and
                above_left not in self.uncovered and 
                above_middle not in self.uncovered and
                above_right not in self.uncovered
            ):
                # Flag the two tiles above the left and right "1" as mines
                for mine in [above_left, above_right]:
                    if mine not in self.flagged:
                        self.flagged.add(mine)
                        self.flag_queue.append(mine)

                return True  # Pattern processed successfully
            elif (
                above_left in self.uncovered and
                above_middle in self.uncovered and
                above_right in self.uncovered and
                below_left not in self.uncovered and 
                below_middle not in self.uncovered and
                below_right not in self.uncovered
            ):
                # Flag the two tiles below the left and right "1" as mines
                for mine in [below_left, below_right]:
                    if mine not in self.flagged:
                        self.flagged.add(mine)
                        self.flag_queue.append(mine)

                return True  # Pattern processed successfully   

        # ensure the above and below neighbors are uncovered "1" tiles
        elif (
            above_cell in self.uncovered and self.uncovered[above_cell] == 1 and
            below_cell in self.uncovered and self.uncovered[below_cell] == 1
        ):
            # Check the three tiles to the left and right (vertically 3)
            right_up = (x + 1, y + 1)
            right_middle = (x + 1, y)
            right_down = (x + 1, y - 1)

            left_up = (x - 1, y + 1)
            left_middle = (x - 1, y)
            left_down = (x - 1, y - 1)

            # Ensure all three tiles to the right are uncovered
            if (
                right_up in self.uncovered and
                right_middle in self.uncovered and
                right_down in self.uncovered and
                left_up not in self.uncovered and 
                left_middle not in self.uncovered and
                left_down not in self.uncovered
            ):
                # Flag the two tiles to the left of the "1"s as mines
                for mine in [left_up, left_down]:
                    if mine not in self.flagged:
                        self.flagged.add(mine)
                        self.flag_queue.append(mine)

                return True  # Pattern processed successfully
            elif (
                left_up in self.uncovered and
                left_middle in self.uncovered and
                left_down in self.uncovered and
                right_up not in self.uncovered and 
                right_middle not in self.uncovered and
                right_down not in self.uncovered
            ):
                # Flag the two tiles to the right of the "1"s as mines
                for mine in [right_up, right_down]:
                    if mine not in self.flagged:
                        self.flagged.add(mine)
                        self.flag_queue.append(mine)

                return True  # Pattern processed successfully   
        return False  # No 1-2-1 pattern detected

    def detect_1221_pattern(self, current_cell):
        x, y = current_cell

        # Ensure the current cell is uncovered and contains "2" (assume the left/top 2)
        if current_cell not in self.uncovered or self.uncovered[current_cell] != 2:
            return False

        # check for horizontal 1-2-2-1 pattern
        left_cell = (x - 1, y)          # 1
        right_cell = (x + 1, y)         # 2
        right_right_cell = (x + 2, y)   # 1

        # check for vertical 1-2-2-1 pattern
        above_cell = (x, y + 1)         # 1
        below_cell = (x, y - 1)         # 2
        below_below_cell = (x, y - 2)   # 1

        # Ensure the left and right_right neighbors are uncovered "1" tiles AND right neighbor is 2
        # horizontal check
        if (
            left_cell in self.uncovered and self.uncovered[left_cell] == 1 and
            right_cell in self.uncovered and self.uncovered[right_cell] == 2 and
            right_right_cell in self.uncovered and self.uncovered[right_right_cell] == 1
        ):
            # Check the 4 tiles below the 1221
            below_left = (x - 1, y - 1)
            below_middle = (x, y - 1)
            below_right = (x + 1, y - 1)
            below_right_right = (x + 2, y - 1)

            # Check the 4 tiles above the 1221
            above_left = (x - 1, y + 1)
            above_middle = (x, y + 1)
            above_right = (x + 1, y + 1)
            above_right_right = (x + 2, y + 1)

            # Ensure all 4 tiles below are uncovered
            if (
                below_left in self.uncovered and
                below_middle in self.uncovered and
                below_right in self.uncovered and
                below_right_right in self.uncovered and
                above_left not in self.uncovered and 
                above_middle not in self.uncovered and
                above_right not in self.uncovered and
                above_right_right not in self.uncovered
            ):
                # Flag the two tiles ABOVE the 2s as mines
                for mine in [above_middle, above_right]:
                    if mine not in self.flagged:
                        self.flagged.add(mine)
                        self.flag_queue.append(mine)

                return True  # Pattern processed successfully
            elif (
                above_left in self.uncovered and
                above_middle in self.uncovered and
                above_right in self.uncovered and
                above_right_right in self.uncovered and
                below_left not in self.uncovered and 
                below_middle not in self.uncovered and
                below_right not in self.uncovered and 
                below_right_right not in self.uncovered
            ):
                # Flag the two tiles BELOW the 2s as mines
                for mine in [below_middle, below_right]:
                    if mine not in self.flagged:
                        self.flagged.add(mine)
                        self.flag_queue.append(mine)

                return True  # Pattern processed successfully   

        # vertical check
        elif (
            above_cell in self.uncovered and self.uncovered[above_cell] == 1 and
            below_cell in self.uncovered and self.uncovered[below_cell] == 2 and
            below_below_cell in self.uncovered and self.uncovered[below_below_cell] == 1
        ):
            # Check the 4 tiles to the right of the 1221
            right_up = (x + 1, y + 1)
            right_middle = (x + 1, y)
            right_below = (x + 1, y - 1)
            right_below_below = (x + 1, y - 2)

            # Check the 4 tiles to the left of the 1221
            left_up = (x - 1, y + 1)
            left_middle = (x - 1, y)
            left_down = (x - 1, y - 1)
            left_down_down = (x - 1, y - 2)

            # Ensure all 4 tiles to the right are uncovered
            if (
                right_up in self.uncovered and
                right_middle in self.uncovered and
                right_below in self.uncovered and
                right_below_below in self.uncovered and
                left_up not in self.uncovered and 
                left_middle not in self.uncovered and
                left_down not in self.uncovered and
                left_down_down not in self.uncovered
            ):
                # Flag the two tiles to the LEFT of the 2s as mines
                for mine in [left_middle, left_down]:
                    if mine not in self.flagged:
                        self.flagged.add(mine)
                        self.flag_queue.append(mine)

                return True  # Pattern processed successfully
            elif (
                left_up in self.uncovered and
                left_middle in self.uncovered and
                left_down in self.uncovered and
                left_down_down in self.uncovered and
                right_up not in self.uncovered and 
                right_middle not in self.uncovered and
                right_below not in self.uncovered and 
                right_below_below not in self.uncovered
            ):
                # Flag the two tiles to the RIGHT the 2s as mines
                for mine in [right_middle, right_below]:
                    if mine not in self.flagged:
                        self.flagged.add(mine)
                        self.flag_queue.append(mine)

                return True  # Pattern processed successfully   

        return False  # No 1-2-2-1 pattern detected




    def getAction(self, number: int) -> "Action Object":
        ########################################################################
        #                            YOUR CODE BEGINS                          #
        ########################################################################

        current_cell = (self.last_uncovered_x, self.last_uncovered_y)

        # if flag/unflag, dont store in uncovered
        if number == -1:
            pass
        else:
            self.uncovered[current_cell] = number

        # if number on cell = 0, mark all neighbors as safe
        if number == 0:
            action = self.found_zero(current_cell)
            if action:
                return action
            
        # always prioritze uncovering safe queue
        action = self.uncover_safe_queue()
        if action:
            return action
        
        # uncover flagged queue (self.flagged to store all flagged cells + flagged queue to flag cells in self.flagged)
        action = self.uncover_flag_queue()
        if action:
            return action

        # exit function if out of spaces
        if len(self.uncovered) + len(self.flagged) == self.rowDimension * self.colDimension:
            return Action(AI.Action.LEAVE)

        # uncover the initial move (guaranteed to be zero)
        if self.initial_move:
            self.initial_move = False
            self.uncovered[(self.startX, self.startY)] = 0      # number?
            neighbors = self.get_neighbors(self.startX, self.startY)
            for cell in neighbors:
                if cell not in self.uncovered:
                    self.safe_queue.append(cell)
            action = self.uncover_safe_queue()
            if action:
                return action
        
        ## no more zeros, so start flagging!!!
        #print(self.uncovered)
        for cell, number in self.uncovered.items():
            if number == 0:
                #print(f"DEBUG: reached number = 0 and continues to other flag conditions {cell}")
                continue # skip cells with no adjacent mines

            # if number on cell = number of flagged neighbor cells, uncover all remaining neighbor cells
            if self.hint_equal_to_flagged_cells(cell, number):
                # Attempt to uncover cells in the safe queue immediately
                action = self.uncover_safe_queue()
                if action:
                    #print(f"DEBUG: reached hint_equal_to_flagged_cells {cell}")
                    return action
            
            # if number on cell = number of covered neighbor cells, flag all of the covered neighbor cells
            action = self.hint_equal_to_covered_cells(cell, number)
            if action:
                #print(f"DEBUG: reached hint_equal_to_covered_cells {cell}")
                return action
            
            # if number of covered cells = number - flagged neighbors --> covered cells need to be flagged
            if self.hint_minus_flagged_equals_covered_neighbors(cell, number):
                action = self.uncover_flag_queue()
                if action:
                    #print(f"DEBUG: reached hint_minus_flagged_equals_covered_neighbors {cell}")
                    return action
                
            action = self.detect_121_pattern(cell)
            if action:
                # flagging actions will be handled automatically by uncover_flag_queue
                action = self.uncover_flag_queue()
                if action:
                    #print(f"DEBUG: detected 121 pattern {cell}")
                    return action

            action = self.detect_1221_pattern(cell)
            if action:
                # flagging actions will be handled automatically by uncover_flag_queue
                action = self.uncover_flag_queue()
                if action:
                    #print(f"DEBUG: detected 1221 pattern {cell}")
                    return action


        # if no safe cells are in the safe queue, uncover a random cell
        x, y = random.randint(0, self.rowDimension - 1), random.randint(0, self.colDimension - 1)
        while (x, y) in self.uncovered or (x, y) in self.flagged:
            x, y = random.randint(0, self.rowDimension - 1), random.randint(0, self.colDimension - 1)
        
        self.last_uncovered_x, self.last_uncovered_y = x, y
        return Action(AI.Action.UNCOVER, x, y)

        ########################################################################
        #                            YOUR CODE ENDS                            #
        ########################################################################



## testing
## cd Minesweeper_Python
## make
## cd bin
## ls
## python3 Main.pyc -d -f ../../WorldGenerator/Problems/ExpertWorld1.txt
## python3 Main.pyc -f ../../WorldGenerator/Problems/
## python3 Main.pyc -f ../../WorldGenerator/Problems/ExpertWorld1.txt



# uncovered is 0 indexed (x+1, Y+1 when reading from print statements)
