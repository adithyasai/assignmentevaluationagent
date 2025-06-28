"""
Main Streamlit application for the Assignment Grading Agent.
"""
import streamlit as st
import sys
from pathlib import Path
import pandas as pd
from datetime import datetime
import traceback

# Add the project root to the Python path
project_root = Path(__file__).parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# Import project modules
import config
from src.ui.file_upload import FileUploadComponent
from src.ui.progress_tracker import ProgressTracker
from src.ui.results_display import ResultsDisplay
from src.core.assignment_processor import AssignmentProcessor

# Configure logging
from loguru import logger
logger.add(
    config.LOG_FILE,
    format=config.LOG_FORMAT,
    rotation=config.LOG_ROTATION,
    retention=config.LOG_RETENTION,
    level="INFO"
)

def initialize_session_state():
    """Initialize Streamlit session state variables."""
    if 'processor' not in st.session_state:
        st.session_state.processor = AssignmentProcessor()
    
    if 'excel_path' not in st.session_state:
        st.session_state.excel_path = None
    
    if 'word_path' not in st.session_state:
        st.session_state.word_path = None
    
    if 'files_loaded' not in st.session_state:
        st.session_state.files_loaded = False
    
    if 'processing_started' not in st.session_state:
        st.session_state.processing_started = False
    
    if 'environment_verified' not in st.session_state:
        st.session_state.environment_verified = False
    
    if 'processing_complete' not in st.session_state:
        st.session_state.processing_complete = False
    
    if 'progress_tracker' not in st.session_state:
        st.session_state.progress_tracker = ProgressTracker()
    
    if 'current_student_index' not in st.session_state:
        st.session_state.current_student_index = 0
    
    if 'processing_results' not in st.session_state:
        st.session_state.processing_results = []

def setup_page_config():
    """Configure Streamlit page settings."""
    st.set_page_config(
        page_title=config.APP_TITLE,
        page_icon=config.STREAMLIT_CONFIG['page_icon'],
        layout=config.STREAMLIT_CONFIG['layout'],
        initial_sidebar_state=config.STREAMLIT_CONFIG['initial_sidebar_state']
    )

def render_header():
    """Render the application header."""
    st.title(config.APP_TITLE)
    st.markdown(f"*{config.APP_DESCRIPTION} - Version {config.APP_VERSION}*")
    st.divider()

def render_sidebar():
    """Render the sidebar with navigation and settings."""
    with st.sidebar:
        st.header("🔧 Settings")
        
        # Environment status
        st.subheader("Environment Status")
        
        # Check if processor is available
        try:
            env_valid, env_info = st.session_state.processor.validate_environment()
            
            if env_valid:
                st.success("✅ Environment Ready")
                st.write(f"**Node.js:** {env_info.get('node_version', 'Unknown')}")
                st.write(f"**npm:** {env_info.get('npm_version', 'Unknown')}")
            else:
                st.error("❌ Environment Issues")
                for error in env_info.get('errors', []):
                    st.write(f"• {error}")
                
                with st.expander("🔧 Setup Help"):
                    st.write("To install Node.js:")
                    st.write("1. Visit https://nodejs.org/")
                    st.write("2. Download Node.js LTS version")
                    st.write("3. Install and restart terminal")
                    st.write("4. Refresh this page")
        
        except Exception as e:
            st.error(f"Error checking environment: {str(e)}")
        
        st.divider()
        
        # Processing options
        st.subheader("Processing Options")
        
        cleanup_after = st.checkbox(
            "Cleanup repositories after processing",
            value=config.CLEANUP_AFTER_PROCESSING,
            help="Remove cloned repositories to save disk space"
        )
        
        max_concurrent = st.slider(
            "Max concurrent processes",
            min_value=1,
            max_value=5,
            value=1,
            help="Number of students to process simultaneously"
        )
        
        build_timeout = st.number_input(
            "Build timeout (seconds)",
            min_value=60,
            max_value=1800,
            value=config.BUILD_TIMEOUT_SECONDS,
            help="Maximum time to wait for project builds"
        )
        
        st.divider()
        
        # Progress summary
        if st.session_state.processing_started:
            st.subheader("📊 Current Session")
            
            if st.session_state.files_loaded:
                students_data = st.session_state.processor.get_excel_handler().get_students_data()
                if students_data is not None:
                    st.write(f"**Total Students:** {len(students_data)}")
                    st.write(f"**Current:** {st.session_state.current_student_index + 1}")
            
            if st.session_state.processing_complete:
                st.success("Processing Complete!")
            
            # Cleanup button
            if st.button("🧹 Cleanup All Files", help="Clean up all temporary files"):
                with st.spinner("Cleaning up..."):
                    st.session_state.processor.cleanup_all()
                st.success("Cleanup completed!")

