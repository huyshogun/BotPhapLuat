import streamlit as st
import pickle
import google.generativeai as genai
import os
import pdfplumber
from function import relevant_context, relevant_passage, relevant_passage1, make_first_prompt, relevant_context0, make_first_prompt_gt, make_first_prompt_gt1
api_key = "AIzaSyB8AbaE7GCBAmsnBWCl5GwH4cCrnzEdsZY"
model="models/text-embedding-004"
models = genai.GenerativeModel('gemini-2.0-flash')
genai.configure(api_key=api_key)
with open('knowledge_graph_13_5_25.pkl', 'rb') as f:
    G = pickle.load(f)
m = 1
Dieu = ""
def read_pdf(file_path):
    text = ""
    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            text += page.extract_text() + "\n"
    return text

file_path = "Nghi_dinh_168.pdf"
content = read_pdf(file_path)
def get_response_from_chatbot(user_question):
   response = models.generate_content("Cho câu hỏi: " + user_question + " Những điều nào trong danh sách sau phù hợp để trả lời câu hỏi trên" + Dieu)
   input = relevant_context(response.text)
#   input = relevant_context0(response.text)
   relevant_passage_text = relevant_passage(input)
   relevant_passage1_text = relevant_passage1(user_question)
   prompt = make_first_prompt(user_question,relevant_passage_text+"\n"+relevant_passage1_text)
   answer = models.generate_content(prompt)
   return answer.text
def get_response_from_chatbot_gt(user_question):
   prompt = make_first_prompt_gt1(user_question,content)
   answer = models.generate_content(prompt)
   return answer.text
st.set_page_config(page_title="Chatbot Luật Giao Thông", layout="wide")
st.title("🤖 Chatbot hỏi đáp Luật xử lý vi phạm An toàn giao thông")

# Hiển thị hình ảnh minh họa (nếu có)
st.image("law_image.jpg", caption="Luật Giao Thông", use_column_width=True)

# Khởi tạo lịch sử cuộc trò chuyện
if "messages" not in st.session_state:
    st.session_state.messages = []

# Hiển thị các tin nhắn đã lưu trong lịch sử
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Nhận đầu vào từ người dùng
if prompt := st.chat_input("Nhập câu hỏi của bạn về luật giao thông..."):
    # Lưu và hiển thị tin nhắn của người dùng
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Gọi hàm để lấy phản hồi từ chatbot
    response = get_response_from_chatbot_gt(prompt)

    # Lưu và hiển thị phản hồi của chatbot
    st.session_state.messages.append({"role": "assistant", "content": response})
    with st.chat_message("assistant"):
        st.markdown(response)
    st.balloons()
    audio_file = open('clap.mp3', 'rb')
    audio_bytes = audio_file.read()
    st.audio(audio_bytes, format='audio/mp3')
