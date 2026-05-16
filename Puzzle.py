import copy, sys, random


class MoveError(Exception):
    '''
    This error type is used to report when an invalid move is attempted.
    '''

    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


def cellfunc_fill_in_xes(puzzle, row, col):
    '''
    Hàm này điền các giá trị 'x' xung quanh các ô hiện đang được
    bao quanh bởi số lượng liên kết được chỉ định bởi số thứ tự của ô. Ví dụ,
    nếu một ô có số '1' và hiện có một liên kết,
    thì các vị trí còn lại sẽ được đặt thành 'x'.
    '''

    cellval = puzzle.get_board(row, col)
    if cellval != ' ':
        links_required = int(cellval)

        num_links = puzzle.count_adjacent_links(row, col)
        num_xes = puzzle.count_adjacent_xes(row, col)

        if links_required == num_links and (num_links + num_xes) != 4:
            # Remaining empty slots are set to 'x'.
            puzzle.cond_set_x(row - 1, col)
            puzzle.cond_set_x(row + 1, col)
            puzzle.cond_set_x(row, col - 1)
            puzzle.cond_set_x(row, col + 1)


def dotfunc_fill_in_xes_links(puzzle, row, col):
    '''
    Hàm này thực thi quy tắc rằng
    mỗi dấu chấm phải có 0/2 links trỏ đến nó.
    Nếu dấu chấm có 2 links thì các ô còn lại đặt thành 'x'.
    Nếu dấu chấm có ít nhất 1 link và 2 'x' thì ô còn lại đặt thành một links.
    Nếu dấu chấm có 3 'x' thì ô còn lại đặt thành 1'x'.
    '''


    num_links = puzzle.count_adjacent_links(row, col)
    num_xes = puzzle.count_adjacent_xes(row, col)

    if num_links == 2 and num_xes < 2:
        # The other two slots should be set to 'x'.
        puzzle.cond_set_x(row - 1, col)
        puzzle.cond_set_x(row + 1, col)
        puzzle.cond_set_x(row, col - 1)
        puzzle.cond_set_x(row, col + 1)

    elif num_xes == 2 and num_links == 1:
        # The remaining slot should be set to a link.
        puzzle.cond_set_link(row - 1, col, '|')
        puzzle.cond_set_link(row + 1, col, '|')
        puzzle.cond_set_link(row, col - 1, '-')
        puzzle.cond_set_link(row, col + 1, '-')

    elif num_xes == 3:
        # The remaining slot should be set to 'x'.
        puzzle.cond_set_x(row - 1, col)
        puzzle.cond_set_x(row + 1, col)
        puzzle.cond_set_x(row, col - 1)
        puzzle.cond_set_x(row, col + 1)


def cellfunc_fill_in_links(puzzle, row, col):
    '''
    Hàm này xử lý trường hợp một ô chứa một số,gọi là cellnum,
    và ô đó được bao quanh bởi 4 - cellnum 'x' giá trị.
    Trong trường hợp này, các vị trí còn lại phải là các liên kết.
    '''

    cellval = puzzle.get_board(row, col)
    if cellval != ' ':
        links_required = int(cellval)

        num_links = puzzle.count_adjacent_links(row, col)
        num_xes = puzzle.count_adjacent_xes(row, col)

        if num_links < links_required and (4 - num_xes) == links_required:
            # Remaining empty slots are set to links!
            puzzle.cond_set_link(row - 1, col, '-')
            puzzle.cond_set_link(row + 1, col, '-')
            puzzle.cond_set_link(row, col - 1, '|')
            puzzle.cond_set_link(row, col + 1, '|')


