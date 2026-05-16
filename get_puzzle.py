#!/usr/bin/python

import requests
from bs4 import BeautifulSoup

def get_puzzle(page_url):
    page = requests.get(page_url, headers={'User-Agent': 'Mozilla/5.0'})
    soup = BeautifulSoup(page.text, 'html.parser')

    puzzle_table = soup.find('table', id='LoopTable')
    if not puzzle_table:
        return None

    puzzle_rows = puzzle_table.findAll('tr')
    puzzle_rows = puzzle_rows[1::2]

    row_specs = []

    for row in puzzle_rows:
        puzzle_cols = row.findAll('td')
        puzzle_cols = puzzle_cols[1::2]

        row_spec = ''

        for col in puzzle_cols:
            cellval = col.string
            if not cellval:
                cellval = ' '
            row_spec += cellval

        row_specs.append(row_spec)

    # [ĐÃ SỬA]: Trả về mảng thay vì in ra màn hình
    return row_specs


# Các ghi chú size của bạn:
# [no size] = 5x5 normal
#         4 = 5x5 hard
#        10 = 7x7 normal
#        ... (giữ nguyên ghi chú của bạn)

# [ĐÃ SỬA]: Bọc phần test này lại để nó không tự chạy khi bị file khác import
if __name__ == "__main__":
    board = get_puzzle('http://www.puzzle-loop.com/?v=0&size=5')
    if board:
        print("%d %d" % (len(board), len(board[0])))
        print('\n'.join(board))