def progress_callback(student_name: str, status: str, current_index: int, success: bool = None):
    """
    Callback function for processing progress updates.
    
    Args:
        student_name: Name of current student
        status: Current processing status
        current_index: Current student index
        success: Whether operation was successful
    """
    timestamp = datetime.now().strftime("%H:%M:%S")
    
    # Create detailed log entry
    log_entry = f"[{timestamp}] 🎓 **{student_name}** - {status}"
    if success is not None:
        log_entry += f" {'✅' if success else '❌'}"
    
    # Store in session state for display
    if 'processing_logs' not in st.session_state:
        st.session_state.processing_logs = []
    
    st.session_state.processing_logs.append(log_entry)
    
    # Keep only last 50 entries to avoid memory issues
    if len(st.session_state.processing_logs) > 50:
        st.session_state.processing_logs = st.session_state.processing_logs[-50:]
    
    st.session_state.current_student_index = current_index
    
    # Update progress tracker
    if hasattr(st.session_state, 'progress_containers'):
        st.session_state.progress_tracker.update_progress(
            st.session_state.progress_containers,
            student_name,
            status,
            success,
            current_index  # Pass the current index to prevent over-incrementing
        )
    
    # Force a rerun to update the UI
    try:
        st.rerun()
    except:
        pass  # In case rerun is not available

def main():
    """Main application function."""
    try:
        # Initialize
        setup_page_config()
        initialize_session_state()
        
        # Verify environment first
        if not st.session_state.environment_verified:
            verify_environment()
        
        # Set progress callback
        st.session_state.processor.set_progress_callback(progress_callback)
        
        # Render UI
        render_header()
        render_sidebar()
        
        # Main content tabs
        tab1, tab2, tab3, tab4 = st.tabs(["📁 File Upload", "🚀 Processing", "📊 Results", "📋 Help"])
        
        with tab1:
            render_file_upload_tab()
        
        with tab2:
            render_processing_tab()
        
        with tab3:
            render_results_tab()
        
        with tab4:
            render_help_tab()
    
    except Exception as e:
        st.error(f"Application error: {str(e)}")
        logger.error(f"Application error: {str(e)}")
        logger.error(traceback.format_exc())

def verify_environment():
    """Verify that the build environment is ready."""
    st.info("🔍 Verifying build environment...")
    
    # Import build checker here to avoid circular imports
    from src.utils.build_checker import BuildChecker
    
    build_checker = BuildChecker()
    success, message = build_checker.verify_environment()
    
    if success:
        st.success(f"✅ {message}")
        st.session_state.environment_verified = True
        logger.info("✅ Environment verification successful")
    else:
        st.error(f"❌ {message}")
        st.warning("⚠️ Some features may not work correctly without a proper Node.js environment.")
        with st.expander("🛠️ Environment Setup Instructions"):
            st.markdown("""
            **Required Software:**
            - **Node.js 16+**: Download from [nodejs.org](https://nodejs.org/)
            - **npm**: Usually comes with Node.js
            
            **Verification Steps:**
            1. Open Command Prompt or PowerShell
            2. Run: `node --version`
            3. Run: `npm --version`
            4. Both commands should return version numbers
            
            **Troubleshooting:**
            - Restart your computer after installing Node.js
            - Make sure Node.js is added to your system PATH
            - Try running the app again after installation
            """)
        
        # Still allow the user to proceed, but with warnings
        if st.button("🚀 Continue Anyway (Build features may not work)"):
            st.session_state.environment_verified = True
            st.rerun()
    
    logger.info(f"Environment verification result: {success} - {message}")

