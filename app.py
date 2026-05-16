from flask import Blueprint, render_template, request, jsonify
import requests
from bs4 import BeautifulSoup
import time
import cv2
import numpy as np
import pytesseract
import os

# Import các logic xử lý game của bạn
# Đảm bảo các file này nằm trong cùng folder Slitherlink
from Slitherlink.Puzzle import Puzzle
from Slitherlink.solve_heuristic import solve_heuristic

# Khởi tạo Blueprint
slitherlink_bp = Blueprint('Slitherlink', __name__,
                           template_folder='templates',
                           static_folder='static',
                           static_url_path='/static')

# Cấu hình Tesseract
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'


# --- CÁC HÀM HELPER (Giữ nguyên logic từ FastAPI của bạn) ---

def scrape_puzzle(size_id: str):
    url = f"http://www.puzzle-loop.com/?v=0&size={size_id}"
    try:
        page = requests.get(url, timeout=5)
        soup = BeautifulSoup(page.text, 'html.parser')
        puzzle_table = soup.find('table', id='LoopTable')
        board = []
        if puzzle_table:
            rows = puzzle_table.find_all('tr')[1::2]
            for r in rows:
                cols = r.find_all('td')[1::2]
                board.append([int(c.string) if c.string else -1 for c in cols])
        return board
    except Exception as e:
        print(f"Lỗi Scrape: {e}")
        return []


def ocr_cell(cell_img, r, c):
    if cell_img is None or cell_img.size == 0:
        return -1
    try:
        gray = cv2.cvtColor(cell_img, cv2.COLOR_BGR2GRAY) if len(cell_img.shape) == 3 else cell_img
        _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if contours:
            main_contour = max(contours, key=cv2.contourArea)
            mask = np.zeros_like(thresh)
            cv2.drawContours(mask, [main_contour], -1, 255, -1)
            ocr_ready = cv2.bitwise_and(thresh, mask)
        else:
            ocr_ready = thresh

        ocr_ready = cv2.bitwise_not(ocr_ready)
        padded = cv2.copyMakeBorder(ocr_ready, 20, 20, 20, 20, cv2.BORDER_CONSTANT, value=255)

        # Tạo thư mục debug nếu chưa có
        if not os.path.exists("debug_cells"):
            os.makedirs("debug_cells")
        cv2.imwrite(f"debug_cells/cell_{r}_{c}.png", padded)

        config = r'-psm 7'
        text = pytesseract.image_to_string(padded, config=config).strip()
        digits = [s for s in text if s.isdigit()]
        if digits:
            val = int(digits[0])
            return val if 0 <= val <= 3 else -1
    except Exception as e:
        print(f"Lỗi OCR ô {r},{c}: {e}")
    return -1


def extract_board_from_image(img, size):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY_INV)
    contours, _ = cv2.findContours(thresh, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)

    dot_points = [cnt for cnt in contours if 2 < cv2.contourArea(cnt) < 500]
    if not dot_points: return None

    all_dots = np.vstack(dot_points)
    x, y, w, h = cv2.boundingRect(all_dots)
    pts = np.array([[x, y], [x + w, y], [x + w, y + h], [x, y + h]], dtype=np.float32)

    side = 600
    dst = np.array([[0, 0], [side, 0], [side, side], [0, side]], dtype=np.float32)
    M = cv2.getPerspectiveTransform(pts, dst)
    warped = cv2.warpPerspective(gray, M, (side, side))

    board = []
    cell_size = side / size
    for r in range(size):
        row = []
        for c in range(size):
            x1, y1 = int(c * cell_size), int(r * cell_size)
            x2, y2 = int((c + 1) * cell_size), int((r + 1) * cell_size)
            cell_img = warped[y1:y2, x1:x2]
            ch, cw = cell_img.shape
            margin = int(cw * 0.15)
            inner_cell = cell_img[margin:ch - margin, margin:cw - margin]
            row.append(ocr_cell(inner_cell, r, c))
        board.append(row)
    return board


# --- CÁC ROUTES CỦA FLASK ---

@slitherlink_bp.route('/')
def index():
    # File này phải nằm trong Slitherlink/templates/slitherlink_index.html
    return render_template('slitherlink_index.html')


@slitherlink_bp.route('/fetch-puzzle/', defaults={'size_id': ''})
@slitherlink_bp.route('/fetch-puzzle/<size_id>')
def fetch_new_puzzle(size_id):
    board = scrape_puzzle(size_id)
    actual_size = len(board) if board else 5
    return jsonify({"size": actual_size, "board": board})


@slitherlink_bp.route('/solve', methods=['POST'])
def solve_api():
    data = request.get_json()
    size = data.get('size')
    board_data = data.get('board')

    cell_values = ["".join([str(v) if v != -1 else " " for v in row]) for row in board_data]
    p = Puzzle(size, size, cell_values)

    start_time = time.time()
    success = solve_heuristic(p)
    end_time = time.time()

    horiz = [
        [1 if p.get_board(2 * r + 1, 2 * c + 2) == '-' else (-1 if p.get_board(2 * r + 1, 2 * c + 2) == 'x' else 0) for
         c in range(size)] for r in range(size + 1)]
    vert = [
        [1 if p.get_board(2 * r + 2, 2 * c + 1) == '|' else (-1 if p.get_board(2 * r + 2, 2 * c + 1) == 'x' else 0) for
         c in range(size + 1)] for r in range(size)]

    return jsonify({
        "success": success,
        "horiz": horiz,
        "vert": vert,
        "time": round(end_time - start_time, 4)
    })


@slitherlink_bp.route('/scan-puzzle-ai/', methods=['POST'])
def scan_puzzle():
    if 'file' not in request.files:
        return jsonify({"error": "Không tìm thấy file ảnh."}), 400

    file = request.files['file']
    expected_size = int(request.form.get('expected_size', 5))

    try:
        # Đọc file ảnh từ request
        filestr = file.read()
        nparr = np.frombuffer(filestr, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        if img is None:
            return jsonify({"error": "File tải lên bị hỏng."}), 400

        board = extract_board_from_image(img, expected_size)
        if board is None:
            return jsonify({"error": "Không tìm thấy khung lưới."}), 400

        return jsonify({"size": len(board), "board": board})
    except Exception as e:
        print(f"LỖI AI: {e}")
        return jsonify({"error": "Lỗi xử lý ảnh."}), 500
