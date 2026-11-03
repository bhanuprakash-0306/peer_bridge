import sqlite3
from datetime import datetime
import pandas as pd
import streamlit as st
import database


# =========================================================
# 1. PAGE CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="PeerBridge | Student Skill Exchange",
    page_icon="🤝",
    layout="wide",
    initial_sidebar_state="expanded",
)


# =========================================================
# 2. DARK THEME
# =========================================================

st.markdown("""
<style>
.stApp {
    background: #0b1120;
    color: #e5eaf5;
}

.block-container {
    max-width: 1500px;
    padding-top: 1.1rem;
    padding-bottom: 1rem;
    padding-left: 2rem;
    padding-right: 2rem;
}

div[data-testid="stVerticalBlock"] {
    gap: 0.75rem;
}

h1, h2, h3, h4 {
    color: #f1f5ff !important;
}

p, label, span, li {
    color: #cbd5e1;
}

section[data-testid="stSidebar"] {
    background: #101a2d;
    border-right: 1px solid #24334d;
}

section[data-testid="stSidebar"] h1,
section[data-testid="stSidebar"] h2,
section[data-testid="stSidebar"] h3 {
    color: #f1f5ff !important;
}

.hero {
    background: linear-gradient(115deg, #142b50, #173c65 55%, #164e63);
    border: 1px solid #28547a;
    border-radius: 15px;
    padding: 22px 26px;
    margin-bottom: 8px;
}

.hero h1 {
    font-size: 2rem;
    font-weight: 800;
    color: white !important;
    margin: 0 0 5px 0;
}

.hero p {
    color: #c6dcf5 !important;
    margin: 0;
}

div[data-testid="stMetric"] {
    background: linear-gradient(145deg, #17243a, #111c30);
    border: 1px solid #2b405f;
    border-radius: 12px;
    padding: 13px 16px;
    min-height: 100px;
}

div[data-testid="stMetricLabel"] {
    color: #a9bdd8 !important;
}

div[data-testid="stMetricValue"] {
    color: #f8fbff !important;
    font-size: 1.8rem;
    font-weight: 750;
}

.info-card {
    background: #131f33;
    border: 1px solid #2a3c58;
    border-radius: 12px;
    padding: 15px 17px;
    min-height: 105px;
}

.info-card h4 {
    color: #9db5d4 !important;
    font-size: 0.8rem;
    margin: 0 0 9px 0;
}

.info-card .value {
    color: #f3f7ff;
    font-size: 1.45rem;
    font-weight: 750;
}

.info-card .sub {
    color: #91a6c2;
    font-size: 0.78rem;
    margin-top: 4px;
}

.section-heading {
    color: #eaf2ff;
    font-size: 1.08rem;
    font-weight: 700;
    padding-bottom: 7px;
    border-bottom: 1px solid #263750;
    margin-top: 8px;
    margin-bottom: 5px;
}

.stButton > button,
.stDownloadButton > button {
    background: #1d5c91;
    color: white !important;
    border: 1px solid #3479b3;
    border-radius: 8px;
    min-height: 39px;
    font-weight: 650;
}

.stButton > button:hover,
.stDownloadButton > button:hover {
    background: #2876b4;
    border-color: #60a5fa;
}

.stTextInput input,
.stTextArea textarea,
.stNumberInput input,
.stDateInput input,
.stTimeInput input {
    background: #111d31 !important;
    color: #f1f5f9 !important;
    border: 1px solid #344967 !important;
    border-radius: 8px !important;
}

div[data-baseweb="select"] > div {
    background: #111d31 !important;
    border-color: #344967 !important;
    color: #f1f5f9 !important;
}

div[data-baseweb="select"] span {
    color: #f1f5f9 !important;
}

.stTabs [data-baseweb="tab-list"] {
    gap: 5px;
    border-bottom: 1px solid #2b3c56;
}

.stTabs [data-baseweb="tab"] {
    background: transparent;
    color: #a9bdd8;
    border-radius: 7px 7px 0 0;
    padding: 8px 14px;
}

.stTabs [aria-selected="true"] {
    color: white !important;
    border-bottom: 2px solid #38bdf8;
}

div[data-testid="stDataFrame"],
div[data-testid="stTable"] {
    border: 1px solid #2b3c56;
    border-radius: 9px;
    overflow: hidden;
}

div[data-testid="stForm"],
div[data-testid="stExpander"] {
    background: #111c2e;
    border: 1px solid #293d59;
    border-radius: 10px;
}

hr {
    border-color: #263750;
    margin: 0.5rem 0;
}

footer {
    visibility: hidden;
}
</style>
""", unsafe_allow_html=True)


