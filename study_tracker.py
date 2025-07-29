import streamlit as st
import pandas as pd
from datetime import date, datetime
import plotly.express as px
from io import BytesIO

# Import MongoDB database functions from your separate connector module
from mongo_connector import (
    add_study_record, get_study_records, delete_study_record,
    add_exam_record, get_exam_records, delete_exam_record,
    add_study_plan, get_study_plans, delete_study_plan
)

st.set_page_config(
    page_title="CBSE Class 10 Study Tracker - Priyanshi",
    page_icon="📚",
    layout="wide"
)

SUBJECT_CHAPTERS = {
    "Science": [
        "Light - Reflection and Refraction",
        "Human Eye and Colourful World",
        "Electricity",
        "Magnetic Effects of Electric Current",
        "Sources of Energy",
        "Life Processes",
        "Control and Coordination",
        "How do Organisms Reproduce",
        "Heredity and Evolution",
        "Our Environment",
        "Natural Resource Management",
        "Acids, Bases and Salts",
        "Metals and Non-metals",
        "Carbon and its Compounds",
        "Periodic Classification of Elements"
    ],
    "Math": [
        "Real Numbers",
        "Polynomials",
        "Pair of Linear Equations in Two Variables",
        "Quadratic Equations",
        "Arithmetic Progressions",
        "Triangles",
        "Coordinate Geometry",
        "Introduction to Trigonometry",
        "Some Applications of Trigonometry",
        "Circles",
        "Constructions",
        "Areas Related to Circles",
        "Surface Areas and Volumes",
        "Statistics",
        "Probability"
    ],
    "English": [
        "A Letter to God",
        "Nelson Mandela: Long Walk to Freedom",
        "Two Stories about Flying",
        "From the Diary of Anne Frank",
        "Glimpses of India",
        "Mijbil the Otter",
        "Madam Rides the Bus",
        "The Sermon at Benares",
        "The Proposal",
        "A Triumph of Surgery",
        "The Thief's Story",
        "The Midnight Visitor",
        "A Question of Trust",
        "Footprints without Feet",
        "The Making of a Scientist",
        "The Necklace",
        "Bholi",
        "The Book That Saved the Earth"
    ],
    "SS": [
        "Resources and Development",
        "Forest and Wildlife Resources",
        "Water Resources",
        "Agriculture",
        "Minerals and Energy Resources",
        "Manufacturing Industries",
        "Lifelines of National Economy",
        "The Rise of Nationalism in Europe",
        "Nationalism in India",
        "The Making of a Global World",
        "The Age of Industrialisation",
        "Print Culture and the Modern World",
        "Power Sharing",
        "Federalism",
        "Democracy and Diversity",
        "Gender, Religion and Caste",
        "Popular Struggles and Movements",
        "Political Parties",
        "Outcomes of Democracy",
        "Challenges to Democracy",
        "Development",
        "Sectors of Indian Economy",
        "Money and Credit",
        "Globalisation and the Indian Economy",
        "Consumer Rights"
    ],
    "Gujarati": [
        "પ્રથમ અધ્યાન: સમજદારીનો માર્ગ",
        "બીજું અધ્યાય: કુદરતના રંગ",
        "તૃતીય અધ്യાય: જીવનના મૂલ્યો",
        "ચોથું અધ્યાય: સંસ્કૃતિ અને પરંપરા",
        "પાંચમું અધ્યાય: વૈજ્ઞાનિક વિચાર",
        "છઠ્ઠું અધ્યાય: સાહિત્યનું મહત્વ",
        "સાતમું અધ્યાય: સમાજ અને એના મુદ્દા",
        "આઠમું અધ્યાય: જીવન કૌશલ્ય",
        "નવમું અધ્યાય: નાયક અને પ્રેરણા",
        "દસમું અધ્યાય: નિવૃત્તિ અને આખરી અભ્યાસ"
    ]
}

BOOK_MATERIALS = [
    "CBSE Textbook",
    "KS QB",
    "US Notes",
    "KS Power Book",
    "KS Objective Book",
    "US Worksheet",
    "Deepa mam Class"
]

