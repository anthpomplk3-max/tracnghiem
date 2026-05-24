import streamlit as st
import json
import random
import re
import streamlit.components.v1 as components

# ---------------------------
# 0. Xác thực đăng nhập
# ---------------------------
VALID_USERNAME = "PECC2.POM"
VALID_PASSWORD = "POM.OCC"

def check_login():
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False

    if not st.session_state.logged_in:
        st.markdown('<div class="login-header"><h1>🔐 ĐĂNG NHẬP HỆ THỐNG</h1></div>', unsafe_allow_html=True)
        with st.form("login_form"):
            username = st.text_input("Tên đăng nhập")
            password = st.text_input("Mật khẩu", type="password")
            submitted = st.form_submit_button("Đăng nhập", use_container_width=True)
            if submitted:
                if username == VALID_USERNAME and password == VALID_PASSWORD:
                    st.session_state.logged_in = True
                    st.rerun()
                else:
                    st.error("❌ Sai tên đăng nhập hoặc mật khẩu!")
        st.stop()
    else:
        with st.sidebar:
            if st.button("🚪 Đăng xuất", use_container_width=True):
                st.session_state.logged_in = False
                st.rerun()

# ---------------------------
# 1. Đọc dữ liệu
# ---------------------------
@st.cache_data(show_spinner=False)
def load_data_cached():
    try:
        with open("GIAITHICH.json", "r", encoding="utf-8") as f:
            giai_thich = json.load(f)
        with open("TN.json", "r", encoding="utf-8") as f:
            tn = json.load(f)
    except Exception as e:
        st.error(f"Lỗi đọc file JSON: {e}")
        return []

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

def reload_data():
    st.cache_data.clear()
    st.rerun()

# ---------------------------
# 2. Tạo bộ đề thi thử
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
st.set_page_config(page_title="Ôn tập và Thi thử - PECC2", layout="wide")

st.markdown(
    """
    <style>
    .stApp {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        background-attachment: fixed;
    }
    .main-header {
        background: rgba(0, 51, 102, 0.85);
        backdrop-filter: blur(5px);
        border-radius: 20px;
        padding: 1rem;
        margin-bottom: 2rem;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
        text-align: center;
    }
    .main-header h1 {
        color: white;
        font-size: 2.5rem;
        font-weight: 700;
        letter-spacing: 1px;
        margin: 0;
        text-shadow: 2px 2px 4px #000000;
    }
    .login-header {
        text-align: center;
        margin-top: 10vh;
        margin-bottom: 2rem;
    }
    .login-header h1 {
        color: #003366;
        font-size: 2.5rem;
        font-weight: bold;
    }
    .content-card {
        background-color: rgba(255,255,255,0.95);
        border-radius: 20px;
        padding: 1.5rem;
        box-shadow: 0 8px 20px rgba(0,0,0,0.1);
        margin-bottom: 1.5rem;
    }
    .stButton button {
        background-color: #0066cc;
        color: white;
        font-weight: 600;
        border-radius: 30px;
        border: none;
        transition: all 0.3s ease;
    }
    .stButton button:hover {
        background-color: #004999;
        transform: scale(1.02);
        box-shadow: 0 2px 8px rgba(0,0,0,0.2);
    }
    .stRadio > div {
        background-color: #f8f9fa;
        padding: 12px;
        border-radius: 15px;
        margin-top: 8px;
        border-left: 4px solid #0066cc;
    }
    .stSelectbox > div {
        background-color: white;
        border-radius: 30px;
    }
    .streamlit-expanderHeader {
        background-color: #e9ecef;
        border-radius: 15px;
        font-weight: bold;
    }
    div[data-testid="stNumberInput"] label {
        display: none;
    }
    div[data-testid="stNumberInput"] {
        margin-top: 0;
        padding-top: 0;
    }
    </style>
    """,
    unsafe_allow_html=True
)

check_login()

with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2232/2232688.png", width=80)
    st.markdown("### ⚙️ QUẢN LÝ")
    if st.button("🔄 Tải lại dữ liệu JSON", use_container_width=True):
        reload_data()

all_questions = load_data_cached()
if not all_questions:
    st.error("Không thể tải dữ liệu. Vui lòng kiểm tra file JSON.")
    st.stop()

total_questions = len(all_questions)
exam_sets = create_exam_sets(all_questions, total_questions)

st.markdown('<div class="main-header"><h1>📚 ÔN TẬP & THI THỬ HỆ THỐNG ĐIỆN</h1></div>', unsafe_allow_html=True)

with st.sidebar:
    st.markdown("---")
    mode = st.radio(
        "🔘 CHẾ ĐỘ",
        [f"📖 Ôn tập (có giải thích - {total_questions} câu)", "✍️ Thi thử (không giải thích)"],
        key="mode_select"
    )
    st.markdown("---")
    if mode.startswith("📖 Ôn tập"):
        st.info(f"📌 Tổng số: {total_questions} câu")
    else:
        set_number = st.selectbox("🎯 Chọn bộ đề (1-25)", options=list(range(1, 26)), index=0)
        if set_number <= 23 and total_questions >= 690:
            st.success(f"📌 Bộ đề {set_number}: 30 câu không trùng")
        else:
            st.warning(f"📌 Bộ đề {set_number}: 30 câu (có thể trùng)")

