import streamlit as st
import pandas as pd
import sqlite3
from datetime import date, datetime
import plotly.express as px
from io import BytesIO

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
        "પ્રથમ અધ્યાય: સમજદારીનો માર્ગ",
        "બીજું અધ્યાય: કુદરતના રંગ",
        "તૃતીય અધ્યાય: જીવનના મૂલ્યો",
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
    "US Worksheet"
]

EXAM_TYPES = [
    "School Exam",
    "KS Class Test",
    "Mock Test",
    "Others"
]

DATABASE_FILE = "study_tracker.db"

def init_db():
    conn = sqlite3.connect(DATABASE_FILE)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS study_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            subject TEXT NOT NULL,
            chapter TEXT NOT NULL,
            book_material TEXT NOT NULL,
            hours_studied REAL NOT NULL,
            remarks TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS exam_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            exam_date TEXT NOT NULL,
            subject TEXT NOT NULL,
            exam_type TEXT NOT NULL,
            maximum_marks INTEGER NOT NULL,
            marks_scored INTEGER NOT NULL,
            improvements TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

def insert_study_record(date, subject, chapter, book_material, hours_studied, remarks):
    conn = sqlite3.connect(DATABASE_FILE)
    c = conn.cursor()
    c.execute(
        '''INSERT INTO study_records (date, subject, chapter, book_material, hours_studied, remarks)
           VALUES (?, ?, ?, ?, ?, ?)''',
        (date, subject, chapter, book_material, hours_studied, remarks)
    )
    conn.commit()
    conn.close()

def insert_exam_record(exam_date, subject, exam_type, maximum_marks, marks_scored, improvements):
    conn = sqlite3.connect(DATABASE_FILE)
    c = conn.cursor()
    c.execute(
        '''INSERT INTO exam_records (exam_date, subject, exam_type, maximum_marks, marks_scored, improvements)
           VALUES (?, ?, ?, ?, ?, ?)''',
        (exam_date, subject, exam_type, maximum_marks, marks_scored, improvements)
    )
    conn.commit()
    conn.close()

def get_study_records():
    conn = sqlite3.connect(DATABASE_FILE)
    df = pd.read_sql_query('SELECT * FROM study_records ORDER BY date DESC, id DESC', conn)
    conn.close()
    return df

def get_exam_records():
    conn = sqlite3.connect(DATABASE_FILE)
    df = pd.read_sql_query('SELECT * FROM exam_records ORDER BY exam_date DESC, id DESC', conn)
    conn.close()
    return df

def delete_study_record(record_id):
    conn = sqlite3.connect(DATABASE_FILE)
    c = conn.cursor()
    c.execute('DELETE FROM study_records WHERE id=?', (record_id,))
    conn.commit()
    conn.close()

def delete_exam_record(record_id):
    conn = sqlite3.connect(DATABASE_FILE)
    c = conn.cursor()
    c.execute('DELETE FROM exam_records WHERE id=?', (record_id,))
    conn.commit()
    conn.close()

def export_all_data():
    study_df = get_study_records()
    exam_df = get_exam_records()
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        study_df.to_excel(writer, sheet_name='Study Records', index=False)
        exam_df.to_excel(writer, sheet_name='Exam Records', index=False)
    return output.getvalue()

