'''
Name(s): Sean Lim
UW netid(s): seanlim
'''
BEAR_OFF = 100
BASELINE_POINT = 1
POINT_SCALE = 0.125
BAR = 20
ALL_HOME = 50
ABOUT_TO_WIN = 500
W = 0
R = 1
CHANCE = 1/36

from game_engine import genmoves

class BackgammonPlayer:
    def __init__(self):
        self.GenMoveInstance = genmoves.GenMoves()
        self.eval = self.staticEval
        self.maxPly = 2

    def nickname(self):
        return "seanlim"

    def count(self, a, side):
        c = 0
        for piece in a:
            if piece == side:
                c +=1
        return c

    # Given a ply, it sets a maximum for how far an agent
    # should go down in the search tree. Count the chance nodes
    # as a ply too!
    def setMaxPly(self, maxply=2):
        self.maxPly = maxply

    # If not None, it update the internal static evaluation
    # function to be func
    def useSpecialStaticEval(self, func):
        if func:
            self.eval = func
        else:
            self.eval = self.staticEval


    # Given a state and a roll of dice, it returns the best move for
    # the state.whose_move
    # Keep in mind: a player can only pass if the player cannot move any checker with that role
    def move(self, state, die1, die2):
        move_generator = self.initialize_move_gen_for_state(state, state.whose_move, die1, die2)        
        ms = self.get_all_possible_moves_and_states(move_generator)
        if len(ms) == 0:
            return "NO MOVES FOUND"
        plyLeft = self.maxPly
        best_value = -1000000 if state.whose_move == W else 1000000
        best_move = 'q'
        for item in ms:
            value = self.expectiminimax(item[1], plyLeft - 1)
            if (state.whose_move == W and value > best_value) or (state.whose_move == R and value < best_value):
                best_move = item[0]
                best_value = value
        print("Value: " + str(value) + "\n" + "Move: " + best_move)
        #print(self.statesAndCutoffsCounts())
        return best_move
        
    def expectiminimax(self, state, plyLeft, state_list = None):
        if plyLeft == 0:
            return self.eval(state)
        if not state_list:
            sum_value = 0
            for i in range(1, 7):
                for j in range(1, 7):
                    move_generator = self.initialize_move_gen_for_state(state, state.whose_move, i, j) 
                    state_list = self.get_all_possible_moves_and_states(move_generator)
                    sum_value += CHANCE * self.expectiminimax(state, plyLeft, state_list=state_list)
                return sum_value
        best_value = -1000000 if state.whose_move == W else 1000000
        for s in state_list:
            newVal = self.expectiminimax(s[1], plyLeft - 1)
            if (state.whose_move == W and newVal > best_value) or (state.whose_move == R and newVal < best_value):
                best_value = newVal
        return best_value

    
    def initialize_move_gen_for_state(self, state, who, die1, die2):
        return self.GenMoveInstance.gen_moves(state, who, die1, die2)
    
    def get_all_possible_moves_and_states(self, move_generator):
        """Uses the mover to generate all legal moves. Returns an array of move commands"""
        move_list = []
        pass_list = []
        done_finding_moves = False
        any_non_pass_moves = False
        while not done_finding_moves:
            try:
                m = next(move_generator)    # Gets a (move, state) pair.
                # print("next returns: ",m[0]) # Prints out the move.    For debugging.
                if m[0] != 'p':
                    any_non_pass_moves = True
                    move_list.append(m)
                else:
                    pass_list.append(m)     # Add the move to the list.
            except StopIteration as e:
                done_finding_moves = True
        if not any_non_pass_moves:
            move_list += pass_list
        return move_list
    # Hint: Look at game_engine/boardState.py for a board state properties you can use.
    def staticEval(self, state):
        score = 0
        score += BAR * self.count(state.bar, R) - BAR * self.count(state.bar, W)
        white_home = 0
        red_home = 0
        for i in range(len(state.pointLists)):
            scale = BASELINE_POINT + min(17,i) * POINT_SCALE
            if i < 6:
                red_home += self.count(state.pointLists[i], R)
            if i > 17:
                white_home += self.count(state.pointLists[i], W)
            score += self.count(state.pointLists[i], W) * scale
            score -= self.count(state.pointLists[23 - i], R) * scale
        score += len(state.white_off) * BEAR_OFF
        score -= len(state.red_off) * BEAR_OFF
        if len(state.white_off) == 14:
            score += 500
        if len(state.red_off) == 14:
            score -= 500
        if white_home == 15:
            score += ALL_HOME
        if red_home == 15:
            score -= ALL_HOME
        #print("home: " + str(white_home))
        return score

