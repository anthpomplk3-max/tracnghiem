import streamlit as st
import json
import random

# ---------------------------
# 1. Đọc và xử lý dữ liệu
# ---------------------------
@st.cache_data
def load_data():
    with open("GIAITHICH.json", "r", encoding="utf-8") as f:
        giai_thich = json.load(f)
    with open("TN.json", "r", encoding="utf-8") as f:
        tn = json.load(f)

    options_map = {item["id"]: item["options"] for item in tn}

    questions = []
    for q in giai_thich:
        qid = q["id"]
        opts = options_map.get(qid, ["A", "B", "C", "D"])
        questions.append({
            "id": qid,
            "question": q["question"],
            "options": opts,
            "answer_letter": q["answer"],
            "explanation": q["explanation"]
        })
    return questions

all_questions = load_data()  # 184 câu

# Xáo trộn 184 câu để tạo 6 bộ đề thi thử (không trùng)
random.seed(42)
shuffled_questions = all_questions.copy()
random.shuffle(shuffled_questions)
exam_sets = {i+1: shuffled_questions[i*30:(i+1)*30] for i in range(6)}

# ---------------------------
# 2. Hàm hỗ trợ định dạng
# ---------------------------
def format_explanation(text):
    lines = text.split('\n')
    formatted = "### 📖 Giải thích chi tiết\n\n"
    for line in lines:
        line = line.strip()
        if not line:
            continue
        if line.startswith(('•', '-', '✓', '●')):
            formatted += f"{line}\n\n"
        elif "Tại sao" in line or "Giải thích" in line:
            formatted += f"**{line}**\n\n"
        else:
            formatted += f"• {line}\n\n"
    return formatted

def option_with_prefix(opts):
    return [f"{chr(65+i)}. {opt}" for i, opt in enumerate(opts)]

def get_selected_letter(selected_prefix):
    return selected_prefix[0] if selected_prefix else None

# ---------------------------
# 3. Cấu hình giao diện
# ---------------------------
st.set_page_config(page_title="Ôn tập và Thi thử", layout="wide")

