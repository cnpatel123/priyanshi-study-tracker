import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime, date
import plotly.express as px
import plotly.graph_objects as go
from io import BytesIO
import os

# Set page config for mobile-friendly UI
st.set_page_config(
    page_title="CBSE Class 10 Study Tracker - Priyanshi",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for mobile-friendly UI
st.markdown("""
<style>
    .main > div {
        padding-top: 2rem;
    }
    .stSelectbox > div > div > select {
        font-size: 16px !important;
    }
    .stNumberInput > div > div > input {
        font-size: 16px !important;
    }
    .stTextInput > div > div > input {
        font-size: 16px !important;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .student-header {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        text-align: center;
        margin-bottom: 2rem;
    }
    @media (max-width: 768px) {
        .stColumns > div {
            min-width: 100% !important;
        }
    }
</style>
""", unsafe_allow_html=True)

# Database setup
DATABASE_FILE = "study_tracker.db"

def init_database():
    """Initialize SQLite database with study_records and exam_records tables"""
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    
    # Study records table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS study_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            subject TEXT NOT NULL,
            chapter TEXT NOT NULL,
            book_material TEXT NOT NULL,
            hours_studied REAL NOT NULL,
            test_given TEXT NOT NULL,
            marks_scored INTEGER,
            remarks TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Exam records table
    cursor.execute('''
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

# Subject-Chapter mapping for CBSE Class 10
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
    "Hindi": [
        "सूरदास के पद",
        "तुलसीदास के दोहे",
        "देव के पद",
        "जयशंकर प्रसाद - आत्मकथ्य",
        "सूर्यकांत त्रिपाठी निराला",
        "नागार्जुन - यह दंतुरित मुस्कान",
        "गिरिजाकुमार माथुर - छाया मत छूना",
        "ऋतुराज - कन्यादान",
        "मंगलेश डबराल - संगतकार",
        "स्वयं प्रकाश - नेताजी का चश्मा",
        "रामवृक्ष बेनीपुरी - बालगोबिन भगत",
        "यशपाल - लखनवी अंदाज",
        "सर्वेश्वरदयाल सक्सेना - मानवीय करुणा",
        "यतीन्द्र मिश्र - एक कहानी यह भी",
        "भदंत आनंद कौसल्यायन - स्त्री शिक्षा के विरोधी कुतर्कों का खंडन",
        "महावीरप्रसाद द्विवेदी - नौबतखाने में इबादत",
        "यतीन्द्र मिश्र - संस्कृति"
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

def insert_study_record(date, subject, chapter, book_material, hours_studied, test_given, marks_scored, remarks):
    """Insert a new study record into the database"""
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO study_records 
        (date, subject, chapter, book_material, hours_studied, test_given, marks_scored, remarks)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (date, subject, chapter, book_material, hours_studied, test_given, marks_scored, remarks))
    
    conn.commit()
    conn.close()

def insert_exam_record(exam_date, subject, exam_type, maximum_marks, marks_scored, improvements):
    """Insert a new exam record into the database"""
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO exam_records 
        (exam_date, subject, exam_type, maximum_marks, marks_scored, improvements)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (exam_date, subject, exam_type, maximum_marks, marks_scored, improvements))
    
    conn.commit()
    conn.close()

def get_study_records():
    """Fetch all study records from database"""
    conn = sqlite3.connect(DATABASE_FILE)
    df = pd.read_sql_query("SELECT * FROM study_records ORDER BY date DESC", conn)
    conn.close()
    return df

def get_exam_records():
    """Fetch all exam records from database"""
    conn = sqlite3.connect(DATABASE_FILE)
    df = pd.read_sql_query("SELECT * FROM exam_records ORDER BY exam_date DESC", conn)
    conn.close()
    return df

def export_to_excel():
    """Export all data to Excel format for download"""
    output = BytesIO()
    
    # Get data
    study_df = get_study_records()
    exam_df = get_exam_records()
    
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        # Write study records
        study_df.to_excel(writer, sheet_name='Study Records', index=False)
        
        # Write exam records
        exam_df.to_excel(writer, sheet_name='Exam Records', index=False)
        
        # Get workbook and worksheets
        workbook = writer.book
        study_worksheet = writer.sheets['Study Records']
        exam_worksheet = writer.sheets['Exam Records']
        
        # Add formatting
        header_format = workbook.add_format({
            'bold': True,
            'text_wrap': True,
            'valign': 'top',
            'fg_color': '#D7E4BC',
            'border': 1
        })
        
        # Format study records sheet
        for col_num, value in enumerate(study_df.columns.values):
            study_worksheet.write(0, col_num, value, header_format)
            column_len = max(study_df[value].astype(str).str.len().max(), len(value) + 2)
            study_worksheet.set_column(col_num, col_num, min(column_len, 50))
        
        # Format exam records sheet
        for col_num, value in enumerate(exam_df.columns.values):
            exam_worksheet.write(0, col_num, value, header_format)
            column_len = max(exam_df[value].astype(str).str.len().max(), len(value) + 2)
            exam_worksheet.set_column(col_num, col_num, min(column_len, 50))
    
    return output.getvalue()

def main():
    # Student header
    st.markdown("""
    <div class="student-header">
        <h1>📚 CBSE Class 10 Study Tracker</h1>
        <h2>Priyanshi C. Patel</h2>
        <p>Track your academic journey • Study smarter, not harder</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Initialize database
    init_database()
    
    # Create tabs for different sections
    tab1, tab2, tab3, tab4 = st.tabs(["📝 Add Study Record", "🎯 Add Exam Result", "📊 Study Dashboard", "📈 Exam Dashboard"])
    
    with tab1:
        st.header("📝 Add New Study Record")
        
        with st.form("study_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            
            with col1:
                study_date = st.date_input("📅 Study Date", value=date.today())
                subject = st.selectbox("📖 Subject", options=list(SUBJECT_CHAPTERS.keys()))
                
                # Dependent dropdown for chapters
                if subject:
                    chapter = st.selectbox("📑 Chapter", options=SUBJECT_CHAPTERS[subject])
                else:
                    chapter = st.selectbox("📑 Chapter", options=[])
                
                book_material = st.selectbox("📘 Book/Material Used", options=BOOK_MATERIALS)
            
            with col2:
                hours_studied = st.number_input("⏰ Hours Studied", min_value=0.0, max_value=24.0, step=0.5)
                test_given = st.selectbox("📝 Test Given?", options=["No", "Yes"])
                
                marks_scored = None
                if test_given == "Yes":
                    marks_scored = st.number_input("📊 Marks Scored", min_value=0, max_value=100, step=1)
                
                remarks = st.text_area("💭 Remarks (Optional)", placeholder="Any additional notes...")
            
            submitted = st.form_submit_button("✅ Add Study Record", use_container_width=True)
            
            if submitted:
                if subject and chapter and book_material and hours_studied > 0:
                    insert_study_record(
                        str(study_date), subject, chapter, book_material, 
                        hours_studied, test_given, marks_scored, remarks
                    )
                    st.success(f"✅ Study record added successfully for {subject} - {chapter}")
                    st.rerun()
                else:
                    st.error("❌ Please fill all required fields")
    
    with tab2:
        st.header("🎯 Add New Exam Result")
        
        with st.form("exam_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            
            with col1:
                exam_date = st.date_input("📅 Exam Date", value=date.today())
                subject = st.selectbox("📖 Subject", options=list(SUBJECT_CHAPTERS.keys()), key="exam_subject")
                exam_type = st.selectbox("🏆 Exam Type", options=EXAM_TYPES)
            
            with col2:
                maximum_marks = st.number_input("📊 Maximum Marks", min_value=1, max_value=200, value=100, step=1)
                marks_scored = st.number_input("✏️ Marks Scored", min_value=0, max_value=maximum_marks if maximum_marks else 100, step=1)
                improvements = st.text_area("🎯 Areas for Improvement (Optional)", placeholder="What can be improved for next time...")
            
            submitted_exam = st.form_submit_button("✅ Add Exam Result", use_container_width=True)
            
            if submitted_exam:
                if subject and exam_type and maximum_marks > 0 and marks_scored >= 0:
                    insert_exam_record(
                        str(exam_date), subject, exam_type, maximum_marks, marks_scored, improvements
                    )
                    percentage = (marks_scored / maximum_marks) * 100
                    st.success(f"✅ Exam result added: {subject} - {percentage:.1f}% ({marks_scored}/{maximum_marks})")
                    st.rerun()
                else:
                    st.error("❌ Please fill all required fields")
    
    with tab3:
        st.header("📊 Study Analytics Dashboard")
        st.markdown("### 📚 Priyanshi's Study Progress")
        
        # Get study records
        study_df = get_study_records()
        
        if study_df.empty:
            st.info("📝 No study records found. Add some study records to see analytics!")
        else:
            # Convert date column to datetime
            study_df['date'] = pd.to_datetime(study_df['date'])
            study_df['marks_scored'] = pd.to_numeric(study_df['marks_scored'], errors='coerce')
            
            # Overview metrics
            st.subheader("📈 Study Overview")
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                total_hours = study_df['hours_studied'].sum()
                st.metric("Total Study Hours", f"{total_hours:.1f} hrs")
            
            with col2:
                total_days = study_df['date'].nunique()
                avg_hours = total_hours / total_days if total_days > 0 else 0
                st.metric("Avg Hours/Day", f"{avg_hours:.1f} hrs")
            
            with col3:
                total_sessions = len(study_df)
                st.metric("Total Sessions", total_sessions)
            
            with col4:
                total_tests = len(study_df[study_df['test_given'] == 'Yes'])
                st.metric("Quick Tests Taken", total_tests)
            
            # Subject-wise analysis
            st.subheader("📚 Subject-wise Study Analysis")
            subject_stats = study_df.groupby('subject').agg({
                'hours_studied': ['sum', 'mean'],
                'date': 'count'
            }).round(2)
            subject_stats.columns = ['Total Hours', 'Avg Hours/Session', 'Sessions']
            
            col1, col2 = st.columns(2)
            with col1:
                st.dataframe(subject_stats, use_container_width=True)
            
            with col2:
                # Subject-wise hours pie chart
                fig_pie = px.pie(
                    values=subject_stats['Total Hours'], 
                    names=subject_stats.index,
                    title="Study Hours Distribution by Subject"
                )
                st.plotly_chart(fig_pie, use_container_width=True)
            
            # Chapter-wise analysis
            st.subheader("📑 Chapter-wise Study Time")
            chapter_stats = study_df.groupby(['subject', 'chapter']).agg({
                'hours_studied': 'sum',
                'test_given': lambda x: (x == 'Yes').sum(),
                'marks_scored': 'mean'
            }).round(2)
            chapter_stats.columns = ['Hours Studied', 'Tests Given', 'Avg Marks']
            
            # Filter by subject for chapter analysis
            selected_subject = st.selectbox("Select Subject for Chapter Analysis", options=study_df['subject'].unique())
            chapter_filtered = chapter_stats.loc[selected_subject].sort_values('Hours Studied', ascending=False)
            st.dataframe(chapter_filtered, use_container_width=True)
            
            # Book/Material usage
            st.subheader("📘 Study Material Usage")
            book_stats = study_df.groupby('book_material').agg({
                'hours_studied': 'sum',
                'date': 'count'
            }).round(2)
            book_stats.columns = ['Total Hours', 'Times Used']
            book_stats = book_stats.sort_values('Total Hours', ascending=False)
            
            col1, col2 = st.columns(2)
            with col1:
                st.dataframe(book_stats, use_container_width=True)
            
            with col2:
                fig_bar = px.bar(
                    x=book_stats.index, 
                    y=book_stats['Total Hours'],
                    title="Study Hours by Material",
                    labels={'x': 'Material', 'y': 'Hours'}
                )
                st.plotly_chart(fig_bar, use_container_width=True)
            
            # Recent study records
            st.subheader("📋 Recent Study Sessions")
            recent_study = study_df.head(10)[['date', 'subject', 'chapter', 'hours_studied', 'book_material']]
            recent_study['date'] = recent_study['date'].dt.strftime('%Y-%m-%d')
            st.dataframe(recent_study, use_container_width=True)
    
    with tab4:
        st.header("📈 Exam Performance Dashboard")
        st.markdown("### 🎯 Priyanshi's Exam Results")
        
        # Get exam records
        exam_df = get_exam_records()
        
        if exam_df.empty:
            st.info("🎯 No exam records found. Add some exam results to see performance analytics!")
        else:
            # Convert date and calculate percentage
            exam_df['exam_date'] = pd.to_datetime(exam_df['exam_date'])
            exam_df['percentage'] = (exam_df['marks_scored'] / exam_df['maximum_marks']) * 100
            
            # Overview metrics
            st.subheader("🏆 Exam Performance Overview")
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                total_exams = len(exam_df)
                st.metric("Total Exams", total_exams)
            
            with col2:
                avg_percentage = exam_df['percentage'].mean()
                st.metric("Average Score", f"{avg_percentage:.1f}%")
            
            with col3:
                highest_score = exam_df['percentage'].max()
                st.metric("Highest Score", f"{highest_score:.1f}%")
            
            with col4:
                latest_score = exam_df.iloc[0]['percentage']
                st.metric("Latest Score", f"{latest_score:.1f}%")
            
            # Subject-wise exam performance
            st.subheader("📚 Subject-wise Exam Performance")
            exam_subject_stats = exam_df.groupby('subject').agg({
                'percentage': ['count', 'mean', 'max', 'min'],
                'marks_scored': 'sum',
                'maximum_marks': 'sum'
            }).round(2)
            exam_subject_stats.columns = ['Exams Taken', 'Avg %', 'Highest %', 'Lowest %', 'Total Marks', 'Total Max Marks']
            
            col1, col2 = st.columns(2)
            with col1:
                st.dataframe(exam_subject_stats, use_container_width=True)
            
            with col2:
                # Subject-wise average performance chart
                fig_bar = px.bar(
                    x=exam_subject_stats.index,
                    y=exam_subject_stats['Avg %'],
                    title="Average Score by Subject",
                    labels={'x': 'Subject', 'y': 'Average Percentage'}
                )
                fig_bar.update_traces(marker_color='lightblue')
                st.plotly_chart(fig_bar, use_container_width=True)
            
            # Exam type analysis
            st.subheader("🎯 Performance by Exam Type")
            exam_type_stats = exam_df.groupby('exam_type').agg({
                'percentage': ['count', 'mean', 'max', 'min']
            }).round(2)
            exam_type_stats.columns = ['Exams Taken', 'Avg %', 'Highest %', 'Lowest %']
            st.dataframe(exam_type_stats, use_container_width=True)
            
            # Performance trend over time
            st.subheader("📊 Score Trends Over Time")
            fig_line = px.line(
                exam_df.sort_values('exam_date'),
                x='exam_date',
                y='percentage',
                color='subject',
                title="Exam Scores Over Time",
                labels={'percentage': 'Score (%)', 'exam_date': 'Date'},
                markers=True
            )
            st.plotly_chart(fig_line, use_container_width=True)
            
            # Recent exam results
            st.subheader("📋 Recent Exam Results")
            recent_exams = exam_df.head(10)[['exam_date', 'subject', 'exam_type', 'marks_scored', 'maximum_marks', 'percentage']]
            recent_exams['exam_date'] = recent_exams['exam_date'].dt.strftime('%Y-%m-%d')
            recent_exams['percentage'] = recent_exams['percentage'].round(1).astype(str) + '%'
            st.dataframe(recent_exams, use_container_width=True)
            
            # Improvement areas
            if not exam_df['improvements'].isna().all():
                st.subheader("🎯 Areas for Improvement")
                recent_improvements = exam_df.dropna(subset=['improvements']).head(5)
                for _, row in recent_improvements.iterrows():
                    if row['improvements'].strip():
                        st.info(f"**{row['subject']} ({row['exam_date'].strftime('%Y-%m-%d')})**: {row['improvements']}")
    
    # Export functionality (available on all tabs)
    st.sidebar.markdown("---")
    st.sidebar.subheader("📥 Export Data")
    if st.sidebar.button("📊 Export All Data to Excel", use_container_width=True):
        excel_data = export_to_excel()
        st.sidebar.download_button(
            label="💾 Download Excel File",
            data=excel_data,
            file_name=f"priyanshi_study_data_{datetime.now().strftime('%Y%m%d')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )

if __name__ == "__main__":
    main()