def cellfunc_handle_adjacent_threes(puzzle, row, col):
    '''
    Hàm này xử lý trường hợp hai ô liền kề (theo chiều ngang, chiều dọc hoặc đường chéo) = 3.
    Trong những trường hợp này, có thể điền vào một số ô trống bằng các links và/hoặc 'x',
    mặc dù không thể gán hoàn toàn các links.
    '''

    if puzzle.get_board(row, col) != '3':
        return

    prev_row = row - 2
    next_row = row + 2
    next_col = col + 2

    if next_row < puzzle.board_height and \
            puzzle.get_board(next_row, col) == '3':
        # This case handles two vertically adjacent '3' cells.

        puzzle.cond_set_link(row - 1, col, '-')
        puzzle.cond_set_link(row + 1, col, '-')
        puzzle.cond_set_link(row + 3, col, '-')

        puzzle.cond_set_x(row + 1, col - 2)
        puzzle.cond_set_x(row + 1, col + 2)

    elif next_col < puzzle.board_width and \
            puzzle.get_board(row, next_col) == '3':
        # This case handles two horizontally adjacent '3' cells.

        puzzle.cond_set_link(row, col - 1, '|')
        puzzle.cond_set_link(row, col + 1, '|')
        puzzle.cond_set_link(row, col + 3, '|')

        puzzle.cond_set_x(row - 2, col + 1)
        puzzle.cond_set_x(row + 2, col + 1)

    elif next_row < puzzle.board_height and \
            next_col < puzzle.board_width and \
            puzzle.get_board(next_row, next_col) == '3':

        # This case handles a '3' cell with another one down and to the right.

        puzzle.cond_set_link(row - 1, col, '-')
        puzzle.cond_set_link(row, col - 1, '|')

        puzzle.cond_set_link(row + 2, col + 3, '|')
        puzzle.cond_set_link(row + 3, col + 2, '-')

    elif prev_row >= 0 and next_col < puzzle.board_width and \
            puzzle.get_board(prev_row, next_col) == '3':

        # This case handles a '3' cell with another one up and to the right.

        puzzle.cond_set_link(row + 1, col, '-')
        puzzle.cond_set_link(row, col - 1, '|')

        puzzle.cond_set_link(row - 2, col + 3, '|')
        puzzle.cond_set_link(row - 3, col + 2, '-')


def cellfunc_handle_diagonal_ones(puzzle, row, col):
    #hai số 1 chéo nhau thường ép buộc các dấu x đối xứng qua điểm chung.
    """
    Chỉ cần biết 2 cạnh của nó là x,
    thì 1 trong 2 cạnh còn lại có thể là vạch nối.
    Nhưng nếu 2 ô số 1 chạm góc nhau, chúng chia sẻ một điểm chung.
    Quy tắc tại điểm chung đó (chỉ có 0 hoặc 2 vạch) sẽ bắt các dấu x phải xuất hiện đối xứng.
    """
    if puzzle.get_board(row, col) != '1':
        return

    for dr in [-1, 1]:
        for dc in [-1, 1]:
            next_row = row + 2 * dr
            next_col = col + 2 * dc

            if next_row < 0 or next_row >= puzzle.board_height or \
                    next_col < 0 or next_col >= puzzle.board_width:
                # Went off the edge of the board.
                continue

            if puzzle.get_board(next_row, next_col) != '1':
                # Not a diagonal 1.  Skip.
                continue

            if puzzle.get_board(row, col - dc) == 'x' and \
                    puzzle.get_board(row - dr, col) == 'x':
                # 'x' values on outer edges of 1-cell.  Put corresponding 'x'
                # values on outer edges of adjacent diagonal 1-cell.
                puzzle.cond_set_x(next_row, next_col + dc)
                puzzle.cond_set_x(next_row + dr, next_col)

            elif puzzle.get_board(row, col + dc) == 'x' and \
                    puzzle.get_board(row + dr, col) == 'x':
                # 'x' values on inner edges of 1-cell.  Put corresponding 'x'
                # values on inner edges of adjacent diagonal 1-cell.
                puzzle.cond_set_x(next_row, next_col - dc)
                puzzle.cond_set_x(next_row - dr, next_col)


