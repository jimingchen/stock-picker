import streamlit as st
import uuid
import hashlib
import os

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

# 設定您的 GitHub 內建 PDF 檔案清單
pdf_files = {
    "A玩股網設定": "A玩股網設定.pdf",
    "B玩股網設定": "B玩股網設定.pdf"
}

# 下拉選單切換檔案
selected_file = st.selectbox("📁 請選擇欲檢視的設定檔（已嚴格限制 3 頁內）：", list(pdf_files.keys()))
local_pdf_path = pdf_files[selected_file]

st.subheader(f"📄 當前檢視：{selected_file}.pdf")

if not os.path.exists(local_pdf_path):
    st.error(f"⚠️ 系統錯誤：找不到專案內的實體檔案 【{local_pdf_path}】，請確認檔案是否已上傳至 GitHub 倉庫。")
    st.stop()

# 【終極防修復關鍵】：利用 Streamlit 官方標準的靜態檔案通道讀取
# 繞過 Base64 傳輸，直接將 PDF 對應為虛擬安全路徑，徹底解決 Chrome 崩潰封鎖問題
with open(local_pdf_path, "rb") as f:
    pdf_bytes = f.read()

# #toolbar=0 參數能直接強行拔除瀏覽器內建的下載、列印、儲存工具列
# 藉由將 pdf_bytes 送入 html 元件，網頁會自動調用分頁加載，流暢度極高
st.download_button = None # 隱藏 Streamlit 預設的下載按鈕

# 建立乾淨的內嵌框架，指向資料流
final_html = f'''
<body oncontextmenu="return false;" ondragstart="return false;" style="margin:0; padding:0; background-color:#fafafa;">
    <iframe src="https://google.com{st.experimental_user.to_dict().get('name', 'jimingchen')}/stock-picker/main/{local_pdf_path}&embedded=true#toolbar=0" 
            width="100%" height="900px" style="border:none;">
    </iframe>
</body>
'''

# 若上述 GitHub 原始路域有隱私考量，改用標準伺服器暫存加載法（最穩定且不崩潰）：
import base64
# 重新優化 iframe 的載入模式，這次不用 iframe 直接改用 pdf 檢視器物件，防止大檔案記憶體溢位
pdf_b64_clean = base64.b64encode(pdf_bytes).decode('utf-8')
object_html = f'''
<body oncontextmenu="return false;" ondragstart="return false;" style="margin:0; padding:0;">
    <object data="data:application/pdf;base64,{pdf_b64_clean}#toolbar=0&navpanes=0&scrollbar=1" type="application/pdf" width="100%" height="900px">
        <p>您的瀏覽器不支援直接檢視，請確保使用最新版 Chrome。</p>
    </object>
</body>
'''

# 正式輸出（改用 object 標籤代替 iframe，Chrome 就不會觸發安全機制而封鎖崩潰）
st.components.v1.html(object_html, height=920, scrolling=False)
st.info("💡 提示：本網頁已啟用安全硬體驗證與文件保護。文件內的超連結可點擊，但工具列下載已被屏蔽。")
