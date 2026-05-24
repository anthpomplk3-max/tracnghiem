# ---------------------------
# 5. ÔN TẬP
# ---------------------------
if mode.startswith("📖 Ôn tập"):
    st.markdown('<div class="content-card">', unsafe_allow_html=True)
    st.subheader("🎓 ÔN TẬP TOÀN BỘ CÂU HỎI")
    st.caption("✏️ Chọn đáp án, xem kết quả và giải thích ngay bên dưới.")

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

    # Hàm xử lý khi chọn câu từ selectbox
    def on_select_question():
        selected_label = st.session_state.question_selector
        # selected_label có dạng "Câu 123 (ID 456)" -> tách lấy index
        # Cách đơn giản: lưu index trực tiếp vào value của selectbox
        # Ta sẽ xây dựng options = list of indices, format = f"Câu {i+1} (ID {q['id']})"
        # và set index = st.session_state.learn_idx
        # Khi change, lấy index từ vị trí được chọn
        # Vì selectbox trả về giá trị là phần tử trong options, ta cần map lại
        # Cách tốt: dùng dictionary mapping label -> index
        # Nhưng đơn giản hơn: dùng list comprehension và lấy chỉ số bằng cách tìm lại
        selected_index = question_labels.index(selected_label)
        if selected_index != st.session_state.learn_idx:
            st.session_state.learn_idx = selected_index

    # Tạo danh sách các lựa chọn cho selectbox
    question_labels = [f"Câu {i+1} / {total_questions} (ID {q['id']})" for i, q in enumerate(all_questions)]
    current_label = question_labels[st.session_state.learn_idx]

    # Bố trí 3 cột: Câu trước | Selectbox + Số thứ tự | Câu tiếp
    col_prev, col_mid, col_next = st.columns([1, 2, 1])
    with col_prev:
        st.button("⬅️ Câu trước", on_click=prev_question, use_container_width=True)
    with col_next:
        st.button("Câu tiếp ➡️", on_click=next_question, use_container_width=True)
    with col_mid:
        # Selectbox duy nhất vừa chọn câu vừa hiển thị số thứ tự
        st.selectbox(
            "Chọn câu hỏi",
            options=question_labels,
            index=st.session_state.learn_idx,
            key="question_selector",
            on_change=on_select_question,
            label_visibility="collapsed"
        )

    q = all_questions[st.session_state.learn_idx]
    st.markdown(f"**📄 {question_labels[st.session_state.learn_idx]}:** {q['question']}")

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
        else:
            st.error(f"❌ SAI. Đáp án đúng là: **{q['answer_letter']}**")
        with st.expander("📖 Xem giải thích chi tiết", expanded=False):
            st.markdown(format_explanation(q['explanation'], q['answer_letter']))
    st.markdown('</div>', unsafe_allow_html=True)
