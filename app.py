import streamlit as st
import json
from difflib import SequenceMatcher

# ---------------------------
# 1. Đọc và ghép dữ liệu từ hai file JSON
# ---------------------------
@st.cache_data
def load_data():
    with open("GIAITHICH.json", "r", encoding="utf-8") as f:
        giai_thich = json.load(f)  # list of {id, question, answer, explanation}
    with open("TN.json", "r", encoding="utf-8") as f:
        tn = json.load(f)          # list of {id, question, options, answer (null)}

    # Tạo map id -> options (vì thứ tự có thể khớp nhau)
    options_map = {}
    for item in tn:
        options_map[item["id"]] = item["options"]

    # Ghép câu hỏi từ file giai_thich, thêm options
    questions = []
    for q in giai_thich:
        qid = q["id"]
        opts = options_map.get(qid, [])
        # Đảm bảo options là list (trong TN có thể là list)
        if not opts:
            opts = ["A", "B", "C", "D"]  # fallback
        questions.append({
            "id": qid,
            "question": q["question"],
            "options": opts,
            "answer": q["answer"],
            "explanation": q["explanation"]
        })
    return questions

questions_all = load_data()          # tổng 184 câu
# Chỉ lấy 180 câu đầu để chia đều 6 bộ * 30 câu
questions_180 = questions_all[:180]

# Chia thành 6 bộ, mỗi bộ 30 câu
def get_set_questions(set_num):
    start = (set_num - 1) * 30
    end = start + 30
    return questions_180[start:end]

# ---------------------------
# 2. Giao diện Streamlit
# ---------------------------
st.set_page_config(page_title="Trắc nghiệm Hệ thống điện", layout="wide")
st.title("📚 HỆ THỐNG HỌC & THI TRẮC NGHIỆM")
st.markdown("---")

# Sidebar: chọn bộ đề và chế độ
with st.sidebar:
    st.header("⚙️ Cài đặt")
    set_number = st.selectbox("Chọn bộ đề (6 bộ, mỗi bộ 30 câu)", options=[1,2,3,4,5,6], index=0)
    mode = st.radio("Chọn chế độ", ["📖 Học tập (có giải thích)", "✍️ Thi thử (không giải thích)"])
    st.markdown("---")
    st.info("Tổng số câu: 180\n\nChia 6 bộ, mỗi bộ 30 câu.")

# Lấy danh sách câu hỏi cho bộ đã chọn
questions = get_set_questions(set_number)

if mode == "📖 Học tập (có giải thích)":
    st.subheader(f"🎓 Bộ đề {set_number} - Chế độ Học tập")
    st.caption("Chọn đáp án cho mỗi câu, hệ thống sẽ hiển thị ngay kết quả đúng/sai và giải thích.")
    
    # Dùng session_state để lưu lựa chọn của từng câu
    if "learn_answers" not in st.session_state:
        st.session_state.learn_answers = {}
    
    for idx, q in enumerate(questions):
        with st.container():
            st.markdown(f"**Câu {idx+1}:** {q['question']}")
            # Lấy lựa chọn hiện tại nếu có
            current = st.session_state.learn_answers.get(q['id'], None)
            # Tạo radio button riêng cho mỗi câu
            selected = st.radio(
                label="Chọn đáp án",
                options=q['options'],
                index= (q['options'].index(current) if current in q['options'] else None),
                key=f"learn_{q['id']}",
                label_visibility="collapsed"
            )
            if selected:
                st.session_state.learn_answers[q['id']] = selected
                # Kiểm tra đúng/sai
                if selected == q['answer']:
                    st.success("✅ Đúng")
                else:
                    st.error(f"❌ Sai. Đáp án đúng là: {q['answer']}")
                with st.expander("📖 Xem giải thích chi tiết"):
                    st.write(q['explanation'])
            st.markdown("---")

elif mode == "✍️ Thi thử (không giải thích)":
    st.subheader(f"📝 Bộ đề {set_number} - THI THỬ")
    st.caption("Hoàn thành 30 câu hỏi, sau đó nhấn **Nộp bài** để chấm điểm.")
    
    # Session state lưu câu trả lời của thí sinh
    if "exam_answers" not in st.session_state:
        st.session_state.exam_answers = {}
    
    # Hiển thị form thi
    with st.form(key="exam_form"):
        for idx, q in enumerate(questions):
            st.markdown(f"**{idx+1}. {q['question']}**")
            # Lấy lựa chọn hiện tại (nếu có)
            default_index = None
            current = st.session_state.exam_answers.get(q['id'], None)
            if current and current in q['options']:
                default_index = q['options'].index(current)
            selected = st.radio(
                label=f"lựa chọn {idx}",
                options=q['options'],
                index=default_index,
                key=f"exam_{q['id']}",
                label_visibility="collapsed"
            )
            if selected:
                st.session_state.exam_answers[q['id']] = selected
            st.markdown("---")
        
        submitted = st.form_submit_button("📤 Nộp bài", use_container_width=True)
    
    if submitted:
        # Chấm điểm
        correct_count = 0
        result_details = []
        for q in questions:
            user_ans = st.session_state.exam_answers.get(q['id'], None)
            is_correct = (user_ans == q['answer'])
            if is_correct:
                correct_count += 1
            result_details.append({
                "Câu hỏi": q['question'][:80] + "...",
                "Đáp án của bạn": user_ans if user_ans else "Chưa chọn",
                "Đáp án đúng": q['answer'],
                "Kết quả": "✅ Đúng" if is_correct else "❌ Sai"
            })
        score = correct_count / len(questions) * 10  # điểm 10
        st.success(f"🎉 Bạn đã trả lời đúng {correct_count}/{len(questions)} câu. Điểm số: {score:.1f}/10")
        
        # Hiển thị bảng chi tiết
        with st.expander("📋 Xem chi tiết đáp án từng câu"):
            st.table(result_details)
        
        # Nút làm lại (reset đáp án)
        if st.button("🔄 Làm lại bài thi", use_container_width=True):
            st.session_state.exam_answers = {}
            st.rerun()