def render_file_upload_tab():
    """Render the file upload tab."""
    st.header("📁 File Upload")
    
    file_upload = FileUploadComponent()
    
    # Environment check
    env_valid = file_upload.render_environment_check()
    
    if not env_valid:
        st.stop()
    
    st.divider()
    
    # File uploads
    col1, col2 = st.columns(2)
    
    with col1:
        excel_path = file_upload.render_excel_upload()
        if excel_path:
            st.session_state.excel_path = excel_path
    
    with col2:
        word_path = file_upload.render_word_upload()
        if word_path:
            st.session_state.word_path = word_path
    
    st.divider()
    
    # File upload summary
    can_proceed = file_upload.render_file_upload_summary(
        st.session_state.excel_path,
        st.session_state.word_path
    )
    
    # Load files button
    if can_proceed and not st.session_state.files_loaded:
        if st.button("📂 Load Files", type="primary"):
            with st.spinner("Loading files..."):
                success, message = st.session_state.processor.load_files(
                    st.session_state.excel_path,
                    st.session_state.word_path
                )
                
                if success:
                    st.session_state.files_loaded = True
                    st.success(message)
                    st.rerun()
                else:
                    st.error(message)
    
    elif st.session_state.files_loaded:
        st.success("✅ Files loaded successfully!")
        
        # Show loaded data preview
        students_data = st.session_state.processor.get_excel_handler().get_students_data()
        if students_data is not None:
            st.subheader("📊 Student Data Preview")
            st.dataframe(students_data.head(10), use_container_width=True)
            
            if len(students_data) > 10:
                st.info(f"Showing first 10 of {len(students_data)} students")
        
        # Show requirements if loaded
        word_parser = st.session_state.processor.get_word_parser()
        requirements = word_parser.get_requirements_list()
        
        if requirements:
            st.subheader("📋 Assignment Requirements")
            requirements_summary = word_parser.generate_requirements_summary()
            st.text(requirements_summary)

def render_processing_tab():
    """Render the processing tab."""
    st.header("🚀 Processing")
    
    if not st.session_state.files_loaded:
        st.warning("⚠️ Please upload and load files first in the File Upload tab")
        return
    
    if st.session_state.processing_complete:
        st.success("✅ Processing already completed!")
        
        # Show option to restart
        if st.button("🔄 Start New Processing", type="secondary"):
            st.session_state.processing_started = False
            st.session_state.processing_complete = False
            st.session_state.current_student_index = 0
            st.session_state.processing_results = []
            st.rerun()
        
        return
    
    # Processing controls
    col1, col2 = st.columns(2)
    
    with col1:
        if not st.session_state.processing_started:
            if st.button("▶️ Start Grading Process", type="primary"):
                st.session_state.processing_started = True
                st.rerun()
        else:
            if st.button("⏹️ Stop Processing", type="secondary"):
                st.session_state.processor.stop_processing()
                st.warning("Stop requested...")
    
    with col2:
        if st.session_state.processing_started:
            st.info("🔄 Processing in progress...")
    
    # Progress tracking
    if st.session_state.processing_started:
        students_data = st.session_state.processor.get_excel_handler().get_students_data()
        
        if students_data is not None:
            st.session_state.progress_tracker.initialize(len(students_data))
            
            # Create progress containers
            st.session_state.progress_containers = st.session_state.progress_tracker.render_progress_header()
            
            # Show real-time logs
            st.subheader("📋 Processing Logs")
            log_container = st.container()
            
            with log_container:
                if 'processing_logs' in st.session_state and st.session_state.processing_logs:
                    # Show last 10 log entries
                    recent_logs = st.session_state.processing_logs[-10:]
                    for log_entry in recent_logs:
                        st.markdown(log_entry)
                else:
                    st.info("Waiting for processing to start...")
            
            st.divider()
            
            # Start processing
            with st.spinner("Processing assignments..."):
                try:
                    success, message = st.session_state.processor.start_processing()
                    
                    if success:
                        st.session_state.processing_complete = True
                        st.success(f"🎉 {message}")
                        
                        # Show final statistics
                        stats = st.session_state.processor.get_results_summary()
                        st.session_state.progress_tracker.render_summary_stats(stats)
                        
                        st.rerun()
                    else:
                        st.error(f"❌ {message}")
                
                except Exception as e:
                    st.error(f"Processing failed: {str(e)}")
                    logger.error(f"Processing error: {str(e)}")

