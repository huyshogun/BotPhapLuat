import streamlit as st
import pickle
import google.generativeai as genai
import os
import pdfplumber
import re
from function import make_first_prompt_gt1
api_key = "AIzaSyAYLp5HQXOAqeWCTOD8cgZJVZqTJipKHLI"
models = genai.GenerativeModel('gemini-2.0-flash')
genai.configure(api_key=api_key)
with open('knowledge_graph_13_5_25.pkl', 'rb') as f:
    G = pickle.load(f)
case = ""
neighbors_0 = list(G.neighbors("Chương II"))
case_0 = ""
for i in neighbors_0:
   for j in list(G.neighbors(i)):
       case_0 = case_0 + "Điều " + j + ": " + G.nodes[j]['content'] + "\n"    
def get_response_from_chatbot_gt(user_question):
   response = models.generate_content("Cho câu hỏi: " + user_question + ". Bạn hãy cho tôi biết và liệt kê số hiệu và tên của của các điều nào trong Nghị định 168/2024/NĐ-CP liên quan đến phương tiện của người vi phạm trong câu hỏi mà tôi cung cấp dưới đây (nếu trong câu hỏi không cho biết cụ thể phương tiện (ví dụ chỉ nói đi xe mà không nói rõ là xe ô tô, xe máy hay xe đạp) thì hãy ghi 'không rõ'.), lưu ý nếu câu hỏi chỉ ghi xe máy có nghĩa là xe máy chuyên dùng, chứ không phải xe mô tô: \n" + case_0)
   pattern = r"Điều\s+(\d+)"
   matches = re.findall(pattern, response.text)
   if "không rõ" in response.text:
      answer = ""
      answer += "Với xe ô tô:\n"
      matches_1 = ['6','13','17']
      answer += process(matches_1, user_question)
      answer += "\n\n"
      answer += "Với xe gắn máy, xe mô tô:\n"
      matches_2 = ['7','14','18']
      answer += process(matches_2, user_question)
      answer += "\n"
      answer += "Với xe máy:\n"
      matches_3 = ['8','16','19']
      answer += process(matches_3, user_question)
      answer += "\n"
      answer += "Với xe đạp, xe máy điện, xe thô sơ:\n"
      matches_4 = ['9','15']
      answer += process(matches_4, user_question)
      answer += "\n"
      return answer

   else:
      answer = process(matches, user_question)
      return answer
def process(matches, user_question):
   case_1 = ""
   for i in matches:
      nei = G.neighbors(i)
      for j in nei:
          case_1 = case_1 + "Điểm " + j + ": " + G.nodes[j]['content'] + "\n"
   for i in list(G.neighbors('12')):
        case_1 = case_1 + "Điểm " + i + ": " + G.nodes[i]['content'] + "\n"
   response_1 = models.generate_content("Cho câu hỏi: " + user_question + " Bạn hãy cho tôi biết và liệt kê số hiệu và tên của của các khoản và điểm nào trong Nghị định 168/2024/NĐ-CP mà tôi cung cấp dưới đây liên quan hoặc giống lỗi mà người trong câu hỏi mắc phải mà tôi cung cấp dưới đây được không: \n" + case_1)
   pattern = r"\b[1-9]\d?\.[1-9]\d?(?:\.[a-zđ]+)?\b"
   matches_1 = re.findall(pattern, response_1.text)
   matches1 = []
   for i in matches_1:
    if i in G:
    neig = list(G.neighbors(i))
    if(len(neig) > 0):
        uc = ""
        k = 0
        uc = uc + "Điểm " + i + ": " + G.nodes[i]['content'] + ".\n"
        for j in neig:
            # Check if the edge has the 'content' attribute before accessing it
            edge_data = G.get_edge_data(i, j)
            if edge_data:
               content = edge_data.get("content", "")
               if content in (
               "trừ các hành vi vi phạm quy định tại",
               "trừ hành vi vi phạm quy định tại"
                ):
                uc = uc + "Điểm " + j + ": " + G.nodes[j]['content'] + ".\n"
                k = k + 1
        if k > 0:
            ucv = models.generate_content("Cho câu hỏi: " + user_question + "Trong các điểm sau thuộc nghị định 168/2024/NĐ-CP chọn và nêu số hiệu của 1 điểm phù hợp và chi tiết nhất với câu hỏi. \n" + uc)
            p = r"\b[1-9]\d?\.[1-9]\d?(?:\.[a-zđ]+)?\b"
            m = re.findall(p, ucv.text)
            if len(m) > 0:
                matches1.append(m[0])
        else:
            matches1.append(i)
    else:
        matches1.append(i)
   matches1 = list(set(matches1))
   relevant_passage = ""
   o = 1
   for i in  matches1:
      relevant_passage = relevant_passage + str(o) + ", "
      o = o + 1
      relevant_passage = relevant_passage + "Điểm" + i + ": " + G.nodes[i]["content"] + "."
      nei = list(G.neighbors(i))
      if len(nei) > 0:
         relevant_passage = relevant_passage + " Khi vi phạm điểm này, người vi phạm phải chịu thêm các hình phạt bổ sung sau:\n"
         for j in nei:
        # Check if the edge exists before accessing its data
            if G.has_edge(i, j):
               edge_data = G.get_edge_data(i, j)
               relation = edge_data.get("content", "")
               if relation not in (
                  "trừ các hành vi vi phạm quy định tại",
                   "trừ hành vi vi phạm quy định tại"
               ):
                  if relation == "Nếu gây tai nạn giao thông," or relation == "Nêu gây tai nạn giao thông,":
                     relevant_passage = relevant_passage + " " + relation + " " + G.nodes[j]["content"] + "(Điểm " + j + ") "
                  else:
                     relevant_passage = relevant_passage + " " + G.nodes[j]["content"] + "(Điểm " + j + "). "

            nei0 = list(G.neighbors(j))
            if len(nei0) > 0:
              relevant_passage = relevant_passage + "Và "
              for l in nei0:  # Iterate through neighbors of j (nei0)
                # Check if the edge exists before accessing its data
                 if G.has_edge(j, l):
                    edge_data = G.get_edge_data(j, l)
                    # Check if edge_data is not None before accessing 'content'
                    if edge_data is not None:
                        relation = edge_data.get("content", "")
                        if relation not in (
                          "trừ các hành vi vi phạm quy định tại",
                          "trừ hành vi vi phạm quy định tại"

                         ):
                           if relation == "Nêu gây tai nạn giao thông," or relation == "Nếu gây tai nạn giao thông,":
                              relevant_passage = relevant_passage + " " + relation + " " + G.nodes[l]["content"] + "(Điểm " + l + ")\n"
                           else:
                              relevant_passage = relevant_passage + " " + G.nodes[l]["content"] + "(Điểm " + l + ")\n"
            else: relevant_passage = relevant_passage + "\n"
      relevant_passage = relevant_passage + "\n"
   prompt = make_first_prompt_gt1(user_question, relevant_passage)
   answer = models.generate_content(prompt)
   return answer.text

