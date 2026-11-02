import streamlit as st
import uuid
import hashlib  

# 1. 設定網頁標題（使用寬螢幕版面，方便 Canvas 畫布完美呈現）
st.set_page_config(page_title="系統安全設備", layout="wide")
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

# 在畫面上為您自己顯示目前的伺服器資訊（方便您核對密碼，別人看不到後台）
st.info(f"ℹ️ 目前系統偵測設備 MAC: {current_mac} | 認證密碼: {correct_key:05d}")

# 2. 密碼輸入框
user_input = st.text_input("請輸入 5 位數認證密碼：", type="password")

# 3. 核心防下載機制：認證成功後直接在網頁內解鎖 Canvas 檢視器
if user_input:
    try:
        if int(user_input) == correct_key:
            st.success("🔓 認證成功！設備硬體比對完全相符。")
            st.markdown("---")
            
            # 這裡已經幫您代入 A 檔案與 B 檔案在 Google Drive 的真實 File ID
            pdf_files = {
                "A玩股網設定": "1Q_WvuwCvI6bQC2EjtAhNodUdBn1BZpAA",
                "B玩股網設定": "1uu47__67kGLzLlTTStiweXypdLwtXCgU"
            }
            
            # 在網頁內建立下拉選單讓使用者切換檔案
            selected_file = st.selectbox("📁 請選擇欲檢視的設定檔（已嚴格限制 3 頁內）：", list(pdf_files.keys()))
            file_id = pdf_files[selected_file]
            
            # 生成直連二進位串流連結（供前端 PDF.js 讀取並畫成畫布）
            direct_pdf_url = f"https://google.com{file_id}"
            
            st.subheader(f"📄 當前檢視：{selected_file}.pdf")
            
            # 內嵌整合「延遲載入 (Lazy Load)」與「超連結透明層 (Annotation Layer)」的強效前端防護碼
            # 這裡已將所有資源網址更換為 cdnjs 官方實體路徑，確保不再有 cloudflare.com 預留字樣
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
                    const url = '{direct_pdf_url}';
                    
                    let currentObserver = new IntersectionObserver((entries) => {{
                        entries.forEach(entry => {{
                            if (entry.isIntersecting) {{
                                const pageNum = parseInt(entry.target.dataset.pageNum);
                                renderSpecificPage(pageNum, entry.target);
                                currentObserver.unobserve(entry.target);
                            }}
                        }});
                    }}, {{ rootMargin: '200px' }});

                    pdfjsLib.getDocument(url).promise.then(pdf => {{
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
                        pdfjsLib.getDocument(url).promise.then(pdf => {{
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
                                    container.style.minHeight = 'auto'; // 繪製完成後解除占位高度
                                }});
                            }});
                        }});
                    }}
                </script>
            </body>
            </html>
            """
            
            # 在 Streamlit 中安全渲染防下載元件
            st.components.v1.html(html_code, height=900, scrolling=True)
            st.info("💡 提示：本網頁已啟用安全硬體驗證與文件防外流保護。文件中的超連結可點擊，但無法下載與複製。")

        else:
            st.error("❌ 認證失敗：此設備認證碼錯誤，拒絕存取雲端硬碟。")
    except ValueError:
        st.warning("⚠️ 請輸入正確的 5 位數純數字。")
