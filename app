import streamlit as st
import json
import pandas as pd
from datetime import datetime
import random

# Cấu hình trang
st.set_page_config(
    page_title="Hệ thống ôn tập trắc nghiệm - Điều độ HTĐ",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
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
    .stat-card {
        background-color: white;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        text-align: center;
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
            st.error("Không tìm thấy file questions.json. Vui lòng chạy extract_questions.py trước!")
            st.stop()
        except json.JSONDecodeError:
            st.error("File questions.json bị lỗi định dạng. Vui lòng kiểm tra lại!")
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
    
    # Chế độ học tập
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
    
    # Thống kê
    total_questions = len(st.session_state.questions)
    answered = len(st.session_state.user_answers)
    score = sum(1 for q in st.session_state.questions 
                if q['id'] in st.session_state.user_answers 
                and st.session_state.user_answers[q['id']] == q['answer'])
    
    if answered > 0:
        st.metric("📊 Tiến độ", f"{answered}/{total_questions}")
        st.progress(answered / total_questions)
        st.metric("✅ Điểm số", f"{score}/{answered}", 
                  delta=f"{score/answered*100:.1f}%" if answered > 0 else "0%")
    else:
        st.info("Bắt đầu làm bài để xem tiến độ")
    
    st.divider()
    
    # Điều khiển nhanh
    if st.session_state.mode == "practice":
        st.subheader("🎯 Điều khiển")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("⬅️ Trước"):
                if st.session_state.current_index > 0:
                    st.session_state.current_index -= 1
                    st.rerun()
        with col2:
            if st.button("➡️ Sau"):
                if st.session_state.current_index < total_questions - 1:
                    st.session_state.current_index += 1
                    st.rerun()
        
        # Jump to question
        st.subheader("🔢 Đến câu")
        jump_to = st.number_input("Nhập số câu:", 1, total_questions, 
                                  st.session_state.current_index + 1)
        if st.button("Đi đến"):
            st.session_state.current_index = jump_to - 1
            st.rerun()
    
    st.divider()
    
    if st.button("🔄 Làm mới", use_container_width=True):
        for key in ['user_answers', 'exam_answers', 'exam_submitted', 'exam_started']:
            if key in st.session_state:
                if key == 'exam_submitted' or key == 'exam_started':
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
            
            # Hiển thị đáp án
            answer_options = {}
            for opt in q['options']:
                if '. ' in opt:
                    key = opt[0]
                    answer_options[key] = opt
            
            # Kiểm tra đã chọn chưa
            saved_answer = st.session_state.user_answers.get(q['id'])
            
            selected = st.radio(
                "Chọn đáp án:",
                options=list(answer_options.keys()),
                format_func=lambda x: answer_options[x],
                key=f"q_{q['id']}",
                index=None if not saved_answer else list(answer_options.keys()).index(saved_answer)
            )
            
            col1, col2, col3 = st.columns([2, 1, 2])
            with col1:
                if st.button("💾 Lưu đáp án", use_container_width=True):
                    if selected:
                        st.session_state.user_answers[q['id']] = selected
                        st.success("✅ Đã lưu đáp án!")
                        st.balloons()
                    else:
                        st.warning("⚠️ Vui lòng chọn đáp án trước khi lưu!")
            
            # Hiển thị giải thích nếu đã chọn
            if saved_answer:
                st.divider()
                if saved_answer == q['answer']:
                    st.markdown(f"""
                    <div class="correct-answer">
                        ✅ <strong>Đáp án đúng: {q['answer']}</strong><br>
                        📖 <strong>Giải thích:</strong> {q.get('explanation', 'Chúc mừng bạn đã trả lời đúng!')}
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div class="wrong-answer">
                        ❌ <strong>Đáp án của bạn: {saved_answer}</strong><br>
                        ✅ <strong>Đáp án đúng: {q['answer']}</strong><br>
                        📖 <strong>Giải thích:</strong> {q.get('explanation', f'Đáp án đúng là {q["answer"]}')}
                    </div>
                    """, unsafe_allow_html=True)
    else:
        st.error("Không có câu hỏi nào. Vui lòng kiểm tra file questions.json!")

# Chế độ thi thử
elif st.session_state.mode == "exam":
    if not st.session_state.exam_started:
        st.markdown("""
        <div class="info-box">
            📝 <strong>Hướng dẫn thi thử:</strong><br>
            - Bạn sẽ làm bài với số câu hỏi ngẫu nhiên<br>
            - Có thời gian giới hạn cho bài thi<br>
            - Sau khi nộp bài sẽ hiển thị kết quả chi tiết
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        with col1:
            num_questions = st.number_input("Số câu hỏi:", 5, min(50, len(st.session_state.questions)), 20)
        with col2:
            time_limit = st.number_input("Thời gian (phút):", 10, 90, 30)
        
        if st.button("🚀 Bắt đầu thi", use_container_width=True):
            # Chọn ngẫu nhiên câu hỏi
            exam_questions = random.sample(st.session_state.questions, num_questions)
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
            time_limit = 30  # phút
            remaining = time_limit * 60 - elapsed
            if remaining <= 0:
                st.session_state.exam_submitted = True
                st.warning("⏰ Hết thời gian!")
                st.rerun()
            
            minutes = int(remaining // 60)
            seconds = int(remaining % 60)
            st.info(f"⏱️ Thời gian còn lại: {minutes:02d}:{seconds:02d}")
            
            # Hiển thị câu hỏi thi
            st.subheader("📝 Bài thi thử")
            
            # Progress bar cho bài thi
            answered_count = len(st.session_state.exam_answers)
            total_count = len(st.session_state.exam_questions)
            st.progress(answered_count / total_count)
            st.caption(f"Đã trả lời: {answered_count}/{total_count}")
            
            for idx, q in enumerate(st.session_state.exam_questions):
                with st.expander(f"Câu {idx+1}: {q['text'][:100]}...", expanded=idx < 3):
                    answer_options = {}
                    for opt in q['options']:
                        if '. ' in opt:
                            key = opt[0]
                            answer_options[key] = opt
                    
                    saved_answer = st.session_state.exam_answers.get(q['id'])
                    
                    selected = st.radio(
                        "Chọn đáp án:",
                        options=list(answer_options.keys()),
                        format_func=lambda x: answer_options[x],
                        key=f"exam_{q['id']}",
                        index=None if not saved_answer else list(answer_options.keys()).index(saved_answer)
                    )
                    
                    if selected and selected != saved_answer:
                        st.session_state.exam_answers[q['id']] = selected
                        st.rerun()
            
            # Nộp bài
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                if st.button("📤 NỘP BÀI", use_container_width=True):
                    st.session_state.exam_submitted = True
                    st.rerun()
        
        else:
            # Hiển thị kết quả thi
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
                    "Kết quả": "✅ Đúng" if is_correct else "❌ Sai"
                })
            
            total = len(st.session_state.exam_questions)
            score_percent = (correct / total) * 100
            
            # Hiển thị thống kê
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("📝 Tổng số câu", total)
            with col2:
                st.metric("✅ Số câu đúng", correct)
            with col3:
                st.metric("❌ Số câu sai", total - correct)
            with col4:
                st.metric("📊 Điểm số", f"{score_percent:.1f}%")
            
            # Hiển thị chi tiết
            st.subheader("📋 Chi tiết các câu")
            df = pd.DataFrame(results)
            st.dataframe(df, use_container_width=True, hide_index=True)
            
            # Nút làm lại
            if st.button("🔄 Làm bài thi mới", use_container_width=True):
                st.session_state.exam_started = False
                st.session_state.exam_submitted = False
                st.session_state.exam_answers = {}
                st.rerun()

# Chế độ xem kết quả
elif st.session_state.mode == "review":
    st.subheader("📊 Thống kê kết quả ôn tập")
    
    if len(st.session_state.user_answers) == 0:
        st.warning("⚠️ Bạn chưa làm câu hỏi nào. Hãy chuyển sang chế độ 'Ôn tập' để bắt đầu!")
    else:
        # Thống kê chi tiết
        total_q = len(st.session_state.questions)
        answered = len(st.session_state.user_answers)
        correct = sum(1 for q in st.session_state.questions 
                     if q['id'] in st.session_state.user_answers 
                     and st.session_state.user_answers[q['id']] == q['answer'])
        incorrect = answered - correct
        unanswered = total_q - answered
        
        # Hiển thị thống kê
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.markdown(f"""
            <div class="stat-card">
                <h3>📊 {answered}/{total_q}</h3>
                <p>Đã làm</p>
                <small>{answered/total_q*100:.1f}%</small>
            </div>
            """, unsafe_allow_html=True)
        with col2:
            st.markdown(f"""
            <div class="stat-card">
                <h3 style="color: #28a745;">✅ {correct}</h3>
                <p>Đúng</p>
                <small>{correct/answered*100:.1f}%</small>
            </div>
            """, unsafe_allow_html=True)
        with col3:
            st.markdown(f"""
            <div class="stat-card">
                <h3 style="color: #dc3545;">❌ {incorrect}</h3>
                <p>Sai</p>
                <small>{incorrect/answered*100:.1f}%</small>
            </div>
            """, unsafe_allow_html=True)
        with col4:
            st.markdown(f"""
            <div class="stat-card">
                <h3>⏳ {unanswered}</h3>
                <p>Chưa làm</p>
                <small>{unanswered/total_q*100:.1f}%</small>
            </div>
            """, unsafe_allow_html=True)
        
        # Thanh tiến độ
        st.progress(answered / total_q)
        
        # Danh sách câu sai
        st.subheader("📝 Các câu trả lời sai cần ôn tập")
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
            st.dataframe(df_wrong, use_container_width=True, hide_index=True)
            
            if st.button("🔄 Ôn lại các câu sai", use_container_width=True):
                st.session_state.mode = "practice"
                st.session_state.current_index = wrong_questions[0]['Câu'] - 1
                st.rerun()
        else:
            st.success("🎉 Tuyệt vời! Bạn đã trả lời đúng tất cả các câu đã làm!")
            
            if answered < total_q:
                st.info(f"💪 Hãy tiếp tục làm {total_q - answered} câu còn lại để hoàn thành!")
                if st.button("📖 Tiếp tục ôn tập", use_container_width=True):
                    st.session_state.mode = "practice"
                    st.rerun()
