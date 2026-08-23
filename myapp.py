import streamlit as st
import pandas as pd
from google import genai
from google.genai import types
from streamlit_mic_recorder import mic_recorder

# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="VoiceStudy AI",
    page_icon="🎤",
    layout="wide"
)

# ============================================================
# GEMINI CLIENT
# ============================================================

api_key = st.secrets["GEMINI_API_KEY"]

client = genai.Client(
    api_key=api_key
)

MODEL = "gemini-3.6-flash"

# ============================================================
# SESSION STATE
# ============================================================

if "audio_bytes" not in st.session_state:
    st.session_state.audio_bytes = None

if "transcription" not in st.session_state:
    st.session_state.transcription = None

if "summary" not in st.session_state:
    st.session_state.summary = None

if "flashcards" not in st.session_state:
    st.session_state.flashcards = None

if "quiz" not in st.session_state:
    st.session_state.quiz = None

if "quiz_answers" not in st.session_state:
    st.session_state.quiz_answers = {}

if "quiz_score" not in st.session_state:
    st.session_state.quiz_score = None

# ============================================================
# HEADER
# ============================================================
st.markdown(
    """
    <style>

    .main-title {
        font-size: 3rem;
        font-weight: 800;
        margin-bottom: 0.2rem;
    }

    .subtitle {
        font-size: 1.1rem;
        opacity: 0.75;
        margin-bottom: 2rem;
    }

    .section-title {
        font-size: 1.8rem;
        font-weight: 700;
        margin-top: 1rem;
    }

    </style>
    """,
    unsafe_allow_html=True
)
st.markdown(
    '<div class="main-title">🎤 VoiceStudy AI</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">'
    'Transform lecture recordings into summaries, '
    'flashcards and AI-powered quizzes.'
    '</div>',
    unsafe_allow_html=True
)

# ============================================================
# NEW STUDY SESSION
# ============================================================

if st.button("🔄 New Study Session"):

    st.session_state.audio_bytes = None
    st.session_state.transcription = None
    st.session_state.summary = None
    st.session_state.flashcards = None
    st.session_state.quiz = None
    st.session_state.quiz_answers = {}
    st.session_state.quiz_score = None

    st.rerun()

# ============================================================
# KPI DASHBOARD
# ============================================================

kpi1, kpi2, kpi3, kpi4 = st.columns(4)

with kpi1:

    st.metric(
        "🎴 Flashcards",
        len(st.session_state.flashcards)
        if st.session_state.flashcards
        else 0,
        delta="Study ready"
        if st.session_state.flashcards
        else None
    )

with kpi2:

    st.metric(
        "📝 Transcript",
        "Ready"
        if st.session_state.transcription
        else "Waiting",
        delta="AI processed"
        if st.session_state.transcription
        else None
    )

with kpi3:

    st.metric(
        "🧠 Summary",
        "Ready"
        if st.session_state.summary
        else "Waiting"
    )

with kpi4:

    st.metric(
        "❓ Quiz",
        len(st.session_state.quiz)
        if st.session_state.quiz
        else 0,
        delta="Questions"
        if st.session_state.quiz
        else None
    )

st.divider()

# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.header("🎓 VoiceStudy AI")

    st.write(
        "Your personal AI-powered study assistant."
    )

    st.divider()

    st.subheader("Pipeline")

    st.write("🎙️ Voice Recording")
    st.write("↓")
    st.write("📝 AI Transcription")
    st.write("↓")
    st.write("🧠 AI Summary")
    st.write("↓")
    st.write("🃏 Flashcards")
    st.write("↓")
    st.write("❓ AI Quiz")

    st.divider()

    st.caption(
        "Powered by Gemini + Streamlit"
    )

# ============================================================
# RECORDING SECTION
# ============================================================

st.header("🎙️ 1. Record Your Lecture")

st.write(
    "Record a lecture, explanation, revision session, "
    "or any study material."
)

audio = mic_recorder(
    start_prompt="🎙️ Start Recording",
    stop_prompt="⏹️ Stop Recording",
    just_once=True,
    use_container_width=True
)

