import random, copy
from Slitherlink.Puzzle import MoveError
def solve_heuristic(p):
    attempts = []
    board_set = set()
    skipped = 0

    assert p.can_solve(), "solve-puzzle was handed a board it couldn't solve!"

    info = (p, 1, None, 0, 0)
    attempts.append(info)

    while len(attempts) > 0:
        print("%d more board configurations to try." % len(attempts))

        # info = attempts.pop(0)
        info = attempts.pop(random.randint(0, len(attempts) - 1))

        (p, depth, move, i_move, n_moves) = info

        if depth > 1:
            print("DEPTH %d:  Move %d of %d:  %s  Attempting to solve." % \
                  (depth, i_move, n_moves, str(move)))
        else:
            print("Attempting initial solution.")

        try:
            p.iter_solve()
        except MoveError:
            print("Encountered an invalid move.  Abandoning this path.")
            # failures.add(p_copy.get_board_as_string())
            continue

        if p.is_solved():
            print("DEPTH %d:  SOLVED" % depth)
            p.pretty_print()
            return True

        elif not p.can_solve():
            print("Couldn't solve this configuration, abandoning.")
            continue

        else:
            print("DEPTH %d:  NOT SOLVED (change-count = %d)" % (depth, p.change_count))

            # Enumerate the remaining moves from this board.
            moves = p.enumerate_moves()
            print("From this board configuration, found %d more moves." % len(moves))

            '''
            # Show the move options:
            p_opts = copy.deepcopy(p)
            for move in moves:
                p_opts.set_board(move[0], move[1], '*')
            p_opts.pretty_print()
            print("moves:  %s" % moves)
            raw_input()
            '''

            # Add each move option into the list of attempts.

            total_moves = len(moves)
            new_moves = 0
            move_infos = []
            for i in range(total_moves):
                move = moves[i]

                p_copy = copy.deepcopy(p)
                p_copy.clear_changed_count()
                p_copy.apply_move(move)

                board_str = p_copy.get_board_as_string()
                if board_str in board_set:
                    print(" * SKIPPING move - it's already enqueued")
                    skipped += 1
                    continue

                new_moves += 1
                info = (p_copy, depth + 1, move, i + 1, total_moves)
                # attempts.append(info)
                # board_set.add(board_str)
                move_infos.append(info)

            # Keep only some of the moves we found.
            if len(move_infos) > 10:
                random.shuffle(move_infos)
                move_infos = move_infos[:10]
                new_moves = len(move_infos)

            attempts.extend(move_infos)
            print("Added %d new moves to the set of attempts." % new_moves)

    print("Couldn't solve puzzle.")
    return False
