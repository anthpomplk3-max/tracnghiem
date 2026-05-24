import streamlit as st
import json
import random
import re

# ---------------------------
# 0. Xác thực đăng nhập
# ---------------------------
VALID_USERNAME = "PECC2.POM"
VALID_PASSWORD = "POM.OCC"

def check_login():
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False

    if not st.session_state.logged_in:
        st.markdown('<div class="main-header"><h1>🔐 ĐĂNG NHẬP</h1></div>', unsafe_allow_html=True)
        with st.form("login_form"):
            username = st.text_input("Tên đăng nhập")
            password = st.text_input("Mật khẩu", type="password")
            submitted = st.form_submit_button("Đăng nhập")
            if submitted:
                if username == VALID_USERNAME and password == VALID_PASSWORD:
                    st.session_state.logged_in = True
                    st.rerun()
                else:
                    st.error("Sai tên đăng nhập hoặc mật khẩu!")
        st.stop()
    else:
        # Thêm nút đăng xuất ở sidebar
        with st.sidebar:
            if st.button("🚪 Đăng xuất"):
                st.session_state.logged_in = False
                st.rerun()

# ---------------------------
# 1. Đọc dữ liệu
# ---------------------------
@st.cache_data
def load_data():
    try:
        with open("GIAITHICH.json", "r", encoding="utf-8") as f:
            giai_thich = json.load(f)
        with open("TN.json", "r", encoding="utf-8") as f:
            tn = json.load(f)
    except Exception as e:
        st.error(f"Lỗi đọc file JSON: {e}")
        st.stop()

    giai_thich_map = {item["id"]: item for item in giai_thich}
    questions = []
    for tn_item in tn:
        qid = tn_item["id"]
        g_item = giai_thich_map.get(qid, {})
        questions.append({
            "id": qid,
            "question": tn_item["question"],
            "options": tn_item["options"],
            "answer_letter": g_item.get("answer"),
            "explanation": g_item.get("explanation", "Không có giải thích")
        })
    return questions

# ---------------------------
# 2. Tạo 25 bộ đề thi thử
# ---------------------------
def create_exam_sets(all_questions, total_questions):
    if total_questions >= 690:
        random.seed(42)
        shuffled = all_questions.copy()
        random.shuffle(shuffled)
        exam_sets = {}
        for i in range(23):
            exam_sets[i+1] = shuffled[i*30:(i+1)*30]
        for i in range(23, 25):
            exam_sets[i+1] = random.sample(all_questions, 30)
    else:
        exam_sets = {i+1: random.sample(all_questions, 30) for i in range(25)}
    return exam_sets

# ---------------------------
# 3. Helper functions
# ---------------------------
def format_explanation(text, correct_answer=None):
    header = ""
    if correct_answer:
        header = f"**✅ Đáp án đúng: {correct_answer}**\n\n"
    processed = re.sub(r'\s*[•\-]\s*', '\n• ', text)
    processed = processed.lstrip('\n')
    lines = processed.split('\n')
    formatted = "### 📖 Giải thích chi tiết\n\n" + header
    for line in lines:
        line = line.strip()
        if not line:
            continue
        if line.startswith('•'):
            formatted += f"{line}\n\n"
        else:
            formatted += f"{line}\n\n"
    formatted = re.sub(r'\n{3,}', '\n\n', formatted)
    return formatted

def option_with_prefix(opts):
    return [f"{chr(65+i)}. {opt}" for i, opt in enumerate(opts)]

def get_selected_letter(selected_prefix):
    return selected_prefix[0] if selected_prefix else None

# ---------------------------
# 4. Giao diện chính
# ---------------------------
st.set_page_config(page_title="Ôn tập và Thi thử", layout="wide")
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

# Kiểm tra đăng nhập trước khi hiển thị nội dung
check_login()

# Sau khi đăng nhập thành công, tiếp tục chạy ứng dụng
all_questions = load_data()
total_questions = len(all_questions)
exam_sets = create_exam_sets(all_questions, total_questions)