def main():
    st.markdown("""
    <div style='background: linear-gradient(90deg, #667eea, #764ba2); padding: 1rem; border-radius: 10px; text-align: center; color: white; margin-bottom: 1rem;'>
        <h1>📚 CBSE Class 10 Study Tracker - Priyanshi C. Patel</h1>
        <p>Track your daily studies and exam performances</p>
    </div>
    """, unsafe_allow_html=True)

    init_db()

    tabs = st.tabs([
        "📝 Add Study Record",
        "🎯 Add Exam Result",
        "📊 Study Dashboard",
        "📈 Exam Dashboard"
    ])

    # --- ADD STUDY RECORD ---
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
                    insert_study_record(str(study_date), sel_subject, chapter, book_material, hours_studied, remarks)
                    st.success("Study record added successfully!")
                    st.rerun()
                else:
                    st.error("Please enter valid hours studied (> 0).")

    # --- ADD EXAM RESULT ---
    with tabs[1]:
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
                    insert_exam_record(str(exam_date), exam_subject, exam_type, maximum_marks, marks_scored, improvements)
                    st.success("Exam result added successfully!")
                    st.rerun()

    # --- STUDY DASHBOARD ---
    with tabs[2]:
        st.header("📊 Study Dashboard")
        df = get_study_records()
        if df.empty:
            st.info("No study records found.")
        else:
            df['date'] = pd.to_datetime(df['date'])
            st.dataframe(
                df[['id','date','subject','chapter','book_material','hours_studied','remarks']]
                .rename(columns={'id':'ID'}),
                use_container_width=True
            )

            st.markdown("### Delete a Study Record")
            del_id = st.number_input("Enter Study Record ID to delete", min_value=0, step=1, key="del_study_id")
            if st.button("Delete Study Record"):
                if int(del_id) in df['id'].values:
                    delete_study_record(int(del_id))
                    st.success(f"Deleted study record ID: {int(del_id)}")
                    st.rerun()
                else:
                    st.error("Invalid Study Record ID")

            st.markdown("---")
            st.subheader("Study Summary")
            total_hours = df['hours_studied'].sum()
            avg_hours_per_day = total_hours / df['date'].nunique() if df['date'].nunique() else 0
            st.metric("Total Hours Studied", f"{total_hours:.1f} hrs")
            st.metric("Average Hours per Day", f"{avg_hours_per_day:.2f} hrs")
            subject_hours = df.groupby('subject')['hours_studied'].sum().sort_values(ascending=False)
            fig = px.pie(values=subject_hours.values, names=subject_hours.index, title='Hours Studied by Subject')
            st.plotly_chart(fig, use_container_width=True)

    # --- EXAM DASHBOARD ---
    with tabs[3]:
        st.header("📈 Exam Dashboard")
        exam_df = get_exam_records()
        if exam_df.empty:
            st.info("No exam records found.")
        else:
            exam_df['exam_date'] = pd.to_datetime(exam_df['exam_date'])
            display = exam_df[['id','exam_date','subject','exam_type','marks_scored','maximum_marks','improvements']].copy()
            display['percentage'] = ((display['marks_scored'] / display['maximum_marks'])*100).round(1).astype(str) + '%'
            display.rename(
                columns={
                    'id':'ID','exam_date':'Exam Date','subject':'Subject','exam_type':'Exam Type',
                    'marks_scored':'Marks','maximum_marks':'Max','improvements':'Improvement'
                },
                inplace=True
            )
            display = display[['ID','Exam Date','Subject','Exam Type','Marks','Max','percentage','Improvement']]
            st.dataframe(display, use_container_width=True)

            st.markdown("### Delete an Exam Record")
            del_exam_id = st.number_input(
                "Enter Exam Record ID to delete",
                min_value=0, step=1, key="del_exam_id"
            )
            if st.button("Delete Exam Record"):
                if int(del_exam_id) in exam_df['id'].values:
                    delete_exam_record(int(del_exam_id))
                    st.success(f"Deleted exam record ID: {int(del_exam_id)}")
                    st.rerun()
                else:
                    st.error("Invalid Exam Record ID")

            st.markdown("---")
            st.subheader("Exam Performance Summary")
            total_score = exam_df['marks_scored'].sum()
            total_max = exam_df['maximum_marks'].sum()
            avg_score = (total_score/total_max)*100 if total_max > 0 else 0
            st.metric("Average Score Across Exams", f"{avg_score:.1f}%")
            exams_per_subject = exam_df.groupby('subject').size().sort_values(ascending=False)
            st.write("Exams taken per subject:")
            st.dataframe(exams_per_subject)
            fig2 = px.bar(
                exam_df, x=exam_df['exam_date'].dt.strftime('%d-%b-%Y'),
                y=(exam_df['marks_scored']/exam_df['maximum_marks'])*100,
                color="subject",
                labels={'x':'Exam Date','y':'Score %'}, title="Exam Scores Over Time"
            )
            st.plotly_chart(fig2, use_container_width=True)

    st.sidebar.markdown("## 📥 Export Data")
    if st.sidebar.button("Export all data to Excel"):
        data = export_all_data()
        st.sidebar.download_button(
            label="Download Excel file",
            data=data,
            file_name=f"study_tracker_data_{datetime.now().strftime('%Y%m%d')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

if __name__ == "__main__":
    main()