if audio:

    st.session_state.audio_bytes = audio["bytes"]

# ============================================================
# AUDIO SECTION
# ============================================================

if st.session_state.audio_bytes:

    st.success("✅ Audio recording captured!")

    st.audio(
        st.session_state.audio_bytes,
        format="audio/wav"
    )

    # --------------------------------------------------------
    # TRANSCRIPTION BUTTON
    # --------------------------------------------------------

    if st.button(
        "📝 Transcribe Lecture",
        type="primary"
    ):

        try:

            with st.spinner(
                "🎧 Gemini is analyzing your lecture..."
            ):

                response = client.models.generate_content(
                    model=MODEL,
                    contents=[
                        (
                            "Transcribe this lecture audio accurately. "
                            "Return only the spoken content. "
                            "Do not summarize it."
                        ),
                        types.Part.from_bytes(
                            data=st.session_state.audio_bytes,
                            mime_type="audio/wav"
                        )
                    ]
                )

            st.session_state.transcription = response.text

            st.success(
                "✅ Transcription completed!"
            )

        except Exception as e:

            st.error(
                f"Transcription failed: {e}"
            )

# ============================================================
# TRANSCRIPTION SECTION
# ============================================================

if st.session_state.transcription:

    st.divider()

    st.header("📝 2. Lecture Transcription")

    with st.expander(
        "View full transcription",
        expanded=True
    ):

        st.write(
            st.session_state.transcription
        )

    # ========================================================
    # STUDY MATERIAL SETTINGS
    # ========================================================

    st.header("⚙️ 3. Study Material Settings")

    with st.form("study_settings"):

        col1, col2, col3 = st.columns(3)

        with col1:

            flashcard_count = st.selectbox(
                "Number of Flashcards",
                [5, 10, 15, 20],
                index=1
            )

        with col2:

            difficulty = st.selectbox(
                "Difficulty",
                [
                    "Easy",
                    "Medium",
                    "Hard"
                ],
                index=1
            )

        with col3:

            study_style = st.selectbox(
                "Study Style",
                [
                    "Exam Preparation",
                    "Quick Revision",
                    "Deep Understanding"
                ],
                index=0
            )

        generate_material = st.form_submit_button(
            "🧠 Generate Study Material",
            type="primary"
        )

    # ========================================================
    # GENERATE SUMMARY + FLASHCARDS
    # ========================================================

    if generate_material:

        study_prompt = f"""
You are VoiceStudy AI, an expert educational assistant.

Your job is to transform a lecture transcription into
high-quality study material.

USER SETTINGS

Number of flashcards: {flashcard_count}

Difficulty: {difficulty}

Study style: {study_style}

TASK

Create:

1. A concise but useful lecture summary.
2. Exactly {flashcard_count} flashcards.

FLASHCARD REQUIREMENTS

Each flashcard must contain:

- question
- answer
- difficulty
- topic

Rules:

- Questions must test important concepts.
- Answers must be concise but educational.
- Match the requested difficulty.
- Match the requested study style.
- Do not invent facts.
- Use only information supported by the lecture.
- Make questions useful for exam preparation.

SUMMARY REQUIREMENTS

- Identify the central topic.
- Explain the most important concepts.
- Keep it easy to revise.
- Use short paragraphs or bullet-style writing.

LECTURE TRANSCRIPTION

{st.session_state.transcription}
"""

        study_schema = {
            "type": "object",
            "properties": {

                "summary": {
                    "type": "string"
                },

                "flashcards": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {

                            "question": {
                                "type": "string"
                            },

                            "answer": {
                                "type": "string"
                            },

                            "difficulty": {
                                "type": "string"
                            },

                            "topic": {
                                "type": "string"
                            }

                        },
                        "required": [
                            "question",
                            "answer",
                            "difficulty",
                            "topic"
                        ]
                    }
                }

            },

            "required": [
                "summary",
                "flashcards"
            ]
        }

        try:

            with st.spinner(
                "🧠 Gemini is creating your study material..."
            ):

                response = client.models.generate_content(
                    model=MODEL,
                    contents=study_prompt,
                    config=types.GenerateContentConfig(
                        response_mime_type="application/json",
                        response_schema=study_schema
                    )
                )

            study_material = response.parsed

            if study_material is None:

                import json

                study_material = json.loads(
                    response.text
                )

            st.session_state.summary = (
                study_material["summary"]
            )

            st.session_state.flashcards = (
                study_material["flashcards"]
            )

            for card in st.session_state.flashcards:

                card["reviewed"] = False

            st.session_state.quiz = None
            st.session_state.quiz_answers = {}
            st.session_state.quiz_score = None

            st.success(
                "✅ Study material generated!"
            )

        except Exception as e:

            st.error(
                f"Study material generation failed: {e}"
            )

