import streamlit as st
import json
import random

# ---------------------------
# 1. Đọc dữ liệu
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

# Xáo trộn ngẫu nhiên 184 câu với seed cố định để các bộ đề ổn định qua các lần chạy
random.seed(42)
shuffled_questions = all_questions.copy()
random.shuffle(shuffled_questions)

# Tạo 6 bộ đề, mỗi bộ 30 câu (lấy từ danh sách đã xáo trộn)
exam_sets = {i+1: shuffled_questions[i*30:(i+1)*30] for i in range(6)}

# ---------------------------
# 2. Hàm hiển thị giải thích chuyên nghiệp
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

# ---------------------------
# 3. Hàm tạo radio với tiền tố A., B., C., D.
# ---------------------------
def option_with_prefix(opts):
    return [f"{chr(65+i)}. {opt}" for i, opt in enumerate(opts)]

def get_selected_letter(selected_prefix):
    if selected_prefix and len(selected_prefix) > 0:
        return selected_prefix[0]
    return None

# ---------------------------
# 4. Giao diện chính
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
        st.info(f"Bộ đề {set_number}: 30 câu được xáo trộn ngẫu nhiên từ 184 câu, không trùng lặp giữa các bộ.")

# ---------------------------
# Chế độ HỌC TẬP (184 câu, giữ nguyên thứ tự gốc)
# ---------------------------
if mode.startswith("📖 Học tập"):
    st.subheader("🎓 Chế độ Học tập - Toàn bộ 184 câu hỏi")
    st.caption("Chọn đáp án cho mỗi câu → hiện ngay kết quả đúng/sai và giải thích chi tiết.")

    if "learn_answers" not in st.session_state:
        st.session_state.learn_answers = {}

    for idx, q in enumerate(all_questions, start=1):
        with st.container():
            st.markdown(f"**Câu {idx}:** {q['question']}")
            current_prefix = st.session_state.learn_answers.get(q['id'], None)
            prefixed_opts = option_with_prefix(q['options'])
            default_index = None
            if current_prefix and current_prefix in prefixed_opts:
                default_index = prefixed_opts.index(current_prefix)

            selected_prefix = st.radio(
                label=f"Chọn đáp án cho câu {idx}",
                options=prefixed_opts,
                index=default_index,
                key=f"learn_{q['id']}",
                label_visibility="collapsed"
            )
            if selected_prefix:
                st.session_state.learn_answers[q['id']] = selected_prefix
                selected_letter = get_selected_letter(selected_prefix)
                if selected_letter == q['answer_letter']:
                    st.success("✅ Đúng")
                else:
                    st.error(f"❌ Sai. Đáp án đúng là: **{q['answer_letter']}**")
                with st.expander("📖 Xem giải thích chi tiết", expanded=True):
                    st.markdown(format_explanation(q['explanation']))
            st.markdown("---")

# ---------------------------
# Chế độ THI THỬ (6 bộ xáo trộn, không trùng)
# ---------------------------
else:
    st.subheader(f"📝 Bộ đề {set_number} - THI THỬ")
    st.caption("Hoàn thành 30 câu, sau đó nhấn **Nộp bài** để chấm điểm (không hiển thị giải thích).")

    questions_exam = exam_sets[set_number]

    # Quản lý phiên bản để reset form
    if "exam_version" not in st.session_state:
        st.session_state.exam_version = 0
    if "exam_answers" not in st.session_state:
        st.session_state.exam_answers = {}

    # Hàm reset bài thi
    def reset_exam():
        st.session_state.exam_answers = {}
        st.session_state.exam_version += 1
        st.rerun()

    # Dùng form để tránh tự động rerun khi chọn đáp án
    with st.form(key=f"exam_form_{st.session_state.exam_version}"):
        for idx, q in enumerate(questions_exam, start=1):
            st.markdown(f"**{idx}. {q['question']}**")
            current_prefix = st.session_state.exam_answers.get(q['id'], None)
            prefixed_opts = option_with_prefix(q['options'])
            default_index = None
            if current_prefix and current_prefix in prefixed_opts:
                default_index = prefixed_opts.index(current_prefix)

            selected_prefix = st.radio(
                label=f"lựa chọn {idx}",
                options=prefixed_opts,
                index=default_index,
                key=f"exam_{q['id']}_{st.session_state.exam_version}",
                label_visibility="collapsed"
            )
            # Cập nhật ngay lập tức vào session_state (vì dùng form, cần lưu tạm)
            if selected_prefix:
                st.session_state.exam_answers[q['id']] = selected_prefix
            st.markdown("---")

        submitted = st.form_submit_button("📤 Nộp bài", use_container_width=True)

    if submitted:
        correct = 0
        for q in questions_exam:
            selected_prefix = st.session_state.exam_answers.get(q['id'], None)
            if selected_prefix:
                selected_letter = get_selected_letter(selected_prefix)
                if selected_letter == q['answer_letter']:
                    correct += 1
        score = correct / len(questions_exam) * 10
        st.success(f"🎉 Đúng {correct}/{len(questions_exam)} câu. Điểm: {score:.1f}/10")

        # Bảng chi tiết
        details = []
        for q in questions_exam:
            selected_prefix = st.session_state.exam_answers.get(q['id'], "Chưa chọn")
            user_letter = get_selected_letter(selected_prefix) if selected_prefix != "Chưa chọn" else "Chưa chọn"
            details.append({
                "Câu hỏi": q['question'][:70] + "...",
                "Đáp án của bạn": user_letter,
                "Đáp án đúng": q['answer_letter'],
                "Kết quả": "✅" if user_letter == q['answer_letter'] else "❌"
            })
        with st.expander("📋 Xem chi tiết đáp án từng câu"):
            st.table(details)

        st.button("🔄 Làm lại bài thi", on_click=reset_exam, use_container_width=True)
