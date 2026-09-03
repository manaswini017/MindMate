import streamlit as st
import random
import time
import pandas as pd
import plotly.express as px

from database import (
    create_tables,
    register_user,
    login_user,
    save_game_result,
    get_user_game_results,
    get_user_statistics,
    get_recent_game_results,
    get_game_average,
    get_latest_game_result,
    add_reminder,
    get_user_reminders,
    complete_reminder,
    delete_reminder,
    get_elderly_users,
    get_caregiver_statistics,
    get_caregiver_game_history
)


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="MINDMATE",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

create_tables()


# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown("""
<style>

.main {
    padding-top: 1rem;
}

.title {
    font-size: 44px;
    font-weight: bold;
    text-align: center;
}

.subtitle {
    font-size: 20px;
    text-align: center;
    margin: 10px auto 30px auto;
    max-width: 850px;
}

.card {
    padding: 25px;
    border-radius: 15px;
    border: 1px solid #dddddd;
    margin-bottom: 20px;
}

.game-card {
    padding: 20px;
    border-radius: 15px;
    border: 1px solid #dddddd;
    margin-bottom: 15px;
}

</style>
""", unsafe_allow_html=True)


# ============================================================
# SESSION STATE
# ============================================================

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "user_name" not in st.session_state:
    st.session_state.user_name = ""

if "user_role" not in st.session_state:
    st.session_state.user_role = "Elderly User"

if "user_id" not in st.session_state:
    st.session_state.user_id = None

if "language" not in st.session_state:
    st.session_state.language = "English"

if "number_sequence" not in st.session_state:
    st.session_state.number_sequence = None

if "number_start_time" not in st.session_state:
    st.session_state.number_start_time = None

if "show_number" not in st.session_state:
    st.session_state.show_number = False

if "assessment_completed" not in st.session_state:
    st.session_state.assessment_completed = False


# ============================================================
# ADAPTIVE DIFFICULTY
# ============================================================

def get_adaptive_difficulty(user_id):
    """
    Explainable adaptive logic:
    - No previous games -> Easy
    - Recent average accuracy < 60% -> Easy
    - 60% to 79.9% -> Medium
    - 80% or above -> Hard
    """
    recent_results = get_recent_game_results(user_id, 5)

    if not recent_results:
        return "Easy", 0.0

    average_accuracy = sum(
        float(result[3]) for result in recent_results
    ) / len(recent_results)

    if average_accuracy >= 80:
        return "Hard", average_accuracy
    elif average_accuracy >= 60:
        return "Medium", average_accuracy
    else:
        return "Easy", average_accuracy


# ============================================================
# LANGUAGE TEXT
# ============================================================

LANGUAGE_TEXT = {

    "English": {
        "welcome": "Welcome",
        "dashboard": "Dashboard",
        "games": "Cognitive Games",
        "reminders": "Memory Assistance",
        "progress": "My Progress",
        "recommendations": "AI Recommendations"
    },

    "Assamese": {
        "welcome": "স্বাগতম",
        "dashboard": "ড্যাশবোর্ড",
        "games": "জ্ঞানীয় খেলাসমূহ",
        "reminders": "স্মৃতি সহায়তা",
        "progress": "মোৰ অগ্ৰগতি",
        "recommendations": "AI পৰামৰ্শ"
    },

    "Bengali": {
        "welcome": "স্বাগতম",
        "dashboard": "ড্যাশবোর্ড",
        "games": "জ্ঞানীয় গেম",
        "reminders": "স্মৃতি সহায়তা",
        "progress": "আমার অগ্রগতি",
        "recommendations": "AI সুপারিশ"
    },

    "Manipuri": {
        "welcome": "স্বাগতম",
        "dashboard": "ড্যাশবোর্ড",
        "games": "Cognitive Games",
        "reminders": "Memory Assistance",
        "progress": "My Progress",
        "recommendations": "AI Recommendations"
    },

    "Khasi": {
        "welcome": "Pdiang sngewbha",
        "dashboard": "Dashboard",
        "games": "Cognitive Games",
        "reminders": "Memory Assistance",
        "progress": "My Progress",
        "recommendations": "AI Recommendations"
    },

    "Mizo": {
        "welcome": "Chibai",
        "dashboard": "Dashboard",
        "games": "Cognitive Games",
        "reminders": "Memory Assistance",
        "progress": "My Progress",
        "recommendations": "AI Recommendations"
    },

    "Hindi": {
        "welcome": "स्वागत है",
        "dashboard": "डैशबोर्ड",
        "games": "संज्ञानात्मक खेल",
        "reminders": "स्मृति सहायता",
        "progress": "मेरी प्रगति",
        "recommendations": "AI सुझाव"
    }
}


# ============================================================
# LOGIN / REGISTRATION SCREEN
# ============================================================

if not st.session_state.logged_in:

    st.markdown(
        """
        <div style="
            text-align:center;
            margin-top:-45px;
            margin-bottom:20px;
        ">
            <div style="
                font-size:42px;
                font-weight:bold;
                margin-bottom:6px;
            ">
                 MINDMATE
            </div>
            <div style="
                font-size:18px;
                font-weight:600;
                white-space:nowrap;
                margin-bottom:6px;
            ">
                AI-Powered Cognitive Gaming & Memory Assistance Platform
            </div>
            <div style="
                font-size:15px;
                margin-bottom:15px;
            ">
             Designed to support memory, attention and cognitive activities for elderly users.
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    # Keep the login/register area narrow and centered.
    left_space, center_area, right_space = st.columns([1, 1.2, 1])

    with center_area:

        st.info(
            "MindMate is a cognitive-support prototype and is "
            "not intended to diagnose or treat medical conditions."
        )

        tab1, tab2 = st.tabs([
            "Login",
            "Register"
        ])

    # ========================================================
    # LOGIN
    # ========================================================

    with tab1:

        st.subheader("Login")

        email = st.text_input(
            "Email",
            key="login_email"
        )

        password = st.text_input(
            "Password",
            type="password",
            key="login_password"
        )

        if st.button(
            "Login",
            use_container_width=True
        ):

            user = login_user(
                email.strip(),
                password
            )

            if user:

                st.session_state.logged_in = True
                st.session_state.user_id = user[0]
                st.session_state.user_name = user[1]
                st.session_state.user_role = user[3]
                st.session_state.language = user[4]

                st.success(
                    "Login successful!"
                )

                st.rerun()

            else:

                st.error(
                    "Invalid email or password."
                )


    # ========================================================
    # REGISTRATION
    # ========================================================

    with tab2:

        st.subheader("Create Account")

        name = st.text_input(
            "Full Name",
            key="register_name"
        )

        email = st.text_input(
            "Email",
            key="register_email"
        )

        password = st.text_input(
            "Password",
            type="password",
            key="register_password"
        )

        role = st.selectbox(
            "Register as",
            [
                "Elderly User",
                "Caregiver"
            ],
            key="register_role"
        )

        language = st.selectbox(
            "Preferred Language",
            [
                "English",
                "Assamese",
                "Bengali",
                "Manipuri",
                "Khasi",
                "Mizo",
                "Hindi"
            ],
            key="register_language"
        )

        if st.button(
            "Create Account",
            use_container_width=True
        ):

            if (
                name.strip() == ""
                or email.strip() == ""
                or password.strip() == ""
            ):

                st.error(
                    "Please fill in all fields."
                )

            elif len(password) < 6:

                st.error(
                    "Password must contain at least 6 characters."
                )

            else:

                success, message = register_user(
                    name.strip(),
                    email.strip(),
                    password,
                    role,
                    language
                )

                if success:

                    st.success(message)

                    st.info(
                        "You can now login using your email and password."
                    )

                else:

                    st.error(message)


