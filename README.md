# CBM HERITAGE - Knowledge Distillation Project 

Hệ thống đánh giá sự tối ưu của mô hình học máy trên thiết bị biên thông qua kỹ thuật **Knowledge Distillation (KD)**. Dự án tích hợp lớp **Bottleneck Concepts (CBM)** và **Mô hình Ngôn ngữ Lớn (LLM)** nhằm mở khóa tính năng minh bạch hóa, giải thích quyết định của hệ thống Trí tuệ Nhân tạo (Explainable AI).

Dự án được ứng dụng vào bài toán nhận dạng **12 lớp Di sản Văn hóa Phi vật thể Nam Bộ Việt Nam** (Chợ nổi Cái Răng, Đờn ca tài tử, Nghề dệt chiếu, Đua bò Bảy Núi,...), góp phần bảo tồn và gìn giữ bản sắc văn hóa dân tộc.

---
## Tính năng Nổi bật

*   **50+ Kiến trúc Đối chứng:** Môi trường thực nghiệm toàn diện so sánh các mô hình từ dạng Baseline Hộp đen, qua chưng cất tri thức (KD 1 Thầy, 5 Thầy Ensemble/Expert) đến CBM và MECK.
*   **Minh bạch hóa Quyết định (XAI):** Mô hình không chỉ đưa ra nhãn phân loại mà còn giải thích lý do dựa trên **62 đặc trưng (concepts)** thị giác đã được kiểm duyệt bởi chuyên gia.
*   **AI Dashboard Tương tác Trực quan:** Giao diện Dark Theme/Glassmorphism hiện đại, hỗ trợ quan sát song song theo từng giai đoạn học hoặc theo dõi hành trình tiến hóa của 1 Backbone duy nhất.
*   **Hiệu năng Tối ưu:** Cấu trúc MECK (CBM + LLM) đề xuất đạt độ chính xác lên đến **~96.2%** trong khi vẫn đảm bảo độ trễ thấp trên thiết bị biên.

---

## ⚙️ Hướng dẫn Cài đặt & Khởi chạy

### 1. Yêu cầu Hệ thống
*   Python 3.8 hoặc cao hơn.
*   Nên sử dụng môi trường ảo (Virtual Environment) để cài đặt các thư viện.

### 2. Cài đặt Mã nguồn
Clone kho lưu trữ này về máy và cài đặt các thư viện cần thiết:
```bash
git clone https://github.com/Minhtc12/DEMO_Luan_Van_MECK.git
pip install -r requirements.txt
```
3. Tải Trọng số Mô hình (Checkpoints)
Do giới hạn dung lượng của GitHub, toàn bộ các file trọng số .pth (tổng cộng 50+ mô hình) được lưu trữ riêng trên Google Drive. Bạn cần tải về để hệ thống có thể chạy được.

Truy cập vào link Google Drive sau: 👉 [TẢI CHECKPOINTS TẠI ĐÂY](https://drive.google.com/drive/folders/19xsUOQdKAg8zMNVnnwOePLzJScOj-ZK0?usp=drive_link) 👈

Tải về máy và giải nén.

Đặt tất cả các file vừa tải vào trong thư mục checkpoints/ ở thư mục gốc của dự án.
(Nếu chưa có thư mục checkpoints/, hãy tạo mới nó).
Cấu trúc thư mục sau khi tải sẽ trông như thế này:
```bash
cbm-heritage-project/
├── checkpoints/                 <-- Thả toàn bộ file .pth vào đây
│   ├── teacher_resnet50_best.pth
│   ├── baseline_efficientnet_b0_best.pth
│   └── ...
├── static/
├── models/
├── main.py
└── README.md
```
4. Khởi chạy Ứng dụng
Khởi động máy chủ FastAPI bằng uvicorn:
```bash
uvicorn main:app --reload
```
Mở trình duyệt web và truy cập vào địa chỉ: http://127.0.0.1:8000 để sử dụng hệ thống.