def cellfunc_handle_diagonal_chains(puzzle, row, col):
    '''
    Hàm này xử lý các chuỗi ô chéo có chứa số,
    trong đó các đầu mút có giá trị '3',
    và các giá trị trung gian là '2', v.v.
    '''

    if puzzle.get_board(row, col) != '3':
        return

    for dr in [-1, 1]:
        for dc in [-1, 1]:
            i = 0
            while True:
                i += 1
                next_row = row + 2 * dr * i
                next_col = col + 2 * dc * i

                if next_row < 0 or next_row >= puzzle.board_height or \
                        next_col < 0 or next_col >= puzzle.board_width:
                    # Went off the edge of the board.  End of potential chain.
                    break

                if puzzle.get_board(next_row, next_col) == '3':
                    # This cell is at the end of a chain of 3/2*/3 values.
                    # Put links at both ends of the chains.
                    puzzle.cond_set_link(row, col - dc, '|')
                    puzzle.cond_set_link(row - dr, col, '-')

                    puzzle.cond_set_link(next_row, next_col + dc, '|')
                    puzzle.cond_set_link(next_row + dr, next_col, '-')

                elif puzzle.get_board(next_row, next_col) == '2':
                    side1 = puzzle.get_board(next_row, next_col + dc)
                    side2 = puzzle.get_board(next_row + dr, next_col)
                    if (side1 in ['-', '|'] and side2 == 'x') or \
                            (side2 in ['-', '|'] and side1 == 'x'):
                        # Even though this is a 2-cell, it is the end of a
                        # chain.  Put links at the start of the chain.
                        puzzle.cond_set_link(row, col - dc, '|')
                        puzzle.cond_set_link(row - dr, col, '-')
                else:
                    # This potential chain is over.  Too bad.
                    break


def cellfunc_handle_links_threes(puzzle, row, col):
    '''
    Hàm này xử lý trường hợp ô '3' có hai giá trị 'x'bao quanh một góc,
    và trường hợp ô '3' có một liên kết đi vào một góc của ô.
    '''

    cellval = puzzle.get_board(row, col)
    if cellval != '3':
        return

    num_links = puzzle.count_adjacent_links(row, col)
    if num_links >= 2:
        return

    for dr in [-1, 1]:
        for dc in [-1, 1]:
            dot_row = row + dr
            dot_col = col + dc

            # If the 3-cell has a pair of 'x' values outside one corner-dot
            # then there must be two links going into that dot.
            if puzzle.get_board(dot_row + dr, dot_col) == 'x' and \
                    puzzle.get_board(dot_row, dot_col + dc) == 'x' and \
                    puzzle.get_board(dot_row - dr, dot_col) != 'x' and \
                    puzzle.get_board(dot_row, dot_col - dc) != 'x':
                puzzle.cond_set_link(row, col + dc, '|')
                puzzle.cond_set_link(row + dr, col, '-')

            # If the 3-cell has one link coming into one corner-dot then
            # there must be two links going through the opposite corner-dot.
            if (puzzle.get_board(dot_row + dr, dot_col) in ['-', '|'] or \
                puzzle.get_board(dot_row, dot_col + dc) in ['-', '|']) and \
                    puzzle.get_board(row - dr, col) != 'x' and \
                    puzzle.get_board(row, col - dc) != 'x':
                puzzle.cond_set_link(row - dr, col, '-')
                puzzle.cond_set_link(row, col - dc, '|')


def dotfunc_avoid_multiple_loops(puzzle, row, col):
    '''
    Hàm này đặt các giá trị 'x' giữa các dấu chấm được nối bởi cùng một đường dẫn,
     để ngăn chặn việc tạo ra nhiều vòng khép kín.
    '''

    # If there is only one path, we don't mind closing it.  (Not quite right;
    # the path also needs to pass by all cells with values in them, but this
    # is good enough.)
    if len(puzzle.path_dots) == 1:
        return

    next_row = row + 2
    next_col = col + 2

    dot1 = (row, col)
    if dot1 not in puzzle.dot_paths:
        # If this dot isn't in a path, just skip it.
        return

    if next_row < puzzle.board_height:
        dot2 = (next_row, col)
        if dot2 in puzzle.dot_paths and \
                puzzle.dot_paths[dot1] == puzzle.dot_paths[dot2]:
            puzzle.cond_set_x(row + 1, col)

    if next_col < puzzle.board_width:
        dot2 = (row, next_col)
        if dot2 in puzzle.dot_paths and \
                puzzle.dot_paths[dot1] == puzzle.dot_paths[dot2]:
            puzzle.cond_set_x(row, col + 1)


