import streamlit as st
import pandas as pd
import re

# --- CẤU HÌNH TRANG & THEME MÀU CAM (PREMIUM UI/UX) ---
st.set_page_config(
    page_title="Hệ thống Quản lý & Lead Scoring (BĐS)", 
    page_icon="🍊",
    layout="wide"
)

# Custom CSS cho giao diện tông màu Cam (Orange Premium Theme)
st.markdown("""
<style>
    /* CSS Tông màu Cam chủ đạo */
    :root {
        --orange-primary: #FF6B00;
        --orange-gradient: linear-gradient(135deg, #FF6B00 0%, #FF3D00 100%);
    }
    
    /* Header tiêu đề */
    .title-container {
        display: flex;
        align-items: center;
        gap: 12px;
        background: linear-gradient(90deg, rgba(255,107,0,0.15) 0%, rgba(255,107,0,0.02) 100%);
        padding: 16px 24px;
        border-radius: 12px;
        border-left: 5px solid #FF6B00;
        margin-bottom: 20px;
    }
    .main-title {
        color: #FF6B00 !important;
        font-weight: 800 !important;
        font-size: 2.2rem !important;
        margin: 0 !important;
    }
    .sub-title {
        color: #D1D5DB;
        margin: 0;
        font-size: 0.95rem;
    }

    /* Metric Cards (Thống kê số liệu) */
    .kpi-card {
        background: linear-gradient(135deg, #1E222D 0%, #151821 100%);
        border: 1px solid rgba(255, 107, 0, 0.25);
        border-radius: 12px;
        padding: 16px 20px;
        box-shadow: 0 4px 15px rgba(255, 107, 0, 0.08);
        transition: transform 0.2s ease, border-color 0.2s ease;
    }
    .kpi-card:hover {
        transform: translateY(-3px);
        border-color: #FF6B00;
    }
    .kpi-title {
        font-size: 0.85rem;
        color: #9CA3AF;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .kpi-number {
        font-size: 2.2rem;
        font-weight: 800;
        margin-top: 4px;
    }
    .txt-orange { color: #FF6B00; }
    .txt-green { color: #10B981; }
    .txt-red { color: #EF4444; }
    .txt-blue { color: #3B82F6; }

    /* Button Tông màu cam */
    div.stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #FF6B00 0%, #FF3D00 100%) !important;
        color: white !important;
        border: none !important;
        font-weight: 700 !important;
        border-radius: 8px !important;
        box-shadow: 0 4px 14px rgba(255, 107, 0, 0.35) !important;
        transition: all 0.3s ease !important;
    }
    div.stButton > button[kind="primary"]:hover {
        box-shadow: 0 6px 20px rgba(255, 107, 0, 0.6) !important;
        transform: scale(1.02);
    }
</style>
""", unsafe_allow_html=True)

# Header Giao diện
st.markdown("""
<div class="title-container">
    <div>
        <h1 class="main-title">🍊 Bảng Quản Lý & Lead Scoring (BĐS)</h1>
        <p class="sub-title">Hệ thống quản lý & tự động chấm điểm chất lượng Khách hàng tiềm năng ngành Bất Động Sản</p>
    </div>
</div>
""", unsafe_allow_html=True)

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
        df.columns = [str(col).strip() for col in df.columns]
        
        # Ánh xạ tên cột chuẩn
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
        
        if 'Tên Khách Hàng' not in df.columns and len(df.columns) > 1:
            df.rename(columns={df.columns[1]: 'Tên Khách Hàng'}, inplace=True)
        if 'Mô tả nhu cầu' not in df.columns and len(df.columns) > 3:
            df.rename(columns={df.columns[3]: 'Mô tả nhu cầu'}, inplace=True)
                
        if 'Điểm' not in df.columns:
            df['Điểm'] = 0
        if 'Trạng thái' not in df.columns:
            df['Trạng thái'] = 'Chờ duyệt'
            
        return df, None
    except Exception as e:
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
    st.info("🍊 Tone màu Cam Premium UI & Thuật toán từ khóa tự động.")
    st.divider()
    
    sheet_url = st.text_input(
        "Đường dẫn Google Sheets", 
        value="https://docs.google.com/spreadsheets/d/1Wm29exfdjYcyXmNVVg3i-rOH7xtzzoZOMNx5ctv3ys8/edit?gid=1542775777",
        help="Dán link Google Sheets của bạn vào đây."
    )
    
    reload_btn = st.button("🔄 Tải lại dữ liệu từ Sheet", use_container_width=True)

