# Slitherlink Puzzle Game and Solver

Ứng dụng web chơi và giải tự động câu đố **Slitherlink**, xây dựng bằng **Flask** (Python) + **Vanilla JS**. Hỗ trợ nhiều kích thước bảng, giải tự động bằng AI, nhận diện puzzle từ ảnh chụp, và animation trực quan hóa thuật toán DFS.

---

## 📋 Mục lục

- [Tính năng](#-tính-năng)
- [Cấu trúc dự án](#-cấu-trúc-dự-án)
- [Yêu cầu hệ thống](#-yêu-cầu-hệ-thống)
- [Cài đặt](#-cài-đặt)
- [Cách chạy](#-cách-chạy)
- [API Endpoints](#-api-endpoints)
- [Các thuật toán](#-các-thuật-toán)
- [Luật chơi Slitherlink](#-luật-chơi-slitherlink)

---

## ✨ Tính năng

| Tính năng | Mô tả |
|---|---|
| 🆕 **Lấy puzzle mới** | Tự động scrape puzzle từ [puzzle-loop.com](http://www.puzzle-loop.com) |
| 📐 **Nhiều kích thước** | Hỗ trợ 5×5, 7×7, 10×10, 15×15, 20×20 (Normal & Hard) |
| 📷 **Scan từ ảnh** | Nhận diện bảng puzzle từ ảnh chụp bằng OpenCV + Tesseract OCR |
| 🤖 **Tự động giải** | Giải puzzle bằng thuật toán Heuristic kết hợp Backtracking |
| 🎬 **Trực quan DFS** | Animation minh họa quá trình tìm đường DFS Backtracking theo từng bước |
| 💡 **Gợi ý (Hint)** | Tiết lộ một cạnh đúng trong solution |
| ✅ **Kiểm tra** | Kiểm tra lời giải của người dùng so với đáp án |
| 🔍 **Phát hiện lỗi** | Highlight real-time các ô vi phạm ràng buộc số |
| 🔎 **Zoom** | Phóng to/thu nhỏ bảng (50% – 200%) |

---

## 📁 Cấu trúc dự án

```
Slitherlink/
├── app.py                      # Flask Blueprint, định nghĩa tất cả routes
├── get_puzzle.py               # Scrape puzzle từ puzzle-loop.com
│
├── Puzzle.py                   # Core: biểu diễn bảng + toàn bộ logic luật
├── solve_heuristic.py          # Thuật toán Heuristic (tìm kiếm ngẫu nhiên có hướng dẫn)
├── solve_branch_and_bound.py   # Thuật toán Branch & Bound (nhánh cận)
│
├── templates/
│   └── slitherlink_index.html  # Giao diện game (HTML + JS)
│
└── static/
    └── css/
        └── style.css           # CSS giao diện
```

---

## 🖥️ Yêu cầu hệ thống

- **Python** ≥ 3.8
- **Tesseract OCR** (cho tính năng Scan ảnh)
  - Windows: tải tại [UB-Mannheim/tesseract](https://github.com/UB-Mannheim/tesseract/wiki)
  - Mặc định cài tại `C:\Program Files\Tesseract-OCR\tesseract.exe`

### Thư viện Python

```txt
flask
requests
beautifulsoup4
opencv-python
numpy
pytesseract
```

Cài đặt tất cả:

```bash
pip install flask requests beautifulsoup4 opencv-python numpy pytesseract
```

---

## 🚀 Cài đặt

### 1. Clone hoặc copy project

```
your_flask_app/
└── Slitherlink/          ← toàn bộ folder này
    ├── app.py
    ├── Puzzle.py
    └── ...
```

### 2. Đăng ký Blueprint trong Flask app chính

```python
# main.py (hoặc __init__.py của Flask app)
from flask import Flask
from Slitherlink.app import slitherlink_bp

app = Flask(__name__)
app.register_blueprint(slitherlink_bp, url_prefix='/slitherlink')

if __name__ == '__main__':
    app.run(debug=True)
```

### 3. (Tuỳ chọn) Cấu hình đường dẫn Tesseract

Nếu Tesseract không ở vị trí mặc định, chỉnh trong `app.py`:

```python
pytesseract.pytesseract.tesseract_cmd = r'C:\đường\dẫn\tới\tesseract.exe'
```

---

## ▶️ Cách chạy

```bash
python main.py
```

Truy cập trình duyệt tại: **http://localhost:5000/slitherlink/**

---

## 🔌 API Endpoints

| Method | Endpoint | Mô tả |
|---|---|---|
| `GET` | `/slitherlink/` | Giao diện game chính |
| `GET` | `/slitherlink/fetch-puzzle/<size_id>` | Lấy puzzle mới từ puzzle-loop.com |
| `POST` | `/slitherlink/solve` | Giải puzzle (nhận JSON `{size, board}`) |
| `POST` | `/slitherlink/scan-puzzle-ai/` | Nhận diện puzzle từ file ảnh upload |


## 🧠 Các thuật toán

### `Puzzle.py` — Core Engine

Lớp `Puzzle` biểu diễn bảng dưới dạng ma trận 2D mở rộng (kích thước `(2n+1) × (2m+1)`), trong đó:
- Vị trí chẵn-chẵn → ô chứa số
- Vị trí lẻ-chẵn / chẵn-lẻ → cạnh ngang/dọc
- Vị trí lẻ-lẻ → góc (dot)

Các luật suy diễn được cài đặt:

| Hàm | Luật |
|---|---|
| `cellfunc_fill_in_xes` | Nếu ô đã đủ links → điền X vào các cạnh còn trống |
| `cellfunc_fill_in_links` | Nếu số X đã đủ để bắt buộc links → điền link |
| `cellfunc_handle_adjacent_threes` | Xử lý hai ô `3` liền kề (ngang/dọc/chéo) |
| `cellfunc_handle_diagonal_chains` | Xử lý chuỗi chéo dạng `3-2-2-...-3` |
| `cellfunc_handle_diagonal_ones` | Hai ô `1` chéo nhau → ép buộc X đối xứng |
| `dotfunc_fill_in_xes_links` | Mỗi điểm phải có đúng 0 hoặc 2 cạnh |
| `dotfunc_avoid_multiple_loops` | Ngăn hình thành nhiều vòng lặp nhỏ |

### `solve_heuristic.py` — Giải Heuristic

Thuật toán tìm kiếm **Best-First** ngẫu nhiên có hướng dẫn:

1. Áp dụng `iter_solve()` để suy diễn tối đa bằng luật.
2. Nếu chưa xong → liệt kê các nước đi khả thi từ các dot đang có 1 cạnh.
3. Chọn ngẫu nhiên tối đa 10 nước đi, nhân bản bảng và thêm vào hàng đợi.
4. Lặp lại cho đến khi tìm ra lời giải hoặc thất bại.

### `solve_branch_and_bound.py` — Giải Nhánh & Cận (Tham khảo để so sánh với Heuristics)

Thuật toán **Branch & Bound** cổ điển:

```
f(n) = g(n) + h(n)
```

- `g(n)` = điểm tích lũy từ các cạnh đã đặt.
- `h(n)` = điểm tiềm năng tối đa từ các cạnh còn trống (heuristic tham lam).

Mỗi cạnh được chấm điểm dựa trên số lân cận (`3` → +15, `0` → +25, `2` → +5, `1` → +2). Nhánh bị cắt sớm (`pruning`) nếu `f(n) < threshold`.

### Trực quan hóa DFS (Frontend)

Animation trong `slitherlink_index.html` mô phỏng quá trình **DFS Backtracking** đi theo vòng lặp:
- 🟡 Vàng = đang khám phá cạnh.
- ❌ X xám = backtrack (sai đường).
- 🔴 Đỏ = cạnh đúng trong lời giải.

---

## 🎮 Luật chơi Slitherlink

1. Nối các điểm kề nhau (ngang hoặc dọc) bằng các đoạn thẳng để tạo thành **một vòng kín duy nhất**.
2. Con số trong ô cho biết đúng **bao nhiêu cạnh** bao quanh ô đó (0, 1, 2 hoặc 3).
3. Ô không có số có thể có bất kỳ số cạnh nào.
4. Vòng lặp **không được giao nhau** và **không được rẽ nhánh**.

### Điều khiển chuột

| Hành động | Kết quả |
|---|---|
| Click 1 lần | Vẽ cạnh (màu xanh) |
| Click 2 lần | Đánh dấu X (không có cạnh) |
| Click 3 lần | Xóa |

---

## 📝 Ghi chú

- Puzzle được scrape live từ `puzzle-loop.com`; cần kết nối Internet khi nhấn **New Puzzle**.
- Tính năng **Scan ảnh** yêu cầu cài Tesseract OCR và hoạt động tốt nhất với ảnh chụp rõ nét, thẳng góc (hiện tại mới scan được size 5*5).
- Ảnh debug của từng ô OCR được lưu vào thư mục `debug_cells/` (tự động tạo).