def cellfunc_handle_closed_corners(puzzle, row, col):
    '''
    This helper function handles cases where a corner of a cell is fully
    closed off (i.e. the cell has 'x' values on two adjacent sides).  This
    is an unusual situation and is already partially covered by other cases,
    but this helps when numbers are in the corners of the puzzles, or when
    other similar cases arise in the middle of the puzzle.
    '''

    cellval = puzzle.get_board(row, col)
    if cellval == ' ':
        return

    for dr in [-1, 1]:
        for dc in [-1, 1]:
            # This will be true if we have a wall above or below.
            # The value of dr will specify which direction it is.
            # v_wall = puzzle.get_board(row + 2 * dr, col + dc) == 'x' and \
            #         puzzle.get_board(row + 2 * dr, col - dc) == 'x'

            # This will be true if we have a wall to the left or right.
            # The value of dc will specify which direction it is.
            # h_wall = puzzle.get_board(row + dr, col + 2 * dc) == 'x' and \
            #         puzzle.get_board(row - dr, col + 2 * dc) == 'x'

            # if v_wall and h_wall:

            corner = puzzle.get_board(row + 2 * dr, col + dc) == 'x' and \
                     puzzle.get_board(row + dr, col + 2 * dc) == 'x'

            if corner:
                if cellval == '1':
                    puzzle.cond_set_x(row + dr, col)
                    puzzle.cond_set_x(row, col + dc)

                elif cellval == '2' and \
                        puzzle.get_board(row + 2 * dr, col - dc) == 'x' and \
                        puzzle.get_board(row - dr, col + 2 * dc) == 'x':

                    # We can only apply this rule if it's a "hard corner".
                    puzzle.cond_set_link(row + dr, col - 2 * dc, '-')
                    puzzle.cond_set_link(row - 2 * dr, col + dc, '|')

                elif cellval == '3':
                    puzzle.cond_set_link(row + dr, col, '-')
                    puzzle.cond_set_link(row, col + dc, '|')


OUTSIDE_COLOR = 'o'


