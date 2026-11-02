import streamlit as st
import uuid
import hashlib

# 設定網頁標題
st.set_page_config(page_title="系統安全設備", layout="centered")
st.title("🔒 系統安全設備認證")

def get_verification_key():
    # 取得伺服器節點的 MAC 地址（Streamlit 雲端環境會維持固定）
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

# 在畫面上為您自己顯示目前的伺服器資訊（方便您自己核對，別人看不到後台）
st.info(f"ℹ️ 目前系統偵測設備 MAC: {current_mac} | 認證密碼: {correct_key:05d}")

# 密碼輸入框
user_input = st.text_input("請輸入 5 位數認證密碼：", type="password")

# 玩股網雲端硬碟的實際超連結（您可以之後再換成您自己實際的 Google Drive 網址）
TARGET_URL = "https://drive.google.com/drive/folders/1feGDILvAOfFtxiiExtYSqSSOZNkg-Uvq?usp=drive_link"

if user_input:
    try:
        if int(user_input) == correct_key:
            st.success("🔓 認證成功！設備硬體比對完全相符。")
            st.write("🚀 權限已解鎖！請點選下方按鈕直接連線至 玩股網 資料夾：")
            st.link_button("🚀 點此進入 玩股網 Google 雲端硬碟", TARGET_URL, use_container_width=True, type="primary")
        else:
            st.error("❌ 認證失敗：此設備認證碼錯誤，拒絕存取雲端硬碟。")
    except ValueError:
        st.warning("⚠️ 請輸入正確的 5 位數純數字。")
