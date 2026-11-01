# 1. 安裝 Gradio 套件（這在 Colab 產生外部超連結非常穩定）
!pip install -q gradio

# 2. 載入套件
import gradio as gr

# 3. 定義計算邏輯
def calculate(num1, num2, operation):
    if operation == "➕ 加加看":
        res = num1 + num2
        symbol = "＋"
    elif operation == "➖ 減減看":
        res = num1 - num2
        symbol = "－"
    elif operation == "✖️ 乘乘看":
        res = num1 * num2
        symbol = "×"
    elif operation == "➗ 分分看":
        if num2 == 0:
            return "❌ 不能除以 0 哦！"
        res = round(num1 / num2, 2)
        symbol = "÷"
        
    # 格式化去掉整數後面的 .0
    n1_disp = int(num1) if num1.is_integer() else num1
    n2_disp = int(num2) if num2.is_integer() else num2
    res_disp = int(res) if isinstance(res, (int, float)) and float(res).is_integer() else res
    
    # 回傳超大字體的 HTML 橫式結果
    return f'<div style="font-size: 65px; font-weight: bold; text-align: center; color: #2E7D32; background-color: #E8F5E9; padding: 20px; border-radius: 15px;">{n1_disp} {symbol} {n2_disp} ＝ {res_disp}</div>'

# 4. 設計專為 iPad 幼兒設計的超大介面 (自訂 CSS 放大所有元件)
css = """
.container { max-width: 800px; margin: auto; padding-top: 20px; }
.title { font-size: 45px !important; font-weight: bold; text-align: center; color: #FF4B4B; margin-bottom: 20px; }
/* 放大數字輸入框與下拉選單的字體 */
input[type="number"] { font-size: 36px !important; height: 75px !important; text-align: center !important; }
span, label { font-size: 26px !important; font-weight: bold !important; }
.secondary { font-size: 32px !important; height: 70px !important; }
"""

with gr.Blocks(css=css) as demo:
    gr.Markdown("# 🦖 幼兒 2位數大計算機 🦄", elem_classes="title")
    
    with gr.Row():
        num1 = gr.Number(value=5, label="第一個數", precision=0)
        num2 = gr.Number(value=3, label="第二個數", precision=0)
        
    operation = gr.Dropdown(
        choices=["➕ 加加看", "➖ 減減看", "✖️ 乘乘看", "➗ 分分看"], 
        value="➕ 加加看", 
        label="請選擇運算方式"
    )
    
    # 點擊這個超大按鈕進行計算
    btn = gr.Button("🎉 開始計算 🎉", variant="primary", elem_classes="secondary")
    
    gr.Markdown("### ✨ 計算結果 ✨", elem_classes="text-align: center;")
    result_html = gr.HTML('<div style="font-size: 40px; text-align: center; color: #888;">請點選上方按鈕看答案</div>')
    
    # 綁定按鈕點擊事件
    btn.click(fn=calculate, inputs=[num1, num2, operation], outputs=result_html)

# 5. 啟動並強制產生對外公開的超連結 (share=True)
demo.launch(share=True, debug=True)
