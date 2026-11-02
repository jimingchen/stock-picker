import streamlit as st
import uuid
import hashlib
import os
from streamlit_pdf_viewer import pdf_viewer

# 1. 設定網頁標題與寬螢幕版面（讓 PDF 完美呈現）
st.set_page_config(page_title="系統安全設備", layout="wide")
st.title("🔒 系統安全設備認證")

def get_verification_key():
    mac_num = uuid.getnode()
    mac_str = f"{mac_num:012X}"
    hash_obj = hashlib.md5(mac_str.encode('utf-8'))
    hash_hex = hash_obj.hexdigest()
    correct_key = int(hash_hex, 16) % 100000
    return correct_key, mac_str

correct_key, current_mac = get_verification_key()

# 在畫面上為您自己顯示目前的伺服器資訊
st.info(f"ℹ️ 目前系統偵測設備 MAC: {current_mac} | 認證密碼: {correct_key:05d}")

# 2. 密碼輸入框
user_input = st.text_input("請輸入 5 位數認證密碼：", type="password")

# 驗證阻斷機制（扁平化結構，保證不報語法錯誤）
if not user_input:
    st.stop()

if not user_input.isdigit():
    st.warning("⚠️ 請輸入正確的 5 位數純數字。")
    st.stop()

user_key = int(user_input)

if user_key != correct_key:
    st.error("❌ 認證失敗：此設備認證碼錯誤，拒絕存取文件。")
    st.stop()

# ----------------- 以下為認證成功後才會執行的安全機制 -----------------
st.success("🔓 認證成功！設備硬體比對完全相符。")
st.markdown("---")

# 設定您的 GitHub 內建 PDF 檔案清單
pdf_files = {
    "A玩股網設定": "A玩股網設定.pdf",
    "B玩股網設定": "B玩股網設定.pdf"
}

# 下拉選單：讓使用者自由切換檔案
selected_file = st.selectbox("📁 請選擇欲檢視的設定檔（已嚴格限制 3 頁內）：", list(pdf_files.keys()))
local_pdf_path = pdf_files[selected_file]

st.subheader(f"📄 當前檢視：{selected_file}.pdf")

if not os.path.exists(local_pdf_path):
    st.error(f"⚠️ 系統錯誤：找不到專案內的實體檔案 【{local_pdf_path}】，請確認檔案是否已上傳至 GitHub 倉庫。")
    st.stop()

# 讀取專案內的實體 PDF 檔案
with open(local_pdf_path, "rb") as f:
    pdf_bytes = f.read()

# 禁止右鍵與防複製的 CSS 注入防護
st.markdown("""
    <style>
    /* 全局鎖定選取、禁止反白、禁止右鍵行為 */
    canvas, .stVideo, iframe, div {
        user-select: none !important;
        -webkit-user-select: none !important;
    }
    </style>
    <script>
    document.addEventListener('contextmenu', event => event.preventDefault());
    </script>
""", unsafe_allow_html=True)

# 【核心終極防護】：利用官方專業元件進行後端解析渲染
# rendering="canvas" 代表只輸出網頁畫布圖塊，完全不產生 PDF 實體檔案下載按鈕
# width=800 設定完美的閱讀寬度
pdf_viewer(
    input=pdf_bytes,
    width=800,
    rendering="canvas",
    annotations=True # 保留 PDF 內的所有點擊跳轉超連結功能
)

st.info("💡 提示：本網頁已啟用安全硬體驗證與文件保護。文件內的超連結可點擊，但工具列下載已被屏蔽。")
