import streamlit as st
import pandas as pd
import google.generativeai as genai
import os

# Cấu hình trang Streamlit
st.set_page_config(page_title="Hệ thống Quản lý & Chấm điểm Lead (BĐS)", layout="wide")
st.title("🏠 Bảng Quản Lý & AI Lead Scoring")
st.markdown("Hệ thống quản lý khách hàng tiềm năng ngành Bất Động Sản với sự hỗ trợ của AI để tự động chấm điểm.")

# --- CẤU HÌNH API KEY ---
with st.sidebar:
    st.header("⚙️ Cấu hình Hệ thống")
    api_key = st.text_input("Nhập Gemini API Key", type="password")
    if api_key:
        genai.configure(api_key=api_key)
        st.success("API Key đã được cấu hình!")
    else:
        st.warning("Vui lòng nhập API Key để sử dụng tính năng AI Scoring.")
        
    st.divider()
    
    # URL Google Sheet
    sheet_url = st.text_input(
        "Đường dẫn Google Sheets (CSV Export)", 
        value="https://docs.google.com/spreadsheets/d/1Wm29exfdjYcyXmNVVg3i-rOH7xtzzoZOMNx5ctv3ys8/export?format=csv&gid=1542775777",
        help="Lưu ý: Google Sheet cần được Share dạng 'Anyone with the link can view'."
    )

# --- LOAD KNOWLEDGE ---
@st.cache_data
def load_knowledge():
    try:
        # Đọc file tiêu chí chấm điểm
        with open("tieu_chi_cham_diem.txt", "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        st.error(f"Lỗi đọc Knowledge: {e}")
        return ""

knowledge = load_knowledge()

# --- LOAD DATA ---
@st.cache_data(show_spinner=False)
def load_data(url):
    try:
        df = pd.read_csv(url)
        # Đảm bảo các cột cần thiết tồn tại
        if 'Điểm' not in df.columns:
            df['Điểm'] = 0
        if 'Trạng thái' not in df.columns:
            df['Trạng thái'] = 'Chờ duyệt'
        return df
    except Exception as e:
        # Nếu sheet bị khóa hoặc lỗi (401), dùng data mẫu
        st.error(f"Không thể tải dữ liệu từ Google Sheets (có thể file đang bị Private). Đang sử dụng dữ liệu mẫu.")
        return pd.DataFrame({
            "Tên Khách Hàng": ["Nguyễn Văn A", "Trần Thị B", "Lê Văn C", "Phạm Thị D"],
            "Số điện thoại": ["0987654321", "0912345678", "0901112223", "0933444555"],
            "Mô tả nhu cầu": [
                "Mình cần tìm 1 căn biệt thự đơn lập view sông, tài chính không thành vấn đề miễn là chỗ đẹp.", 
                "Nhầm số rồi em ơi.",
                "Đang tìm nhà 1-2 tỷ ở trung tâm Quận 1 có chỗ đậu ô tô.",
                "Tôi muốn tìm chung cư khu vực Cầu Giấy khoảng 3-4 tỷ."
            ],
            "Điểm": [0, 0, 0, 0],
            "Trạng thái": ["Chờ duyệt", "Chờ duyệt", "Chờ duyệt", "Chờ duyệt"]
        })

if 'df' not in st.session_state:
    st.session_state.df = load_data(sheet_url)

df = st.session_state.df

# --- AI SCORING LOGIC ---
def score_lead(description):
    if not api_key:
        return 0
    
    prompt = f"""
Bạn là một AI đánh giá khách hàng Bất động sản (Lead Scoring Agent).
Dựa vào Bộ Knowledge sau đây để tính điểm:

{knowledge}

Hãy chấm điểm cho khách hàng có mô tả nhu cầu sau:
"{description}"

Yêu cầu trả kết quả: CHỈ IN RA DUY NHẤT 1 CON SỐ (ví dụ: 50, -50, 0). KHÔNG ĐƯỢC GIẢI THÍCH THÊM.
    """
    
    try:
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(prompt)
        score_text = response.text.strip()
        # Ép kiểu an toàn
        return int(score_text)
    except Exception as e:
        print(f"Error AI: {e}")
        return 0

# --- GIAO DIỆN CHÍNH ---
col1, col2 = st.columns([3, 1])

with col1:
    st.subheader("📋 Danh sách Khách hàng")
with col2:
    if st.button("🤖 AI Scoring (Agent)", use_container_width=True, type="primary"):
        if not api_key:
            st.error("Vui lòng nhập API Key!")
        else:
            with st.spinner("AI đang quét và chấm điểm..."):
                for idx, row in df.iterrows():
                    # Bỏ qua nếu mô tả trống
                    if pd.notna(row.get('Mô tả nhu cầu')):
                        ai_score = score_lead(row['Mô tả nhu cầu'])
                        df.at[idx, 'Điểm'] = ai_score
                
                # Cập nhật state
                st.session_state.df = df
                st.success("Hoàn tất chấm điểm bằng AI!")
                st.rerun()

# Data Editor cho phép chỉnh sửa
edited_df = st.data_editor(
    st.session_state.df,
    num_rows="dynamic",
    use_container_width=True,
    height=400,
    column_config={
        "Trạng thái": st.column_config.SelectboxColumn(
            "Trạng thái",
            help="Duyệt trạng thái khách hàng",
            options=["Chờ duyệt", "Đã duyệt", "Loại"],
            required=True,
        ),
        "Điểm": st.column_config.NumberColumn(
            "Điểm",
            help="Điểm đánh giá tiềm năng"
        ),
        "Mô tả nhu cầu": st.column_config.TextColumn(
            "Mô tả nhu cầu",
            width="large"
        )
    }
)

# Nút lưu thay đổi
if st.button("💾 Lưu thay đổi", use_container_width=False):
    st.session_state.df = edited_df
    st.success("Đã lưu các thay đổi vào phiên làm việc! (Nếu cần lưu về Google Sheets, bạn sẽ cần tích hợp Google Sheets API)")

st.markdown("---")
with st.expander("📖 Xem Knowledge Base (Tiêu chí chấm điểm)"):
    st.text(knowledge)
