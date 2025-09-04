import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import requests
import json
import os
from streamlit_autorefresh import st_autorefresh

# Page config
st.set_page_config(
    page_title="🤖 AI Test Tracker",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
.main-header {
    font-size: 2.5rem;
    color: #1f77b4;
    text-align: center;
    margin-bottom: 2rem;
}
.metric-card {
    background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
    padding: 1rem;
    border-radius: 10px;
    color: white;
    text-align: center;
}
.status-pass { background-color: #d4edda; color: #155724; padding: 5px 10px; border-radius: 15px; }
.status-fail { background-color: #f8d7da; color: #721c24; padding: 5px 10px; border-radius: 15px; }
.status-progress { background-color: #fff3cd; color: #856404; padding: 5px 10px; border-radius: 15px; }
</style>
""", unsafe_allow_html=True)

# Auto-refresh every 30 seconds
st_autorefresh(interval=30000, key="data_refresh")

@st.cache_data(ttl=60)
def load_data():
    """Load Excel data with caching"""
    try:
        if os.path.exists("sample_data.xlsx"):
            df = pd.read_excel("sample_data.xlsx")
        else:
            # Create sample data if file doesn't exist
            df = create_sample_data()
            df.to_excel("sample_data.xlsx", index=False)
        return df
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return create_sample_data()

def create_sample_data():
    """Create sample data for demonstration"""
    data = {
        'Test_ID': ['TST_001', 'TST_002', 'TST_003', 'TST_004', 'TST_005'],
        'Date': ['2024-09-01', '2024-09-01', '2024-09-02', '2024-09-02', '2024-09-03'],
        'Project': ['Apache', 'MD1', 'N597', 'Apache', 'MD1'],
        'Title': ['Center Stand Test', 'Brake System', 'Side Stand', 'Swingarm Test', 'Rear Brake'],
        'Test_Type': ['Endurance', 'Performance', 'Endurance', 'Strength', 'Performance'],
        'Status': ['Fail', 'Pass', 'In Progress', 'Pass', 'Fail'],
        'Failure_Type': ['Structural', '', '', '', 'Hydraulic'],
        'Failure_Description': ['Weld crack at joint', '', '', '', 'Brake fluid leak'],
        'Observations': ['Visible fatigue crack', 'All specs met', 'Test ongoing', 'No issues', 'Seal failure'],
        'Cycles_Completed': [50000, '', 25000, '', '']
    }
    return pd.DataFrame(data)

def query_ai(prompt, data_context):
    """Simple AI query function using local analysis"""
    df = pd.read_excel("sample_data.xlsx") if os.path.exists("sample_data.xlsx") else create_sample_data()
    
    # Simple pattern matching for common queries
    prompt_lower = prompt.lower()
    
    if "how many" in prompt_lower and "fail" in prompt_lower:
        failed_count = len(df[df['Status'] == 'Fail'])
        return f"There are {failed_count} failed tests in the database."
    
    elif "which project" in prompt_lower and "fail" in prompt_lower:
        failed_tests = df[df['Status'] == 'Fail']
        projects = failed_tests['Project'].value_counts()
        result = "Failed tests by project:\n"
        for project, count in projects.items():
            result += f"• {project}: {count} failures\n"
        return result
    
    elif "failure type" in prompt_lower:
        failure_types = df[df['Failure_Type'] != '']['Failure_Type'].value_counts()
        result = "Failure types:\n"
        for failure_type, count in failure_types.items():
            result += f"• {failure_type}: {count} occurrences\n"
        return result
    
    elif "endurance" in prompt_lower:
        endurance_tests = df[df['Test_Type'] == 'Endurance']
        total = len(endurance_tests)
        failed = len(endurance_tests[endurance_tests['Status'] == 'Fail'])
        passed = len(endurance_tests[endurance_tests['Status'] == 'Pass'])
        return f"Endurance Tests Summary:\n• Total: {total}\n• Passed: {passed}\n• Failed: {failed}\n• Success Rate: {(passed/total)*100:.1f}%"
    
    else:
        return "I can help you analyze test data. Try asking:\n• 'How many tests failed?'\n• 'Which projects have failures?'\n• 'Show me failure types'\n• 'Analyze endurance tests'"

def main():
    st.markdown('<h1 class="main-header">🤖 AI-Powered Test Tracker</h1>', unsafe_allow_html=True)
    
    # Load data
    df = load_data()
    
    # Sidebar navigation
    st.sidebar.title("📋 Navigation")
    page = st.sidebar.selectbox("Select Page", [
        "🏠 Dashboard",
        "📊 AI Analysis", 
        "📝 Data Entry",
        "📄 Reports"
    ])
    
    if page == "🏠 Dashboard":
        show_dashboard(df)
    elif page == "📊 AI Analysis":
        show_ai_analysis(df)
    elif page == "📝 Data Entry":
        show_data_entry(df)
    elif page == "📄 Reports":
        show_reports(df)

def show_dashboard(df):
    st.header("📊 Test Dashboard")
    
    # Key metrics
    col1, col2, col3, col4 = st.columns(4)
    
    total_tests = len(df)
    passed_tests = len(df[df['Status'] == 'Pass'])
    failed_tests = len(df[df['Status'] == 'Fail'])
    in_progress = len(df[df['Status'] == 'In Progress'])
    
    with col1:
        st.markdown(f"""<div class="metric-card"><h3>Total Tests</h3><h2>{total_tests}</h2></div>""", unsafe_allow_html=True)
    with col2:
        st.markdown(f"""<div class="metric-card"><h3>Passed</h3><h2>{passed_tests}</h2></div>""", unsafe_allow_html=True)
    with col3:
        st.markdown(f"""<div class="metric-card"><h3>Failed</h3><h2>{failed_tests}</h2></div>""", unsafe_allow_html=True)
    with col4:
        st.markdown(f"""<div class="metric-card"><h3>In Progress</h3><h2>{in_progress}</h2></div>""", unsafe_allow_html=True)
    
    # Charts
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Status Distribution")
        status_counts = df['Status'].value_counts()
        fig = px.pie(values=status_counts.values, names=status_counts.index, 
                    title="Test Status Breakdown")
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("Tests by Project")
        project_counts = df['Project'].value_counts()
        fig = px.bar(x=project_counts.index, y=project_counts.values,
                    title="Project Test Distribution")
        st.plotly_chart(fig, use_container_width=True)
    
    # Data table with filters
    st.subheader("Test Data")
    
    # Filters
    col1, col2, col3 = st.columns(3)
    with col1:
        status_filter = st.selectbox("Filter by Status", ["All"] + list(df['Status'].unique()))
    with col2:
        project_filter = st.selectbox("Filter by Project", ["All"] + list(df['Project'].unique()))
    with col3:
        test_type_filter = st.selectbox("Filter by Test Type", ["All"] + list(df['Test_Type'].unique()))
    
    # Apply filters
    filtered_df = df.copy()
    if status_filter != "All":
        filtered_df = filtered_df[filtered_df['Status'] == status_filter]
    if project_filter != "All":
        filtered_df = filtered_df[filtered_df['Project'] == project_filter]
    if test_type_filter != "All":
        filtered_df = filtered_df[filtered_df['Test_Type'] == test_type_filter]
    
    st.dataframe(filtered_df, use_container_width=True)

def show_ai_analysis(df):
    st.header("🤖 AI Analysis Assistant")
    
    st.markdown("""
    Ask questions about your test data in natural language. The AI will analyze your data and provide insights.
    """)
    
    # Sample questions
    st.subheader("Sample Questions You Can Ask:")
    sample_questions = [
        "How many tests failed?",
        "Which projects have the most failures?",
        "Show me failure types and their frequency",
        "Analyze endurance test performance"
    ]
    
    for question in sample_questions:
        if st.button(f"📝 {question}", key=f"sample_{question}"):
            st.session_state.ai_prompt = question
    
    # AI Query input
    prompt = st.text_area("Enter your question:", 
                         value=st.session_state.get('ai_prompt', ''),
                         height=100)
    
    if st.button("🔍 Analyze", type="primary"):
        if prompt:
            with st.spinner("Analyzing your data..."):
                response = query_ai(prompt, df)
                st.subheader("📊 Analysis Results")
                st.write(response)
        else:
            st.warning("Please enter a question to analyze.")

def show_data_entry(df):
    st.header("📝 Add New Test Record")
    
    with st.form("new_test_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        
        with col1:
            test_id = st.text_input("Test ID*", placeholder="TST_006")
            date = st.date_input("Date*", datetime.now())
            project = st.selectbox("Project*", ["Apache", "MD1", "N597", "Other"])
            title = st.text_input("Test Title*", placeholder="Test description")
        
        with col2:
            test_type = st.selectbox("Test Type*", ["Endurance", "Performance", "Strength", "Safety"])
            status = st.selectbox("Status*", ["Not Started", "In Progress", "Pass", "Fail"])
            failure_type = st.text_input("Failure Type", placeholder="Only if status is Fail")
            cycles = st.number_input("Cycles Completed", min_value=0, step=1000)
        
        failure_description = st.text_area("Failure Description", placeholder="Detailed description of failure")
        observations = st.text_area("Observations", placeholder="Additional notes and observations")
        
        submitted = st.form_submit_button("➕ Add Test Record", type="primary")
        
        if submitted:
            if test_id and project and title:
                new_record = {
                    'Test_ID': test_id,
                    'Date': date.strftime('%Y-%m-%d'),
                    'Project': project,
                    'Title': title,
                    'Test_Type': test_type,
                    'Status': status,
                    'Failure_Type': failure_type,
                    'Failure_Description': failure_description,
                    'Observations': observations,
                    'Cycles_Completed': cycles if cycles > 0 else ''
                }
                
                # Add to dataframe and save
                updated_df = pd.concat([df, pd.DataFrame([new_record])], ignore_index=True)
                updated_df.to_excel("sample_data.xlsx", index=False)
                st.success("✅ Test record added successfully!")
                st.balloons()
                st.experimental_rerun()
            else:
                st.error("❌ Please fill in all required fields marked with *")

def show_reports(df):
    st.header("📄 Test Reports")
    
    # Summary Report
    st.subheader("📊 Summary Report")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric("Total Tests", len(df))
        st.metric("Success Rate", f"{(len(df[df['Status'] == 'Pass']) / len(df) * 100):.1f}%")
    
    with col2:
        st.metric("Failed Tests", len(df[df['Status'] == 'Fail']))
        st.metric("Tests in Progress", len(df[df['Status'] == 'In Progress']))
    
    # Failure Analysis
    if len(df[df['Status'] == 'Fail']) > 0:
        st.subheader("🔍 Failure Analysis")
        failed_df = df[df['Status'] == 'Fail']
        
        failure_by_project = failed_df['Project'].value_counts()
        fig = px.bar(x=failure_by_project.index, y=failure_by_project.values,
                    title="Failures by Project")
        st.plotly_chart(fig, use_container_width=True)
        
        st.subheader("Failed Tests Details")
        st.dataframe(failed_df[['Test_ID', 'Project', 'Title', 'Failure_Type', 'Failure_Description']], 
                    use_container_width=True)
    
    # Download options
    st.subheader("💾 Download Reports")
    csv = df.to_csv(index=False)
    st.download_button(
        label="📥 Download Full Report (CSV)",
        data=csv,
        file_name=f"test_report_{datetime.now().strftime('%Y%m%d')}.csv",
        mime="text/csv"
    )

if __name__ == "__main__":
    main()