EXAM_TYPES = [
    "School Exam",
    "KS Class Test",
    "Mock Test",
    "Deepa mam Class",
    "Others"
]

def export_all_data():
    study_df = get_study_records()
    exam_df = get_exam_records()
    plan_df = get_study_plans()
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        for df, sheet_name in [(study_df, 'Study Records'), (exam_df, 'Exam Records'), (plan_df, 'Study Plans')]:
            if not df.empty:
                # Rename MongoDB _id to ID
                if "_id" in df.columns:
                    df.rename(columns={"_id": "ID"}, inplace=True)
                df.to_excel(writer, sheet_name=sheet_name, index=False)
    return output.getvalue()

def main():
    st.markdown("""
    <div style='background: linear-gradient(90deg, #667eea, #764ba2); padding: 1rem; border-radius: 10px; text-align: center; color: white; margin-bottom: 1rem;'>
        <h1>📚 CBSE Class 10 Study Tracker - Priyanshi C. Patel</h1>
        <p>Track your daily studies, plans, and exam performances</p>
    </div>
    """, unsafe_allow_html=True)

    tabs = st.tabs([
        "📝 Add Study Record",
        "📅 Plan Study",
        "🎯 Add Exam Result",
        "📊 Study Dashboard",
        "📈 Exam Dashboard"
    ])

    # ========== Add Study Record ==========
    with tabs[0]:
        st.header("📝 Add New Study Record")
        sel_subject = st.selectbox("📖 Subject", options=list(SUBJECT_CHAPTERS.keys()), key="study_subject")
        with st.form("study_record_form", clear_on_submit=True):
            chapter = st.selectbox("📑 Chapter", options=SUBJECT_CHAPTERS[sel_subject], key="study_chapter")
            study_date = st.date_input("📅 Study Date", value=date.today())
            book_material = st.selectbox("📘 Book/Material Used", options=BOOK_MATERIALS)
            hours_studied = st.number_input("⏰ Hours Studied", min_value=0.0, max_value=24.0, step=0.5)
            remarks = st.text_area("💭 Remarks (Optional)", max_chars=250)
            submitted = st.form_submit_button("Add Study Record")
            if submitted:
                if hours_studied > 0:
                    try:
                        add_study_record(str(study_date), sel_subject, chapter, book_material, hours_studied, remarks)
                        st.success("Study record added successfully!")
                        st.experimental_rerun()
                    except Exception as e:
                        st.error(f"Failed to add study record: {e}")
                else:
                    st.error("Please enter valid hours studied (> 0).")

    # ========== Plan Study ==========
    with tabs[1]:
        st.header("📅 Plan a Study Session")
        plan_subject = st.selectbox("📖 Subject", options=list(SUBJECT_CHAPTERS.keys()), key="plan_subject")
        with st.form("study_plan_form", clear_on_submit=True):
            plan_chapter = st.selectbox("📑 Chapter", options=SUBJECT_CHAPTERS[plan_subject], key="plan_chapter")
            plan_date = st.date_input("📅 Plan Date", value=date.today())
            planned_hours = st.number_input("⏰ Planned Hours", min_value=0.0, max_value=24.0, step=0.5)
            plan_remarks = st.text_area("💭 Notes/Remarks (Optional)", max_chars=250)
            submitted = st.form_submit_button("Add Study Plan")
            if submitted:
                if planned_hours > 0:
                    try:
                        add_study_plan(str(plan_date), plan_subject, plan_chapter, planned_hours, plan_remarks)
                        st.success("Study plan added successfully!")
                        st.experimental_rerun()
                    except Exception as e:
                        st.error(f"Failed to add study plan: {e}")
                else:
                    st.error("Please enter valid planned hours (> 0).")

    # ========== Add Exam Result ==========
    with tabs[2]:
        st.header("🎯 Add New Exam Result")
        with st.form("exam_result_form", clear_on_submit=True):
            exam_subject = st.selectbox("📖 Subject", options=list(SUBJECT_CHAPTERS.keys()), key="exam_subject")
            exam_type = st.selectbox("🏆 Exam Type", options=EXAM_TYPES)
            exam_date = st.date_input("📅 Exam Date", value=date.today())
            col1, col2 = st.columns(2)
            with col1:
                maximum_marks = st.number_input("📊 Maximum Marks", min_value=1, max_value=1000, value=100, step=1, key="maximum_marks")
            with col2:
                marks_scored = st.number_input("✏️ Marks Scored", min_value=0, max_value=1000, value=0, step=1, key="marks_scored")
            improvements = st.text_area("🎯 Areas for Improvement (Optional)")
            submitted = st.form_submit_button("Add Exam Result")
            if submitted:
                if marks_scored > maximum_marks:
                    st.error("Marks scored cannot be more than maximum marks!")
                else:
                    try:
                        add_exam_record(str(exam_date), exam_subject, exam_type, maximum_marks, marks_scored, improvements)
                        st.success("Exam result added successfully!")
                        st.experimental_rerun()
                    except Exception as e:
                        st.error(f"Failed to add exam record: {e}")

    # ========== Study Dashboard ==========
    with tabs[3]:
        st.header("📊 Study Dashboard")
        df = get_study_records()
        plan_df = get_study_plans()

        if df.empty and plan_df.empty:
            st.info("No study or plan records found yet.")
        else:
            # Safe sets for filters to avoid KeyErrors
            subj_set_study = set(df['subject']) if 'subject' in df.columns else set()
            subj_set_plan = set(plan_df['subject']) if 'subject' in plan_df.columns else set()
            subj_set = subj_set_study.union(subj_set_plan)

            chap_set_study = set(df['chapter']) if 'chapter' in df.columns else set()
            chap_set_plan = set(plan_df['chapter']) if 'chapter' in plan_df.columns else set()
            chap_set = chap_set_study.union(chap_set_plan)

            book_set = set(df['book_material']) if 'book_material' in df.columns else set()

            with st.expander("Filters", expanded=True):
                f_subject = st.multiselect("Subject", options=sorted(subj_set), key="filter_subject")
                f_chapter = st.multiselect("Chapter", options=sorted(chap_set), key="filter_chapter")
                f_book = st.multiselect("Book/Material Used", options=sorted(book_set), key="filter_book")
                start_date_col, end_date_col = st.columns(2)
                f_start_date = start_date_col.date_input("Start Date", value=None, key="filter_start_date")
                f_end_date = end_date_col.date_input("End Date", value=None, key="filter_end_date")

            # Filter study records based on selections
            if f_subject:
                df = df[df['subject'].isin(f_subject)]
                plan_df = plan_df[plan_df['subject'].isin(f_subject)]
            if f_chapter:
                df = df[df['chapter'].isin(f_chapter)]
                plan_df = plan_df[plan_df['chapter'].isin(f_chapter)]
            if f_book:
                df = df[df['book_material'].isin(f_book)]
            if f_start_date:
                df = df[pd.to_datetime(df['date']) >= pd.to_datetime(f_start_date)]
                plan_df = plan_df[pd.to_datetime(plan_df['plan_date']) >= pd.to_datetime(f_start_date)]
            if f_end_date:
                df = df[pd.to_datetime(df['date']) <= pd.to_datetime(f_end_date)]
                plan_df = plan_df[pd.to_datetime(plan_df['plan_date']) <= pd.to_datetime(f_end_date)]

            # Convert dates to datetime
            if not df.empty:
                df['date'] = pd.to_datetime(df['date'])
            if not plan_df.empty:
                plan_df['plan_date'] = pd.to_datetime(plan_df['plan_date'])

            # Planned vs Actual aggregate table
            st.subheader("Planned vs Actual Study Hours")
            planned_agg = plan_df.groupby(['plan_date', 'subject', 'chapter']).agg({'planned_hours': 'sum'}).reset_index()
            actual_agg = df.groupby(['date', 'subject', 'chapter']).agg({'hours_studied': 'sum'}).reset_index()
            merged = pd.merge(planned_agg, actual_agg,
                              left_on=['plan_date', 'subject', 'chapter'],
                              right_on=['date', 'subject', 'chapter'],
                              how='outer')
            merged['plan_date'] = merged['plan_date'].fillna(merged['date'])
            merged['planned_hours'] = merged['planned_hours'].fillna(0)
            merged['hours_studied'] = merged['hours_studied'].fillna(0)
            merged = merged.rename(columns={
                'plan_date': 'Date',
                'subject': 'Subject',
                'chapter': 'Chapter',
                'planned_hours': 'Planned Hours',
                'hours_studied': 'Actual Hours'
            })
            merged = merged[['Date', 'Subject', 'Chapter', 'Planned Hours', 'Actual Hours']].sort_values('Date', ascending=False)
            st.dataframe(merged, use_container_width=True)

            # Show study records table
            st.markdown("### Study Records")
            display_df = df.copy()
            # Rename MongoDB _id to ID for display
            if '_id' in display_df.columns:
                display_df = display_df.rename(columns={'_id': 'ID'})
            st.dataframe(
                display_df[['ID', 'date', 'subject', 'chapter', 'book_material', 'hours_studied', 'remarks']],
                use_container_width=True
            )

            # Record deletion input and button
            st.markdown("### Delete a Study Record")
            del_id = st.text_input("Enter Study Record ID to delete (copy from ID column above)", key="del_study_id")
            if st.button("Delete Study Record"):
                if del_id:
                    try:
                        delete_study_record(del_id)
                        st.success(f"Deleted study record ID: {del_id}")
                        st.experimental_rerun()
                    except Exception as e:
                        st.error(f"Error deleting record: {e}")
                else:
                    st.error("Please enter a valid Study Record ID")

    # ========== Exam Dashboard ==========
    with tabs[4]:
        st.header("📈 Exam Dashboard")
        exam_df = get_exam_records()

        if exam_df.empty:
            st.info("No exam records found.")
        else:
            with st.expander("Filters", expanded=True):
                f_subject_exam = st.multiselect("Subject", options=sorted(exam_df['subject'].unique()), key="filter_exam_subject")
                f_exam_type = st.multiselect("Exam Type", options=sorted(exam_df['exam_type'].unique()), key="filter_exam_type")
                start_exam_col, end_exam_col = st.columns(2)
                start_exam_date = start_exam_col.date_input("Exam Start Date", value=None, key="filter_exam_start_date")
                end_exam_date = end_exam_col.date_input("Exam End Date", value=None, key="filter_exam_end_date")

            if f_subject_exam:
                exam_df = exam_df[exam_df['subject'].isin(f_subject_exam)]
            if f_exam_type:
                exam_df = exam_df[exam_df['exam_type'].isin(f_exam_type)]
            if start_exam_date:
                exam_df = exam_df[pd.to_datetime(exam_df['exam_date']) >= pd.to_datetime(start_exam_date)]
            if end_exam_date:
                exam_df = exam_df[pd.to_datetime(exam_df['exam_date']) <= pd.to_datetime(end_exam_date)]

            # Convert exam_date
            exam_df['exam_date'] = pd.to_datetime(exam_df['exam_date'])

            display = exam_df.copy()
            if '_id' in display.columns:
                display.rename(columns={'_id':'ID'}, inplace=True)

            display['percentage'] = ((display['marks_scored'] / display['maximum_marks'])*100).round(1).astype(str) + '%'

            display = display[['ID','exam_date','subject','exam_type','marks_scored','maximum_marks','percentage','improvements']]
            display.rename(columns={
                'exam_date': 'Exam Date',
                'subject': 'Subject',
                'exam_type': 'Exam Type',
                'marks_scored':'Marks',
                'maximum_marks':'Max',
                'improvements':'Improvement'
            }, inplace=True)

            st.dataframe(display, use_container_width=True)

            st.markdown("### Delete an Exam Record")
            del_exam_id = st.text_input(
               del_exam_id = st.text_input(
    "Enter Exam Record ID to delete (copy from ID column above)",
    key="del_exam_id"
)