# CSS background và styling
st.markdown(
    """
    <style>
    .stApp {
        background-image: url("https://images.unsplash.com/photo-1581094288338-1f4b2d6f9b5a?q=80&w=2070&auto=format&fit=crop");
        background-size: cover;
        background-attachment: fixed;
        background-position: center;
    }
    .main-header {
        text-align: center;
        padding: 20px;
        background-color: rgba(0,0,0,0.6);
        border-radius: 15px;
        margin-bottom: 25px;
    }
    .main-header h1 {
        color: white;
        font-size: 3em;
        text-shadow: 2px 2px 4px #000000;
        margin: 0;
    }
    .stRadio > div {
        background-color: rgba(255,255,255,0.95);
        padding: 12px;
        border-radius: 12px;
        margin-top: 5px;
    }
    .stButton button {
        background-color: #4CAF50;
        color: white;
        font-weight: bold;
        border-radius: 8px;
    }
    .stSelectbox > div {
        background-color: rgba(255,255,255,0.9);
        border-radius: 8px;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.markdown('<div class="main-header"><h1>📚 ÔN TẬP VÀ THI THỬ</h1></div>', unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.header("⚙️ Cài đặt")
    mode = st.radio("Chọn chế độ", ["📖 Ôn tập (có giải thích - 184 câu)", "✍️ Thi thử (không giải thích)"])
    if mode == "✍️ Thi thử (không giải thích)":
        set_number = st.selectbox("Chọn bộ đề (1-6, mỗi bộ 30 câu)", options=[1,2,3,4,5,6], index=0)
    st.markdown("---")
    if mode == "📖 Ôn tập (có giải thích - 184 câu)":
        st.info("📌 **184 câu hỏi**\n\nMỗi lần hiển thị 1 câu. Bạn có thể chọn câu bằng dropdown hoặc nút chuyển.")
    else:
        st.info(f"📌 **Bộ đề {set_number}**\n\n30 câu xáo trộn, không trùng lặp giữa các bộ.")

# ---------------------------
# 4. Chế độ ÔN TẬP
# ---------------------------
if mode.startswith("📖 Ôn tập"):
    st.subheader("🎓 Ôn tập toàn bộ câu hỏi")
    st.caption("Chọn câu hỏi, trả lời và xem giải thích ngay bên dưới.")

    if "current_idx" not in st.session_state:
        st.session_state.current_idx = 0
    if "learn_answers" not in st.session_state:
        st.session_state.learn_answers = {}

    # Dropdown chọn nhanh theo ID gốc
    q_ids = [q["id"] for q in all_questions]
    selected_id = st.selectbox(
        "🔍 Chọn câu hỏi (theo ID gốc)",
        options=q_ids,
        index=st.session_state.current_idx,
        key="q_selector"
    )
    new_idx = q_ids.index(selected_id)
    if new_idx != st.session_state.current_idx:
        st.session_state.current_idx = new_idx
        st.rerun()

    # Nút điều hướng
    col1, col2, col3 = st.columns([1, 10, 1])
    with col1:
        if st.button("⬅️ Câu trước", disabled=(st.session_state.current_idx == 0)):
            st.session_state.current_idx -= 1
            st.rerun()
    with col3:
        if st.button("Câu tiếp ➡️", disabled=(st.session_state.current_idx == len(all_questions)-1)):
            st.session_state.current_idx += 1
            st.rerun()

    # Hiển thị câu hỏi
    q = all_questions[st.session_state.current_idx]
    st.markdown(f"**Câu {st.session_state.current_idx+1} (ID {q['id']}):** {q['question']}")

    current_ans = st.session_state.learn_answers.get(q['id'], None)
    prefixed_opts = option_with_prefix(q['options'])
    default_idx = prefixed_opts.index(current_ans) if current_ans in prefixed_opts else None

    selected = st.radio(
        "Chọn đáp án",
        options=prefixed_opts,
        index=default_idx,
        key=f"learn_{q['id']}",
        label_visibility="collapsed"
    )
    if selected:
        st.session_state.learn_answers[q['id']] = selected
        user_letter = get_selected_letter(selected)
        if user_letter == q['answer_letter']:
            st.success("✅ Đúng")
        else:
            st.error(f"❌ Sai. Đáp án đúng là: **{q['answer_letter']}**")
        with st.expander("📖 Xem giải thích chi tiết", expanded=False):
            st.markdown(format_explanation(q['explanation']))

# ---------------------------
# 5. Chế độ THI THỬ
# ---------------------------
else:
    st.subheader(f"📝 Bộ đề {set_number} - THI THỬ")
    st.caption("Hoàn thành 30 câu, sau đó nhấn **Nộp bài** để chấm điểm (không hiển thị giải thích khi làm).")

    questions_exam = exam_sets[set_number]

    if "exam_version" not in st.session_state:
        st.session_state.exam_version = 0
    if "exam_answers" not in st.session_state:
        st.session_state.exam_answers = {}

    def reset_exam():
        st.session_state.exam_answers = {}
        st.session_state.exam_version += 1
        st.rerun()

    with st.form(key=f"exam_form_{st.session_state.exam_version}"):
        for i, q in enumerate(questions_exam, start=1):
            st.markdown(f"**{i}. {q['question']}**")
            current = st.session_state.exam_answers.get(q['id'], None)
            prefixed = option_with_prefix(q['options'])
            default_idx = prefixed.index(current) if current in prefixed else None
            selected = st.radio(
                label=f"opt_{i}",
                options=prefixed,
                index=default_idx,
                key=f"exam_{q['id']}_{st.session_state.exam_version}",
                label_visibility="collapsed"
            )
            if selected:
                st.session_state.exam_answers[q['id']] = selected
            st.markdown("---")
        submitted = st.form_submit_button("📤 Nộp bài", use_container_width=True)

    if submitted:
        correct = 0
        results = []
        for i, q in enumerate(questions_exam, start=1):
            selected = st.session_state.exam_answers.get(q['id'], None)
            user_letter = get_selected_letter(selected) if selected else "Chưa chọn"
            is_correct = (user_letter == q['answer_letter'])
            if is_correct:
                correct += 1
            results.append({
                "stt": i,
                "id_goc": q['id'],
                "question": q['question'],
                "options": q['options'],
                "user_letter": user_letter,
                "correct_letter": q['answer_letter'],
                "is_correct": is_correct,
                "explanation": q['explanation']
            })
        score = correct / len(questions_exam) * 10
        st.success(f"🎉 Đúng {correct}/{len(questions_exam)} câu. Điểm: {score:.1f}/10")

        with st.expander("📋 Xem chi tiết đáp án từng câu (nhấn để mở/đóng)", expanded=False):
            for res in results:
                with st.expander(f"Câu {res['stt']} (ID gốc {res['id_goc']}) - {'✅ Đúng' if res['is_correct'] else '❌ Sai'}"):
                    st.markdown(f"**Câu hỏi:** {res['question']}")
                    for idx_opt, opt in enumerate(res['options']):
                        prefix = chr(65+idx_opt)
                        if prefix == res['correct_letter']:
                            st.markdown(f"- **{prefix}. {opt}** (Đáp án đúng)")
                        else:
                            st.markdown(f"- {prefix}. {opt}")
                    st.markdown(f"**Đáp án của bạn:** {res['user_letter']}")
                    if not res['is_correct']:
                        st.markdown(f"**Đáp án đúng:** {res['correct_letter']}")
                    st.markdown(format_explanation(res['explanation']))
                    st.markdown("---")

        st.button("🔄 Làm lại bài thi", on_click=reset_exam, use_container_width=True)
