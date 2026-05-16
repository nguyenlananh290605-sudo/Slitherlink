import copy
import sys

try:
    from Slitherlink.Puzzle import Puzzle, MoveError
except ImportError:
    try:
        from Puzzle import Puzzle, MoveError
    except ImportError:
        class MoveError(Exception): pass

def evaluate_single_edge(p, r, c):
    """
    HÀM LƯỢNG GIÁ: Tính điểm ưu tiên cho một vị trí cạnh.
    Giúp Branching chọn được 'nhánh' thơm nhất để thử trước.
    """
    score = 0
    is_horizontal = (r % 2 != 0)
    # Lấy tọa độ các ô số lân cận
    neighbors = [(r - 1, c), (r + 1, c)] if is_horizontal else [(r, c - 1), (r, c + 1)]

    for nr, nc in neighbors:
        if (0 <= nr < p.board_height and 0 <= nc < p.board_width
                and nr % 2 == 0 and nc % 2 == 0):
            val = p.get_board(nr, nc)
            if val == '3':   score += 15
            elif val == '0': score += 25
            elif val == '2': score += 5
            elif val == '1': score += 2
    return score

def get_potential_score(p):
    """
    HÀM CẬN (Bounding): Tính tổng điểm tối đa có thể đạt được từ các cạnh còn trống.
    """
    potential = 0
    for r in range(p.board_height):
        for c in range(p.board_width):
            # Kiểm tra xem có phải vị trí cạnh không
            if (r % 2 != 0 or c % 2 != 0) and not (r % 2 != 0 and c % 2 != 0):
                if p.get_board(r, c) == ' ':
                    potential += evaluate_single_edge(p, r, c)
    return potential

def solve_branch_and_bound(p, current_score=0, threshold=0):
    """
    THUẬT TOÁN NHÁNH VÀ CẬN CỔ ĐIỂN
    """
    # 1. KIỂM TRA ĐÍCH (GOAL)
    if p.is_solved():
        return True

    # 2. TÍNH TOÁN CẬN (BOUNDING)
    # Công thức: $$f(n) = g(n) + h(n)$$
    # (Điểm hiện tại + Điểm tiềm năng tối đa)
    max_possible_score = current_score + get_potential_score(p)
    if max_possible_score < threshold:
        return False  # PRUNING: Cắt nhánh vì không bao giờ đạt đủ điểm threshold

    # 3. CHỌN CẠNH ĐỂ RẼ NHÁNH (BRANCHING)
    best_r, best_c, max_val = -1, -1, -1
    for r in range(p.board_height):
        for c in range(p.board_width):
            if (r % 2 != 0 or c % 2 != 0) and not (r % 2 != 0 and c % 2 != 0):
                if p.get_board(r, c) == ' ':
                    val = evaluate_single_edge(p, r, c)
                    if val > max_val:
                        max_val = val
                        best_r, best_c = r, c

    if best_r == -1:
        return False

    edge_type = '-' if best_r % 2 != 0 else '|'

    # --- NHÁNH 1: THỬ ĐẶT VẠCH (Ưu tiên vì có điểm cao) ---
    p_link = copy.deepcopy(p)
    try:
        p_link.apply_move((best_r, best_c, edge_type))
        if p_link.can_solve():
            if solve_branch_and_bound(p_link, current_score + max_val, threshold):
                sync_puzzle(p, p_link)
                return True
    except (MoveError, Exception):
        pass

    # --- NHÁNH 2: THỬ ĐẶT X ---
    p_x = copy.deepcopy(p)
    try:
        p_x.cond_set_x(best_r, best_c)
        if p_x.can_solve():
            if solve_branch_and_bound(p_x, current_score, threshold):
                sync_puzzle(p, p_x)
                return True
    except (MoveError, Exception):
        pass

    return False

def sync_puzzle(p_target, p_source):
    """ Sao chép trạng thái để trả về kết quả cho hàm gọi đệ quy trước đó """
    p_target.board = p_source.board
    p_target.dot_paths = p_source.dot_paths
    p_target.path_dots = p_source.path_dots