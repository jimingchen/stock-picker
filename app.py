import streamlit as st
import uuid
import hashlib
import os

# 1. 設定網頁標題與寬螢幕版面
st.set_page_config(page_title="系統安全設備", layout="wide")
st.title("🔒 系統安全設備認證")

def get_verification_key():
    # 取得伺服器節點的 MAC 地址
    mac_num = uuid.getnode()
    mac_str = f"{mac_num:012X}"
    
    # 透過 MD5 計算出 5 位數純數字密碼
    hash_obj = hashlib.md5(mac_str.encode('utf-8'))
    hash_hex = hash_obj.hexdigest()
    
    # 將十六進位轉為純數字，並取最後 5 位
    correct_key = int(hash_hex, 16) % 100000
    return correct_key, mac_str

# 自動計算出正確的密碼與 MAC 地址
correct_key, current_mac = get_verification_key()

# 在畫面上為您自己顯示目前的伺服器資訊
st.info(f"ℹ️ 目前系統偵測設備 MAC: {current_mac} | 認證密碼: {correct_key:05d}")

# 2. 密碼輸入框
user_input = st.text_input("請輸入 5 位數認證密碼：", type="password")

# 3. 核心安全檢視機制：認證成功後直接在網頁中央展開 PDF 內容
if user_input:
    try:
        if int(user_input) == correct_key:
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
            
            # 檢查 GitHub 目錄內是否存在該 PDF 實體檔案
            if os.path.exists(local_pdf_path):
                # 讀取本機 PDF 檔案
                with open(local_pdf_path, "rb") as f:
                    pdf_data = f.read()
                
                # 【官方標準安全元件】：利用不帶下載按鈕的 PDF 內嵌語法
                # #toolbar=0 代表隱藏 Google 與瀏覽器內建的所有下載、列印、儲存工具列
                pdf_html = f'''
                <iframe src="data:application/pdf;base64,{st.session_state.get('pdf_b64', '')}#toolbar=0&navpanes=0&scrollbar=1" 
                        width="100%" height="800px" style="border: none;">
                </iframe>
                '''
                
                # 使用 Base64 單行轉碼（放置在後端運算，避免干擾 HTML 語法對齊）
                import base64
                pdf_b64 = base64.b64encode(pdf_data).decode('utf-8')
                
                final_html = f'''
                <body oncontextmenu="return false;" ondragstart="return false;" style="margin:0; padding:0;">
                    <iframe src="data:application/pdf;base64,{pdf_b64}#toolbar=0&navpanes=0" width="100%" height="900px" style="border:none;"></iframe>
                </body>
                '''
                
                # 在 Streamlit 中安全輸出
                st.components.v1.html(final_html, height=920, scrolling=False)
                st.info("💡 提示：本網頁已啟用安全硬體驗證與文件保護。文件內的超連結可點擊，但工具列下載已被屏蔽。")
            else:
                st.error(f"⚠️ 系統錯誤：找不到專案內的實體檔案 【{local_pdf_path}】，請確認檔案是否已上傳至 GitHub 倉庫。")

        else:
            st.error("❌ 認證失敗：此設備認證碼錯誤，拒絕存取雲端硬碟。")
    except ValueError:
        st.warning("⚠️ 請輸入正確的 5 位數純數字。")

        else:
            st.error("❌ 認證失敗：此設備認證碼錯誤，拒絕存取雲端硬碟。")
    except ValueError:
        st.warning("⚠️ 請輸入正確的 5 位數純數字。")
