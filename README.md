# 🤖 Assignment Grading Agent

An advanced **automated grading system** for React assignments that combines static code analysis with **end-to-end functional testing**. This application clones student GitHub repositories, builds React applications, performs comprehensive UI testing, and evaluates assignments against requirements documents with detailed scoring and feedback.

## 🚀 Key Features

### **Comprehensive Evaluation System**
- **Static Code Analysis**: File structure, code quality, and React patterns validation
- **Build Verification**: Automated dependency installation and project building
- **End-to-End Functional Testing**: Real browser automation testing (forms, buttons, navigation)
- **Requirements-Based Grading**: Automatic evaluation against Word document specifications
- **Multi-Criteria Scoring**: 100-point scale across 5 evaluation categories

### **Advanced Functional Testing**
- **Cross-Browser Testing**: Playwright, Selenium, and BeautifulSoup integration
- **UI Interaction Testing**: Button clicks, form submissions, navigation flows
- **Adaptive Form Detection**: Recognizes diverse contact form implementations
- **Dynamic Content Testing**: Tests React state changes and user interactions
- **Error Resilience**: Multiple fallback testing strategies

### **Enterprise-Grade Processing**
- **Batch Processing**: Dynamic batch sizing for optimal performance
- **Memory Management**: Automatic cleanup and resource optimization
- **Progress Tracking**: Real-time progress with detailed logging
- **Error Recovery**: Robust error handling with detailed diagnostics
- **Scalable Architecture**: Handles large classes (100+ students)

### **Professional Reporting**
- **Detailed Feedback**: Comprehensive analysis with specific improvement suggestions
- **Multi-Format Export**: Excel, HTML, JSON, CSV report generation
- **Analytics Dashboard**: Success rates, common issues, performance metrics
- **Audit Trail**: Complete logging of all grading decisions and processes

## 🛠️ Tech Stack

### **Backend & Core Processing**
- **Python 3.8+**: Core application logic and processing engine
- **Streamlit**: Modern web interface with real-time updates
- **Pandas**: Data manipulation and Excel file processing
- **python-docx**: Word document parsing and requirements extraction
- **GitPython**: Repository cloning and Git operations
- **Loguru**: Advanced logging and debugging

### **Frontend Testing & Automation**
- **Playwright**: Modern browser automation (primary testing engine)
- **Selenium**: Cross-browser compatibility testing (fallback)
- **BeautifulSoup**: HTML parsing and static content analysis
- **Asyncio**: Asynchronous processing for improved performance

### **Build & Development Tools**
- **Node.js & NPM**: React project building and dependency management
- **Git**: Version control and repository access
- **Threading**: Concurrent processing for batch operations
- **JSON/CSV**: Data export and configuration management

### **File Processing & Data Handling**
- **openpyxl**: Excel file reading and writing
- **pathlib**: Cross-platform file path handling
- **tempfile**: Secure temporary file management
- **os/subprocess**: System command execution

## 📊 Grading Algorithm

The system uses a **comprehensive 100-point evaluation scale**:

### **1. File Structure Analysis (20 points)**
- React project structure validation
- Essential files presence (`package.json`, `src/`, `public/`)
- React entry points verification
- Component organization assessment

### **2. Code Quality Evaluation (20 points)**
- React patterns and best practices
- Import/export structure analysis
- Component naming conventions
- Modern JavaScript/JSX usage

### **3. Build & Dependencies (20 points)**
- Dependency installation success
- Build process completion
- Warning and error analysis
- Package.json validation

### **4. End-to-End Functionality (25 points)**
- **Application Loading**: Tests if the React app starts successfully
- **UI Interaction**: Button clicks, navigation, user flows
- **Form Testing**: Contact forms, input validation, submission
- **Dynamic Content**: State changes, React component behavior
- **Browser Compatibility**: Cross-browser testing results

### **5. Requirements Compliance (15 points)**
- Word document requirements parsing
- Keyword matching and feature detection
- Specific functionality verification
- Assignment objective fulfillment

## 🧪 Functional Testing Capabilities

### **Contact Form Testing** (Example Use Case)
The system can evaluate diverse contact form implementations:

```python
# Different student implementations - all detected and tested:
# Student A: <form><input name="fullName">
# Student B: <input placeholder="Enter your name">
# Student C: <TextField label="Name" />
```

### **Testing Process**
1. **App Startup**: Launches React development server
2. **Page Loading**: Waits for application to fully load
3. **Element Discovery**: Finds interactive elements (forms, buttons)
4. **Interaction Testing**: Simulates user interactions
5. **Validation Testing**: Tests form validation and error handling
6. **Submission Testing**: Tests form submission workflows
7. **Results Analysis**: Scores functionality and provides feedback