class Puzzle:
    def __init__(self, rows, cols, cell_values):

        self.rows = rows
        self.cols = cols

        '''
        Xây dựng bảng, bao gồm các yếu tố cho các chấm, các ô chứa số và
        cuối cùng là các giá trị 'x' hoặc liên kết giữa các chấm | -.
        '''
        self.board_width = 2 * (cols + 1) + 1
        self.board_height = 2 * (rows + 1) + 1
        self.board = bytearray()

        top_bottom_row = b'#x' * (cols + 1) + b'#'
        dot_row = b'x' + b'. ' * cols + b'.x'

        assert len(top_bottom_row) == self.board_width, \
            'board-width %d doesn\'t match length of top/bottom row %d:\n"%s"' % \
            (self.board_width, len(top_bottom_row), top_bottom_row)

        assert len(dot_row) == self.board_width, \
            'board-width %d doesn\'t match length of dot-row %d:\n"%s"' % \
            (self.board_width, len(dot_row), dot_row)

        self.board.extend(top_bottom_row)
        # print('1:' + str(self.board))
        for r in range(rows):
            self.board.extend(dot_row)
            # print('2:' + str(self.board))

            row_values = [bytes(ch, 'ascii') for ch in cell_values[r]]
            cell_row = b'# ' + b' '.join(row_values) + b' #'

            assert len(cell_row) == self.board_width, \
                'board-width %d doesn\'t match length of cell-row %d:\n"%s"' % \
                (self.board_width, len(cell_row), cell_row)

            self.board.extend(cell_row)

        self.board.extend(dot_row)
        self.board.extend(top_bottom_row)

        assert float(len(self.board)) / self.board_width == float(self.board_height), \
            'board-height %d doesn\'t match length of board %d' % \
            (len(self.board), self.board_height)

        # Các trường được sử dụng để theo dõi các đường dẫn khác nhau
        self.next_path_id = 1
        self.dot_paths = {}  #Điểm -> Thuộc dây nào
        self.path_dots = {}  #Dây -> Gồm những điểm nào

        '''
        # Giá trị changed sử dụng để theo dõi trạng thái của câu đố đã được thay đổi hay chưa.
         Nếu cố gắng áp dụng các quy tắc giải và không có thay đổi nào được thực hiện,-> phải bắt đầu đoán.
        '''
        self.changed = False
        self.change_count = 0

        self.board_colors = bytearray((self.rows + 2) * (self.cols + 2))

        for r in range(1, self.rows + 2):
            for c in range(1, self.cols + 2):
                self.set_board_color(r, c, 'i');

        for r in range(self.rows + 2):
            self.set_board_color(r, 0, OUTSIDE_COLOR)
            self.set_board_color(r, self.cols + 1, OUTSIDE_COLOR)

        for c in range(self.cols + 2):
            self.set_board_color(0, c, OUTSIDE_COLOR)
            self.set_board_color(self.rows + 1, c, OUTSIDE_COLOR)

    def get_board(self, r, c):
        assert r >= 0 and r < self.board_height, \
            "Invalid row index %d (must be in range [0, %d)" % \
            (r, self.board_height)
        assert c >= 0 and c < self.board_width, \
            "Invalid column index %d (must be in range [0, %d)" % \
            (c, self.board_width)

        return chr(self.board[r * self.board_width + c])

    def set_board(self, r, c, val):
        assert r >= 0 and r < self.board_height, \
            "Invalid row index %d (must be in range [0, %d)" % \
            (r, self.board_height)
        assert c >= 0 and c < self.board_width, \
            "Invalid column index %d (must be in range [0, %d)" % \
            (c, self.board_width)

        self.board[r * self.board_width + c] = ord(val)

    def set_board_color(self, r, c, val):
        assert r >= 0 and r < self.rows + 2
        assert c >= 0 and c < self.cols + 2

        self.board_colors[r * (self.cols + 2) + c] = ord(val)

    def get_board_color(self, r, c):
        assert r >= 0 and r < self.rows + 2
        assert c >= 0 and c < self.cols + 2

        return chr(self.board_colors[r * (self.cols + 2) + c])

    def is_changed(self):
        '''
        xem bảng đã được thay đổi kể từ lần cuối cùng cờ "changed" được xóa.
        '''
        return self.changed

    def set_changed(self, value=True):
        '''
        Sets the "changed".
        '''
        self.changed = value

    def clear_changed_count(self):
        '''
        Clears "changed" flag, and reset"change-count"= 0.
        '''
        self.changed = False
        self.change_count = 0

    def get_board_as_string(self):
        # row_strs = map(lambda r: ''.join(r), self.board)
        # return '\n'.join(row_strs)
        return str(self.board)

    def pretty_print(self, include_xes=True, include_numbers=True):
        #in

        print("Puzzle size:  %d x %d" % (self.rows, self.cols))

        for r in range(1, 2 * self.rows + 2):
            row_start = r * self.board_width
            row_end = row_start + self.board_width
            rowdata = self.board[row_start:row_end]
            rowdata = rowdata.decode('ascii')

            if not include_numbers:
                for i in range(len(rowdata)):
                    if rowdata[i] in ['0', '1', '2', '3']:
                        rowdata[i] = ' '

            if not include_xes:
                for i in range(len(rowdata)):
                    if rowdata[i] == 'x':
                        rowdata[i] = ' '

            print(' '.join(rowdata[1:2 * self.cols + 2]))
    #Điều kiện dừng (Base case).
    def is_solved(self):
        #một vòng khép kín duy nhất
        if len(self.path_dots) > 1:
            return False

        # Với mỗi ô có số, nó đếm số vạch thực tế (count_adjacent_links)
        #Nếu số vạch thực tế không khớp với số yêu cầu (required != actual), câu đố chưa xong
        # around that cell.
        for r in range(2, 2 * self.rows + 1, 2):
            for c in range(2, 2 * self.cols + 1, 2):
                val = self.get_board(r, c)
                if val != ' ':
                    required = int(val)
                    actual = self.count_adjacent_links(r, c)
                    if required != actual:
                        return False

        # Mọi dấu chấm đã có vạch đi qua thì bắt buộc phải có đúng 2 vạch (1 vạch đi vào, 1 vạch đi ra)
        # around it.  (This ensures that the path is closed.)
        path_id = list(self.path_dots.keys())[0]
        path = self.path_dots[path_id]
        for dot in path:
            (r, c) = dot
            links = self.count_adjacent_links(r, c)
            assert links <= 2, \
                "Invalid number of links at (%d,%d):  %d" % (r, c, links)
            if links != 2:
                return False

        return True
    #Cắt tỉa (Pruning).
    def can_solve(self):
        '''
        Nếu bất kỳ ô nào có một số đã bị ràng buộc sao cho nó KHÔNG THỂ có số lượng liên kết được chỉ định thì báo lỗi false.
        '''
        for r in range(2, 2 * self.rows + 1, 2):
            for c in range(2, 2 * self.cols + 1, 2):
                val = self.get_board(r, c)
                if val != ' ':
                    required = int(val)
                    actual = self.count_adjacent_links(r, c)
                    xes = self.count_adjacent_xes(r, c)

                    if 4 - xes < required:
                        #print("Can't solve:  too many x-es around the cell")
                        return False

                    if actual + xes == 4 and required != actual:
                        #print("Can't solve:  wrong number of links around cell")
                        return False

        return True

    def iter_cells(self, cell_func):
        for r in range(2, 2 * self.rows + 1, 2):
            for c in range(2, 2 * self.cols + 1, 2):
                cell_func(self, r, c)

    def iter_dots(self, dot_func):
        for r in range(1, 2 * self.rows + 2, 2):
            for c in range(1, 2 * self.cols + 2, 2):
                # print('(%d, %d)' % (r, c))
                dot_func(self, r, c)

    def count_adjacent_links(self, row, col):
        count = 0
        for r in range(row - 1, row + 2):
            for c in range(col - 1, col + 2):
                if self.get_board(r, c) in ['-', '|']:
                    count += 1
        return count

    def count_adjacent_xes(self, row, col):
        count = 0
        for r in range(row - 1, row + 2):
            for c in range(col - 1, col + 2):
                if self.get_board(r, c) == 'x':
                    count += 1
        return count

    def cond_set_x(self, row, col):
        if self.get_board(row, col) == ' ':
            self.set_board(row, col, 'x')
            self.set_changed()
            self.change_count += 1

    def cond_set_link(self, row, col, value):
        assert (value in ['-', '|'])

        if self.get_board(row, col) == ' ':
            if value == '-':
                assert (self.get_board(row, col - 1) == '.' and \
                        self.get_board(row, col + 1) == '.')
            else:
                assert (self.get_board(row - 1, col) == '.' and \
                        self.get_board(row + 1, col) == '.')

            self.set_board(row, col, value)
            self.set_changed()
            self.change_count += 1

            # Update the path information!

            if value == '-':
                dot1 = (row, col - 1)
                dot2 = (row, col + 1)
            else:
                dot1 = (row - 1, col)
                dot2 = (row + 1, col)

            if dot1 not in self.dot_paths and dot2 not in self.dot_paths:
                # Easy case:  neither dot is in a path!

                path_id = self.next_path_id
                self.next_path_id += 1
                # print("Creating new path with ID %d" % path_id)

                self.dot_paths[dot1] = path_id
                self.dot_paths[dot2] = path_id

                self.path_dots[path_id] = [dot1, dot2]

            elif dot1 not in self.dot_paths:
                # dot2 is in an existing path.

                path_id = self.dot_paths[dot2]
                # print("Adding dot1 to dot2's path with ID %d" % path_id)

                self.dot_paths[dot1] = path_id
                self.path_dots[path_id].append(dot1)

            elif dot2 not in self.dot_paths:
                # dot1 is in an existing path.

                path_id = self.dot_paths[dot1]
                # print("Adding dot2 to dot1's path with ID %d" % path_id)

                self.dot_paths[dot2] = path_id
                self.path_dots[path_id].append(dot2)

            else:
                # Both dots are in paths

                dot1_path_id = self.dot_paths[dot1]
                dot2_path_id = self.dot_paths[dot2]

                # print("Dot 1:  %s\t\tDot 2:  %s" % (dot1, dot2))

                if dot1_path_id == dot2_path_id:
                    if len(self.path_dots) > 1:
                        # self.pretty_print()
                        raise MoveError("Can't join dots %s and %s" % (dot1, dot2))
                    else:
                        # In this situation we are joining two ends of a single
                        # path together.  Thus, all path-dots are already in the path.
                        return

                # Update dot2's path to be part of dot1's path

                dot2_path_dots = self.path_dots[dot2_path_id]
                # print(dot2_path_dots)
                for dot in dot2_path_dots:
                    self.dot_paths[dot] = dot1_path_id

                self.path_dots[dot1_path_id].extend(dot2_path_dots)
                del self.path_dots[dot2_path_id]

    def fill_in_xes(self):
        self.iter_cells(cellfunc_fill_in_xes)

    def fill_in_links(self):
        self.iter_cells(cellfunc_fill_in_links)

    def handle_ones(self):
        self.iter_cells(cellfunc_handle_diagonal_ones)

    def handle_threes(self):
        self.iter_cells(cellfunc_handle_adjacent_threes)
        self.iter_cells(cellfunc_handle_links_threes)

    def update_dot_state(self):
        self.iter_dots(dotfunc_fill_in_xes_links)

    def avoid_multiple_loops(self):
        self.iter_dots(dotfunc_avoid_multiple_loops)

    def handle_closed_corners(self):
        self.iter_cells(cellfunc_handle_closed_corners)

    def handle_diagonal_chains(self):
        '''
        xác định các chuỗi chéo [3, 2, 2, ..., 2, 3],
        cho phép chúng ta đặt hai mắt xích ở mỗi đầu của chuỗi.
        '''
        self.iter_cells(cellfunc_handle_diagonal_chains)

    def check_row_links(self):
        for r in range(2, 2 * self.rows + 1, 2):
            num_links = 0
            num_unknowns = 0
            unknown = None

            for c in range(1, 2 * self.cols + 2, 2):
                val = self.get_board(r, c)
                if val == '|':
                    num_links += 1
                elif val == ' ':
                    num_unknowns += 1
                    if num_unknowns == 1:
                        unknown = (r, c)

            if num_unknowns == 1:
                r, c = unknown
                if num_links % 2 == 0:
                    print("FOUND ROW LINK, SETTING TO X")
                    self.cond_set_x(r, c)
                else:
                    print("FOUND ROW LINK, SETTING TO |")
                    self.cond_set_link(r, c, '|')

    def check_col_links(self):
        for c in range(2, 2 * self.cols + 1, 2):
            num_links = 0
            num_unknowns = 0
            unknown = None

            for r in range(1, 2 * self.rows + 2, 2):
                val = self.get_board(r, c)
                if val == '-':
                    num_links += 1
                elif val == ' ':
                    num_unknowns += 1
                    if num_unknowns == 1:
                        unknown = (r, c)

            if num_unknowns == 1:
                r, c = unknown
                if num_links % 2 == 0:
                    # print("FOUND COLUMN LINK, SETTING TO X")
                    self.cond_set_x(r, c)
                else:
                    # print("FOUND COLUMN LINK, SETTING TO -")
                    self.cond_set_link(r, c, '-')

    def iter_solve(self, verbose=False):
        '''
        Cố gắng giải câu đố bằng cách áp dụng lặp đi lặp lại các quy tắc
        được mã hóa trong các hàm hỗ trợ khác nhau.
        Nếu hoàn thành một vòng lặp mà không thực hiện bất kỳ thay đổi nào thì chúng ta sẽ dừng lại.
        Điều này có thể báo hiệu rằng đã tìm ra giải pháp,
        hoặc đã đạt đến giới hạn của những gì có thể giải quyết bằng các quy tắc đơn giản,
        hoặc đã gặp phải cấu hình bảng không hợp lệ.
        '''

        operations = [
            (self.handle_closed_corners, "Handling closed corners"),
            (self.fill_in_xes, "Filling in x-es based on cell values"),
            (self.fill_in_links, "Filling in links based on cell values"),
            (self.handle_threes, "Filling in links based on adjacent 3-cells"),
            (self.handle_ones, "Filling in x-es based on adjacent 1-cells"),
            (self.update_dot_state, "Filling in x-es and links based on state adjacent to dots"),
            (self.avoid_multiple_loops, "Avoid multiple loops"),
        ]

        iter = 0
        while True:
            iter += 1
            made_change = False

            # Do basic operations
            for op in operations:
                self.set_changed(False)
                op[0]()
                if self.is_changed():
                    if verbose:
                        print("%d:  %s" % (iter, op[1]))
                        # p.pretty_print()
                    made_change = True

            # If we didn't have any changes so far, do some of the
            # more compute-intensive operations.
            if not made_change:
                self.set_changed(False)
                self.handle_diagonal_chains()
                if self.is_changed():
                    if verbose:
                        print("%d:  (ADV) Handle diagonal chains" % iter)
                    made_change = True

                self.set_changed(False)
                self.check_row_links()
                self.check_col_links()
                if self.is_changed():
                    if verbose:
                        print("%d:  (ADV) Check row/column links" % iter)
                    made_change = True

            if not self.can_solve():
                print("Cannot solve this board:  invalid configuration reached.")
                break

            if not made_change:
                break

    def dots_are_connected(self, dot1, dot2):
        if dot1 in self.dot_paths and dot2 in self.dot_paths:
            dot1_path_id = self.dot_paths[dot1]
            dot2_path_id = self.dot_paths[dot2]

            return dot1_path_id == dot2_path_id
        else:
            return False

    def score_move(self, cell_r, cell_c):
        score = 0
        cellval = self.get_board(cell_r, cell_c)
        if cellval in ['0', '1', '2', '3']:
            cellval = int(cellval)
            links = self.count_adjacent_links(cell_r, cell_c)

            if cellval == links:
                print("UNEXPECTED:  can't add another link!")
                score = -10

            score = 5 - cellval + links

        return score

    def enumerate_moves(self):
        moves = set()
        for r in range(1, 2 * self.rows + 2, 2):
            for c in range(1, 2 * self.cols + 2, 2):
                if self.count_adjacent_links(r, c) == 1:
                    # Construct a tuple so we can look up in the dot-maps whether
                    # two dots are already connected by another line.
                    dot = (r, c)
                    score = 0

                    if self.get_board(r, c - 1) == ' ' and \
                            not self.dots_are_connected(dot, (r, c - 1)):
                        score = self.score_move(r - 1, c - 1) + \
                                self.score_move(r + 1, c - 1)
                        moves.add((r, c - 1, '-', score))

                    if self.get_board(r, c + 1) == ' ' and \
                            not self.dots_are_connected(dot, (r, c + 1)):
                        score = self.score_move(r - 1, c + 1) + \
                                self.score_move(r + 1, c + 1)
                        moves.add((r, c + 1, '-', score))

                    if self.get_board(r - 1, c) == ' ' and \
                            not self.dots_are_connected(dot, (r - 1, c)):
                        score = self.score_move(r - 1, c - 1) + \
                                self.score_move(r - 1, c + 1)
                        moves.add((r - 1, c, '|', score))

                    if self.get_board(r + 1, c) == ' ' and \
                            not self.dots_are_connected(dot, (r + 1, c)):
                        score = self.score_move(r + 1, c - 1) + \
                                self.score_move(r + 1, c + 1)
                        moves.add((r + 1, c, '|', score))

        moves = list(moves)

        # moves.sort(lambda m1, m2: m2[3] - m1[3])
        moves.sort(key=lambda m: m[3])

        return moves

    def apply_move(self, move):
        self.cond_set_link(move[0], move[1], move[2])


def load_puzzle(filename):
    '''
    Loads a puzzle from the simple text format:

    [rows] [cols]
    [row 0 data]
    [row 1 data]
    ...
    '''

    f = open(filename)

    line = f.readline()
    dims = line.split()
    rows = int(dims[0])
    cols = int(dims[1])

    cell_values = []
    for i in range(rows):
        row_values = f.readline()
        cell_values.append(row_values[:-1])

    f.close()

    return Puzzle(rows, cols, cell_values)