# Tải dữ liệu vào session_state
if reload_btn or 'df' not in st.session_state or st.session_state.get('loaded_url') != sheet_url:
    df_loaded, err = fetch_data_from_sheet(sheet_url)
    st.session_state.df = df_loaded
    st.session_state.loaded_url = sheet_url
    if err:
        st.sidebar.error(f"⚠️ Lỗi kết nối: {err}")
    else:
        st.sidebar.success("✅ Đã kết nối Google Sheet thành công!")

df = st.session_state.df

# --- PHẦN a: DASHBOARD THỐNG KÊ SỐ LIỆU TRỰC QUAN (KPI METRICS) ---
total_leads = len(df)
vip_leads = len(df[df['Điểm'] >= 50])
spam_leads = len(df[df['Điểm'] < 0])
pending_leads = len(df[df['Trạng thái'] == 'Chờ duyệt'])

kpi_col1, kpi_col2, kpi_col3, kpi_col4 = st.columns(4)

with kpi_col1:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-title">📊 Tổng số Lead</div>
        <div class="kpi-number txt-blue">{total_leads}</div>
    </div>
    """, unsafe_allow_html=True)

with kpi_col2:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-title">🌟 Khách VIP (≥50đ)</div>
        <div class="kpi-number txt-orange">{vip_leads}</div>
    </div>
    """, unsafe_allow_html=True)

with kpi_col3:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-title">⚠️ Khách Rác (<0đ)</div>
        <div class="kpi-number txt-red">{spam_leads}</div>
    </div>
    """, unsafe_allow_html=True)

with kpi_col4:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-title">⏳ Cần xử lý</div>
        <div class="kpi-number txt-green">{pending_leads}</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# Biểu đồ thống kê trực quan
with st.expander("📊 Xem Biểu đồ phân bổ phân loại Khách hàng", expanded=True):
    chart_col1, chart_col2 = st.columns(2)
    with chart_col1:
        st.caption("📈 Biểu đồ Phân bổ Điểm số Lead")
        score_counts = pd.DataFrame({
            "Phân loại": ["Khách VIP (≥50đ)", "Tiềm năng trung bình (0đ)", "Khách Rác (<0đ)"],
            "Số lượng": [
                len(df[df['Điểm'] >= 50]),
                len(df[df['Điểm'] == 0]),
                len(df[df['Điểm'] < 0])
            ]
        }).set_index("Phân loại")
        st.bar_chart(score_counts, color="#FF6B00")
        
    with chart_col2:
        st.caption("📋 Biểu đồ Trạng thái Xử lý")
        status_counts = df['Trạng thái'].value_counts().to_frame()
        st.bar_chart(status_counts, color="#FF8C00")

st.markdown("<br>", unsafe_allow_html=True)

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

# --- QUẢN LÝ DANH SÁCH LEAD ---
col1, col2 = st.columns([3, 1])

with col1:
    st.subheader("📋 Danh sách Khách hàng Chi tiết")
with col2:
    if st.button("🤖 Chấm điểm tự động", use_container_width=True, type="primary"):
        with st.spinner("Đang tự động quét và chấm điểm..."):
            for idx, row in df.iterrows():
                col_name = 'Mô tả nhu cầu' if 'Mô tả nhu cầu' in row else ('nhu_cau_mo_ta' if 'nhu_cau_mo_ta' in row else None)
                if col_name and pd.notna(row[col_name]):
                    score = score_lead(str(row[col_name]))
                    df.at[idx, 'Điểm'] = score
            
            st.session_state.df = df
            st.success("Hoàn tất chấm điểm!")
            st.rerun()

# Bảng Data Editor chỉnh sửa trực tiếp
edited_df = st.data_editor(
    st.session_state.df,
    num_rows="dynamic",
    use_container_width=True,
    height=380,
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
    st.success("Đã lưu các thay đổi vào phiên làm việc!")

st.markdown("---")
with st.expander("📖 Xem tiêu chí chấm điểm (Knowledge Base)"):
    st.text(knowledge if knowledge else "Không tìm thấy file tieu_chi_cham_diem.txt")