def render_results_tab():
    """Render the results tab."""
    st.header("📊 Results")
    
    if not st.session_state.processing_complete:
        st.info("ℹ️ Results will be available after processing is complete")
        return
    
    # Get results data
    excel_handler = st.session_state.processor.get_excel_handler()
    students_data = excel_handler.get_students_data()
    summary_stats = excel_handler.get_summary_stats()
    
    if students_data is None or students_data.empty:
        st.warning("No results data available")
        return
    
    # Create results display
    results_display = ResultsDisplay()
    
    # Results overview
    results_display.render_results_overview(summary_stats)
    
    st.divider()
    
    # Visualizations
    col1, col2 = st.columns(2)
    
    with col1:
        results_display.render_grade_distribution(students_data)
    
    with col2:
        results_display.render_build_status_overview(students_data)
    
    st.divider()
    
    # Detailed results
    results_display.render_detailed_results_table(students_data)
    
    st.divider()
    
    # Requirements analysis
    word_parser = st.session_state.processor.get_word_parser()
    if word_parser.get_requirements_list():
        results_display.render_requirements_analysis(word_parser)
        st.divider()
    
    # Download options
    results_display.render_download_options(excel_handler, students_data)

def render_help_tab():
    """Render the help tab."""
    st.header("📋 Help & Documentation")
    
    # Quick start guide
    with st.expander("🚀 Quick Start Guide", expanded=True):
        st.markdown("""
        ### Getting Started
        1. **Check Environment**: Ensure Node.js 16+ and npm are installed
        2. **Upload Files**: 
           - Excel file with student names and GitHub URLs
           - Word document with assignment requirements (optional)
        3. **Load Files**: Click "Load Files" to validate and load your data
        4. **Start Processing**: Begin the automated grading process
        5. **Review Results**: View grades, statistics, and download reports
        
        ### File Requirements
        **Excel File must contain:**
        - `Name` column with student names
        - `GitHubRepoURL` column with repository links
        
        **Word Document should include:**
        - Assignment requirements as bullet points
        - Point values for different sections (optional)
        """)
    
    # Troubleshooting
    with st.expander("🔧 Troubleshooting"):
        st.markdown("""
        ### Common Issues
        
        **Environment Problems:**
        - Install Node.js from https://nodejs.org/
        - Restart your terminal after installation
        - Verify with `node --version` and `npm --version`
        
        **File Upload Issues:**
        - Ensure Excel file has required columns
        - Check that GitHub URLs are public repositories
        - Word document should be in .docx format
        
        **Build Failures:**
        - Check if student repositories contain valid React projects
        - Verify package.json exists with React dependencies
        - Some repositories might be private or deleted
        
        **Performance Issues:**
        - Reduce concurrent processes in sidebar settings
        - Increase timeout values for slow builds
        - Enable cleanup to save disk space
        """)
    
    # File format examples
    with st.expander("📄 File Format Examples"):
        st.markdown("### Excel File Example")
        example_excel = pd.DataFrame({
            'Name': ['Alice Johnson', 'Bob Smith', 'Carol Davis'],
            'StudentID': ['CS001', 'CS002', 'CS003'],
            'Email': ['alice@uni.edu', 'bob@uni.edu', 'carol@uni.edu'],
            'GitHubRepoURL': [
                'https://github.com/alice/react-todo',
                'https://github.com/bob/react-weather',
                'https://github.com/carol/react-calculator'
            ]
        })
        st.dataframe(example_excel)
        
        st.markdown("### Word Document Example")
        st.code("""
Technical Requirements (40 points):
• Project must build successfully
• Use Create React App or Vite
• Include proper package.json

Component Structure (30 points):
• Minimum 3 functional components
• Proper props usage
• State management with hooks

UI/Styling (20 points):
• Responsive design
• Professional appearance
• CSS organization

Code Quality (10 points):
• Clean code practices
• Proper file organization
• No console errors
        """, language='markdown')
    
    # About
    with st.expander("ℹ️ About"):
        st.markdown(f"""
        ### Assignment Grading Agent
        
        **Version:** {config.APP_VERSION}  
        **Purpose:** Automated grading system for React assignments  
        **Developer:** Built with Python, Streamlit, and ❤️
        
        **Features:**
        - Automated GitHub repository cloning
        - React project build validation
        - Comprehensive grading reports
        - Excel integration for easy data management
        - Real-time progress tracking
        
        **System Requirements:**
        - Python 3.10+
        - Node.js 16+
        - npm
        - Git
        """)

if __name__ == "__main__":
    main()
