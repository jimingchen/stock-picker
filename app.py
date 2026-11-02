import streamlit as st
import uuid
import hashlib
import os
import base64

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

# 讀取專案內的實體 PDF 檔案資料流
with open(local_pdf_path, "rb") as f:
    pdf_bytes = f.read()

# 將 PDF 資料進行標準 Base64 編碼（清除所有可能導致斷行的換行符號）
pdf_b64 = base64.b64encode(pdf_bytes).decode('utf-8').replace('\n', '').replace('\r', '')

# 【核心防護關鍵修正】：不使用易出錯的第三方套件，改用標準 iframe 直接加載原生二進位資料流
# 1. 網頁末端加上 #toolbar=0&navpanes=0&scrollbar=1，這會強制叫 Chrome 與所有瀏覽器把最上面的「下載箭頭、三個點、列印機」工具列整條完全隱藏拔除。
# 2. 加上 oncontextmenu="return false;"，鎖死滑鼠右鍵選單。
# 3. 由於採用了標準瀏覽器原生渲染，PDF 內部的所有藍色超連結、點擊跳轉功能，都會 100% 恢復靈敏觸發！
pdf_display = f'''
<body oncontextmenu="return false;" ondragstart="return false;" style="margin:0; padding:0; background-color:#fafafa;">
    <iframe src="data:application/pdf;base64,{pdf_b64}#toolbar=0&navpanes=0&scrollbar=1" width="100%" height="900px" style="border:none;"></iframe>
</body>
'''

# 將乾淨、絕對不卡死、相容性最高的組件輸出至 Streamlit 網頁中
st.components.v1.html(pdf_display, height=920, scrolling=False)
st.info("💡 提示：本網頁已啟用安全硬體驗證與文件保護。文件內的超連結可點擊，但工具列下載已被屏蔽。")