# ============================================================
# MAIN APPLICATION
# ============================================================

else:

    language = st.session_state.language

    text = LANGUAGE_TEXT.get(
        language,
        LANGUAGE_TEXT["English"]
    )


    # ========================================================
    # SIDEBAR
    # ========================================================

    st.sidebar.title("MINDMATE")

    st.sidebar.write(
        f"**{text['welcome']}, "
        f"{st.session_state.user_name}**"
    )

    st.sidebar.write(
        f"Role: {st.session_state.user_role}"
    )

    st.sidebar.write(
        f"Language: {language}"
    )

    st.sidebar.divider()


    # ========================================================
    # NAVIGATION
    # ========================================================

    if st.session_state.user_role == "Elderly User":

        page = st.sidebar.radio(
            "Navigation",
            [
                "🏠 Dashboard",
                "🧠 Cognitive Assessment",
                "🎮 Cognitive Games",
                "🔔 Memory Assistance",
                "🤖 AI Recommendations",
                "📊 My Progress"
            ]
        )

    else:

        page = st.sidebar.radio(
            "Navigation",
            [
                "🏠 Dashboard",
                "👨‍⚕️ Caregiver Dashboard"
            ]
        )


    st.sidebar.divider()


    # ========================================================
    # LOGOUT
    # ========================================================

    if st.sidebar.button(
        "Logout",
        use_container_width=True
    ):

        st.session_state.logged_in = False
        st.session_state.user_id = None
        st.session_state.user_name = ""
        st.session_state.user_role = "Elderly User"

        st.rerun()


    # ========================================================
    # DASHBOARD
    # ========================================================

    if page == "🏠 Dashboard":

        st.title("🏠 Dashboard")

        st.subheader(
            f"{text['welcome']}, "
            f"{st.session_state.user_name}! 👋"
        )

        st.write(
            "Welcome to MindMate, your cognitive support platform."
        )

        stats = get_user_statistics(
            st.session_state.user_id
        )

        total_games = stats[0] or 0
        average_accuracy = stats[1] or 0

        reminders = get_user_reminders(
            st.session_state.user_id
        )

        pending_reminders = len([
            r for r in reminders
            if r[5] == 0
        ])

        current_level, _ = get_adaptive_difficulty(
            st.session_state.user_id
        )


        col1, col2, col3, col4 = st.columns(4)

        with col1:

            st.metric(
                "🎮 Games Completed",
                total_games
            )

        with col2:

            st.metric(
                "🎯 Average Accuracy",
                f"{average_accuracy:.1f}%"
            )

        with col3:

            st.metric(
                "🧠 Current Level",
                current_level
            )

        with col4:

            st.metric(
                "🔔 Pending Reminders",
                pending_reminders
            )


        st.divider()

        st.subheader(
            "🌟 MindMate Features"
        )

        col1, col2, col3 = st.columns(3)

        with col1:

            st.markdown("""
            ### 🧠 Cognitive Assessment

            Perform simple activities to establish
            an initial performance baseline.
            """)

        with col2:

            st.markdown("""
            ### 🎮 Cognitive Games

            Play memory, number, pattern and
            sequence-based activities.
            """)

        with col3:

            st.markdown("""
            ### 🔔 Memory Assistance

            Manage medicine, meal and
            appointment reminders.
            """)

        st.divider()

        st.success(
            "MindMate analyzes game performance to "
            "personalize future cognitive activities."
        )


    # ========================================================
    # COGNITIVE ASSESSMENT
    # ========================================================

    elif page == "🧠 Cognitive Assessment":

        st.title("🧠 Cognitive Assessment")

        st.write(
            "Complete this simple activity to establish "
            "your initial memory performance."
        )

        st.subheader(
            "🔢 Memory Test"
        )

        st.write(
            "Remember these numbers:"
        )

        st.info(
            "7   3   9   2   5"
        )

        answer = st.text_input(
            "Enter the numbers you remember",
            key="assessment_answer"
        )

        if st.button(
            "Submit Assessment",
            use_container_width=True
        ):

            cleaned_answer = (
                answer.replace(" ", "")
                .replace("-", "")
            )

            if cleaned_answer == "73925":

                st.success(
                    "🎉 Excellent! You remembered all the numbers."
                )

                st.session_state.assessment_completed = True

            else:

                st.warning(
                    "Good attempt! Your future activities "
                    "will adapt based on your performance."
                )

                st.session_state.assessment_completed = True

        if st.session_state.assessment_completed:

            st.divider()

            st.subheader(
                "📌 Assessment Status"
            )

            st.success(
                "Initial assessment completed."
            )

            st.write(
                "You can now start playing cognitive games."
            )


    # ========================================================
    # COGNITIVE GAMES
    # ========================================================

    elif page == "🎮 Cognitive Games":

        st.title("🎮 Cognitive Games")

        st.write(
            "Play engaging activities designed to exercise "
            "memory, attention and pattern recognition."
        )

        recommended_difficulty, recent_accuracy = get_adaptive_difficulty(
            st.session_state.user_id
        )

        st.success(
            f"🤖 Adaptive Difficulty: **{recommended_difficulty}**"
        )

        if recent_accuracy == 0:
            st.caption(
                "Your first game starts at Easy level. "
                "MindMate will adjust future difficulty based on your performance."
            )
        elif recommended_difficulty == "Hard":
            st.caption(
                f"Your recent average accuracy is {recent_accuracy:.1f}%. "
                "MindMate increased the challenge."
            )
        elif recommended_difficulty == "Medium":
            st.caption(
                f"Your recent average accuracy is {recent_accuracy:.1f}%. "
                "MindMate selected a moderate challenge."
            )
        else:
            st.caption(
                f"Your recent average accuracy is {recent_accuracy:.1f}%. "
                "MindMate selected an easier level for practice."
            )

        game = st.selectbox(
            "Select a game",
            [
                "Memory Matching",
                "Number Memory",
                "Pattern Recognition",
                "Sequence Recall"
            ]
        )


        # ====================================================
        # MEMORY MATCHING
        # ====================================================

        if game == "Memory Matching":

            st.header("🧠 Memory Matching")

            st.write(
                "Find matching pairs by remembering the position of each card."
            )

            difficulty = recommended_difficulty

            symbol_sets = {
                "Easy": ["🍎", "🐱", "⭐", "🌸"],
                "Medium": ["🍎", "🐱", "⭐", "🌸", "🚗", "🐶"],
                "Hard": ["🍎", "🐱", "⭐", "🌸", "🚗", "🐶", "🍕", "⚽"]
            }

            pair_symbols = symbol_sets[difficulty]

            # Create a shuffled board only when a new game is needed.
            if (
                "memory_cards" not in st.session_state
                or st.session_state.get("memory_game_difficulty") != difficulty
                or st.session_state.get("memory_game_user") != st.session_state.user_id
            ):
                cards = pair_symbols + pair_symbols
                random.shuffle(cards)

                st.session_state.memory_cards = cards
                st.session_state.memory_matched = []
                st.session_state.memory_revealed = []
                st.session_state.memory_attempts = 0
                st.session_state.memory_start_time = time.time()
                st.session_state.memory_mismatch = False
                st.session_state.memory_game_difficulty = difficulty
                st.session_state.memory_game_user = st.session_state.user_id
                st.session_state.memory_completed = False

            cards = st.session_state.memory_cards
            matched = st.session_state.memory_matched
            revealed = st.session_state.memory_revealed

            pairs = len(pair_symbols)

            st.info(
                f"Difficulty: **{difficulty}** | "
                f"Pairs to find: **{pairs}**"
            )

            if st.session_state.memory_completed:

                accuracy = st.session_state.memory_accuracy
                score = st.session_state.memory_score

                st.success("🎉 Excellent! You found all matching pairs.")

                col1, col2, col3 = st.columns(3)

                with col1:
                    st.metric("Score", score)

                with col2:
                    st.metric("Accuracy", f"{accuracy:.1f}%")

                with col3:
                    st.metric(
                        "Attempts",
                        st.session_state.memory_attempts
                    )

                if st.button(
                    "🔄 Play Again",
                    use_container_width=True,
                    key="memory_play_again"
                ):
                    for key in [
                        "memory_cards",
                        "memory_matched",
                        "memory_revealed",
                        "memory_attempts",
                        "memory_start_time",
                        "memory_mismatch",
                        "memory_game_difficulty",
                        "memory_completed",
                        "memory_accuracy",
                        "memory_score"
                    ]:
                        st.session_state.pop(key, None)
                    st.rerun()

            else:

                st.write("### Find the matching pairs")

                # Display cards in a compact grid.
                card_columns = 4

                for row_start in range(0, len(cards), card_columns):

                    row = st.columns(card_columns)

                    for offset, col in enumerate(row):
                        index = row_start + offset

                        if index >= len(cards):
                            continue

                        with col:

                            if (
                                index in matched
                                or index in revealed
                            ):
                                label = f"### {cards[index]}"
                            else:
                                label = "### ❓"

                            st.markdown(
                                f"""
                                <div style="
                                    text-align:center;
                                    font-size:34px;
                                    padding:14px;
                                    border:2px solid #cccccc;
                                    border-radius:16px;
                                    margin-bottom:6px;
                                ">
                                {label}
                                </div>
                                """,
                                unsafe_allow_html=True
                            )

                            if (
                                index not in matched
                                and index not in revealed
                                and not st.session_state.memory_mismatch
                            ):
                                if st.button(
                                    "Select",
                                    key=f"memory_card_{index}",
                                    use_container_width=True
                                ):
                                    st.session_state.memory_revealed.append(index)

                                    if len(st.session_state.memory_revealed) == 2:

                                        first, second = st.session_state.memory_revealed

                                        st.session_state.memory_attempts += 1

                                        if cards[first] == cards[second]:

                                            st.session_state.memory_matched.extend(
                                                [first, second]
                                            )
                                            st.session_state.memory_revealed = []

                                            if len(
                                                st.session_state.memory_matched
                                            ) == len(cards):

                                                attempts = st.session_state.memory_attempts
                                                pairs_found = len(cards) // 2

                                                accuracy = min(
                                                    100,
                                                    (pairs_found / attempts) * 100
                                                )

                                                score = int(accuracy)

                                                response_time = (
                                                    time.time()
                                                    - st.session_state.memory_start_time
                                                )

                                                save_game_result(
                                                    st.session_state.user_id,
                                                    "Memory Matching",
                                                    difficulty,
                                                    score,
                                                    accuracy,
                                                    attempts,
                                                    response_time
                                                )

                                                st.session_state.memory_accuracy = accuracy
                                                st.session_state.memory_score = score
                                                st.session_state.memory_completed = True

                                            st.rerun()

                                        else:
                                            st.session_state.memory_mismatch = True

                                    st.rerun()

                if st.session_state.memory_mismatch:

                    st.warning(
                        "Not a matching pair. Remember these two cards and try again."
                    )

                    if st.button(
                        "↩️ Continue",
                        use_container_width=True,
                        key="memory_continue"
                    ):
                        st.session_state.memory_revealed = []
                        st.session_state.memory_mismatch = False
                        st.rerun()


        # ====================================================
        # NUMBER MEMORY
        # ====================================================

        elif game == "Number Memory":

            st.header("🔢 Number Memory")

            st.write(
                "Remember the number sequence and enter it after hiding it."
            )

            difficulty = recommended_difficulty

            sequence_lengths = {
                "Easy": 4,
                "Medium": 6,
                "Hard": 8
            }

            sequence_length = sequence_lengths[difficulty]

            st.info(
                f"Adaptive Difficulty: **{difficulty}** | "
                f"Remember **{sequence_length} digits**."
            )

            if (
                st.session_state.number_sequence is None
                and not st.session_state.show_number
            ):
                if st.button(
                    "▶️ Start Number Memory",
                    use_container_width=True,
                    key="start_number_memory"
                ):

                    sequence = [
                        random.randint(0, 9)
                        for _ in range(sequence_length)
                    ]

                    st.session_state.number_sequence = sequence
                    st.session_state.number_start_time = time.time()
                    st.session_state.show_number = True

                    st.rerun()

            if (
                st.session_state.show_number
                and st.session_state.number_sequence
            ):

                number_display = "".join(
                    map(
                        str,
                        st.session_state.number_sequence
                    )
                )

                st.subheader(
                    "👀 Remember this number:"
                )

                st.markdown(
                    f"""
                    <div style="
                        font-size:40px;
                        font-weight:bold;
                        text-align:center;
                        padding:30px;
                        border:2px solid #ddd;
                        border-radius:15px;
                    ">
                    {number_display}
                    </div>
                    """,
                    unsafe_allow_html=True
                )

                st.warning(
                    "Try to memorize the number!"
                )

                if st.button(
                    "🙈 Hide Number",
                    use_container_width=True,
                    key="hide_number"
                ):

                    st.session_state.show_number = False
                    st.rerun()

            elif (
                st.session_state.number_sequence
                and not st.session_state.show_number
            ):

                st.subheader(
                    "✍️ Enter the number you remember"
                )

                user_answer = st.text_input(
                    "Your answer",
                    key="number_answer"
                )

                if st.button(
                    "Submit Answer",
                    use_container_width=True,
                    key="submit_number"
                ):

                    correct_answer = "".join(
                        map(
                            str,
                            st.session_state.number_sequence
                        )
                    )

                    response_time = (
                        time.time()
                        - st.session_state.number_start_time
                    )

                    cleaned_answer = "".join(
                        ch for ch in user_answer if ch.isdigit()
                    )

                    correct_digits = sum(
                        1
                        for i in range(
                            min(
                                len(cleaned_answer),
                                len(correct_answer)
                            )
                        )
                        if cleaned_answer[i] == correct_answer[i]
                    )

                    accuracy = (
                        correct_digits
                        / len(correct_answer)
                    ) * 100

                    score = int(accuracy)

                    if score == 100:
                        st.success(
                            "🎉 Excellent! Complete sequence remembered."
                        )
                    else:
                        st.warning(
                            f"Good attempt! The correct number was "
                            f"**{correct_answer}**."
                        )

                    save_game_result(
                        st.session_state.user_id,
                        "Number Memory",
                        difficulty,
                        score,
                        accuracy,
                        1,
                        response_time
                    )

                    col1, col2 = st.columns(2)

                    with col1:
                        st.metric("Score", score)

                    with col2:
                        st.metric(
                            "Accuracy",
                            f"{accuracy:.1f}%"
                        )

                    st.session_state.number_sequence = None
                    st.session_state.number_start_time = None
                    st.session_state.show_number = False
                    st.session_state.pop("number_answer", None)


        # ====================================================
        # PATTERN RECOGNITION
        # ====================================================

        elif game == "Pattern Recognition":

            st.header("🧩 Pattern Recognition")

            st.write(
                "Identify the missing value in the pattern. "
                "Choose the answer instead of typing."
            )

            difficulty = recommended_difficulty

            patterns = {
                "Easy": {
                    "sequence": "2 → 4 → 6 → 8 → ?",
                    "answer": 10,
                    "options": [8, 10, 12, 14]
                },
                "Medium": {
                    "sequence": "3 → 6 → 9 → 12 → ?",
                    "answer": 15,
                    "options": [13, 15, 18, 21]
                },
                "Hard": {
                    "sequence": "2 → 6 → 12 → 20 → ?",
                    "answer": 30,
                    "options": [24, 28, 30, 32]
                }
            }

            pattern = patterns[difficulty]

            st.info(
                f"Adaptive Difficulty: **{difficulty}**"
            )

            st.markdown(
                f"""
                <div style="
                    text-align:center;
                    font-size:30px;
                    font-weight:bold;
                    padding:25px;
                    border:2px solid #ddd;
                    border-radius:15px;
                ">
                {pattern["sequence"]}
                </div>
                """,
                unsafe_allow_html=True
            )

            answer = st.radio(
                "Choose the correct answer:",
                pattern["options"],
                horizontal=True,
                key=f"pattern_answer_{difficulty}"
            )

            if st.button(
                "✅ Submit Pattern",
                use_container_width=True,
                key="submit_pattern"
            ):

                if answer == pattern["answer"]:

                    score = 100
                    accuracy = 100.0

                    st.success(
                        "🎉 Correct! Excellent pattern recognition."
                    )

                else:

                    score = 0
                    accuracy = 0.0

                    st.warning(
                        f"Good attempt! The correct answer is "
                        f"**{pattern['answer']}**."
                    )

                save_game_result(
                    st.session_state.user_id,
                    "Pattern Recognition",
                    difficulty,
                    score,
                    accuracy,
                    1,
                    0
                )


        # ====================================================
        # SEQUENCE RECALL
        # ====================================================

        elif game == "Sequence Recall":

            st.header("🔄 Sequence Recall")

            st.write(
                "Remember the order of the colored circles. "
                "Then select them in the same order."
            )

            difficulty = recommended_difficulty

            sequence_lengths = {
                "Easy": 3,
                "Medium": 4,
                "Hard": 6
            }

            colors = [
                ("🔴", "Red"),
                ("🔵", "Blue"),
                ("🟢", "Green"),
                ("🟡", "Yellow"),
                ("🟣", "Purple"),
                ("🟠", "Orange")
            ]

            sequence_length = sequence_lengths[difficulty]

            # Generate a new sequence for a new round.
            if (
                "sequence_colors" not in st.session_state
                or st.session_state.get("sequence_game_difficulty") != difficulty
                or st.session_state.get("sequence_game_user") != st.session_state.user_id
            ):

                sequence = random.sample(
                    colors,
                    sequence_length
                )

                st.session_state.sequence_colors = sequence
                st.session_state.sequence_game_difficulty = difficulty
                st.session_state.sequence_game_user = st.session_state.user_id
                st.session_state.sequence_hidden = False
                st.session_state.sequence_selected = []
                st.session_state.sequence_start_time = None
                st.session_state.sequence_completed = False

            sequence = st.session_state.sequence_colors

            st.info(
                f"Adaptive Difficulty: **{difficulty}** | "
                f"Remember **{sequence_length} colors**."
            )

            if not st.session_state.sequence_hidden:

                st.subheader("👀 Remember this sequence:")

                cols = st.columns(sequence_length)

                for i, (icon, name) in enumerate(sequence):

                    with cols[i]:
                        st.markdown(
                            f"""
                            <div style="
                                text-align:center;
                                font-size:48px;
                                padding:15px;
                                border:2px solid #ddd;
                                border-radius:50%;
                                width:80px;
                                height:80px;
                                margin:auto;
                            ">
                            {icon}
                            </div>
                            <p style="text-align:center;"><b>{name}</b></p>
                            """,
                            unsafe_allow_html=True
                        )

                if st.button(
                    "🙈 Hide Sequence",
                    use_container_width=True,
                    key="hide_sequence"
                ):

                    st.session_state.sequence_hidden = True
                    st.session_state.sequence_selected = []
                    st.session_state.sequence_start_time = time.time()
                    st.rerun()

            else:

                st.subheader(
                    "🎯 Select the colors in the same order"
                )

                st.write(
                    "Selected:"
                )

                if st.session_state.sequence_selected:

                    selected_names = [
                        colors[index][1]
                        for index in st.session_state.sequence_selected
                    ]

                    st.info(
                        " → ".join(selected_names)
                    )
                else:
                    st.info("No color selected yet.")

                option_cols = st.columns(3)

                for index, (icon, name) in enumerate(colors):

                    with option_cols[index % 3]:

                        if st.button(
                            f"{icon}  {name}",
                            use_container_width=True,
                            key=f"sequence_option_{index}"
                        ):

                            if (
                                index not in st.session_state.sequence_selected
                                and len(st.session_state.sequence_selected) < sequence_length
                            ):

                                st.session_state.sequence_selected.append(index)
                                st.rerun()

                col1, col2 = st.columns(2)

                with col1:

                    if st.button(
                        "↩️ Clear Selection",
                        use_container_width=True,
                        key="clear_sequence_selection"
                    ):
                        st.session_state.sequence_selected = []
                        st.rerun()

                with col2:

                    if st.button(
                        "✅ Submit Sequence",
                        use_container_width=True,
                        key="submit_sequence"
                    ):

                        correct_indexes = [
                            colors.index(item)
                            for item in sequence
                        ]

                        selected = st.session_state.sequence_selected

                        correct_positions = sum(
                            1
                            for i in range(
                                min(
                                    len(selected),
                                    len(correct_indexes)
                                )
                            )
                            if selected[i] == correct_indexes[i]
                        )

                        accuracy = (
                            correct_positions
                            / len(correct_indexes)
                        ) * 100

                        score = int(accuracy)

                        response_time = (
                            time.time()
                            - st.session_state.sequence_start_time
                        )

                        if selected == correct_indexes:

                            st.success(
                                "🎉 Perfect! You remembered the complete sequence."
                            )

                        else:

                            st.warning(
                                "Good attempt! The correct order was: "
                                + " → ".join(
                                    item[1]
                                    for item in sequence
                                )
                            )

                        save_game_result(
                            st.session_state.user_id,
                            "Sequence Recall",
                            difficulty,
                            score,
                            accuracy,
                            1,
                            response_time
                        )

                        st.metric(
                            "Accuracy",
                            f"{accuracy:.1f}%"
                        )

                        st.session_state.sequence_completed = True

                        if st.button(
                            "🔄 New Sequence",
                            use_container_width=True,
                            key="new_sequence"
                        ):
                            for key in [
                                "sequence_colors",
                                "sequence_game_difficulty",
                                "sequence_game_user",
                                "sequence_hidden",
                                "sequence_selected",
                                "sequence_start_time",
                                "sequence_completed"
                            ]:
                                st.session_state.pop(key, None)
                            st.rerun()


    # ========================================================
    # MEMORY ASSISTANCE
    # ========================================================

    elif page == "🔔 Memory Assistance":

        st.title("🔔 Memory Assistance")

        st.write(
            "Create and manage important daily reminders."
        )

        reminder_type = st.selectbox(
            "Reminder Type",
            [
                "💊 Medicine",
                "🍽️ Meal",
                "🏥 Appointment",
                "📌 Other"
            ],
            key="reminder_type"
        )

        reminder = st.text_input(
            "Reminder description",
            key="reminder_description"
        )

        reminder_date = st.date_input(
            "Reminder date",
            key="reminder_date"
        )

        reminder_time = st.time_input(
            "Reminder time",
            key="reminder_time"
        )

        if st.button(
            "➕ Add Reminder",
            use_container_width=True,
            key="add_reminder_button"
        ):

            if reminder.strip() == "":

                st.error(
                    "Please enter a reminder description."
                )

            else:

                add_reminder(
                    st.session_state.user_id,
                    reminder_type,
                    reminder.strip(),
                    str(reminder_time),
                    str(reminder_date)
                )

                st.success(
                    "🔔 Reminder saved successfully!"
                )

                st.rerun()


        st.divider()

        st.subheader(
            "📋 My Reminders"
        )

        reminders = get_user_reminders(
            st.session_state.user_id
        )

        if reminders:

            for reminder_data in reminders:

                reminder_id = reminder_data[0]
                reminder_type = reminder_data[1]
                description = reminder_data[2]
                reminder_time_value = reminder_data[3]
                reminder_date_value = reminder_data[4]
                completed = reminder_data[5]

                with st.container(border=True):

                    col1, col2, col3 = st.columns([3, 2, 1])

                    with col1:

                        st.write(
                            f"### {reminder_type}"
                        )

                        st.write(
                            description
                        )

                    with col2:

                        st.write(
                            f"📅 {reminder_date_value}"
                        )

                        st.write(
                            f"⏰ {reminder_time_value}"
                        )

                    with col3:

                        if completed == 1:

                            st.success(
                                "Completed"
                            )

                        else:

                            if st.button(
                                "✓ Complete",
                                key=f"complete_{reminder_id}"
                            ):

                                complete_reminder(
                                    reminder_id
                                )

                                st.rerun()

                            if st.button(
                                "🗑️ Delete",
                                key=f"delete_{reminder_id}"
                            ):

                                delete_reminder(
                                    reminder_id
                                )

                                st.rerun()

        else:

            st.info(
                "No reminders added yet."
            )


    # ========================================================
    # AI RECOMMENDATIONS
    # ========================================================

    elif page == "🤖 AI Recommendations":

        st.title("🤖 AI Recommendations")

        st.write(
            "MindMate analyzes your game performance "
            "and recommends suitable difficulty levels."
        )

        stats = get_user_statistics(
            st.session_state.user_id
        )

        total_games = stats[0] or 0
        average_accuracy = stats[1] or 0

        recommended_difficulty, recent_accuracy = get_adaptive_difficulty(
            st.session_state.user_id
        )

        if total_games == 0:

            st.info(
                "🎮 Play at least one cognitive game "
                "to receive a personalized recommendation."
            )


        st.subheader(
            "🎯 Recommended Difficulty"
        )

        if recommended_difficulty == "Hard":

            st.success(
                "🔥 Recommended Difficulty: HARD"
            )

            st.write(
                "Your current performance is strong. "
                "You can try more challenging activities."
            )

        elif recommended_difficulty == "Medium":

            st.warning(
                "⭐ Recommended Difficulty: MEDIUM"
            )

            st.write(
                "Your performance is developing well. "
                "A moderate challenge is recommended."
            )

        else:

            st.info(
                "🌱 Recommended Difficulty: EASY"
            )

            st.write(
                "Start with simpler activities and "
                "gradually build confidence."
            )


        st.divider()

        st.subheader(
            "📊 Performance Summary"
        )

        col1, col2 = st.columns(2)

        with col1:

            st.metric(
                "Games Completed",
                total_games
            )

        with col2:

            st.metric(
                "Average Accuracy",
                f"{average_accuracy:.1f}%"
            )


        st.divider()

        st.subheader(
            "🧠 Adaptive Learning"
        )

        st.write(
            "MindMate automatically selects Easy, Medium or Hard "
            "for your cognitive games using your recent performance. "
            "This is an explainable rule-based adaptive AI prototype."
        )

        recent_results = get_recent_game_results(
            st.session_state.user_id,
            5
        )

        if recent_results:

            st.write(
                "### Recent Performance"
            )

            for result in recent_results:

                st.write(
                    f"🎮 **{result[0]}** — "
                    f"{result[3]:.1f}% accuracy — "
                    f"{result[1]}"
                )


    # ========================================================
    # MY PROGRESS
    # ========================================================

    elif page == "📊 My Progress":

        st.title("📊 My Progress")

        stats = get_user_statistics(
            st.session_state.user_id
        )

        total_games = stats[0] or 0
        average_accuracy = stats[1] or 0
        average_score = stats[2] or 0

        col1, col2, col3 = st.columns(3)

        with col1:

            st.metric(
                "🎮 Games Completed",
                total_games
            )

        with col2:

            st.metric(
                "🎯 Average Accuracy",
                f"{average_accuracy:.1f}%"
            )

        with col3:

            st.metric(
                "⭐ Average Score",
                f"{average_score:.1f}"
            )


        st.divider()

        results = get_user_game_results(
            st.session_state.user_id
        )

        if results:

            st.subheader(
                "📈 Performance Overview"
            )

            chart_data = []

            for result in results:

                chart_data.append({
                    "Game": result[0],
                    "Accuracy": result[3],
                    "Score": result[2],
                    "Difficulty": result[1],
                    "Date": result[6]
                })

            df = pd.DataFrame(
                chart_data
            )

            fig = px.bar(
                df,
                x="Game",
                y="Accuracy",
                title="Accuracy by Game",
                text="Accuracy"
            )

            fig.update_layout(
                yaxis_title="Accuracy (%)",
                xaxis_title="Game"
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )


            st.divider()

            st.subheader(
                "📋 Game History"
            )

            for result in results:

                game_name = result[0]
                difficulty = result[1]
                score = result[2]
                accuracy = result[3]
                attempts = result[4]
                response_time = result[5]
                played_at = result[6]

                with st.container(border=True):

                    col1, col2, col3 = st.columns(3)

                    with col1:

                        st.write(
                            f"### 🎮 {game_name}"
                        )

                        st.write(
                            f"Difficulty: **{difficulty}**"
                        )

                    with col2:

                        st.metric(
                            "Score",
                            score
                        )

                        st.metric(
                            "Accuracy",
                            f"{accuracy:.1f}%"
                        )

                    with col3:

                        st.write(
                            f"Attempts: **{attempts}**"
                        )

                        st.write(
                            f"Response Time: "
                            f"**{response_time:.1f}s**"
                        )

                        st.caption(
                            f"Played: {played_at}"
                        )

        else:

            st.info(
                "No games completed yet. "
                "Play a cognitive game to see your progress here."
            )


    # ========================================================
    # CAREGIVER DASHBOARD
    # ========================================================

    elif page == "👨‍⚕️ Caregiver Dashboard":

        st.title(
            "👨‍⚕️ Caregiver Dashboard"
        )

        st.write(
            "Monitor cognitive activities and "
            "performance of elderly users."
        )

        elderly_users = get_elderly_users()

        if not elderly_users:

            st.info(
                "No elderly users have registered yet."
            )

        else:

            user_options = {
                f"{user[1]} ({user[2]})": user[0]
                for user in elderly_users
            }

            selected_user_label = st.selectbox(
                "Select Elderly User",
                list(user_options.keys())
            )

            selected_user_id = user_options[
                selected_user_label
            ]

            selected_user = next(
                user for user in elderly_users
                if user[0] == selected_user_id
            )

            st.divider()

            st.subheader(
                f"👤 {selected_user[1]}"
            )

            st.write(
                f"Email: {selected_user[2]}"
            )

            st.write(
                f"Preferred Language: {selected_user[3]}"
            )


            caregiver_stats = get_caregiver_statistics(
                selected_user_id
            )

            total_games = caregiver_stats[0] or 0
            average_score = caregiver_stats[1] or 0
            average_accuracy = caregiver_stats[2] or 0
            average_response_time = caregiver_stats[3] or 0


            col1, col2, col3, col4 = st.columns(4)

            with col1:

                st.metric(
                    "🎮 Games",
                    total_games
                )

            with col2:

                st.metric(
                    "⭐ Avg Score",
                    f"{average_score:.1f}"
                )

            with col3:

                st.metric(
                    "🎯 Avg Accuracy",
                    f"{average_accuracy:.1f}%"
                )

            with col4:

                st.metric(
                    "⏱️ Avg Response",
                    f"{average_response_time:.1f}s"
                )


            st.divider()

            history = get_caregiver_game_history(
                selected_user_id
            )

            if history:

                st.subheader(
                    "📈 Performance Report"
                )

                chart_data = []

                for result in history:

                    chart_data.append({
                        "Game": result[0],
                        "Accuracy": result[3],
                        "Score": result[2],
                        "Difficulty": result[1],
                        "Date": result[6]
                    })

                df = pd.DataFrame(
                    chart_data
                )

                fig = px.line(
                    df,
                    x="Date",
                    y="Accuracy",
                    markers=True,
                    title="Accuracy Trend"
                )

                fig.update_layout(
                    yaxis_title="Accuracy (%)",
                    xaxis_title="Date"
                )

                st.plotly_chart(
                    fig,
                    use_container_width=True
                )


                st.subheader(
                    "📋 Game History"
                )

                history_df = pd.DataFrame(
                    history,
                    columns=[
                        "Game",
                        "Difficulty",
                        "Score",
                        "Accuracy",
                        "Attempts",
                        "Response Time",
                        "Played At"
                    ]
                )

                st.dataframe(
                    history_df,
                    use_container_width=True,
                    hide_index=True
                )

            else:

                st.info(
                    "This user has not completed any games yet."
                )

            st.divider()

            st.subheader(
                "🔔 Caregiver Note"
            )

            st.info(
                "This dashboard is intended for monitoring "
                "activity and engagement. It should not be used "
                "as a medical diagnosis."
            )