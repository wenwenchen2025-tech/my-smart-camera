import streamlit as st
from PIL import Image
import google.generativeai as genai

# --- 配置 (建议在 Streamlit Secrets 中配置) ---
# 修改代码第 6-11 行左右
if "GEMINI_API_KEY" in st.secrets:
    API_KEY = st.secrets["GEMINI_API_KEY"]
else:
    # 确保这里的 Key 是你从 Google AI Studio 复制的最新 Key
    API_KEY = "AIzaSyCqOqb1OLQcO3XdFP0JRz_HlBt13gGfhvo" 

genai.configure(api_key=API_KEY)
# 确保使用最通用的模型名称
try:
    model = genai.GenerativeModel('gemini-1.5-flash-latest')
except Exception as e:
    st.error(f"模型加载失败，请检查 API Key 权限或模型名称: {e}")

st.set_page_config(page_title="AI 随身翻译官", page_icon="🎤")

# --- 核心 JavaScript 逻辑：语音识别 + 语音合成 ---
def st_speech_interaction():
    js_code = """
    <script>
    const recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
    recognition.lang = 'zh-CN'; // 监听中文
    
    // 朗读函数
    function speak(text) {
        const msg = new SpeechSynthesisUtterance(text);
        msg.lang = 'en-US';
        window.speechSynthesis.speak(msg);
    }

    // 当用户点击按钮时启动识别
    window.parent.document.addEventListener('start_speech', () => {
        recognition.start();
    });

    recognition.onresult = (event) => {
        const text = event.results[0][0].transcript;
        // 把识别到的中文传回 Streamlit
        const streamlit_input = window.parent.document.querySelector('textarea');
        if (streamlit_input) {
            streamlit_input.value = text;
            streamlit_input.dispatchEvent(new Event('input', {bubbles: true}));
        }
    };
    </script>
    """
    st.components.v1.html(js_code, height=0)

# --- UI 界面 ---
tab1, tab2 = st.tabs(["📸 拍照识物", "🎤 语音翻译"])

# --- Tab 1: 拍照识物 (保留原有功能) ---
with tab1:
    img_file = st.camera_input("拍照识别物体")
    if img_file:
        img = Image.open(img_file)
        with st.spinner('分析中...'):
            prompt = "Identify this object. Provide: 1. Word 2. Chinese Translation 3. Example sentence."
            res = model.generate_content([prompt, img])
            st.write(res.text)

# --- Tab 2: 语音对话 ---
with tab2:
    st.write("点击下方按钮并说中文，我会用英文回答你并朗读。")
    
    # 输入框，用于接收语音转文字的结果
    user_query = st.text_area("识别到的中文：", key="voice_input", placeholder="正在听你说...")

    if st.button("🔴 按下开始说话"):
        # 触发 JS 开始录音
        st.components.v1.html("<script>window.parent.dispatchEvent(new Event('start_speech'));</script>", height=0)

    if user_query:
        with st.spinner('思考中...'):
            # 这里的 Prompt 强制 AI 用英文回答
            prompt = f"The user said in Chinese: '{user_query}'. Please translate/respond to this in natural English ONLY. Keep it conversational."
            response = model.generate_content(prompt)
            answer = response.text
            
            st.subheader("AI 英文回复：")
            st.info(answer)
            
            # 自动朗读回复内容
            st.components.v1.html(f"""
                <script>
                var msg = new SpeechSynthesisUtterance(`{answer.replace('`','')}`);
                msg.lang = 'en-US';
                window.speechSynthesis.speak(msg);
                </script>
            """, height=0)

st_speech_interaction()