### **Adaptive Recognition**
- **Field Detection**: Recognizes contact fields by name, placeholder, label, or type
- **Button Identification**: Finds submit buttons regardless of styling or framework
- **Form Discovery**: Locates forms using multiple CSS selectors and patterns
- **Error Handling**: Graceful degradation when elements aren't found

## 🏗️ Architecture Overview

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Streamlit UI  │───▶│ Assignment       │───▶│ Batch Processor │
│   (Frontend)    │    │ Processor        │    │ (Core Engine)   │
└─────────────────┘    │ (Orchestrator)   │    └─────────────────┘
                       └──────────────────┘             │
                                │                       │
                ┌───────────────┼───────────────────────┼──────────────┐
                │               │                       │              │
                ▼               ▼                       ▼              ▼
        ┌──────────────┐ ┌─────────────┐ ┌──────────────────┐ ┌──────────────┐
        │ Repo Cloner  │ │ Build       │ │ Functional       │ │ Grader &     │
        │ (Git Ops)    │ │ Checker     │ │ Tester           │ │ Feedback     │
        └──────────────┘ │ (Node.js)   │ │ (Playwright/     │ │ Generator    │
                         └─────────────┘ │  Selenium)       │ └──────────────┘
                                         └──────────────────┘
                                                   │
                         ┌─────────────────────────┼─────────────────────────┐
                         │                         │                         │
                         ▼                         ▼                         ▼
                ┌──────────────┐        ┌──────────────┐        ┌──────────────┐
                │ Excel        │        │ Word Parser  │        │ Report       │
                │ Handler      │        │ (Requirements│        │ Generator    │
                │ (Data I/O)   │        │  Extraction) │        │ (Multi-format│
                └──────────────┘        └──────────────┘        └──────────────┘
```

## ⚡ Quick Start

### **Prerequisites**
- **Python 3.8+**: Core runtime environment
- **Node.js & npm**: React project building
- **Git**: Repository access and cloning
- **Modern Browser**: For functional testing (auto-installed by Playwright)

### **Installation**

1. **Clone this repository:**
   ```powershell
   git clone <repository-url>
   cd AssignmentAgent
   ```

2. **Install Python dependencies:**
   ```powershell
   py -m pip install -r requirements.txt
   ```

3. **Install Playwright browsers:**
   ```powershell
   playwright install
   ```

4. **Verify Node.js setup:**
   ```powershell
   node --version
   npm --version
   ```

### **Launch Application**

```powershell
py -m streamlit run app.py
```

🌐 Open browser to: `http://localhost:8501`

## 📋 Usage Workflow

### **Step 1: File Preparation**
- **Excel File**: Student roster with Name and GitHub Repository columns
- **Word Document**: Assignment requirements and grading criteria
- **Sample Files**: Use `data/sample_students.xlsx` and `data/sample_requirements.docx` for testing

### **Step 2: Upload & Validation**
- Upload Excel file → System validates columns and data format
- Upload Word document → System extracts requirements and scoring criteria
- Review parsed requirements → Verify accuracy before processing

### **Step 3: Grading Configuration**
- **Test Mode**: Process first 2 students for verification
- **Batch Size**: Dynamic sizing (automatic) or manual configuration
- **Concurrency**: Set parallel processing limit (default: 3)

### **Step 4: Automated Processing**
For each student repository:
1. **Clone Repository** → Downloads and validates React project
2. **Install Dependencies** → Runs `npm install` or `yarn install`
3. **Build Project** → Executes `npm run build` 
4. **Launch App** → Starts development server
5. **Functional Testing** → Automated UI testing with browser automation
6. **Requirements Analysis** → Compares against Word document criteria
7. **Grade Calculation** → Comprehensive scoring across all categories
8. **Feedback Generation** → Detailed improvement suggestions

### **Step 5: Results & Reports**
- **Real-time Progress**: Live updates with detailed status
- **Interactive Results Table**: Sortable, filterable grade overview
- **Detailed Feedback**: Per-student analysis and suggestions
- **Export Options**: Updated Excel, HTML reports, JSON data, CSV summaries
- **Analytics Dashboard**: Class performance metrics and insights

## 📁 Project Structure

```
AssignmentAgent/
├── 📱 Frontend & UI
│   ├── app.py                          # Main Streamlit application
│   └── src/ui/                         # UI components and layouts
│
├── ⚙️ Core Processing Engine
│   ├── src/core/
│   │   ├── assignment_processor.py     # Main orchestration logic
│   │   ├── grade_calculator.py         # Advanced scoring algorithms
│   │   └── report_generator.py         # Multi-format report creation
│   │
├── 🛠️ Utility Modules
│   ├── src/utils/
│   │   ├── repo_cloner.py              # Git operations and repository management
│   │   ├── build_checker.py            # Node.js build and dependency handling
│   │   ├── functional_tester.py        # End-to-end browser automation testing
│   │   ├── grader.py                   # Grading logic and feedback generation
│   │   ├── excel_handler.py            # Excel file processing and updates
│   │   └── word_parser.py              # Requirements document parsing
│   │
├── 📊 Data & Configuration
│   ├── data/                           # Sample files and processed data
│   │   ├── sample_students.xlsx        # Example student roster
│   │   └── sample_requirements.docx    # Example assignment requirements
│   ├── config.py                       # Application configuration
│   └── requirements.txt                # Python dependencies
│
├── 📝 Documentation & Tooling
│   ├── README.md                       # This comprehensive guide
│   ├── .gitignore                      # Version control exclusions
│   ├── Instruction/                    # Project documentation
│   └── create_sample_data.py           # Sample data generator
│
└── 🗂️ Runtime Directories
    ├── temp/                           # Temporary cloned repositories
    ├── logs/                           # Application logs and debugging
    └── reports/                        # Generated grading reports
```

## 🔧 Advanced Configuration

### **Core Settings** (`config.py`)

```python
# Grading Scale Distribution
GRADING_SCALE = {
    'FILE_STRUCTURE': 20,    # React project structure
    'CODE_QUALITY': 20,      # Code patterns and best practices  
    'BUILD_SUCCESS': 20,     # Compilation and dependencies
    'E2E_FUNCTIONALITY': 25, # End-to-end testing results
    'REQUIREMENTS': 15       # Assignment-specific criteria
}

# Processing Configuration
BATCH_PROCESSING = {
    'DYNAMIC_SIZING': True,      # Auto-calculate optimal batch size
    'MAX_CONCURRENT': 3,         # Parallel processing limit
    'MEMORY_MANAGEMENT': True,   # Auto-cleanup between batches
    'TIMEOUT_SETTINGS': {
        'CLONE': 300,            # Git clone timeout (seconds)
        'BUILD': 600,            # Build process timeout
        'TEST': 180              # Functional test timeout
    }
}

# Functional Testing Configuration  
TESTING_CONFIG = {
    'PRIMARY_ENGINE': 'playwright',     # playwright|selenium|beautifulsoup
    'FALLBACK_ENABLED': True,          # Enable fallback testing
    'BROWSER_TIMEOUT': 30,             # Page load timeout
    'INTERACTION_DELAY': 1,            # Delay between interactions
    'SCREENSHOT_ON_ERROR': True        # Capture screenshots for debugging
}
```

### **Environment Variables**

Create `.env` file for sensitive configuration:
```bash
# Optional: GitHub token for private repositories
GITHUB_TOKEN=your_github_token_here

# Optional: Custom Node.js path
NODE_PATH=/custom/path/to/node

# Optional: Logging level
LOG_LEVEL=INFO
```

## 🎯 Use Cases & Examples

### **Example 1: Contact Form Assignment**
**Requirements Document Contains:**
- "Create a contact form with name, email, and message fields"
- "Form should validate email format"
- "Display success message after submission"

**System Automatically Tests:**
- ✅ Form presence and field detection
- ✅ Email validation functionality
- ✅ Form submission workflow  
- ✅ Success/error message display
- ✅ User interaction flows

### **Example 2: Multi-Page React App**
**Requirements Document Contains:**
- "Implement navigation between Home, About, and Contact pages"
- "Use React Router for client-side routing"
- "Include responsive navigation menu"

**System Automatically Tests:**
- ✅ Navigation menu functionality
- ✅ Route transitions and page loads
- ✅ Responsive design elements
- ✅ React Router implementation
- ✅ URL changes during navigation

### **Example 3: Interactive Component**
**Requirements Document Contains:**
- "Create a counter component with increment/decrement buttons"
- "Display current count value"
- "Reset functionality"

**System Automatically Tests:**
- ✅ Button click interactions
- ✅ State updates and display
- ✅ Reset functionality
- ✅ Component responsiveness
- ✅ Error handling

## 🚨 Troubleshooting

### **Common Issues & Solutions**

#### **🔧 Environment Setup**
```powershell
# Python not found
py --version                    # Verify Python installation
py -m pip install --upgrade pip # Update pip

# Node.js issues  
node --version && npm --version # Verify installation
npm install -g npm@latest      # Update npm

# Git access problems
git --version                   # Verify Git installation
git config --global user.name "Your Name"  # Configure Git
```

#### **🌐 Functional Testing Issues**
```powershell
# Playwright browser installation
playwright install              # Install all browsers
playwright install chromium     # Install specific browser

# Permission errors
# Run as administrator or check antivirus settings
```

#### **📊 Processing Errors**
- **Excel file issues**: Ensure required columns (Name, GitHub Repository)
- **Repository access**: Verify URLs are public or provide GitHub token
- **Build failures**: Check Node.js version compatibility (14+ recommended)
- **Memory issues**: Reduce batch size or increase system RAM

### **🔍 Debug Information**

#### **Log Files Location**
```
logs/
├── assignment_agent.log        # Main application log
├── functional_testing.log      # UI testing details  
├── build_processes.log         # Node.js build logs
└── error_reports.log           # Error analysis and solutions
```

#### **Verbose Logging**
Set environment variable for detailed debugging:
```powershell
$env:LOG_LEVEL="DEBUG"
py -m streamlit run app.py
```

## 📈 Performance & Scalability

### **Recommended System Requirements**

| Class Size | RAM | CPU Cores | Processing Time |
|------------|-----|-----------|-----------------|
| 1-20 students | 8GB | 4 cores | 15-30 minutes |
| 21-50 students | 16GB | 6 cores | 30-60 minutes |
| 51-100 students | 32GB | 8 cores | 1-2 hours |
| 100+ students | 32GB+ | 12+ cores | 2+ hours |

### **Optimization Strategies**
- **Dynamic Batching**: Automatically calculates optimal batch sizes
- **Memory Management**: Cleans up repositories between batches
- **Concurrent Processing**: Parallel execution with configurable limits
- **Incremental Processing**: Resume from last processed student
- **Resource Monitoring**: Real-time memory and CPU usage tracking

## 🔒 Security & Privacy

### **Data Protection**
- **Local Processing**: All data stays on your machine
- **Temporary Files**: Automatic cleanup of cloned repositories
- **No Data Transmission**: No student data sent to external services
- **Access Control**: Repository access uses standard Git permissions

### **Best Practices**
- Use `.gitignore` to exclude student data from version control
- Regular cleanup of `temp/` and `logs/` directories
- Secure storage of GitHub tokens in environment variables
- Review generated reports before sharing

## 🤝 Contributing & Development

### **Adding New Features**

#### **1. New Testing Strategies**
```python
# Extend functional_tester.py
def test_custom_functionality(self, app_url, requirements):
    # Implement new testing logic
    pass
```

#### **2. Custom Grading Criteria** 
```python
# Extend grader.py
def calculate_custom_grade(self, build_result, custom_criteria):
    # Implement custom scoring logic
    pass
```

#### **3. Additional File Formats**
```python
# Create new parser in src/utils/
class PDFParser:
    def parse_requirements(self, pdf_path):
        # Implement PDF parsing logic
        pass
```

### **Testing Framework**
```powershell
# Run with sample data
py -m streamlit run app.py
# Upload data/sample_students.xlsx and data/sample_requirements.docx

# Create custom test data
py create_sample_data.py --students 5 --requirements custom
```

## 📜 License & Academic Use

This project is designed for **educational purposes** and automated grading in academic environments.

### **Usage Guidelines**
- ✅ Educational institutions and instructors
- ✅ Academic research and development
- ✅ Student project evaluation and feedback
- ❌ Commercial grading services without permission
- ❌ Plagiarism detection (not designed for this purpose)

### **Ethical Considerations**
- Always inform students about automated grading processes
- Provide human review for contested grades
- Respect student privacy and data protection laws
- Use secure, institution-approved systems for sensitive data

## 📞 Support & Documentation

### **Getting Help**
1. **Check Logs**: Review `logs/assignment_agent.log` for detailed error information
2. **Sample Data**: Test with provided sample files to isolate issues
3. **Environment**: Verify all prerequisites are correctly installed
4. **Configuration**: Review `config.py` settings for your use case

### **Feature Requests & Issues**
- Detailed error logs and reproduction steps help with troubleshooting
- Include system specifications and Python/Node.js versions
- Test with sample data to confirm issues

---

## 🎓 Educational Impact

This Assignment Grading Agent represents a **significant advancement** in automated educational assessment, combining traditional static analysis with modern **end-to-end functional testing** to provide comprehensive, fair, and detailed evaluation of student React projects.

**Key Educational Benefits:**
- **Consistent Grading**: Eliminates human bias and inconsistency
- **Detailed Feedback**: Provides specific, actionable improvement suggestions  
- **Time Efficiency**: Allows instructors to focus on teaching rather than repetitive grading
- **Scalability**: Handles large classes with consistent quality
- **Real-World Skills**: Tests actual functionality, not just code structure

**Perfect for evaluating diverse student implementations** where creativity is encouraged but functionality requirements must be met - such as contact forms, interactive components, and multi-page applications.