# ---------------------------
# 5. ÔN TẬP (CÓ CONFETTI BẰNG components.html)
# ---------------------------
if mode.startswith("📖 Ôn tập"):
    st.markdown('<div class="content-card">', unsafe_allow_html=True)
    st.subheader("🎓 ÔN TẬP TOÀN BỘ CÂU HỎI")
    st.caption("✏️ Chọn đáp án, xem kết quả và giải thích ngay bên dưới.")

    if "learn_idx" not in st.session_state:
        st.session_state.learn_idx = 0
    if "learn_answers" not in st.session_state:
        st.session_state.learn_answers = {}
    if "confetti_trigger" not in st.session_state:
        st.session_state.confetti_trigger = False

    def go_prev():
        st.session_state.confetti_trigger = False
        if st.session_state.learn_idx > 0:
            st.session_state.learn_idx -= 1

    def go_next():
        st.session_state.confetti_trigger = False
        if st.session_state.learn_idx < total_questions - 1:
            st.session_state.learn_idx += 1

    def go_to_question():
        st.session_state.confetti_trigger = False
        jump_num = st.session_state.jump_number
        if 1 <= jump_num <= total_questions:
            st.session_state.learn_idx = jump_num - 1

    col1, col2, col3, col4 = st.columns([1, 1.2, 1, 1.5])
    with col1:
        st.button("⬅️ Câu trước", on_click=go_prev, use_container_width=True)
    with col2:
        st.markdown(
            f"<div style='text-align: center; font-size: 1rem; font-weight: bold; padding-top: 8px;'>📌 Câu {st.session_state.learn_idx+1}/{total_questions}</div>",
            unsafe_allow_html=True
        )
    with col3:
        st.button("Câu tiếp ➡️", on_click=go_next, use_container_width=True)
    with col4:
        st.number_input(
            "Số câu",
            min_value=1,
            max_value=total_questions,
            value=st.session_state.learn_idx + 1,
            step=1,
            key="jump_number",
            on_change=go_to_question,
            label_visibility="collapsed"
        )

    q = all_questions[st.session_state.learn_idx]
    st.markdown(f"**📄 Câu {st.session_state.learn_idx+1} (ID {q['id']}):** {q['question']}")

    prefixed_opts = option_with_prefix(q['options'])
    current_ans = st.session_state.learn_answers.get(q['id'], None)
    default_idx = prefixed_opts.index(current_ans) if current_ans in prefixed_opts else None
    selected = st.radio(
        "Lựa chọn đáp án:",
        options=prefixed_opts,
        index=default_idx,
        key=f"learn_{q['id']}",
        label_visibility="visible"
    )

    if selected:
        st.session_state.learn_answers[q['id']] = selected
        user_letter = get_selected_letter(selected)
        if user_letter == q['answer_letter']:
            st.success("✅ CHÍNH XÁC! Bạn đã trả lời đúng.")
            if not st.session_state.confetti_trigger:
                st.session_state.confetti_trigger = True
                # Dùng components.html để chạy canvas-confetti 100%
                confetti_html = """
                    <script src="https://cdn.jsdelivr.net/npm/canvas-confetti@1"></script>
                    <script>
                        canvasConfetti({ particleCount: 180, spread: 100, origin: { y: 0.6 }, startVelocity: 20, colors: ['#ff0000', '#00ff00', '#0000ff', '#ffff00', '#ff00ff', '#00ffff'] });
                        canvasConfetti({ particleCount: 120, spread: 140, origin: { y: 0.5, x: 0.2 }, startVelocity: 25 });
                        canvasConfetti({ particleCount: 120, spread: 140, origin: { y: 0.5, x: 0.8 }, startVelocity: 25 });
                        setTimeout(() => {
                            canvasConfetti({ particleCount: 400, spread: 80, origin: { y: 0.7 }, startVelocity: 10, decay: 0.9 });
                        }, 200);
                    </script>
                """
                components.html(confetti_html, height=0, width=0)
        else:
            st.error(f"❌ SAI. Đáp án đúng là: **{q['answer_letter']}**")
            st.session_state.confetti_trigger = False
        with st.expander("📖 Xem giải thích chi tiết", expanded=False):
            st.markdown(format_explanation(q['explanation'], q['answer_letter']))
    else:
        st.session_state.confetti_trigger = False

    st.markdown('</div>', unsafe_allow_html=True)

# ---------------------------
# 6. THI THỬ
# ---------------------------
else:
    st.markdown('<div class="content-card">', unsafe_allow_html=True)
    st.subheader(f"📝 BỘ ĐỀ {set_number} - THI THỬ")
    st.caption("⏳ Hoàn thành 30 câu, nhấn Nộp bài để chấm điểm (không giải thích trong khi làm).")
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
        submitted = st.form_submit_button("📤 NỘP BÀI", use_container_width=True)

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
        st.balloons()
        st.success(f"🎉 KẾT QUẢ: Đúng {correct}/{len(questions_exam)} câu. Điểm: {score:.1f}/10")

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
    st.markdown('</div>', unsafe_allow_html=True)
