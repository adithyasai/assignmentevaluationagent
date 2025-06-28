"""
File upload interface components for Streamlit UI.
"""
import streamlit as st
from pathlib import Path
from typing import Optional, Tuple
import config
from src.utils.file_validator import FileValidator


class FileUploadComponent:
    """Handles file upload functionality in the Streamlit interface."""
    
    def __init__(self):
        """Initialize the file upload component."""
        self.validator = FileValidator()
    
    def render_excel_upload(self) -> Optional[str]:
        """
        Render Excel file upload interface.
        
        Returns:
            Path to uploaded file or None if no file uploaded
        """
        st.subheader("📊 Upload Student Data (Excel)")
        
        # File uploader
        uploaded_file = st.file_uploader(
            "Choose Excel file with student information",
            type=['xlsx', 'xls'],
            help="Excel file must contain 'Name' and 'GitHubRepoURL' columns"
        )
        
        if uploaded_file is not None:
            # Save uploaded file temporarily
            temp_path = config.TEMP_DIR / f"uploaded_{uploaded_file.name}"
            
            try:
                with open(temp_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                
                # Validate the file
                is_valid, errors, warnings = self.validator.validate_excel_file(str(temp_path))
                
                # Display validation results
                if is_valid:
                    st.success("✅ Excel file is valid!")
                    
                    # Show file info
                    file_info = self.validator.get_file_info(str(temp_path))
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.metric("File Size", file_info.get('size', 'Unknown'))
                    with col2:
                        st.metric("File Type", file_info.get('extension', 'Unknown'))
                    with col3:
                        st.metric("Modified", file_info.get('modified', 'Unknown')[:10] if file_info.get('modified') else 'Unknown')
                    
                    # Show warnings if any
                    if warnings:
                        st.warning("⚠️ Warnings found:")
                        for warning in warnings:
                            st.write(f"• {warning}")
                    
                    return str(temp_path)
                else:
                    st.error("❌ Excel file validation failed:")
                    for error in errors:
                        st.write(f"• {error}")
                    
                    if warnings:
                        st.warning("Additional warnings:")
                        for warning in warnings:
                            st.write(f"• {warning}")
                
            except Exception as e:
                st.error(f"Failed to process uploaded file: {str(e)}")
        
        # Show example format
        with st.expander("📋 View Required Excel Format"):
            st.write("Your Excel file should have the following columns:")
            
            example_data = {
                'Name': ['Alice Johnson', 'Bob Smith', 'Carol Davis'],
                'GitHubRepoURL': [
                    'https://github.com/alice/react-todo',
                    'https://github.com/bob/react-weather',
                    'https://github.com/carol/react-calculator'
                ],
                'StudentID': ['CS2023001', 'CS2023002', 'CS2023003'],
                'Email': ['alice@university.edu', 'bob@university.edu', 'carol@university.edu']
            }
            
            st.table(example_data)
            st.write("**Required columns:** Name, GitHubRepoURL")
            st.write("**Optional columns:** StudentID, Email")
        
        return None
    
    def render_word_upload(self) -> Optional[str]:
        """
        Render Word document upload interface.
        
        Returns:
            Path to uploaded file or None if no file uploaded
        """
        st.subheader("📄 Upload Assignment Requirements (Word)")
        
        # File uploader
        uploaded_file = st.file_uploader(
            "Choose Word document with assignment requirements",
            type=['docx', 'doc'],
            help="Word document should contain assignment requirements and grading criteria"
        )
        
        if uploaded_file is not None:
            # Save uploaded file temporarily
            temp_path = config.TEMP_DIR / f"uploaded_{uploaded_file.name}"
            
            try:
                with open(temp_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                
                # Validate the file
                is_valid, errors, warnings = self.validator.validate_word_file(str(temp_path))
                
                # Display validation results
                if is_valid:
                    st.success("✅ Word document is valid!")
                    
                    # Show file info
                    file_info = self.validator.get_file_info(str(temp_path))
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.metric("File Size", file_info.get('size', 'Unknown'))
                    with col2:
                        st.metric("File Type", file_info.get('extension', 'Unknown'))
                    with col3:
                        st.metric("Modified", file_info.get('modified', 'Unknown')[:10] if file_info.get('modified') else 'Unknown')
                    
                    # Show warnings if any
                    if warnings:
                        st.warning("⚠️ Warnings found:")
                        for warning in warnings:
                            st.write(f"• {warning}")
                    
                    return str(temp_path)
                else:
                    st.error("❌ Word document validation failed:")
                    for error in errors:
                        st.write(f"• {error}")
                    
                    if warnings:
                        st.warning("Additional warnings:")
                        for warning in warnings:
                            st.write(f"• {warning}")
                
            except Exception as e:
                st.error(f"Failed to process uploaded file: {str(e)}")
        
        # Show example format
        with st.expander("📝 View Example Requirements Format"):
            st.write("Your Word document should contain structured requirements like:")
            
            example_requirements = """
**Technical Requirements (40 points):**
• Project must build successfully without errors
• Use Create React App or Vite as build tool
• Include package.json with proper dependencies
• Application must start with npm start

**Component Structure (30 points):**
• Minimum 3 functional components
• Proper component composition and hierarchy
• Use of props for data passing
• State management with useState hook

**Styling & UI (20 points):**
• Responsive design implementation
• CSS modules or styled-components usage
• Clean and professional appearance
• Mobile-friendly interface

**Code Quality (10 points):**
• Proper file organization
• Meaningful variable and function names
• Clean code practices
• No console errors in browser
            """
            
            st.code(example_requirements, language='markdown')
        
        return None
    
    def render_file_upload_summary(self, excel_path: Optional[str], word_path: Optional[str]) -> bool:
        """
        Render summary of uploaded files.
        
        Args:
            excel_path: Path to Excel file
            word_path: Path to Word file
            
        Returns:
            True if both files are uploaded, False otherwise
        """
        st.subheader("📁 File Upload Summary")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if excel_path:
                st.success("✅ Student data Excel file uploaded")
                st.write(f"📊 **File:** {Path(excel_path).name}")
            else:
                st.error("❌ No Excel file uploaded")
                st.write("📊 **Status:** Missing student data")
        
        with col2:
            if word_path:
                st.success("✅ Requirements Word document uploaded")
                st.write(f"📄 **File:** {Path(word_path).name}")
            else:
                st.warning("⚠️ No Word document uploaded")
                st.write("📄 **Status:** Will use default grading criteria")
        
        # Overall status
        both_uploaded = excel_path is not None and word_path is not None
        excel_only = excel_path is not None and word_path is None
        
        if both_uploaded:
            st.success("🎉 Ready to start grading process!")
            return True
        elif excel_only:
            st.info("ℹ️ Can proceed with basic grading (Excel file only)")
            return True
        else:
            st.error("🚫 Cannot proceed without student data (Excel file)")
            return False
    
    def render_environment_check(self) -> bool:
        """
        Render environment validation check.
        
        Returns:
            True if environment is valid, False otherwise
        """
        st.subheader("🔧 Environment Check")
        
        from src.utils.build_checker import BuildChecker
        build_checker = BuildChecker()
        
        with st.spinner("Checking Node.js environment..."):
            is_valid, env_message = build_checker.verify_environment()
        
        if is_valid:
            st.success("✅ Node.js environment is ready!")
            st.info(f"Details: {env_message}")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Node.js", "✅ Available")
            with col2:
                st.metric("npm", "✅ Available")
            with col3:
                st.metric("Status", "Ready")
            
            return True
        else:
            st.error("❌ Node.js environment check failed!")
            st.error(f"Error: {env_message}")
            
            st.warning("Please ensure Node.js 16+ and npm are installed and accessible from PATH")
            
            with st.expander("🔧 Installation Help"):
                st.write("To install Node.js:")
                st.write("1. Visit https://nodejs.org/")
                st.write("2. Download and install Node.js LTS version")
                st.write("3. Restart your terminal/command prompt")
                st.write("4. Refresh this page to check again")
            
            return False
