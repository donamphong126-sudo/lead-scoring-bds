import streamlit as st
import pandas as pd
import re

# Cấu hình trang Streamlit
st.set_page_config(page_title="Hệ thống Quản lý & Chấm điểm Lead (BĐS)", layout="wide")
st.title("🏠 Bảng Quản Lý & AI Lead Scoring")
st.markdown("Hệ thống quản lý khách hàng tiềm năng ngành Bất Động Sản với sự hỗ trợ của AI để tự động chấm điểm.")

# --- TỰ ĐỘNG CHUYỂN LINK GOOGLE SHEETS SANG CSV ---
def get_csv_url(url):
    if not url or not isinstance(url, str):
        return ""
    if "/export?format=csv" in url:
        return url
    match = re.search(r'/spreadsheets/d/([a-zA-Z0-9-_]+)', url)
    if match:
        sheet_id = match.group(1)
        gid_match = re.search(r'gid=([0-9]+)', url)
        gid = gid_match.group(1) if gid_match else "0"
        return f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid={gid}"
    return url

# --- LOAD KNOWLEDGE ---
@st.cache_data
def load_knowledge():
    try:
        with open("tieu_chi_cham_diem.txt", "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        return ""

knowledge = load_knowledge()

# --- LOAD DATA TỪ GOOGLE SHEETS ---
def fetch_data_from_sheet(raw_url):
    csv_url = get_csv_url(raw_url)
    try:
        df = pd.read_csv(csv_url)
        # Làm sạch tên cột
        df.columns = [str(col).strip() for col in df.columns]
        
        # Tự động ánh xạ (rename) tiêu đề cột
        mapping = {
            'ten_khach': 'Tên Khách Hàng',
            'ten_khach_hang': 'Tên Khách Hàng',
            'sdt': 'Số điện thoại',
            'so_dien_thoai': 'Số điện thoại',
            'nhu_cau_mo_ta': 'Mô tả nhu cầu',
            'mo_ta': 'Mô tả nhu cầu',
            'mo_ta_nhu_cau': 'Mô tả nhu cầu'
        }
        df = df.rename(columns=mapping)
        
        # Đảm bảo các cột bắt buộc phải có
        if 'Tên Khách Hàng' not in df.columns:
            # Nếu không tìm thấy cột Tên Khách Hàng, lấy cột 0 hoặc cột 1
            if len(df.columns) > 1:
                df.rename(columns={df.columns[1]: 'Tên Khách Hàng'}, inplace=True)
        if 'Mô tả nhu cầu' not in df.columns:
            if len(df.columns) > 3:
                df.rename(columns={df.columns[3]: 'Mô tả nhu cầu'}, inplace=True)
                
        if 'Điểm' not in df.columns:
            df['Điểm'] = 0
        if 'Trạng thái' not in df.columns:
            df['Trạng thái'] = 'Chờ duyệt'
            
        return df, None
    except Exception as e:
        # Nếu lỗi thì dùng dữ liệu mẫu
        dummy_df = pd.DataFrame({
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
        return dummy_df, str(e)

# --- CẤU HÌNH SIDEBAR ---
with st.sidebar:
    st.header("⚙️ Cấu hình Hệ thống")
    st.info("Thuật toán chấm điểm tự động từ khóa (Không cần API Key).")
    st.divider()
    
    sheet_url = st.text_input(
        "Đường dẫn Google Sheets", 
        value="https://docs.google.com/spreadsheets/d/1Wm29exfdjYcyXmNVVg3i-rOH7xtzzoZOMNx5ctv3ys8/edit?gid=1542775777",
        help="Dán link Google Sheets của bạn vào đây."
    )
    
    reload_btn = st.button("🔄 Tải lại dữ liệu từ Sheet", use_container_width=True)

# Kiểm tra nếu cần reload dữ liệu
if reload_btn or 'df' not in st.session_state or st.session_state.get('loaded_url') != sheet_url:
    df_loaded, err = fetch_data_from_sheet(sheet_url)
    st.session_state.df = df_loaded
    st.session_state.loaded_url = sheet_url
    if err:
        st.sidebar.error(f"⚠️ Lỗi đọc Sheet: {err}")
        st.sidebar.warning("Đang dùng dữ liệu mẫu!")
    else:
        st.sidebar.success("✅ Đã kết nối dữ liệu Google Sheet thành công!")

df = st.session_state.df

# --- LOGIC CHẤM ĐIỂM TỪ KHÓA ---
def score_lead(description):
    if not isinstance(description, str):
        return 0
        
    desc_lower = description.lower()
    score = 0
    
    vip_keywords = [
        "20 tỷ", "tài chính mạnh", "không thành vấn đề", 
        "biệt thự đơn lập", "penthouse", "shophouse", 
        "quỹ đất", "sàn văn phòng", "quận 1", "ven sông", 
        "vinhomes", "phú mỹ hưng", "chủ doanh nghiệp", 
        "nhà đầu tư", "mua sỉ", "mua số lượng", 
        "pháp lý chuẩn", "sổ hồng riêng", "gặp trực tiếp"
    ]
    
    spam_keywords = [
        "1-2 tỷ", "nhầm số", "không có nhu cầu", 
        "dữ liệu cũ", "nhầm ngành", "hỏi giá cho vui", 
        "chưa có ý định", "bảo hiểm", "vay vốn", 
        "thuê bao", "không bắt máy", "không phản hồi"
    ]
    
    for kw in vip_keywords:
        if kw in desc_lower:
            score += 50
            break
            
    for kw in spam_keywords:
        if kw in desc_lower:
            score -= 50
            break
            
    return score

# --- GIAO DIỆN CHÍNH ---
col1, col2 = st.columns([3, 1])

with col1:
    st.subheader("📋 Danh sách Khách hàng")
with col2:
    if st.button("🤖 Chấm điểm tự động", use_container_width=True, type="primary"):
        with st.spinner("Đang tự động quét và chấm điểm..."):
            for idx, row in df.iterrows():
                # Tìm cột mô tả nhu cầu
                col_name = 'Mô tả nhu cầu' if 'Mô tả nhu cầu' in row else ('nhu_cau_mo_ta' if 'nhu_cau_mo_ta' in row else None)
                if col_name and pd.notna(row[col_name]):
                    score = score_lead(str(row[col_name]))
                    df.at[idx, 'Điểm'] = score
            
            st.session_state.df = df
            st.success("Hoàn tất chấm điểm!")
            st.rerun()

# Hiển thị bảng Data Editor
edited_df = st.data_editor(
    st.session_state.df,
    num_rows="dynamic",
    use_container_width=True,
    height=400,
    column_config={
        "Trạng thái": st.column_config.SelectboxColumn(
            "Trạng thái",
            options=["Chờ duyệt", "Đã duyệt", "Loại"],
            required=True,
        ),
        "Điểm": st.column_config.NumberColumn("Điểm"),
        "Mô tả nhu cầu": st.column_config.TextColumn("Mô tả nhu cầu", width="large")
    }
)

if st.button("💾 Lưu thay đổi phiên làm việc"):
    st.session_state.df = edited_df
    st.success("Đã lưu thay đổi vào phiên!")

st.markdown("---")
with st.expander("📖 Xem tiêu chí chấm điểm (Knowledge Base)"):
    st.text(knowledge if knowledge else "Không tìm thấy file tieu_chi_cham_diem.txt")
