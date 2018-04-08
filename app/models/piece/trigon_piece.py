#this code need to be fix
class Position:
    def __init__(self, state=-1, x=-1, y=-1, z=-1):
        self.state = state
        self.x = x
        self.y = y
        self.z = z

    @staticmethod
    def from_dict(data):
        ret = Position()
        ret.state = data["state"]
        ret.x = data["x"]
        ret.y = data["y"]
        ret.z = data["z"]
        return ret

    def to_dict(self):
        return {
            "state": self.state,
            "x": self.x,
            "y": self.y,
            "z": self.z
        }

# 0-lack of corner
# 1-can be placed
# 2-occupied or share edge with same color or illegal or out of board
lack_of_corner = 0
can_be_placed = 1
illegal = 2

# 0 - share_corner
# 1 - share_edge
# 2 - occupy
share_corner = 0
share_edge = 1
occupy = 2

class Piece:
    def __init__(self, shape_set, start_point, board_size, initialize_position=None):
        self.shape_set = shape_set
        self.cell_num = 0 if len(shape_set) == 0 else len(shape_set[0])
        self.board_size = board_size
        self.start_point = start_point

        self.possible_position = []
        if initialize_position is None:
            for state in range(12):
                self.possible_position.append(
                    self._generate_piece_initialize_legal_position(
                        self.shape_set[state],
                        start_point
                    )
                )
        else:
            self.possible_position = initialize_position

        self.action = []
        for state in range(12):
            self.action.append(
                self._action_generate(
                    self.shape_set[state]
                )
            )
        self.is_drop = False

        self.state_update_table = [
            [[0, 1, 2],
             [0, 1, 2],
             [2, 2, 2]],

            [[1, 1, 2],
             [2, 2, 2],
             [2, 2, 2]]
        ]

    def _in_board(self, x, y, z): # 判断三角形是否在棋盘内
        if (z > 1) or (z < 0):
            return False
        if (x > 2 * self.board_size - 1) or (y > 2 * self.board_size - 1):
            return False
        if z == 1:
            if (x + y < self.board_size - 1) or (x + y > 3 * self.board_size - 2):
                return False
        else:
            if (x + y < self.board_size) or (x + y > 3 * self.board_size - 1):
                return False
        return True

    def try_drop(self, position):
        if self.is_drop:
            return False
        if not self.is_possible_position(position):
            return False
        self.is_drop = True
        return True

    def is_possible_position(self, dict_position):
        position = Position.from_dict(dict_position)
        if 0 > position.state or position.state > 11:
            return False
        if not self._in_board(position.x, position.y, position.z):
            return False

        return self.possible_position[position.state][position.x][position.y][position.z] == can_be_placed

    def get_one_possible_position(self):
        if self.is_drop:
            return Position().to_dict()
        for state in range(12):
            for x, y, z in [(x, y, z) for x in range(2 * self.board_size) for y in range(2 * self.board_size) for z in range(2)]:
                if self.possible_position[state][x][y][z] == can_be_placed:
                    return Position(state, x, y, z).to_dict()
        return Position().to_dict()

    def get_cell_list(self, state):
        return self.shape_set[state]

    def update_possible_position(self, piece_shape, dict_position, is_same_player):
        position = Position.from_dict(dict_position)

        for state in range(12):
            for one_cell in piece_shape:
                for act in self.action[state]:
                    self._update_one_position(
                        state, 
                        one_cell[0] + position.x + act[0],
                        one_cell[1] + position.y + act[1],
                        one_cell[2] + act[2],
                        act[3],
                        is_same_player
                    )
    
    def _update_one_position(self, state, x, y, z, action, is_same_player):
        if not self._in_board(x, y, z):
            return

        new_state = self.state_update_table[is_same_player][action][self.possible_position[state][x][y][z]]
        self.possible_position[state][x][y][z] = new_state

    def _action_generate(self, piece_shape): # todo
        irrelevant = -1
        def get_act(x, y, z, ano_pos):
            dist = abs(x - ano_pos[0]) + abs(y - ano_pos[1])
            same_direction = ano_pos[2] == z
            if dist == 0:
                return occupy if same_direction else share_edge
            if dist == 1 and same_direction:
                return share_corner
            if (x + 1, y - 1) ==  ano_pos[:2] or (x - 1, y + 1) == ano_pos[:2]:
                return share_corner
            step = -1 if z == 0 else 1
            if (x + step, y) == ano_pos[:2] or (x, y + step) == ano_pos[:2]:
                return share_edge
            if (x + step, y + step, 1 - z) == ano_pos:
                return share_corner
            return irrelevant

        res_action = []
        for x, y, z in [(x, y, z) for x in range(-4, 4) for y in range(-4, 4) for z in range(2)]:
            action = irrelevant
            for ano_pos in piece_shape:
                action = max(action, get_act(x, y, z, ano_pos))
                if action == occupy:
                    break
            if action == irrelevant:
                continue
            res_action.append((x, y, action))
        return res_action

    def _generate_piece_initialize_legal_position(self, piece_shape, start_point):

        def can_place(x, y):
            for piece_point in piece_shape:
                if not self._in_board(piece_point[0] + x, piece_point[1] + y, piece_point[2]):
                    return False
            return True
        
        begin_position = [[[0 for z in range(2)] for y in range(2 * self.board_size)] for x in range(2 * self.board_size)]

        for x, y, z in [(x, y, z) for x in range(2 * self.board_size) for y in range(2 * self.board_size) for z in range(2)]:
            if not can_place(x, y, z):
                begin_position[x][y][z] = illegal
                continue
            state = lack_of_corner
            for point in piece_shape:
                if (x + point[0], y + point[1], point[2]) == start_point:
                    state = can_be_placed
                    break
            begin_position[x][y][z] = state 
        return begin_position

def edge_direct(pos, direct):
    direction = [
        [(0, 1), (1, 0), (0, 0)],
        [(0, -1), (0, -1), (0, 0)]
    ]
    dx, dy = direction[pos[0]][direct]
    return (pos[0] + dx, pos[1] + dy, 1 - pos[2])