# ============================================================
# SUMMARY
# ============================================================

if st.session_state.summary:

    st.divider()

    st.header("🧠 AI Study Summary")

    with st.expander(
        "📖 Open AI Summary",
        expanded=True
    ):

        st.write(
            st.session_state.summary
        )

# ============================================================
# FLASHCARDS
# ============================================================

if st.session_state.flashcards:

    st.divider()

    st.header("🃏 4. Flashcards")

    flashcard_df = pd.DataFrame(
        st.session_state.flashcards
    )

    edited_df = st.data_editor(
        flashcard_df,
        use_container_width=True,
        num_rows="dynamic",
        column_config={

            "reviewed":
                st.column_config.CheckboxColumn(
                    "Reviewed",
                    help="Mark this card as reviewed."
                ),

            "difficulty":
                st.column_config.TextColumn(
                    "Difficulty"
                ),

            "topic":
                st.column_config.TextColumn(
                    "Topic"
                )
        }
    )

    # --------------------------------------------------------
    # REVIEW PROGRESS
    # --------------------------------------------------------

    total_cards = len(
        edited_df
    )

    reviewed_cards = int(
        edited_df["reviewed"].sum()
    )

    progress = (
        reviewed_cards / total_cards
        if total_cards > 0
        else 0
    )

    progress1, progress2, progress3 = st.columns(3)

    with progress1:

        st.metric(
            "📚 Total Cards",
            total_cards
        )

    with progress2:

        st.metric(
            "✅ Reviewed",
            reviewed_cards,
            delta=f"{progress:.0%} complete"
        )

    with progress3:

        st.metric(
            "⏳ Remaining",
            total_cards - reviewed_cards
        )

    st.progress(
        progress
    )

    # --------------------------------------------------------
    # VISUAL STUDY CARDS
    # --------------------------------------------------------

    st.subheader(
        "📖 Interactive Study Cards"
    )

    for index, row in edited_df.iterrows():

        with st.expander(
            f"🃏 Card {index + 1}: "
            f"{row['question']}"
        ):

            st.markdown(
                "### Answer"
            )

            st.write(
                row["answer"]
            )

            st.caption(
                f"Topic: {row['topic']}  |  "
                f"Difficulty: {row['difficulty']}"
            )

            if row["reviewed"]:

                st.success(
                    "✅ Reviewed"
                )

            else:

                st.info(
                    "📚 Not reviewed yet"
                )

    # --------------------------------------------------------
    # DOWNLOAD
    # --------------------------------------------------------

    st.subheader(
        "📥 Export"
    )

    csv_data = edited_df.to_csv(
        index=False
    )

    st.download_button(
        label="📥 Download Flashcards as CSV",
        data=csv_data,
        file_name="voice_study_flashcards.csv",
        mime="text/csv"
    )

# ============================================================
# QUIZ SECTION
# ============================================================