import base64
from pathlib import Path

# Cấu hình trang
st.set_page_config(page_title="Chatbot Luật Giao Thông", layout="wide")

# Nhúng hình ảnh nền dưới dạng base64 để CSS có thể hiển thị chính xác
img_path = Path("law_image.jpg")
if img_path.exists():
    img_bytes = img_path.read_bytes()
    encoded = base64.b64encode(img_bytes).decode()
    bg_url = f"data:image/jpeg;base64,{encoded}"
else:
    bg_url = ""

# CSS: đặt hình nền full-screen và overlay chat trong suốt, chữ màu vàng
if bg_url:
    st.markdown(
        f"""
        <style>
        /* Đặt ảnh nền full-screen */
        .stApp {{
            background-image: url('{bg_url}');
            background-size: cover;
            background-position: center;
            background-repeat: no-repeat;
        }}
        /* Overlay chat box: trong suốt, đè lên ảnh nền, chữ màu vàng */
        .chat-wrapper {{
            position: relative;
            z-index: 1;
            background: rgba(0, 0, 0, 0.5);
            padding: 1rem;
            border-radius: 10px;
            max-width: 800px;
            margin: auto;
            color: yellow;
        }}
        /* Ẩn thanh bên nếu muốn */
        .css-1d391kg, .css-1offfwp {{
            visibility: hidden;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

# Tiêu đề
st.markdown("<div class='chat-wrapper'><h1>🤖 Chatbot hỏi đáp Luật Giao thông</h1></div>", unsafe_allow_html=True)

# Khởi tạo lịch sử trò chuyện nếu chưa có
if "messages" not in st.session_state:
    st.session_state.messages = []

# Hiển thị lịch sử chat
for message in st.session_state.messages:
    role = message["role"]
    content = message["content"]
    st.markdown(f"<div class='chat-wrapper'><strong>{role.title()}:</strong> {content}</div>", unsafe_allow_html=True)

# Nhận input
if prompt := st.chat_input("Nhập câu hỏi của bạn về luật giao thông..."):
    # Lưu tin nhắn user
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.markdown(f"<div class='chat-wrapper'><strong>User:</strong> {prompt}</div>", unsafe_allow_html=True)

    # Gom toàn bộ lịch sử thành một chuỗi duy nhất
    prompt_all = "\n".join([f"{m['role']}: {m['content']}" for m in st.session_state.messages])

    # Gọi chatbot với chuỗi đầu vào
    response = get_response_from_chatbot_gt(prompt_all)

    # Lưu và hiển thị response
    st.session_state.messages.append({"role": "assistant", "content": response})
    st.markdown(f"<div class='chat-wrapper'><strong>Assistant:</strong> {response}</div>", unsafe_allow_html=True)

    # Hiệu ứng vui
    st.balloons()

    # Phát audio tự động
    audio_path = Path('clap.mp3')
    if audio_path.exists():
        audio_bytes = audio_path.read_bytes()
        b64_audio = base64.b64encode(audio_bytes).decode()
        audio_html = f"<audio autoplay><source src='data:audio/mp3;base64,{b64_audio}' type='audio/mp3'></audio>"
        st.markdown(audio_html, unsafe_allow_html=True)
    else:
        st.error("Không tìm thấy file clap.mp3 để phát âm thanh.")
