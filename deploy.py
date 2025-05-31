import streamlit as st
import pickle
import google.generativeai as genai
import os
import pdfplumber
import re
import openai
# from dotenv import load_dotenv
from function import make_first_prompt_gt1, make_first_prompt_gt_tt
# load_dotenv()  # Tải các biến môi trường từ tệp .env
# api_key = os.getenv("api_key_google")
api_key = st.secrets["api_key_google"]
models = genai.GenerativeModel('gemini-2.0-flash')
genai.configure(api_key=api_key)
# 1. Cấu hình OpenRouter với API key trực tiếp
# API_KEY = os.getenv("API_KEY_OPENROUTER")
API_KEY = st.secrets["API_KEY_OPENROUTER"]
# Instantiate the client using the new syntax
client = openai.OpenAI(
    api_key=API_KEY,
    base_url="https://openrouter.ai/api/v1"
)
# 2. Chọn model meta-llama/llama-4-maverick:free
MODEL1 = "meta-llama/llama-4-maverick:free"
MODEL2  = "deepseek/deepseek-r1:free"
# 3. Định nghĩa hàm hỏi đáp chatbot
def question_identification(client: openai.OpenAI, question: str) -> str:
    """
    Gửi câu hỏi tới model và trả về câu trả lời.
    Requires an initialized openai.OpenAI client object.
    """
    response = client.chat.completions.create( # Use the client instance
        model=MODEL2,
        messages=[
            {"role": "system", "content": (
                "Bạn là một trợ lý ảo thân thiện và hữu ích."
            )},
            {"role": "user", "content": question}
        ],
        temperature=0.0,
        max_tokens=2048,
        top_p=0.9,
        # frequency_penalty=1.0, # These parameters might not be supported by all models/providers
        # presence_penalty=0.0   # Check OpenRouter documentation for supported parameters
    )
    # Trả về nội dung từ assistant
    return response.choices[0].message.content.strip()
def extract_article(client: openai.OpenAI, question: str) -> str:
    """
    Gửi câu hỏi tới model và trả về câu trả lời.
    Requires an initialized openai.OpenAI client object.
    """
    response = client.chat.completions.create( # Use the client instance
        model=MODEL2,
        messages=[
            {"role": "system", "content": (
                "Bạn là một trợ lý ảo thân thiện và hữu ích."
            )},
            {"role": "user", "content": question}
        ],
        temperature=0.0,
        max_tokens=2048,
        top_p=0.9,
        # frequency_penalty=1.0, # These parameters might not be supported by all models/providers
        # presence_penalty=0.0   # Check OpenRouter documentation for supported parameters
    )
    # Trả về nội dung từ assistant
    return response.choices[0].message.content.strip()
with open('knowledge_graph_13_5_25.pkl', 'rb') as f:
    G = pickle.load(f)
case = ""
neighbors_0 = list(G.neighbors("Chương II"))
case_0 = ""
for i in neighbors_0:
   for j in list(G.neighbors(i)):
       case_0 = case_0 + "Điều " + j + ": " + G.nodes[j]['content'] + "\n"    
