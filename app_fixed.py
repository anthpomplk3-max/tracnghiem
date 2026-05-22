import streamlit as st
import json
import pandas as pd
from datetime import datetime
import random

# Cấu hình trang
st.set_page_config(
    page_title="Hệ thống ôn tập trắc nghiệm - Điều độ HTĐ",
    page_icon="📚",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
    .stButton > button {
        width: 100%;
        background-color: #4CAF50;
        color: white;
        font-weight: bold;
    }
    .stButton > button:hover {
        background-color: #45a049;
    }
    .correct-answer {
        background-color: #d4edda;
        padding: 15px;
        border-radius: 5px;
        border-left: 5px solid #28a745;
        margin: 10px 0;
    }
    .wrong-answer {
        background-color: #f8d7da;
        padding: 15px;
        border-radius: 5px;
        border-left: 5px solid #dc3545;
        margin: 10px 0;
    }
    .question-card {
        background-color: #f8f9fa;
        padding: 20px;
        border-radius: 10px;
        margin-bottom: 20px;
        border: 1px solid #dee2e6;
    }
    .info-box {
        background-color: #d1ecf1;
        padding: 15px;
        border-radius: 5px;
        border-left: 5px solid #17a2b8;
        margin: 10px 0;
    }
</style>
""", unsafe_allow_html=True)

# Khởi tạo session state
def init_session_state():
    if 'questions' not in st.session_state:
        try:
            with open("questions.json", "r", encoding="utf-8") as f:
                st.session_state.questions = json.load(f)
        except FileNotFoundError:
            st.error("❌ Không tìm thấy file questions.json!")
            st.info("📝 Tạo file questions.json bằng lệnh: python extract_questions.py")
            st.stop()
        except json.JSONDecodeError:
            st.error("❌ File questions.json bị lỗi định dạng!")
            st.stop()
    
    if 'user_answers' not in st.session_state:
        st.session_state.user_answers = {}
    if 'current_index' not in st.session_state:
        st.session_state.current_index = 0
    if 'mode' not in st.session_state:
        st.session_state.mode = "practice"
    if 'exam_started' not in st.session_state:
        st.session_state.exam_started = False
    if 'exam_answers' not in st.session_state:
        st.session_state.exam_answers = {}
    if 'exam_submitted' not in st.session_state:
        st.session_state.exam_submitted = False

init_session_state()

# Sidebar
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2232/2232688.png", width=80)
    st.title("📚 MENU")
    
    mode = st.radio(
        "Chọn chế độ:",
        ["📖 Ôn tập", "📝 Thi thử", "📊 Kết quả"],
        format_func=lambda x: x
    )
    
    if mode == "📖 Ôn tập":
        st.session_state.mode = "practice"
    elif mode == "📝 Thi thử":
        st.session_state.mode = "exam"
    else:
        st.session_state.mode = "review"
    
    st.divider()
    
    total_questions = len(st.session_state.questions)
    answered = len(st.session_state.user_answers)
    
    if answered > 0:
        st.metric("📊 Tiến độ", f"{answered}/{total_questions}")
        st.progress(answered / total_questions)
    
    st.divider()
    
    if st.button("🔄 Làm mới", use_container_width=True):
        for key in ['user_answers', 'exam_answers', 'exam_submitted', 'exam_started']:
            if key in st.session_state:
                if key in ['exam_submitted', 'exam_started']:
                    st.session_state[key] = False
                else:
                    st.session_state[key] = {}
        st.rerun()

# Main content
st.title("🎓 Hệ thống ôn tập trắc nghiệm")
st.caption(f"Bộ môn: Vận hành Hệ thống điện quốc gia | Tổng số câu: {len(st.session_state.questions)}")

# Chế độ ôn tập
if st.session_state.mode == "practice":
    if len(st.session_state.questions) > 0:
        current = st.session_state.current_index
        q = st.session_state.questions[current]
        
        with st.container():
            st.markdown(f"""
            <div class="question-card">
                <h3>Câu {q['id']}: {q['text']}</h3>
            </div>
            """, unsafe_allow_html=True)
            
            # Xử lý options
            answer_options = {}
            for opt in q['options']:
                if len(opt) > 1 and opt[1] == '.':
                    key = opt[0]
                    answer_options[key] = opt
            
            saved_answer = st.session_state.user_answers.get(q['id'])
            
            # Tìm index hiện tại
            current_index = 0
            if saved_answer and saved_answer in answer_options:
                current_index = list(answer_options.keys()).index(saved_answer)
            
            selected = st.radio(
                "Chọn đáp án:",
                options=list(answer_options.keys()),
                format_func=lambda x: answer_options[x],
                key=f"q_{q['id']}",
                index=current_index if saved_answer else None
            )
            
            col1, col2, col3 = st.columns([2, 1, 2])
            with col1:
                if st.button("💾 Lưu đáp án", use_container_width=True):
                    if selected:
                        st.session_state.user_answers[q['id']] = selected
                        st.success("✅ Đã lưu đáp án!")
                        st.balloons()
                    else:
                        st.warning("⚠️ Vui lòng chọn đáp án!")
            
            # Hiển thị kết quả
            if saved_answer:
                st.divider()
                if saved_answer == q['answer']:
                    st.markdown(f"""
                    <div class="correct-answer">
                        ✅ <strong>Đáp án đúng: {q['answer']}</strong><br>
                        📖 {q.get('explanation', 'Chúc mừng bạn đã trả lời đúng!')}
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div class="wrong-answer">
                        ❌ <strong>Đáp án của bạn: {saved_answer}</strong><br>
                        ✅ <strong>Đáp án đúng: {q['answer']}</strong><br>
                        📖 {q.get('explanation', f'Đáp án đúng là {q["answer"]}')}
                    </div>
                    """, unsafe_allow_html=True)
            
            # Điều hướng
            col1, col2, col3, col4 = st.columns([1, 1, 1, 3])
            with col1:
                if st.button("⬅️ Trước", use_container_width=True) and current > 0:
                    st.session_state.current_index -= 1
                    st.rerun()
            with col2:
                if st.button("➡️ Sau", use_container_width=True) and current < total_questions - 1:
                    st.session_state.current_index += 1
                    st.rerun()
            with col3:
                if st.button("🎲 Ngẫu nhiên", use_container_width=True):
                    st.session_state.current_index = random.randint(0, total_questions - 1)
                    st.rerun()

# Chế độ thi thử
elif st.session_state.mode == "exam":
    if not st.session_state.exam_started:
        st.markdown("""
        <div class="info-box">
            📝 <strong>Hướng dẫn thi thử:</strong><br>
            - Làm bài với 20 câu hỏi ngẫu nhiên<br>
            - Có thời gian giới hạn 30 phút<br>
            - Sau khi nộp bài sẽ hiển thị kết quả
        </div>
        """, unsafe_allow_html=True)
        
        num_questions = st.number_input("Số câu hỏi:", 5, 50, 20)
        
        if st.button("🚀 Bắt đầu thi", use_container_width=True):
            exam_questions = random.sample(st.session_state.questions, min(num_questions, len(st.session_state.questions)))
            st.session_state.exam_questions = exam_questions
            st.session_state.exam_answers = {}
            st.session_state.exam_started = True
            st.session_state.exam_submitted = False
            st.session_state.exam_start_time = datetime.now()
            st.rerun()
    else:
        if not st.session_state.exam_submitted:
            # Timer
            elapsed = (datetime.now() - st.session_state.exam_start_time).total_seconds()
            remaining = 30 * 60 - elapsed
            if remaining <= 0:
                st.session_state.exam_submitted = True
                st.warning("⏰ Hết thời gian!")
                st.rerun()
            
            minutes = int(remaining // 60)
            seconds = int(remaining % 60)
            st.info(f"⏱️ Thời gian còn lại: {minutes:02d}:{seconds:02d}")
            
            st.subheader("📝 Bài thi thử")
            
            answered_count = len(st.session_state.exam_answers)
            total_count = len(st.session_state.exam_questions)
            st.progress(answered_count / total_count)
            st.caption(f"Đã trả lời: {answered_count}/{total_count}")
            
            for idx, q in enumerate(st.session_state.exam_questions):
                with st.expander(f"Câu {idx+1}: {q['text'][:100]}...", expanded=idx < 3):
                    answer_options = {}
                    for opt in q['options']:
                        if len(opt) > 1 and opt[1] == '.':
                            key = opt[0]
                            answer_options[key] = opt
                    
                    saved_answer = st.session_state.exam_answers.get(q['id'])
                    
                    selected = st.radio(
                        "Chọn đáp án:",
                        options=list(answer_options.keys()),
                        format_func=lambda x: answer_options[x],
                        key=f"exam_{q['id']}",
                        index=None
                    )
                    
                    if selected and selected != saved_answer:
                        st.session_state.exam_answers[q['id']] = selected
                        st.rerun()
            
            if st.button("📤 NỘP BÀI", use_container_width=True):
                st.session_state.exam_submitted = True
                st.rerun()
        else:
            # Kết quả
            st.subheader("📊 Kết quả bài thi")
            correct = 0
            results = []
            for q in st.session_state.exam_questions:
                user_answer = st.session_state.exam_answers.get(q['id'])
                is_correct = (user_answer == q['answer'])
                if is_correct:
                    correct += 1
                results.append({
                    "Câu": q['id'],
                    "Đáp án của bạn": user_answer or "Chưa trả lời",
                    "Đáp án đúng": q['answer'],
                    "Kết quả": "✅" if is_correct else "❌"
                })
            
            total = len(st.session_state.exam_questions)
            st.metric("Điểm số", f"{correct}/{total} ({correct/total*100:.1f}%)")
            
            df = pd.DataFrame(results)
            st.dataframe(df, use_container_width=True)
            
            if st.button("🔄 Làm bài thi mới", use_container_width=True):
                st.session_state.exam_started = False
                st.session_state.exam_submitted = False
                st.rerun()

# Chế độ xem kết quả
elif st.session_state.mode == "review":
    st.subheader("📊 Thống kê kết quả ôn tập")
    
    if len(st.session_state.user_answers) == 0:
        st.warning("⚠️ Bạn chưa làm câu hỏi nào. Hãy chuyển sang chế độ 'Ôn tập' để bắt đầu!")
    else:
        total_q = len(st.session_state.questions)
        answered = len(st.session_state.user_answers)
        correct = sum(1 for q in st.session_state.questions 
                     if q['id'] in st.session_state.user_answers 
                     and st.session_state.user_answers[q['id']] == q['answer'])
        incorrect = answered - correct
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("📊 Đã làm", f"{answered}/{total_q}")
        with col2:
            st.metric("✅ Đúng", correct)
        with col3:
            st.metric("❌ Sai", incorrect)
        
        st.progress(answered / total_q)
        
        # Hiển thị câu sai
        st.subheader("📝 Các câu cần ôn tập")
        wrong_questions = []
        for q in st.session_state.questions:
            user_ans = st.session_state.user_answers.get(q['id'])
            if user_ans and user_ans != q['answer']:
                wrong_questions.append({
                    "Câu": q['id'],
                    "Nội dung": q['text'][:100] + "...",
                    "Đáp án của bạn": user_ans,
                    "Đáp án đúng": q['answer']
                })
        
        if wrong_questions:
            df_wrong = pd.DataFrame(wrong_questions)
            st.dataframe(df_wrong, use_container_width=True)
            
            if st.button("🔄 Ôn lại câu sai", use_container_width=True):
                st.session_state.mode = "practice"
                st.session_state.current_index = wrong_questions[0]['Câu'] - 1
                st.rerun()
        else:
            st.success("🎉 Tuyệt vời! Bạn đã trả lời đúng tất cả các câu đã làm!")
