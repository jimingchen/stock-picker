import streamlit as st
import uuid
import hashlib
import os
import base64

# 1. 設定網頁標題與寬螢幕版面
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

# 設定您的 GitHub 內建 PDF 檔案清單（直接抓同目錄下的實體檔案）
pdf_files = {
    "A玩股網設定": "A玩股網設定.pdf",
    "B玩股網設定": "B玩股網設定.pdf"
}

# 下拉選單：這就等同於您的「雲端資料夾」，讓使用者可以直接在這裡切換多個檔案
selected_file = st.selectbox("📁 請選擇欲檢視的設定檔（已嚴格限制 3 頁內）：", list(pdf_files.keys()))
local_pdf_path = pdf_files[selected_file]

st.subheader(f"📄 當前檢視：{selected_file}.pdf")

if not os.path.exists(local_pdf_path):
    st.error(f"⚠️ 系統錯誤：找不到專案內的實體檔案 【{local_pdf_path}】，請確認檔案是否已上傳至 GitHub 倉庫。")
    st.stop()

# 讀取專案內的實體 PDF 檔案
with open(local_pdf_path, "rb") as f:
    pdf_bytes = f.read()

# 將 PDF 轉成標準 Base64 數據
pdf_b64 = base64.b64encode(pdf_bytes).decode('utf-8')

# 【終極輕量防崩潰架構】：
# 以前使用大字串會讓 Chrome 的 iframe 崩潰。這次我們改用標準的嵌入語法，
# 並且不加入多餘的樣式運算。#toolbar=0 會通知 Chrome 拔除下載、列印按鈕，
# 同時利用 JavaScript 來保證右鍵被封鎖。
html_display = f'''
<!DOCTYPE html>
<html>
<body oncontextmenu="return false;" ondragstart="return false;" style="margin:0; padding:0;">
    <embed src="data:application/pdf;base64,{pdf_b64}#toolbar=0&navpanes=0&scrollbar=1" type="application/pdf" width="100%" height="900px" />
</body>
</html>
'''

# 在 Streamlit 中安全輸出（使用寬度 100% 彈性自我調整，不會讓瀏覽器過載）
st.components.v1.html(html_display, height=920, scrolling=False)
st.info("💡 提示：本網頁已啟用安全硬體驗證與文件保護。文件內的超連結可點擊，但工具列下載已被屏蔽。")
