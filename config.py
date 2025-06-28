"""
Configuration settings and constants for the Assignment Agent.
"""
import os
from pathlib import Path
from typing import Dict, List

# Application Settings
APP_TITLE = "🤖 React Assignment Grading Agent"
APP_VERSION = "1.0.0-beta"
APP_DESCRIPTION = "Automated grading system for React assignments"

# Directory Paths
BASE_DIR = Path(__file__).parent
TEMP_DIR = BASE_DIR / "temp"
REPOS_DIR = TEMP_DIR / "repos"
LOGS_DIR = BASE_DIR / "logs"
DATA_DIR = BASE_DIR / "data"

# Ensure directories exist
for directory in [TEMP_DIR, REPOS_DIR, LOGS_DIR, DATA_DIR]:
    directory.mkdir(exist_ok=True)

# File Settings
SUPPORTED_EXCEL_EXTENSIONS = ['.xlsx', '.xls']
SUPPORTED_WORD_EXTENSIONS = ['.docx', '.doc']
MAX_FILE_SIZE_MB = 50

# Excel Column Names
EXCEL_COLUMNS = {
    'REQUIRED': {
        'NAME': 'Name',
        'GITHUB_URL': 'GitHubRepoURL'
    },
    'OPTIONAL': {
        'STUDENT_ID': 'StudentID',
        'EMAIL': 'Email'
    },
    'OUTPUT': {
        'BUILD_STATUS': 'BuildStatus',
        'GRADE': 'Grade',
        'FEEDBACK': 'Feedback',
        'PROCESSED_AT': 'ProcessedAt',
        'BUILD_ERRORS': 'BuildErrors'
    }
}

# Build Settings
BUILD_TIMEOUT_SECONDS = 300  # 5 minutes
INSTALL_TIMEOUT_SECONDS = 600  # 10 minutes
CLEANUP_AFTER_PROCESSING = True

# Grading Settings
GRADING_SCALE = {
    'BUILD_SUCCESS': 100,
    'BUILD_WITH_WARNINGS': 50,
    'BUILD_FAILURE': 0
}

# React Project Requirements
REACT_REQUIRED_FILES = ['package.json']
REACT_BUILD_COMMANDS = {
    'INSTALL': 'npm install',
    'BUILD': 'npm run build',
    'START': 'npm start'
}

# GitHub Settings
GITHUB_CLONE_TIMEOUT = 300  # 5 minutes - increased for large repos
GITHUB_API_TIMEOUT = 30

# Logging Configuration
LOG_FORMAT = "{time:YYYY-MM-DD HH:mm:ss} | {level} | {name}:{function}:{line} | {message}"
LOG_FILE = LOGS_DIR / "grading_agent.log"
LOG_ROTATION = "10 MB"
LOG_RETENTION = "1 week"

# UI Settings
STREAMLIT_CONFIG = {
    'page_title': APP_TITLE,
    'page_icon': '🤖',
    'layout': 'wide',
    'initial_sidebar_state': 'expanded'
}

# Error Messages
ERROR_MESSAGES = {
    'FILE_NOT_FOUND': "File not found. Please check the file path.",
    'INVALID_FILE_FORMAT': "Invalid file format. Please upload a valid file.",
    'GITHUB_CLONE_FAILED': "Failed to clone GitHub repository.",
    'BUILD_FAILED': "React application build failed.",
    'NETWORK_ERROR': "Network connection error.",
    'PERMISSION_ERROR': "Permission denied. Check file access rights."
}

# Success Messages
SUCCESS_MESSAGES = {
    'FILE_UPLOADED': "File uploaded successfully!",
    'REPO_CLONED': "Repository cloned successfully.",
    'BUILD_SUCCESS': "Build completed successfully!",
    'GRADING_COMPLETE': "Grading process completed!"
}

# Status Constants
BUILD_STATUS = {
    'SUCCESS': 'Success',
    'FAILED': 'Failed',
    'ERROR': 'Error',
    'WARNING': 'Warning',
    'PENDING': 'Pending',
    'PROCESSING': 'Processing'
}

# File naming patterns
OUTPUT_FILE_PATTERNS = {
    'GRADED_EXCEL': 'students_graded_{timestamp}.xlsx',
    'HTML_REPORT': 'grading_report_{timestamp}.html',
    'ERROR_LOG': 'error_log_{timestamp}.txt',
    'SUMMARY_STATS': 'summary_stats_{timestamp}.json'
}