st.markdown('<div class="main-header"><h1>📚 ÔN TẬP VÀ THI THỬ</h1></div>', unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.header("⚙️ Cài đặt")
    mode = st.radio(
        "Chọn chế độ",
        [f"📖 Ôn tập (có giải thích - {total_questions} câu)", "✍️ Thi thử (không giải thích)"],
        key="mode_select"
    )
    st.markdown("---")
    if mode.startswith("📖 Ôn tập"):
        st.info(f"📌 {total_questions} câu hỏi. Dùng nút hoặc dropdown để chuyển câu.")
    else:
        set_number = st.selectbox("Chọn bộ đề (1-25)", options=list(range(1, 26)), index=0)
        if set_number <= 23 and total_questions >= 690:
            st.info(f"📌 Bộ đề {set_number}: 30 câu xáo trộn, không trùng với các bộ khác.")
        else:
            st.info(f"📌 Bộ đề {set_number}: 30 câu xáo trộn (có thể trùng).")

# ---------------------------
# 5. ÔN TẬP
# ---------------------------
if mode.startswith("📖 Ôn tập"):
    st.subheader("🎓 Ôn tập toàn bộ câu hỏi")
    st.caption("Chọn đáp án, xem kết quả và giải thích ngay bên dưới.")

    if "learn_idx" not in st.session_state:
        st.session_state.learn_idx = 0
    if "learn_answers" not in st.session_state:
        st.session_state.learn_answers = {}

    def prev_question():
        if st.session_state.learn_idx > 0:
            st.session_state.learn_idx -= 1

    def next_question():
        if st.session_state.learn_idx < len(all_questions) - 1:
            st.session_state.learn_idx += 1

    def jump_to_question():
        selected_id = st.session_state.jump_select
        for idx, q in enumerate(all_questions):
            if q["id"] == selected_id:
                st.session_state.learn_idx = idx
                break

    col1, col2, col3 = st.columns([1, 3, 1])
    with col1:
        st.button("⬅️ Câu trước", on_click=prev_question, use_container_width=True)
    with col3:
        st.button("Câu tiếp ➡️", on_click=next_question, use_container_width=True)
    with col2:
        q_ids = [q["id"] for q in all_questions]
        current_id = all_questions[st.session_state.learn_idx]["id"]
        st.selectbox(
            "Nhảy tới câu (ID gốc)",
            options=q_ids,
            index=q_ids.index(current_id),
            key="jump_select",
            on_change=jump_to_question,
            label_visibility="collapsed"
        )

    q = all_questions[st.session_state.learn_idx]
    st.markdown(f"**Câu {st.session_state.learn_idx+1} (ID {q['id']}):** {q['question']}")

    prefixed_opts = option_with_prefix(q['options'])
    current_ans = st.session_state.learn_answers.get(q['id'], None)
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
            st.markdown(format_explanation(q['explanation'], q['answer_letter']))

# ---------------------------
# 6. THI THỬ
# ---------------------------
else:
    st.subheader(f"📝 Bộ đề {set_number} - THI THỬ")
    st.caption("Hoàn thành 30 câu, nhấn Nộp bài để chấm điểm (không giải thích trong khi làm).")
    questions_exam = exam_sets[set_number]

    if "exam_version" not in st.session_state:
        st.session_state.exam_version = 0
    if "exam_answers" not in st.session_state:
        st.session_state.exam_answers = {}

    def reset_exam():
        st.session_state.exam_answers = {}
        st.session_state.exam_version += 1

    with st.form(key=f"exam_form_{st.session_state.exam_version}"):
        for i, q in enumerate(questions_exam, start=1):
            st.markdown(f"**{i}. {q['question']}**")
            prefixed = option_with_prefix(q['options'])
            current = st.session_state.exam_answers.get(q['id'], None)
            default_idx = prefixed.index(current) if current in prefixed else None
            selected = st.radio(
                f"opt_{i}",
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

        with st.expander("📋 Xem chi tiết từng câu", expanded=False):
            for res in results:
                with st.expander(f"Câu {res['stt']} (ID {res['id_goc']}) - {'✅ Đúng' if res['is_correct'] else '❌ Sai'}"):
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
                    st.markdown(format_explanation(res['explanation'], res['correct_letter']))
                    st.markdown("---")
        st.button("🔄 Làm lại bài thi", on_click=reset_exam, use_container_width=True)