def get_response_from_chatbot_gt(user_question):
 ans = question_identification(client, "Cho câu hỏi sau:" + user_question +"Hãy phân loại vào 5 dạng câu hỏi: 1, Câu hỏi về mức phạt.\n2,câu hỏi về quy tắc tham gia giao thông đường bộ.\n3,Câu hỏi về đường sắt.\n4,Câu hỏi về đường hàng không.\n5,Câu hỏi về đường hàng hải.\n Nếu là dạng 1 trả về 'Dạng 1', dạng 2 trả về 'Dạng 2', tương tự là 'Dạng 3','Dạng 4','Dạng 5'")
 if 'Dạng 1' in ans:  
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
 if 'Dạng 2' in ans:
     Dieu = ""
     for i in list(G.neighbors('Luật Trật tự'))[2:]:
        if i == "tt.9" or i ==  'tt.10':
           continue
        Dieu  +=   "Điều " + i[3:] + ": " + G.nodes[i]['content'] + "\n"
     pr = "Cho các điều sau trong Luật sau: " +  Dieu + ".Trích xuất các điều mà bạn thấy nội dung của nó phù hợp vầ liên quan đến câu hỏi nhất: " + user_question + ".Hãy trả lại số hiệu của điều. Ví dụ nếu bạn thấy điều 12 phù hợp trả lại 'Điều 12', điều 3 là 'Điều 3',\
      tương tự như vậy với các điều khác. Nếu không tìm thấy điều nào phù hợp, trả về rỗng"
     ex = extract_article(client, pr)
     numbers = re.findall(r"Điều\s+(\d+)", ex)
     result = list(map(int, numbers))
     result = set(result)
     excluded_articles = ["tt.1","tt.2","tt.9","tt.10"]
     Diem = Diem_m(result, excluded_articles, 'Luật Trật tự', 'tt')
     prompt = get_prompt(Diem, user_question, 'Luật Trật tự, an toàn giao thông đường bộ năm 2024')
     answer = extract_article(client, prompt)
     return answer
 
 if 'Dạng 3' in ans:
     Dieu = ""
     for i in list(G.neighbors('Luật Đường sắt'))[3:]:
        if i == "ds.9":
           continue
        Dieu  +=   "Điều " + i[3:] + ": " + G.nodes[i]['content'] + "\n"
     pr = "Cho các điều sau trong Luật sau: " +  Dieu + ".Trích xuất các điều mà bạn thấy nội dung của nó phù hợp vầ liên quan đến câu hỏi nhất: " + user_question + ".Hãy trả lại số hiệu của điều. Ví dụ nếu bạn thấy điều 12 phù hợp trả lại 'Điều 12', điều 3 là 'Điều 3',\
      tương tự như vậy với các điều khác. Nếu không tìm thấy điều nào phù hợp, trả về rỗng"
     ex = extract_article(client, pr)
     numbers = re.findall(r"Điều\s+(\d+)", ex)
     result = list(map(int, numbers))
     result = set(result)
     excluded_articles = ["ds.1","ds.2","ds.3","ds.4", "ds.9"]
     Diem = Diem_m(result, excluded_articles, 'Luật Đường sắt', 'ds')
     prompt = get_prompt(Diem, user_question, 'Luật Đường  sắt năm 2017')
     answer = extract_article(client, prompt)
     return answer
 
 if 'Dạng 4' in ans:
     Dieu = ""
     for i in list(G.neighbors('Luật Hàng không'))[3:]:
        if i == "hk.5" or i ==  'tt.12':
           continue
        Dieu  +=   "Điều " + i[3:] + ": " + G.nodes[i]['content'] + "\n"
     pr = "Cho các điều sau trong Luật sau: " +  Dieu + ".Trích xuất các điều mà bạn thấy nội dung của nó phù hợp vầ liên quan đến câu hỏi nhất: " + user_question + ".Hãy trả lại số hiệu của điều. Ví dụ nếu bạn thấy điều 12 phù hợp trả lại 'Điều 12', điều 3 là 'Điều 3',\
      tương tự như vậy với các điều khác. Nếu không tìm thấy điều nào phù hợp, trả về rỗng"
     ex = extract_article(client, pr)
     numbers = re.findall(r"Điều\s+(\d+)", ex)
     result = list(map(int, numbers))
     result = set(result)
     excluded_articles = ["hk.1","hk.2","hk.3","hk.5","hk.12"]
     Diem = Diem_m(result, excluded_articles, 'Luật Hàng không', 'hk')
     prompt = get_prompt(Diem, user_question, 'Luật Hàng không Dân dụng Việt Nam năm 2025')
     answer = extract_article(client, prompt)
     return answer
 
 if 'Dạng 5' in ans:
     Dieu = ""
     for i in list(G.neighbors('Luật Hàng hải'))[2:]:
        if i == "hh.4" or i == 'tt.6':
           continue
        if i == 'hh.12':
           continue
        Dieu  +=   "Điều " + i[3:] + ": " + G.nodes[i]['content'] + "\n"
     pr = "Cho các điều sau trong Luật sau: " +  Dieu + ".Trích xuất các điều mà bạn thấy nội dung của nó phù hợp vầ liên quan đến câu hỏi nhất: " + user_question + ".Hãy trả lại số hiệu của điều. Ví dụ nếu bạn thấy điều 12 phù hợp trả lại 'Điều 12', điều 3 là 'Điều 3',\
      tương tự như vậy với các điều khác. Nếu không tìm thấy điều nào phù hợp, trả về rỗng"
     ex = extract_article(client, pr)
     numbers = re.findall(r"Điều\s+(\d+)", ex)
     result = list(map(int, numbers))
     result = set(result)
     excluded_articles = ["hh.1","hh.2","hh.4","hh.6","hh.12"]
     Diem = Diem_m(result, excluded_articles, 'Luật Hàng hải', 'hh')
     prompt = get_prompt(Diem, user_question, "Bộ Luật Hàng hải Việt Nam năm 2015")
     answer = extract_article(client, prompt)
     return answer
def Diem_m(result, excluded_articles, ten_luat, so_hieu):
     Diem = ""