if st.session_state.transcription:

    st.divider()

    st.header("❓ 5. AI Quiz")

    st.write(
        "Test your understanding using an AI-generated quiz."
    )

    if st.button(
        "🎯 Generate 5-Question Quiz",
        type="primary"
    ):

        quiz_prompt = f"""
You are an expert educational quiz creator.

Create exactly 5 multiple-choice questions from the
lecture transcription below.

Each question must contain:

- question
- options: exactly 4 options
- correct_answer
- explanation

The correct_answer must be the exact text of one
of the four options.

Rules:

- Questions must be based ONLY on the lecture.
- Do not invent information.
- Make the questions educational.
- Mix conceptual and factual questions.
- Difficulty should be medium.
- Avoid ambiguous questions.

LECTURE

{st.session_state.transcription}
"""

        quiz_schema = {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {

                    "question": {
                        "type": "string"
                    },

                    "options": {
                        "type": "array",
                        "items": {
                            "type": "string"
                        }
                    },

                    "correct_answer": {
                        "type": "string"
                    },

                    "explanation": {
                        "type": "string"
                    }

                },

                "required": [
                    "question",
                    "options",
                    "correct_answer",
                    "explanation"
                ]
            }
        }

        try:

            with st.spinner(
                "🧠 Creating your quiz..."
            ):

                quiz_response = client.models.generate_content(
                    model=MODEL,
                    contents=quiz_prompt,
                    config=types.GenerateContentConfig(
                        response_mime_type="application/json",
                        response_schema=quiz_schema
                    )
                )

            quiz_data = quiz_response.parsed

            if quiz_data is None:

                import json

                quiz_data = json.loads(
                    quiz_response.text
                )

            st.session_state.quiz = quiz_data

            st.session_state.quiz_answers = {}

            st.session_state.quiz_score = None

            st.success(
                "✅ Quiz generated!"
            )

        except Exception as e:

            st.error(
                f"Quiz generation failed: {e}"
            )

# ============================================================
# DISPLAY QUIZ
# ============================================================

if st.session_state.quiz:

    st.subheader(
        "📝 Take the Quiz"
    )

    with st.form("quiz_form"):

        for index, question in enumerate(
            st.session_state.quiz
        ):

            st.markdown(
                f"### Question {index + 1}"
            )

            st.write(
                question["question"]
            )

            answer = st.radio(
                "Choose your answer:",
                question["options"],
                key=f"quiz_{index}"
            )

            st.session_state.quiz_answers[index] = (
                answer
            )

            st.divider()

        submit_quiz = st.form_submit_button(
            "🎯 Submit Quiz"
        )

    if submit_quiz:

        score = 0

        for index, question in enumerate(
            st.session_state.quiz
        ):

            selected = (
                st.session_state.quiz_answers
                .get(index)
            )

            if selected == question[
                "correct_answer"
            ]:

                score += 1

        st.session_state.quiz_score = score

# ============================================================
# QUIZ RESULTS
# ============================================================

if st.session_state.quiz_score is not None:

    score = st.session_state.quiz_score

    total = len(
        st.session_state.quiz
    )

    percentage = (
        score / total
    ) * 100

    st.divider()

    st.header("🏆 Quiz Results")

    result1, result2, result3 = st.columns(3)

    with result1:

        st.metric(
            "🎯 Score",
            f"{score}/{total}"
        )

    with result2:

        st.metric(
            "📊 Percentage",
            f"{percentage:.0f}%"
        )

    with result3:

        if percentage >= 80:

            message = "Excellent!"

        elif percentage >= 60:

            message = "Good Job!"

        else:

            message = "Keep Practicing!"

        st.metric(
            "🏆 Performance",
            message
        )

    if percentage >= 80:

        st.success(
            "🔥 Excellent understanding!"
        )

    elif percentage >= 60:

        st.info(
            "👍 Good work! Review the missed concepts."
        )

    else:

        st.warning(
            "📚 Review your study material and try again."
        )

    st.subheader(
        "📖 Answer Explanations"
    )

    for index, question in enumerate(
        st.session_state.quiz
    ):

        selected = (
            st.session_state.quiz_answers
            .get(index)
        )

        with st.expander(
            f"Question {index + 1}"
        ):

            st.write(
                question["question"]
            )

            st.write(
                f"**Your answer:** {selected}"
            )

            st.write(
                f"**Correct answer:** "
                f"{question['correct_answer']}"
            )

            st.info(
                question["explanation"]
            )

# ============================================================
# FOOTER
# ============================================================

st.divider()

st.caption(
    "VoiceStudy AI • AI Summer Internship Capstone • "
    "Powered by Gemini and Streamlit"
)