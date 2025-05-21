import streamlit as st
import pickle
import google.generativeai as genai
import os
import pdfplumber
import re
from function import make_first_prompt_gt1
api_key = "AIzaSyB8AbaE7GCBAmsnBWCl5GwH4cCrnzEdsZY"
models = genai.GenerativeModel('gemini-2.0-flash')
genai.configure(api_key=api_key)
with open('knowledge_graph_13_5_25.pkl', 'rb') as f:
    G = pickle.load(f)
case = ""
neighbors_0 = list(G.neighbors("Chương II"))
neighbors_1 = []
for i in neighbors_0:
   nei = list(G.neighbors(i))
   neighbors_1 = neighbors_1 + nei
neighbors_2 = []
for i in neighbors_1:
   nei = list(G.neighbors(i))
   neighbors_2 = neighbors_2 + nei
case_0 = ""
for i in neighbors_0:
   for j in list(G.neighbors(i)):
       case_0 = case_0 + "Điều " + j + ": " + G.nodes[j]['content'] + "\n"
def get_response_from_chatbot_gt(user_question):
   response = models.generate_content("Cho câu hỏi: " + user_question + " Bạn hãy cho tôi biết và liệt kê số hiệu và tên của của các điều nào trong Nghị định 168/2024/NĐ-CP liên quan đến phương tiện của người vi phạm trong câu hỏi mà tôi cung cấp dưới đây (nếu trong câu hỏi không cho biết phương tiện, hãy ghi số 0), lưu ý nếu câu hỏi chỉ ghi xe máy có nghĩa là xe máy chuyên dùng, chứ không phải xe mô tô: \n" + case_0)
   case_1 = ""
   if "**0**" in response.text:
    print(1)
   else:
   # pattern = r"\*\*Điều\s+(\d+):\*\*"
     pattern = r"Điều\s+(\d+)"
     matches = re.findall(pattern, response.text)
     for i in matches:
        nei = G.neighbors(i)
        for j in nei:
           case_1 = case_1 + "Điểm " + j + ": " + G.nodes[j]['content'] + "\n"
   response_1 = models.generate_content("Cho câu hỏi: " + user_question + " Bạn hãy cho tôi biết và liệt kê số hiệu và tên của của các điều khoản điểm nào trong Nghị định 168/2024/NĐ-CP mà tôi cung cấp dưới đây liên quan hoặc giống lỗi mà người trong câu hỏi mắc phải mà tôi cung cấp dưới đây được không: \n" + case_1)
   # pattern = r"\b6\.[1-9]\d*(?:\.[a-zA-ZđĐ0-9]+)?\b"
   pattern = r"Điểm\s+([0-9]+(?:\.(?:[0-9]+|[a-zđ]+))*)\s*"
   matches_1 = re.findall(pattern, response_1.text)
   matches1 = []
   for i in matches_1:
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
            p = r"Điểm\s+([0-9]+(?:\.(?:[0-9]+|[a-z]+))*)\s*"
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
   # answer = models.generate_content(prompt)
   # return answer.text 
   return relevant_passage
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
