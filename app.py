import streamlit as st
import json

# ---------------------------
# 1. Đọc và ghép dữ liệu
# ---------------------------
@st.cache_data
def load_data():
    with open("GIAITHICH.json", "r", encoding="utf-8") as f:
        giai_thich = json.load(f)          # list of {id, question, answer, explanation}
    with open("TN.json", "r", encoding="utf-8") as f:
        tn = json.load(f)                  # list of {id, question, options, answer (null)}

    options_map = {item["id"]: item["options"] for item in tn}

    questions = []
    for q in giai_thich:
        qid = q["id"]
        opts = options_map.get(qid, ["A", "B", "C", "D"])
        questions.append({
            "id": qid,
            "question": q["question"],
            "options": opts,
            "answer": q["answer"],
            "explanation": q["explanation"]
        })
    return questions

questions_all = load_data()                 # 184 câu
# Tạo 6 bộ đề cho thi thử (mỗi bộ 30 câu, lấy từ 180 câu đầu)
questions_180 = questions_all[:180]
exam_sets = {i+1: questions_180[i*30:(i+1)*30] for i in range(6)}

# ---------------------------
# 2. Hàm hiển thị giải thích chuyên nghiệp
# ---------------------------
def format_explanation(text):
    """
    Định dạng lại giải thích: thêm tiêu đề, bullet, in đậm các ý chính.
    """
    lines = text.split('\n')
    formatted = "### 📖 Giải thích chi tiết\n\n"
    for line in lines:
        line = line.strip()
        if not line:
            continue
        # Nếu dòng bắt đầu bằng "•" hoặc "-" thì giữ nguyên bullet
        if line.startswith(('•', '-', '✓', '●')):
            formatted += f"{line}\n\n"
        # Nếu dòng có dạng "Tại sao là X?" -> in đậm câu hỏi
        elif "Tại sao" in line or "Giải thích" in line:
            formatted += f"**{line}**\n\n"
        # Nếu dòng bắt đầu bằng số hoặc từ khóa đặc biệt
        else:
            # Thêm bullet cho các ý nhỏ
            formatted += f"• {line}\n\n"
    return formatted

# ---------------------------
# 3. Giao diện Streamlit
# ---------------------------
st.set_page_config(page_title="Trắc nghiệm Hệ thống điện", layout="wide")
st.title("📚 HỆ THỐNG HỌC & THI TRẮC NGHIỆM")
st.markdown("---")

with st.sidebar:
    st.header("⚙️ Cài đặt")
    mode = st.radio("Chọn chế độ", ["📖 Học tập (có giải thích - 184 câu)", "✍️ Thi thử (không giải thích)"])
    if mode == "✍️ Thi thử (không giải thích)":
        set_number = st.selectbox("Chọn bộ đề (1-6, mỗi bộ 30 câu)", options=[1,2,3,4,5,6], index=0)
    st.markdown("---")
    if mode == "📖 Học tập (có giải thích - 184 câu)":
        st.info("Tổng số câu học tập: **184**\n\nKhông phân bộ, tự do luyện tập.")
    else:
        st.info(f"Bộ đề {set_number}: 30 câu. Thi thử không hiển thị giải thích.")

# ---------------------------
# Chế độ HỌC TẬP (184 câu, có giải thích chuyên nghiệp)
# ---------------------------
if mode.startswith("📖 Học tập"):
    st.subheader("🎓 Chế độ Học tập - Toàn bộ 184 câu hỏi")
    st.caption("Chọn đáp án cho mỗi câu → hiện ngay kết quả đúng/sai và giải thích chi tiết.")

    if "learn_answers" not in st.session_state:
        st.session_state.learn_answers = {}

    # Hiển thị lần lượt từng câu
    for idx, q in enumerate(questions_all, start=1):
        with st.container():
            st.markdown(f"**Câu {idx}:** {q['question']}")
            current = st.session_state.learn_answers.get(q['id'], None)
            selected = st.radio(
                label=f"Chọn đáp án cho câu {idx}",
                options=q['options'],
                index=(q['options'].index(current) if current in q['options'] else None),
                key=f"learn_{q['id']}",
                label_visibility="collapsed"
            )
            if selected:
                st.session_state.learn_answers[q['id']] = selected
                if selected == q['answer']:
                    st.success("✅ Đúng")
                else:
                    st.error(f"❌ Sai. Đáp án đúng là: **{q['answer']}**")
                # Hiển thị giải thích đã được định dạng lại
                with st.expander("📖 Xem giải thích chi tiết", expanded=True):
                    st.markdown(format_explanation(q['explanation']))
            st.markdown("---")

# ---------------------------
# Chế độ THI THỬ (6 bộ, mỗi bộ 30 câu, không giải thích)
# ---------------------------
else:
    st.subheader(f"📝 Bộ đề {set_number} - THI THỬ")
    st.caption("Hoàn thành 30 câu, sau đó nhấn **Nộp bài** để chấm điểm (không hiển thị giải thích).")

    questions_exam = exam_sets[set_number]
    if "exam_answers" not in st.session_state:
        st.session_state.exam_answers = {}

    with st.form(key="exam_form"):
        for idx, q in enumerate(questions_exam, start=1):
            st.markdown(f"**{idx}. {q['question']}**")
            current = st.session_state.exam_answers.get(q['id'], None)
            selected = st.radio(
                label=f"lựa chọn {idx}",
                options=q['options'],
                index=(q['options'].index(current) if current in q['options'] else None),
                key=f"exam_{q['id']}",
                label_visibility="collapsed"
            )
            if selected:
                st.session_state.exam_answers[q['id']] = selected
            st.markdown("---")

        submitted = st.form_submit_button("📤 Nộp bài", use_container_width=True)

    if submitted:
        correct = sum(1 for q in questions_exam if st.session_state.exam_answers.get(q['id']) == q['answer'])
        score = correct / len(questions_exam) * 10
        st.success(f"🎉 Đúng {correct}/{len(questions_exam)} câu. Điểm: {score:.1f}/10")

        # Bảng chi tiết kết quả
        details = []
        for q in questions_exam:
            user_ans = st.session_state.exam_answers.get(q['id'], "Chưa chọn")
            details.append({
                "Câu hỏi": q['question'][:70] + "...",
                "Đáp án của bạn": user_ans,
                "Đáp án đúng": q['answer'],
                "Kết quả": "✅" if user_ans == q['answer'] else "❌"
            })
        with st.expander("📋 Xem chi tiết đáp án từng câu"):
            st.table(details)

        if st.button("🔄 Làm lại bài thi", use_container_width=True):
            st.session_state.exam_answers = {}
            st.rerun()