# =========================================================
# 3. HELPER FUNCTIONS
# =========================================================

def section(title):
    st.markdown(
        f'<div class="section-heading">{title}</div>',
        unsafe_allow_html=True,
    )


def make_card(title, value, subtitle):
    st.markdown(
        f"""
        <div class="info-card">
            <h4>{title}</h4>
            <div class="value">{value}</div>
            <div class="sub">{subtitle}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def show_table(data, columns):
    if data:
        df = pd.DataFrame(data, columns=columns)
        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True,
            height=min(380, 45 + len(df) * 35),
        )
    else:
        st.info("No records available yet.")


def safe_action(function, *args):
    """Run a database action and report its real success or failure."""
    try:
        result = function(*args)

        # Some database functions return (success, message).
        if isinstance(result, tuple) and len(result) == 2:
            success, message = result
            if success:
                st.success(message)
                return True

            st.error(message)
            return False

        # Other create functions return None after a successful insert.
        st.success("Operation completed successfully.")
        return True

    except (sqlite3.Error, ValueError, TypeError) as error:
        st.error(f"Database error: {error}")
        return False


def go_to_page(target):
    """Callback used by dashboard quick-action buttons."""
    st.session_state["navigation"] = target


def refresh_application():
    """Clear Streamlit caches and display a refresh confirmation."""
    st.cache_data.clear()
    st.cache_resource.clear()
    st.session_state["refresh_notice"] = True


# =========================================================
# 4. DATABASE INITIALIZATION
# =========================================================

try:
    database.init_db()
except sqlite3.Error as error:
    st.error(f"Database initialization failed: {error}")
    st.stop()


# =========================================================
# 5. SIDEBAR
# =========================================================

PAGES = [
    "Dashboard",
    "Find a Match",
    "Students",
    "Skills",
    "Requests",
    "Sessions",
    "Reviews",
    "Database Explorer",
]

if "navigation" not in st.session_state:
    st.session_state["navigation"] = "Dashboard"

if st.session_state["navigation"] not in PAGES:
    st.session_state["navigation"] = "Dashboard"

with st.sidebar:

    st.markdown("## 🤝 PeerBridge")
    st.caption("Student Skill Exchange Platform")
    st.divider()

    st.radio(
        "NAVIGATION",
        PAGES,
        key="navigation",
        label_visibility="visible",
    )

    st.divider()

    st.markdown("**PLATFORM STATUS**")
    st.markdown("🟢 Database connected")
    st.caption("Peer learning • Skill sharing • Collaboration")

    st.button(
        "↻ Refresh application",
        use_container_width=True,
        on_click=refresh_application,
    )

if st.session_state.pop("refresh_notice", False):
    st.success("Application refreshed successfully.")


page = st.session_state["navigation"]


# =========================================================
# 6. DASHBOARD
# =========================================================

if page == "Dashboard":

    students = database.get_students()
    skills = database.get_skills()
    requests = database.get_requests()
    sessions = database.get_sessions()
    reviews = database.get_reviews()

    open_requests = sum(
        1 for row in requests if str(row[4]).lower() == "open"
    )

    scheduled_sessions = sum(
        1 for row in sessions if str(row[5]).lower() == "scheduled"
    )

    st.markdown("""
    <div class="hero">
        <h1>🤝 PeerBridge Dashboard</h1>
        <p>Connect with students, exchange skills, and grow together.</p>
    </div>
    """, unsafe_allow_html=True)

    section("PLATFORM OVERVIEW")

    c1, c2, c3, c4, c5 = st.columns(5, gap="small")

    with c1:
        st.metric("👨‍🎓 Students", len(students))
    with c2:
        st.metric("💡 Skills", len(skills))
    with c3:
        st.metric("📨 Requests", len(requests))
    with c4:
        st.metric("📅 Sessions", len(sessions))
    with c5:
        st.metric("⭐ Reviews", len(reviews))

    st.markdown("")

    c1, c2, c3 = st.columns(3, gap="small")

    with c1:
        make_card("OPEN REQUESTS", open_requests, "Waiting for a student match")
    with c2:
        make_card(
            "SCHEDULED SESSIONS",
            scheduled_sessions,
            "Learning sessions planned",
        )
    with c3:
        make_card(
            "PLATFORM ACTIVITY",
            len(students) + len(skills) + len(requests),
            "Students, skills and requests",
        )

    st.markdown("")

    left, right = st.columns([1.15, 1], gap="medium")

    with left:
        section("👨‍🎓 RECENT STUDENTS")
        show_table(
            students[:6],
            ["ID", "Student Name", "Email", "Department", "Year"],
        )

    with right:
        section("📅 RECENT SESSIONS")
        show_table(
            sessions[:6],
            ["ID", "Learner", "Tutor", "Topic", "Session Time", "Status"],
        )

    section("⚡ QUICK ACTIONS")

    q1, q2, q3, q4 = st.columns(4, gap="small")

    with q1:
        st.button(
            "➕ Add Student",
            use_container_width=True,
            on_click=go_to_page,
            args=("Students",),
        )

    with q2:
        st.button(
            "💡 Add Skill",
            use_container_width=True,
            on_click=go_to_page,
            args=("Skills",),
        )

    with q3:
        st.button(
            "📨 New Request",
            use_container_width=True,
            on_click=go_to_page,
            args=("Requests",),
        )

    with q4:
        st.button(
            "🔍 Find Match",
            use_container_width=True,
            on_click=go_to_page,
            args=("Find a Match",),
        )


# =========================================================
# 7. FIND A MATCH
# =========================================================

elif page == "Find a Match":

    st.title("🔍 Find a Skill Match")
    st.caption("Discover students who can teach the skills you want to learn.")

    students = database.get_students()

    if not students:
        st.info("Register students and add their skills to start matching.")
    else:
        with st.form("match_form"):
            topic = st.text_input(
                "Skill you want to learn",
                placeholder="Example: Python",
            )
            offer = st.text_input(
                "Skill you can offer in exchange (optional)",
                placeholder="Example: Graphic Design",
            )
            submitted = st.form_submit_button(
                "🔍 Find Matching Students",
                type="primary",
                use_container_width=True,
            )

        if submitted:
            if not topic.strip():
                st.warning("Please enter a skill you want to learn.")
            else:
                matches = database.find_matches(topic, offer)

                section("MATCH RESULTS")

                if matches:
                    st.success(f"{len(matches)} possible match(es) found.")
                    show_table(
                        matches,
                        [
                            "Student ID",
                            "Student Name",
                            "Department",
                            "Can Teach",
                            "Wants to Learn",
                        ],
                    )
                else:
                    st.info("No matching students found. Try another skill.")


# =========================================================
# 8. STUDENTS — CREATE AND READ
# =========================================================

elif page == "Students":

    st.title("👨‍🎓 Student Management")
    st.caption("Register students and view the student directory.")

    tab1, tab2 = st.tabs(["➕ Add Student", "📋 Student Directory"])

    with tab1:
        with st.form("student_form", clear_on_submit=True):

            name = st.text_input("Full Name")
            email = st.text_input("Email Address")
            department = st.text_input("Department")

            year = st.selectbox(
                "Academic Year",
                ["1st Year", "2nd Year", "3rd Year", "4th Year", "Other"],
            )

            submitted = st.form_submit_button(
                "Register Student",
                type="primary",
                use_container_width=True,
            )

        if submitted:
            if not name.strip() or not department.strip():
                st.warning("Name and department are required.")
            else:
                safe_action(
                    database.add_student,
                    name.strip(),
                    email.strip(),
                    department.strip(),
                    year,
                )

    with tab2:
        students = database.get_students()
        section("REGISTERED STUDENTS")
        st.caption(f"Total registered students: {len(students)}")

        show_table(
            students,
            ["ID", "Name", "Email", "Department", "Year"],
        )


# =========================================================
# 9. SKILLS — CREATE AND READ
# =========================================================

elif page == "Skills":

    st.title("💡 Skill Management")
    st.caption("Add skills students can teach or want to learn.")

    students = database.get_students()

    tab1, tab2 = st.tabs(["➕ Add Skill", "📋 Available Skills"])

    with tab1:

        if not students:
            st.warning("Please register a student before adding a skill.")
        else:
            student_options = {
                f"{s[1]} — {s[3]} (ID: {s[0]})": s[0]
                for s in students
            }

            with st.form("skill_form", clear_on_submit=True):

                selected_student = st.selectbox(
                    "Select Student",
                    list(student_options.keys()),
                )

                skill_name = st.text_input("Skill Name")

                skill_type = st.selectbox(
                    "Skill Type",
                    ["Can teach", "Wants to learn"],
                )

                level = st.selectbox(
                    "Skill Level",
                    ["Beginner", "Intermediate", "Advanced"],
                )

                submitted = st.form_submit_button(
                    "Add Skill",
                    type="primary",
                    use_container_width=True,
                )

            if submitted:
                if not skill_name.strip():
                    st.warning("Please enter a skill name.")
                else:
                    safe_action(
                        database.add_skill,
                        student_options[selected_student],
                        skill_name.strip(),
                        skill_type,
                        level,
                    )

    with tab2:
        skills = database.get_skills()
        section("SKILL DIRECTORY")
        st.caption(f"Total skills listed: {len(skills)}")

        show_table(
            skills,
            ["Skill ID", "Student", "Skill", "Skill Type", "Level"],
        )


# =========================================================
# 10. REQUESTS — CREATE AND READ
# =========================================================

elif page == "Requests":

    st.title("📨 Skill Exchange Requests")
    st.caption("Create and view student learning requests.")

    students = database.get_students()

    tab1, tab2 = st.tabs(["➕ Create Request", "📋 All Requests"])

    with tab1:

        if not students:
            st.warning("Register a student before creating a request.")
        else:
            student_options = {
                f"{s[1]} — {s[3]} (ID: {s[0]})": s[0]
                for s in students
            }

            with st.form("request_form", clear_on_submit=True):

                selected_student = st.selectbox(
                    "Student",
                    list(student_options.keys()),
                )

                requested_skill = st.text_input("Skill to Learn")
                offer_skill = st.text_input("Skill to Offer")
                details = st.text_area("Additional Details", height=90)

                submitted = st.form_submit_button(
                    "Submit Request",
                    type="primary",
                    use_container_width=True,
                )

            if submitted:
                if not requested_skill.strip():
                    st.warning("Please enter the skill you want to learn.")
                else:
                    safe_action(
                        database.create_request,
                        student_options[selected_student],
                        requested_skill.strip(),
                        offer_skill.strip(),
                        details.strip(),
                    )

    with tab2:
        requests = database.get_requests()
        section("ALL REQUESTS")
        st.caption(f"Total requests: {len(requests)}")

        show_table(
            requests,
            [
                "Request ID",
                "Student",
                "Requested Skill",
                "Offer / Details",
                "Status",
                "Created At",
            ],
        )


# =========================================================
# 11. SESSIONS — CREATE AND READ
# =========================================================

elif page == "Sessions":

    st.title("📅 Learning Sessions")
    st.caption("Schedule peer-to-peer learning sessions.")

    students = database.get_students()

    tab1, tab2 = st.tabs(["➕ Schedule Session", "📋 All Sessions"])

    with tab1:

        if len(students) < 2:
            st.warning("At least two registered students are needed.")
        else:
            student_options = {
                f"{s[1]} — {s[3]} (ID: {s[0]})": s[0]
                for s in students
            }

            with st.form("session_form", clear_on_submit=True):

                learner_name = st.selectbox(
                    "Select Learner",
                    list(student_options.keys()),
                )

                tutor_name = st.selectbox(
                    "Select Tutor",
                    list(student_options.keys()),
                )

                topic = st.text_input("Session Topic")
                session_date = st.date_input("Session Date")
                session_time = st.time_input("Session Time")

                submitted = st.form_submit_button(
                    "Schedule Session",
                    type="primary",
                    use_container_width=True,
                )

            if submitted:
                learner_id = student_options[learner_name]
                tutor_id = student_options[tutor_name]

                if learner_id == tutor_id:
                    st.warning("Learner and tutor must be different students.")
                elif not topic.strip():
                    st.warning("Please enter a session topic.")
                else:
                    session_datetime = datetime.combine(
                        session_date,
                        session_time,
                    ).strftime("%Y-%m-%d %H:%M")

                    safe_action(
                        database.create_session,
                        learner_id,
                        tutor_id,
                        topic.strip(),
                        session_datetime,
                    )

    with tab2:
        sessions = database.get_sessions()
        section("SCHEDULED SESSIONS")
        st.caption(f"Total sessions: {len(sessions)}")

        show_table(
            sessions,
            [
                "Session ID",
                "Learner",
                "Tutor",
                "Topic",
                "Session Time",
                "Status",
            ],
        )


# =========================================================
# 12. REVIEWS — CREATE AND READ
# =========================================================

elif page == "Reviews":

    st.title("⭐ Student Reviews")
    st.caption("Share feedback about completed learning sessions.")

    sessions = database.get_sessions()

    tab1, tab2 = st.tabs(["➕ Add Review", "📋 Review Directory"])

    with tab1:

        if not sessions:
            st.info("No sessions are available for review yet.")
        else:
            session_options = {
                f"{s[3]} — {s[1]} with {s[2]} (ID: {s[0]})": s[0]
                for s in sessions
            }

            with st.form("review_form", clear_on_submit=True):

                selected_session = st.selectbox(
                    "Select Session",
                    list(session_options.keys()),
                )

                rating = st.select_slider(
                    "Rating",
                    options=[1, 2, 3, 4, 5],
                    value=5,
                )

                comment = st.text_area("Your Feedback", height=100)

                submitted = st.form_submit_button(
                    "Submit Review",
                    type="primary",
                    use_container_width=True,
                )

            if submitted:
                safe_action(
                    database.add_review,
                    session_options[selected_session],
                    rating,
                    comment.strip(),
                )

    with tab2:
        reviews = database.get_reviews()
        section("STUDENT FEEDBACK")
        st.caption(f"Total reviews: {len(reviews)}")

        show_table(
            reviews,
            ["Review ID", "Session Topic", "Rating", "Comment"],
        )


# =========================================================
# 13. DATABASE EXPLORER — FULL CRUD MANAGEMENT
# =========================================================

elif page == "Database Explorer":

    st.title("🗄️ Database Explorer")
    st.caption(
        "Browse, edit and delete records from the PeerBridge database."
    )

    try:
        table_names = database.get_table_names()
        table_counts = database.get_table_counts()

        total_records = (
            sum(table_counts.values())
            if isinstance(table_counts, dict)
            else 0
        )

        section("DATABASE OVERVIEW")

        c1, c2 = st.columns(2)

        with c1:
            st.metric("Database Tables", len(table_names))

        with c2:
            st.metric("Total Records", total_records)

        browse_tab, edit_tab, delete_tab, structure_tab, health_tab = st.tabs(
            [
                "📋 Browse Records",
                "✏️ Update Records",
                "🗑️ Delete Records",
                "🏗️ Database Structure",
                "🩺 Database Health",
            ]
        )

        # -------------------------------------------------
        # READ
        # -------------------------------------------------

        with browse_tab:

            selected_table = st.selectbox(
                "Select table to browse",
                table_names,
                key="browse_table",
            )

            search_text = st.text_input(
                "Search records",
                placeholder="Search by any value...",
                key="browse_search",
            )

            columns = database.get_table_columns(selected_table)

            rows = database.get_table_data(
                selected_table,
                search_text,
            )

            st.caption(f"{len(rows)} record(s) displayed.")

            if rows:
                df = pd.DataFrame(rows, columns=columns)

                st.dataframe(
                    df,
                    use_container_width=True,
                    hide_index=True,
                )

                st.download_button(
                    "⬇️ Export CSV",
                    data=df.to_csv(index=False).encode("utf-8"),
                    file_name=f"{selected_table}.csv",
                    mime="text/csv",
                )
            else:
                st.info("No matching records found.")

        # -------------------------------------------------
        # UPDATE
        # -------------------------------------------------

        with edit_tab:

            st.markdown("### Edit an existing record")
            st.caption(
                "Choose a table and record ID, change its values, "
                "and save your changes."
            )

            edit_table = st.selectbox(
                "Choose table",
                table_names,
                key="edit_table",
            )

            edit_columns = database.get_table_columns(edit_table)
            edit_rows = database.get_table_data(edit_table)

            if not edit_rows:
                st.info("There are no records to edit in this table.")
            else:
                id_column = edit_columns[0]

                record_ids = [row[0] for row in edit_rows]

                selected_id = st.selectbox(
                    "Select record ID",
                    record_ids,
                    key="edit_record_id",
                )

                selected_record = next(
                    row for row in edit_rows if row[0] == selected_id
                )

                st.markdown("#### Record details")

                with st.form("update_record_form"):

                    updated_values = {}

                    for index, column_name in enumerate(edit_columns):

                        if index == 0:
                            st.text_input(
                                f"{column_name} (Primary Key)",
                                value=str(selected_record[index]),
                                disabled=True,
                            )
                            continue

                        current_value = selected_record[index]

                        if isinstance(current_value, int):
                            updated_values[column_name] = st.number_input(
                                column_name.replace("_", " ").title(),
                                value=int(current_value),
                                step=1,
                                key=f"edit_{edit_table}_{selected_id}_{column_name}",
                            )

                        elif isinstance(current_value, float):
                            updated_values[column_name] = st.number_input(
                                column_name.replace("_", " ").title(),
                                value=float(current_value),
                                key=f"edit_{edit_table}_{selected_id}_{column_name}",
                            )

                        else:
                            updated_values[column_name] = st.text_input(
                                column_name.replace("_", " ").title(),
                                value="" if current_value is None
                                else str(current_value),
                                key=f"edit_{edit_table}_{selected_id}_{column_name}",
                            )

                    save_changes = st.form_submit_button(
                        "💾 Save Changes",
                        type="primary",
                        use_container_width=True,
                    )

                if save_changes:
                    success = safe_action(
                        database.update_record,
                        edit_table,
                        selected_id,
                        updated_values,
                    )

                    if success:
                        st.rerun()

        # -------------------------------------------------
        # DELETE
        # -------------------------------------------------

        with delete_tab:

            st.markdown("### Delete an existing record")

            st.warning(
                "Deleting a student may also delete related skills, "
                "requests, sessions and reviews because of database "
                "cascade rules. Check the selected record carefully."
            )

            delete_table = st.selectbox(
                "Choose table",
                table_names,
                key="delete_table",
            )

            delete_columns = database.get_table_columns(delete_table)
            delete_rows = database.get_table_data(delete_table)

            if not delete_rows:
                st.info("There are no records to delete in this table.")
            else:
                delete_ids = [row[0] for row in delete_rows]

                delete_id = st.selectbox(
                    "Select record ID to delete",
                    delete_ids,
                    key="delete_record_id",
                )

                selected_delete_record = next(
                    row for row in delete_rows if row[0] == delete_id
                )

                st.markdown("#### Selected record")

                st.dataframe(
                    pd.DataFrame(
                        [selected_delete_record],
                        columns=delete_columns,
                    ),
                    use_container_width=True,
                    hide_index=True,
                )

                confirm_delete = st.checkbox(
                    "I understand this action cannot be undone.",
                    key="confirm_delete",
                )

                if st.button(
                    "🗑️ Permanently Delete Record",
                    type="primary",
                    disabled=not confirm_delete,
                    use_container_width=True,
                ):
                    success = safe_action(
                        database.delete_record,
                        delete_table,
                        delete_id,
                    )

                    if success:
                        st.rerun()

        # -------------------------------------------------
        # DATABASE STRUCTURE
        # -------------------------------------------------

        with structure_tab:

            st.markdown("### Database Schema")

            schema = database.get_database_schema()
            st.json(schema)

            st.markdown("### Table Record Counts")

            if isinstance(table_counts, dict):
                count_rows = [
                    {"Table": name, "Records": count}
                    for name, count in table_counts.items()
                ]

                st.dataframe(
                    pd.DataFrame(count_rows),
                    use_container_width=True,
                    hide_index=True,
                )

        # -------------------------------------------------
        # DATABASE HEALTH
        # -------------------------------------------------

        with health_tab:

            st.markdown("### Database Health Report")

            health = database.database_health()
            st.json(health)

            if st.button("↻ Check Database Health"):
                st.rerun()

    except (sqlite3.Error, ValueError, TypeError, AttributeError) as error:
        st.error(f"Database Explorer error: {error}")


# =========================================================
# 14. FOOTER
# =========================================================

st.markdown("---")

st.markdown("""
<div style="text-align:center; color:#7186a3; font-size:0.78rem;">
    PeerBridge · Student Skill Exchange Platform
    <br>
    Learn together. Teach together. Grow together.
</div>
""", unsafe_allow_html=True)