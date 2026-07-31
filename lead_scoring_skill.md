---
name: Lead Scoring
description: Hướng dẫn lấy dữ liệu từ Google Sheets và thực hiện chấm điểm (Lead Scoring) cho ngành Bất động sản
---

# Kỹ năng Chấm điểm Khách hàng (Lead Scoring Skill)

## 1. Mục đích
Kỹ năng này hướng dẫn AI (Agent) cách kết nối, lấy dữ liệu từ Google Sheets, đọc các yêu cầu của khách hàng (leads) và chấm điểm (Lead Scoring) tự động dựa trên các tiêu chí Knowledge (tri thức) đã được định nghĩa, đặc thù cho ngành Bất động sản.

## 2. Quy trình thực hiện (Workflow)

### Bước 1: Lấy dữ liệu (Data Extraction)
- Truy cập Google Sheets chứa danh sách khách hàng tiềm năng.
- Phương pháp: Sử dụng Export link định dạng CSV (nếu file public) hoặc Google Sheets API.
- Dữ liệu cần thiết phải có các cột: `Tên Khách Hàng`, `Mô tả nhu cầu`, `Điểm`, `Trạng thái`.

### Bước 2: Nạp Knowledge (Knowledge Ingestion)
- Đọc nội dung file `tieu_chi_cham_diem.txt` để lấy tiêu chí.
- Các quy tắc cơ bản trong Knowledge: 
  - Khách hàng VIP/Siêu tiềm năng (ví dụ: mua biệt thự, tài chính lớn, vị trí đắc địa) được **cộng 50 điểm**.
  - Khách hàng rác/không tiềm năng (ví dụ: nhầm số, không có nhu cầu, giá phi thực tế) bị **trừ 50 điểm**.
  - Các trường hợp khác có thể giữ nguyên điểm hoặc cộng/trừ ít.

### Bước 3: Thực thi AI Scoring (Agent Processing)
- Duyệt qua từng bản ghi dữ liệu khách hàng.
- AI (LLM Model như Gemini) đọc phần `Mô tả nhu cầu`.
- LLM đối chiếu mô tả với Knowledge và suy luận để đưa ra quyết định điểm số chính xác nhất cho lead đó.
- Trích xuất điểm số dưới dạng số nguyên.

### Bước 4: Hiển thị và Cập nhật (Human-in-the-loop)
- Sử dụng Streamlit để tạo giao diện hiển thị bảng dữ liệu (Data Editor).
- Cập nhật số điểm đã chấm vào bảng.
- Cho phép người dùng (Sale/Admin) xem, chỉnh sửa điểm nếu AI chấm chưa chuẩn, và phê duyệt `Trạng thái` của từng lead (ví dụ: "Đã duyệt", "Chờ duyệt", "Loại").

## 3. Công nghệ sử dụng
- **Python**: Ngôn ngữ xử lý logic.
- **Pandas**: Đọc và thao tác với dữ liệu dạng bảng.
- **Streamlit**: Xây dựng UI nhanh chóng, sử dụng hàm `st.data_editor`.
- **Google Generative AI**: Đóng vai trò là "Bộ não" Agent để đọc hiểu ngôn ngữ tự nhiên và chấm điểm.
