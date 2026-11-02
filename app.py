import streamlit as st
import uuid
import hashlib
import os
import base64

# 1. 設定網頁標題（使用寬螢幕版面，方便 Canvas 畫布完美呈現）
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

# 3. 核心防下載機制：認證成功後解鎖 Canvas 檢視器
if user_input:
    try:
        if int(user_input) == correct_key:
            st.success("🔓 認證成功！設備硬體比對完全相符。")
            st.markdown("---")
            
            # 設定您的 GitHub 內建 PDF 檔案清單（直接抓同目錄下的實體檔案）
            pdf_files = {
                "A玩股網設定": "A玩股網設定.pdf",
                "B玩股網設定": "B玩股網設定.pdf"
            }
            
            # 下拉選單切換檔案
            selected_file = st.selectbox("📁 請選擇欲檢視的設定檔（已嚴格限制 3 頁內）：", list(pdf_files.keys()))
            local_pdf_path = pdf_files[selected_file]
            
            st.subheader(f"📄 當前檢視：{selected_file}.pdf")
            
            # 檢查檔案是否真的存在於 GitHub 目錄
            if os.path.exists(local_pdf_path):
                # 將本機 PDF 檔案讀取並轉化為 base64 編碼
                with open(local_pdf_path, "rb") as f:
                    # 【核心修正】：務必使用 .replace('\n', '') 和 .replace('\r', '') 徹底清空所有換行符號
                    # 確保整串 Base64 是完美的一長條單行字串，JS 才不會語法崩潰
                    base64_pdf = base64.b64encode(f.read()).decode('utf-8').replace('\n', '').replace('\r', '')
                
                # 終極防護網頁 Canvas 程式碼
                html_code = f"""
                <!DOCTYPE html>
                <html>
                <head>
                    <script src="https://cloudflare.com"></script>
                    <link rel="stylesheet" href="https://cloudflare.com">
                    <style>
                        body {{ background-color: #fafafa; margin: 0; padding: 10px; user-select: none; -webkit-user-select: none; }}
                        .page-container {{ position: relative; background: white; margin-bottom: 25px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); min-height: 500px; max-width: 800px; margin-left: auto; margin-right: auto; }}
                        canvas {{ width: 100%; height: auto; display: block; }}
                        .annotationLayer {{ position: absolute; top: 0; left: 0; width: 100%; height: 100%; }}
                    </style>
                </head>
                <body oncontextmenu="return false;" ondragstart="return false;">
                    <div id="viewer"></div>
                    <script>
                        pdfjsLib.GlobalWorkerOptions.workerSrc = 'https://cloudflare.com';
                        
                        // 使用 base64 資料流直接加載，完全切斷外網直連下載
                        const pdfData = atob("{base64_pdf}");
                        
                        let currentObserver = new IntersectionObserver((entries) => {{
                            entries.forEach(entry => {{
                                if (entry.isIntersecting) {{
                                    const pageNum = parseInt(entry.target.dataset.pageNum);
                                    renderSpecificPage(pageNum, entry.target);
                                    currentObserver.unobserve(entry.target);
                                }}
                            }});
                        }}, {{ rootMargin: '200px' }});

                        pdfjsLib.getDocument({{ data: pdfData }}).promise.then(pdf => {{
                            const viewer = document.getElementById('viewer');
                            const pagesToRender = Math.min(pdf.numPages, 3); // 嚴格限制最多 3 頁
                            
                            for (let num = 1; num <= pagesToRender; num++) {{
                                const container = document.createElement('div');
                                container.className = 'page-container';
                                container.dataset.pageNum = num;
                                viewer.appendChild(container);
                                currentObserver.observe(container);
                            }}
                        }});

                        function renderSpecificPage(pageNum, container) {{
                            pdfjsLib.getDocument({{ data: pdfData }}).promise.then(pdf => {{
                                pdf.getPage(pageNum).then(page => {{
                                    const canvas = document.createElement('canvas');
                                    const ctx = canvas.getContext('2d');
                                    const viewport = page.getViewport({{ scale: 1.5 }});
                                    canvas.height = viewport.height;
                                    canvas.width = viewport.width;
                                    container.appendChild(canvas);
                                    
                                    page.render({{ canvasContext: ctx, viewport: viewport }}).promise.then(() => {{
                                        const annotDiv = document.createElement('div');
                                        annotDiv.className = 'annotationLayer';
                                        container.appendChild(annotDiv);
                                        page.getAnnotations().then(annots => {{
                                            pdfjsLib.AnnotationLayer.render({{
                                                viewport: viewport.clone({{ dontFlip: true }}),
                                                div: annotDiv, annotations: annots, page: page,
                                                linkService: {{ navigateTo:()=>{{}}, getDestinationHash:()=>'#', getAnchorUrl:()=>'#' }},
                                                downloadManager: null
                                            }});
                                        }});
                                        container.style.minHeight = 'auto';
                                    }});
                                }});
                            }});
                        }}
                    </script>
                </body>
                </html>
                """
                st.components.v1.html(html_code, height=900, scrolling=True)
                st.info("💡 提示：本網頁已啟用安全硬體驗證與文件防外流保護。文件中的超連結可點擊，但無法下載與複製。")
            else:
                st.error(f"⚠️ 系統錯誤：找不到伺服器內部的實體檔案 【{local_pdf_path}】，請確認檔案是否已成功上傳至 GitHub 倉庫中。")

        else:
            st.error("❌ 認證失敗：此設備認證碼錯誤，拒絕存取雲端硬碟。")
    except ValueError:
        st.warning("⚠️ 請輸入正確的 5 位數純數字。")