# Changed variable name from 'except' to 'excluded_articles'
     for i in excluded_articles:
        if len(i) == 4:
           Diem += "Điều " + i[3] + ": "+ G.nodes[i]['content'] + ".\n"
        else:
           Diem += "Điều " + i[3:] + ": "+ G.nodes[i]['content'] + ".\n"
        for j in list(G.neighbors(i)):
           Diem += "Khoản " + j[3:] + ": " + G.nodes[j]['content'] + ".\n"
           if list(G.neighbors(j)):
              for k in list(G.neighbors(j)):
                 Diem += "Điểm " + k[3:] + ": " + G.nodes[k]['content'] + ".\n"
     if result:
       for i in result:
      # Updated the variable name here as well
          Diem += "Điều " + str(i) + ": " + G.nodes[f'{so_hieu}.{str(i)}']['content'] + ".\n"
          for j in list(G.neighbors(f'{so_hieu}.{str(i)}')):
              Diem += "Khoản " + j[3:] + ": " + G.nodes[j]['content'] + ".\n"
              if list(G.neighbors(j)):
                 for k in list(G.neighbors(j)):
                   Diem += "Điểm " + k[3:] + ": " + G.nodes[k]['content'] + ".\n"
     else:
        for i in list(G.neighbors(ten_luat)):
      # Updated the variable name here as well
           if i not in excluded_articles:
             Diem += "Điều " + i[3:] + ": " + G.nodes[i]['content'] + ".\n"
             for j in list(G.neighbors(i)):
                Diem += "Khoản " + j[3:] + ": " + G.nodes[j]['content'] + ".\n"
                if list(G.neighbors(j)):
                   for k in list(G.neighbors(j)):
                      Diem += "Điểm " + k[3:] + ": " + G.nodes[k]['content'] + ".\n"
     return Diem

def get_prompt(Diem, user_question,  law_name):
     eva =  evaluator_extract_text(Diem, user_question)
     if 'Đã đủ' in eva:
        prompt = make_first_prompt_gt_tt(user_question, Diem, law_name)
     else:
        bonus = extract_database(eva,user_question)
        prompt = make_first_prompt_gt_tt(user_question, Diem + "\nBạn được bổ sung văn bản pháp luật sau (Lưu ý vẫn cần nêu rõ tên của bộ luật (Ví dụ Thông tư 38/2024/TT-BGTVT) và nêu cụ thể điều, khoản, điểm bạn tham khảo)" + bonus, law_name)
     return prompt
def evaluator_extract_text(relevant_passage, user_question):
    prompt = "Cho câu hỏi " + user_question + " và văn bản đã truy xuất được sau đây:\n" + relevant_passage + "\n Bạn hãy đánh giá sau các nội dung trong văn bản truy xuất đã đủ để trả lời câu hỏi chưa. \
          Nếu đủ thì trả về 'Đã đủ', nếu không trả về 'Chưa đủ' kèm những nội dung trong câu hỏi cần truy xuất thêm ở phía sau."
    res = question_identification(client, prompt)
    return res

def extract_database(relevant_passge, user_question):
    law_list = [
       "Thông tư 38/2024/TT-BGTVT"
    ]
    Diem = ""
    for i in law_list:
        Diem += i + ": "
        Diem  +=  G.nodes[i]['content'] + ":\n"
        for j in list(G.neighbors(i)):
            Diem += "Điều " + j[3:] + ": " + G.nodes[j]['content'] + ".\n"
            for k in list(G.neighbors(j)):
                Diem += "Khoản " + k[3:] + ": " + G.nodes[k]['content'] + ".\n"
                if list(G.neighbors(k)):
                   for m in list(G.neighbors(k)):
                      Diem += "Điểm " + m[3:] + ": " + G.nodes[m]['content'] + ".\n"
    return Diem
              
def process(matches, user_question):
   case_1 = ""
   for i in matches:
      nei = G.neighbors(i)
      for j in nei:
          case_1 = case_1 + "Điểm " + j + ": " + G.nodes[j]['content'] + "\n"
   for i in list(G.neighbors('12')):
      case_1 = case_1 + "Điểm " + i + ": " + G.nodes[i]['content'] + "\n"
   for i in list(G.neighbors('Mục 2')):
       if i not in matches:
           for j in list(G.neighbors(i)):
               case_1 = case_1 + "Điểm " + j + ": " + G.nodes[j]['content'] + "\n"
   for i in list(G.neighbors('Mục 3')):
       if i not in matches:
           for j in list(G.neighbors(i)):
               case_1 = case_1 + "Điểm " + j + ": " + G.nodes[j]['content'] + "\n"
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
               "trừ hành vi vi phạm quy định tại",
               'trừ trường hợp quy định tại'
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
                   "trừ hành vi vi phạm quy định tại",
                   'trừ trường hợp quy định tại'
               ):
                  if relation == "Nếu gây tai nạn giao thông," or relation  == 'Nếu gây tai nạn giao thông':
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
                          "trừ hành vi vi phạm quy định tại",
                          'trừ trường hợp quy định tại'

                         ):
                           if relation == "Nếu gây tai nạn giao thông," or relation == 'Nếu gây tai nạn giao thông':
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
st.markdown("<div class='chat-wrapper'><h1>🤖 Chatbot hỏi đáp Luật Xử lý Vi phạm An toàn Giao thông</h1></div>", unsafe_allow_html=True)

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
