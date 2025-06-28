# Assignment Grading Agent

A comprehensive Python-based Assignment Grading Agent for React assignments. This application automates the grading process by cloning student GitHub repositories, building React applications, and updating an Excel file with results through an intuitive Streamlit web interface.

## Features

- **Automated GitHub Repository Processing**: Clone and validate student repositories
- **React Project Building**: Automatically install dependencies and build React applications
- **Requirements Parsing**: Extract assignment requirements from Word documents
- **Excel Integration**: Load student data from Excel files and update with grades
- **Progress Tracking**: Real-time progress visualization during grading
- **Comprehensive Reporting**: Generate detailed reports in multiple formats (HTML, JSON, CSV)
- **Error Handling**: Robust error handling with detailed logging
- **Modern UI**: Clean, intuitive Streamlit interface with multiple tabs

## Prerequisites

- Python 3.8 or higher
- Node.js and npm (for building React projects)
- Git (for cloning repositories)

## Installation

1. **Clone or download this project to your local machine**

2. **Install Python dependencies:**
   ```powershell
   cd "d:\Personal\Projects\AssignmentAgent"
   py -m pip install -r requirements.txt
   ```

3. **Verify Node.js and npm are installed:**
   ```powershell
   node --version
   npm --version
   ```

## Quick Start

1. **Run the application:**
   ```powershell
   cd "d:\Personal\Projects\AssignmentAgent"
   py -m streamlit run app.py
   ```

2. **Open your web browser** and navigate to the URL shown in the terminal (typically `http://localhost:8501`)

3. **Use the sample files** for testing:
   - Sample Excel file: `data/sample_students.xlsx`
   - Sample requirements document: `data/sample_requirements.docx`

## Usage

### Step 1: File Upload
- Upload an Excel file containing student information (Name, GitHub Repository URL)
- Upload a Word document containing assignment requirements
- The application will validate both files automatically

### Step 2: Start Grading
- Review the uploaded files and requirements
- Click "Start Grading Process" to begin automated grading
- Monitor real-time progress through the progress tracker

### Step 3: Review Results
- View grading results in an interactive table
- Download updated Excel file with grades and feedback
- Generate comprehensive reports in various formats
- View analytics and statistics

## File Formats

### Excel File Structure
The Excel file should contain the following columns:
- **Name**: Student's full name
- **GitHub Repository**: Full GitHub repository URL
- **Grade**: (Optional) Will be populated by the system
- **Feedback**: (Optional) Will be populated by the system
- **Status**: (Optional) Will be populated by the system

### Requirements Document
The Word document should contain:
- Assignment description and objectives
- Technical requirements and specifications
- Grading criteria and rubric
- Any special instructions or considerations

## Project Structure

```
AssignmentAgent/
├── src/
│   ├── core/           # Core grading logic
│   ├── ui/             # Streamlit UI components
│   └── utils/          # Utility functions
├── data/               # Sample and processed data files
├── logs/               # Application logs
├── temp/               # Temporary files (cloned repos)
├── Instruction/        # Project documentation
├── app.py              # Main Streamlit application
├── config.py           # Configuration settings
├── requirements.txt    # Python dependencies
└── README.md           # This file
```

## Configuration

Key configuration options can be modified in `config.py`:

- **Repository handling**: Clone timeouts, retry attempts
- **Build settings**: Node.js commands, build timeouts
- **Grading parameters**: Default scores, weight distributions
- **File paths**: Temporary directories, log locations
- **UI settings**: Streamlit configuration

## Troubleshooting

### Common Issues

1. **"Python was not found"**
   - Use `py` command instead of `python`
   - Ensure Python is installed and in PATH

2. **Node.js/npm not found**
   - Install Node.js from [nodejs.org](https://nodejs.org)
   - Restart terminal after installation

3. **Git clone failures**
   - Ensure Git is installed and configured
   - Check repository URLs are valid and accessible
   - Verify network connectivity

4. **Excel file errors**
   - Ensure Excel file has required columns
   - Check file is not corrupted or password-protected

### Logs

Application logs are stored in the `logs/` directory:
- `assignment_agent.log`: Main application log
- Error details and debugging information

## Sample Data

The application includes sample data for testing:
- `data/sample_students.xlsx`: Sample student roster
- `data/sample_requirements.docx`: Sample assignment requirements

Generate new sample data by running:
```powershell
py create_sample_data.py
```

## Development

### Adding New Features

1. **Grading Logic**: Modify `src/utils/grader.py`
2. **UI Components**: Add to `src/ui/`
3. **Core Processing**: Extend `src/core/assignment_processor.py`
4. **Utilities**: Add helper functions to `src/utils/`

### Testing

Use the sample data files for testing new features:
1. Start the application
2. Upload sample files
3. Run grading process
4. Verify results and logs

## License

This project is for educational purposes. Please ensure you have appropriate permissions when accessing student repositories and grading data.

## Support

For issues or questions:
1. Check the logs in the `logs/` directory
2. Review error messages in the Streamlit interface
3. Verify all prerequisites are installed correctly
4. Ensure sample data works before using real data

---

**Note**: This application is designed for educational use. Always respect student privacy and institutional policies when handling assignment data.
