"""
Main assignment processing engine for the Assignment Agent.
"""
import asyncio
from concurrent.futures import ThreadPoolExecutor
from typing import Callable, Dict, List, Optional, Tuple
from loguru import logger
import config
from src.utils.repo_cloner import RepoCloner
from src.utils.build_checker import BuildChecker
from src.utils.grader import Grader
from src.utils.excel_handler import ExcelHandler
from src.utils.word_parser import WordParser
from src.utils.functional_tester import FunctionalTester


class AssignmentProcessor:
    """Main processing engine that orchestrates the grading workflow."""
    
    def __init__(self):
        """Initialize the assignment processor."""
        self.repo_cloner = RepoCloner()
        self.build_checker = BuildChecker()
        self.grader = Grader()
        self.excel_handler = ExcelHandler()
        self.word_parser = WordParser()
        self.functional_tester = FunctionalTester()
        
        self.is_processing = False
        self.should_stop = False
        self.progress_callback: Optional[Callable] = None
    
    def set_progress_callback(self, callback: Callable):
        """
        Set callback function for progress updates.
        
        Args:
            callback: Function to call with progress updates
        """
        self.progress_callback = callback
    
    def load_files(self, excel_path: str, word_path: Optional[str] = None) -> Tuple[bool, str]:
        """
        Load and validate input files.
        
        Args:
            excel_path: Path to Excel file with student data
            word_path: Optional path to Word file with requirements
            
        Returns:
            Tuple of (success, message)
        """
        try:
            # Load Excel file
            success, message = self.excel_handler.load_students_file(excel_path)
            if not success:
                return False, f"Failed to load Excel file: {message}"
            
            # Load Word file if provided
            if word_path:
                success, message = self.word_parser.parse_requirements_document(word_path)
                if not success:
                    logger.warning(f"Failed to parse Word document: {message}")
                    # Continue without requirements - use basic grading
                else:
                    # Set requirements for grader
                    requirements = self.word_parser.get_requirements_list()
                    point_values = self.word_parser.get_point_values()
                    self.grader.set_requirements(requirements, point_values)
            
            students_data = self.excel_handler.get_students_data()
            student_count = len(students_data) if students_data is not None else 0
            
            logger.info(f"Successfully loaded files: {student_count} students")
            return True, f"Files loaded successfully. {student_count} students found."
            
        except Exception as e:
            logger.error(f"Error loading files: {str(e)}")
            return False, f"Error loading files: {str(e)}"
    
    def start_processing(self, max_concurrent: int = 3, test_mode: bool = False, dynamic_batching: bool = True) -> Tuple[bool, str]:
        """
        Start the main grading process.
        
        Args:
            max_concurrent: Maximum number of concurrent processes
            test_mode: If True, only process first 2 records for testing (default: False)
            dynamic_batching: If True, automatically calculate optimal batch size (default: True)
            
        Returns:
            Tuple of (success, message)
        """
        if self.is_processing:
            return False, "Processing is already in progress"
        
        try:
            self.is_processing = True
            self.should_stop = False
            
            students_data = self.excel_handler.get_students_data()
            if students_data is None or students_data.empty:
                return False, "No student data loaded"
            
            # Limit to first 2 records in test mode
            if test_mode:
                students_data = students_data.head(2)
                logger.info(f"🧪 TEST MODE: Processing only first {len(students_data)} students")
            
            # Store total for progress tracking
            self.total_students = len(students_data)
            
            # Calculate optimal batch size dynamically
            if dynamic_batching:
                batch_size = self._calculate_optimal_batch_size(self.total_students)
                logger.info(f"🧮 Dynamic batching enabled: Calculated optimal batch size of {batch_size} for {self.total_students} students")
            else:
                batch_size = 50  # Default fallback
                logger.info(f"📦 Fixed batching: Using batch size of {batch_size}")
            
            total_batches = (self.total_students + batch_size - 1) // batch_size
            logger.info(f"Starting processing for {self.total_students} students in {total_batches} batches")
            
            # Process students in batches for memory management
            success_count = 0
            error_count = 0
            
            for batch_num in range(total_batches):
                if self.should_stop:
                    logger.info("Processing stopped by user")
                    break
                
                start_idx = batch_num * batch_size
                end_idx = min(start_idx + batch_size, self.total_students)
                batch_data = students_data.iloc[start_idx:end_idx]
                
                logger.info(f"📦 Processing batch {batch_num + 1}/{total_batches} (students {start_idx + 1}-{end_idx})")
                
                # Process current batch
                batch_success, batch_error = self._process_batch(batch_data, start_idx)
                success_count += batch_success
                error_count += batch_error
                
                # Cleanup repositories after each batch to free memory
                if batch_num < total_batches - 1:  # Don't cleanup on last batch
                    logger.info(f"🧹 Cleaning up batch {batch_num + 1} repositories...")
                    self.repo_cloner.cleanup_all_repositories()
            
            self.is_processing = False
            
            # Final statistics
            total_processed = success_count + error_count
            message = f"Processing completed: {success_count} successful, {error_count} failed out of {total_processed} students"
            
            logger.info(message)
            return True, message
            
        except Exception as e:
            self.is_processing = False
            logger.error(f"Error during processing: {str(e)}")
            return False, f"Processing failed: {str(e)}"
    
    def _process_batch(self, batch_data, start_index: int) -> Tuple[int, int]:
        """
        Process a batch of students.
        
        Args:
            batch_data: DataFrame with batch of students to process
            start_index: Starting index for this batch
            
        Returns:
            Tuple of (success_count, error_count)
        """
        success_count = 0
        error_count = 0
        
        for relative_idx, (index, row) in enumerate(batch_data.iterrows()):
            if self.should_stop:
                break
                
            student_info = self.excel_handler.get_student_info(index)
            if not student_info:
                continue
            
            # Update progress
            if self.progress_callback:
                self.progress_callback(
                    student_name=student_info['name'],
                    status="Starting processing",
                    current_index=index
                )
            
            # Process individual student
            success = self._process_student(student_info, index)
            
            if success:
                success_count += 1
            else:
                error_count += 1
        
        return success_count, error_count
    
    def _calculate_optimal_batch_size(self, total_students: int) -> int:
        """
        Calculate optimal batch size based on total number of students.
        
        Algorithm:
        - 1-20 students: Process all at once (batch_size = total)
        - 21-50 students: Divide into 2-5 batches
        - 51-100 students: Divide into 4-10 batches  
        - 101-200 students: Divide into 8-16 batches
        - 201-500 students: Divide into 10-20 batches
        - 500+ students: Use batch size of 25-50
        
        Args:
            total_students: Total number of students to process
            
        Returns:
            Optimal batch size
        """
        if total_students <= 20:
            # Small datasets - process all at once
            return total_students
        elif total_students <= 50:
            # Medium datasets - aim for 2-5 batches
            target_batches = min(5, max(2, total_students // 10))
            return max(10, total_students // target_batches)
        elif total_students <= 100:
            # Large datasets - aim for 4-10 batches
            target_batches = min(10, max(4, total_students // 12))
            return max(10, total_students // target_batches)
        elif total_students <= 200:
            # Very large datasets - aim for 8-16 batches
            target_batches = min(16, max(8, total_students // 15))
            return max(12, total_students // target_batches)
        elif total_students <= 500:
            # Extra large datasets - aim for 10-20 batches
            target_batches = min(20, max(10, total_students // 20))
            return max(15, total_students // target_batches)
        else:
            # Massive datasets - use fixed optimal batch size
            return 25
    
    def _evaluate_project_requirements(self, local_path: str, project_info: Dict, build_success: bool, functional_results: Dict = None) -> Dict:
        """
        Evaluate project against requirements document.
        
        Args:
            local_path: Path to the cloned repository
            project_info: Information about the project structure
            build_success: Whether the build was successful
            functional_results: Results from functional testing (optional)
            
        Returns:
            Dictionary with evaluation results
        """
        evaluation = {
            'requirements_met': [],
            'requirements_failed': [],
            'code_quality_score': 0,
            'functionality_score': 0,
            'file_structure_score': 0,
            'total_score': 0,
            'detailed_analysis': []
        }
        
        try:
            logger.info(f"🔍 Starting comprehensive project evaluation...")
            
            # Get requirements from word parser
            requirements = self.word_parser.get_requirements_list()
            point_values = self.word_parser.get_point_values()
            
            if not requirements:
                logger.info(f"📝 No requirements document found, using basic evaluation")
                evaluation['detailed_analysis'].append("No requirements document provided - using basic evaluation criteria")
                return self._basic_project_evaluation(local_path, project_info, build_success, functional_results)
            
            logger.info(f"📋 Found {len(requirements)} requirements to evaluate")
            
            # 1. File Structure Analysis (20 points)
            structure_score = self._evaluate_file_structure(local_path, requirements)
            evaluation['file_structure_score'] = structure_score
            evaluation['detailed_analysis'].append(f"File Structure: {structure_score}/20 points")
            
            # 2. Code Quality Analysis (20 points)
            quality_score = self._evaluate_code_quality(local_path)
            evaluation['code_quality_score'] = quality_score
            evaluation['detailed_analysis'].append(f"Code Quality: {quality_score}/20 points")
            
            # 3. Build & Basic Functionality (20 points)
            build_score = self._evaluate_build_functionality(local_path, requirements, build_success)
            evaluation['build_score'] = build_score
            evaluation['detailed_analysis'].append(f"Build & Basic Functionality: {build_score}/20 points")
            
            # 4. End-to-End Functionality (25 points) - NEW!
            if functional_results:
                functional_score = functional_results.get('functionality_score', 0)
                # Scale to 25 points max
                functional_score = min(25, functional_score * 25 / 100)
                evaluation['e2e_functionality_score'] = functional_score
                evaluation['detailed_analysis'].append(f"End-to-End Functionality: {functional_score}/25 points")
                
                # Add detailed functional test results
                for detail in functional_results.get('test_details', []):
                    evaluation['detailed_analysis'].append(f"  {detail}")
            else:
                evaluation['e2e_functionality_score'] = 0
                evaluation['detailed_analysis'].append("End-to-End Functionality: 0/25 points (testing skipped)")
            
            # 5. Requirements Matching (15 points)
            requirements_score = self._evaluate_requirements_matching(local_path, requirements, point_values)
            evaluation['requirements_score'] = requirements_score
            evaluation['detailed_analysis'].append(f"Requirements Met: {requirements_score}/15 points")
            
            # Calculate total score (out of 100)
            evaluation['total_score'] = (structure_score + quality_score + build_score + 
                                       evaluation['e2e_functionality_score'] + requirements_score)
            
            logger.info(f"✅ Evaluation completed: {evaluation['total_score']}/100 points")
            return evaluation
            
        except Exception as e:
            logger.error(f"❌ Error during project evaluation: {str(e)}")
            evaluation['detailed_analysis'].append(f"Evaluation error: {str(e)}")
            return evaluation
    
    def _basic_project_evaluation(self, local_path: str, project_info: Dict, build_success: bool, functional_results: Dict = None) -> Dict:
        """Basic evaluation when no requirements document is available."""
        evaluation = {
            'requirements_met': [],
            'requirements_failed': [],
            'code_quality_score': 15 if build_success else 5,
            'build_score': 20 if build_success else 5,
            'file_structure_score': 20 if project_info.get('has_package_json') else 10,
            'e2e_functionality_score': 0,
            'requirements_score': 15 if build_success else 5,
            'total_score': 0,
            'detailed_analysis': ['Basic evaluation - no requirements document']
        }
        
        # Add functional testing score if available
        if functional_results:
            functional_score = functional_results.get('functionality_score', 0)
            functional_score = min(25, functional_score * 25 / 100)
            evaluation['e2e_functionality_score'] = functional_score
            evaluation['detailed_analysis'].append(f"End-to-End Functionality: {functional_score}/25 points")
        
        evaluation['total_score'] = (evaluation['code_quality_score'] + 
                                   evaluation['build_score'] + 
                                   evaluation['file_structure_score'] + 
                                   evaluation['e2e_functionality_score'] +
                                   evaluation['requirements_score'])
        
        return evaluation
    
    def _evaluate_file_structure(self, local_path: str, requirements: List[str]) -> int:
        """Evaluate React project file structure."""
        score = 0
        import os
        
        # Check for standard React files and folders
        standard_files = ['package.json', 'src/', 'public/', 'README.md']
        react_files = ['src/App.js', 'src/App.jsx', 'src/index.js', 'src/index.jsx']
        
        for file_path in standard_files:
            full_path = os.path.join(local_path, file_path)
            if os.path.exists(full_path):
                score += 5
                logger.debug(f"✅ Found: {file_path}")
            else:
                logger.debug(f"❌ Missing: {file_path}")
        
        # Check for React entry files
        has_react_entry = any(os.path.exists(os.path.join(local_path, rf)) for rf in react_files)
        if has_react_entry:
            score += 5
            logger.debug(f"✅ Found React entry file")
        
        return min(score, 20)
    
    def _evaluate_code_quality(self, local_path: str) -> int:
        """Evaluate code quality based on file analysis."""
        score = 0
        import os
        import re
        
        try:
            # Check src directory for React components
            src_path = os.path.join(local_path, 'src')
            if not os.path.exists(src_path):
                return 5
            
            js_files = []
            for root, dirs, files in os.walk(src_path):
                for file in files:
                    if file.endswith(('.js', '.jsx', '.ts', '.tsx')):
                        js_files.append(os.path.join(root, file))
            
            if len(js_files) == 0:
                return 5
            
            # Analyze files for quality indicators
            has_components = False
            has_imports = False
            has_exports = False
            proper_naming = False
            
            for file_path in js_files[:5]:  # Check first 5 files
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                        
                        # Check for React patterns
                        if re.search(r'import.*React', content) or re.search(r'from [\'"]react[\'"]', content):
                            has_imports = True
                        
                        if re.search(r'export\s+default', content) or re.search(r'export\s+{', content):
                            has_exports = True
                        
                        if re.search(r'function\s+[A-Z]\w*|const\s+[A-Z]\w*\s*=.*=>', content):
                            has_components = True
                            proper_naming = True
                            
                except Exception:
                    continue
            
            # Score based on quality indicators
            if has_imports: score += 5
            if has_exports: score += 5
            if has_components: score += 8
            if proper_naming: score += 7
            
            logger.debug(f"Code quality indicators: imports={has_imports}, exports={has_exports}, components={has_components}")
            
        except Exception as e:
            logger.debug(f"Code quality evaluation error: {str(e)}")
            score = 10
        
        return min(score, 20)
    
    def _evaluate_build_functionality(self, local_path: str, requirements: List[str], build_success: bool) -> int:
        """Evaluate build success and basic functionality indicators."""
        score = 0
        
        # Base score for successful build
        if build_success:
            score += 20
            logger.debug(f"✅ Build successful: +20 points")
        else:
            score += 5
            logger.debug(f"❌ Build failed: +5 points")
        
        # Additional functionality checks
        try:
            import os
            
            # Check for routing (if mentioned in requirements)
            if any('route' in req.lower() or 'navigation' in req.lower() for req in requirements):
                router_files = ['Router', 'router', 'Route', 'route']
                src_path = os.path.join(local_path, 'src')
                
                if os.path.exists(src_path):
                    for root, dirs, files in os.walk(src_path):
                        for file in files:
                            if any(router in file for router in router_files):
                                score += 5
                                logger.debug(f"✅ Found routing implementation: +5 points")
                                break
            
            # Check for state management
            if any('state' in req.lower() or 'useState' in req.lower() for req in requirements):
                score += 5
                logger.debug(f"✅ State management indicated: +5 points")
        
        except Exception as e:
            logger.debug(f"Functionality evaluation error: {str(e)}")
        
        return min(score, 20)
    
    def _evaluate_requirements_matching(self, local_path: str, requirements: List[str], point_values: List[int]) -> int:
        """Evaluate how well the project matches specific requirements."""
        score = 0
        total_possible = sum(point_values) if point_values else 20
        
        try:
            import os
            
            # Read all source files to check for requirement keywords
            src_content = ""
            src_path = os.path.join(local_path, 'src')
            
            if os.path.exists(src_path):
                for root, dirs, files in os.walk(src_path):
                    for file in files:
                        if file.endswith(('.js', '.jsx', '.ts', '.tsx')):
                            try:
                                with open(os.path.join(root, file), 'r', encoding='utf-8', errors='ignore') as f:
                                    src_content += f.read().lower() + " "
                            except:
                                continue
            
            # Check requirements against source code
            for i, requirement in enumerate(requirements):
                req_lower = requirement.lower()
                point_value = point_values[i] if i < len(point_values) else 2
                
                # Simple keyword matching (can be enhanced)
                keywords = req_lower.split()
                matches = sum(1 for keyword in keywords if len(keyword) > 2 and keyword in src_content)
                
                if matches >= len(keywords) // 2:  # At least half the keywords found
                    score += point_value
                    logger.debug(f"✅ Requirement matched: '{requirement}' (+{point_value} points)")
                else:
                    logger.debug(f"❌ Requirement not matched: '{requirement}'")
        
        except Exception as e:
            logger.debug(f"Requirements matching error: {str(e)}")
            score = 10  # Give some points for effort
        
        # Scale to 15 points max
        return min(int((score / total_possible) * 15), 15)
    
    def _process_student(self, student_info: Dict[str, str], index: int) -> bool:
        """
        Process a single student's assignment.
        
        Args:
            student_info: Dictionary with student information
            index: Student index in the Excel file
            
        Returns:
            True if processing successful, False otherwise
        """
        student_name = student_info['name']
        github_url = student_info['github_url']
        
        try:
            logger.info(f"🎓 Starting processing for student: {student_name}")
            logger.info(f"📂 GitHub URL: {github_url}")
            
            # Step 1: Clone repository
            if self.progress_callback:
                self.progress_callback(
                    student_name=student_name,
                    status="Cloning repository",
                    current_index=index
                )
            
            logger.info(f"📥 Cloning repository for {student_name}...")
            clone_success, clone_message, local_path = self.repo_cloner.clone_repository(github_url, student_name)
            
            if clone_success:
                logger.info(f"✅ Repository cloned successfully to: {local_path}")
            else:
                logger.error(f"❌ Repository clone failed: {clone_message}")
            
            if not clone_success:
                logger.error(f"❌ Failed to clone repository for {student_name}: {clone_message}")
                self.excel_handler.update_student_result(
                    index=index,
                    build_status=config.BUILD_STATUS['ERROR'],
                    grade=0,
                    feedback=f"Repository clone failed: {clone_message}",
                    build_errors=clone_message
                )
                return False
            
            # Step 2: Verify React project
            if self.progress_callback:
                self.progress_callback(
                    student_name=student_name,
                    status="Verifying React project",
                    current_index=index
                )
            
            logger.info(f"🔍 Verifying React project structure for {student_name}...")
            is_react, verify_message, project_info = self.repo_cloner.verify_react_project(local_path)
            
            if is_react:
                logger.info(f"✅ Valid React project detected")
                logger.info(f"📋 Project info: {project_info}")
            else:
                logger.warning(f"⚠️ Not a valid React project: {verify_message}")
            
            if not is_react:
                logger.warning(f"⚠️ Not a valid React project for {student_name}: {verify_message}")
                self.excel_handler.update_student_result(
                    index=index,
                    build_status=config.BUILD_STATUS['ERROR'],
                    grade=0,
                    feedback=f"Invalid React project: {verify_message}",
                    build_errors=verify_message
                )
                
                # Cleanup
                if config.CLEANUP_AFTER_PROCESSING:
                    self.repo_cloner.cleanup_repository(local_path)
                
                return False
            
            # Step 3: Install dependencies
            if self.progress_callback:
                self.progress_callback(
                    student_name=student_name,
                    status="Installing dependencies",
                    current_index=index
                )
            
            package_manager = project_info.get('package_manager', 'npm')
            logger.info(f"📦 Installing dependencies using {package_manager} for {student_name}...")
            install_success, install_stdout, install_stderr = self.build_checker.install_dependencies(
                local_path, package_manager
            )
            
            if install_success:
                logger.info(f"✅ Dependencies installed successfully")
                if install_stdout:
                    logger.debug(f"Install stdout: {install_stdout[:500]}...")
            else:
                logger.error(f"❌ Dependency installation failed")
                logger.error(f"Install stderr: {install_stderr}")
                logger.error(f"Install stdout: {install_stdout}")
            
            if not install_success:
                logger.error(f"❌ Dependency installation failed for {student_name}")
                self.excel_handler.update_student_result(
                    index=index,
                    build_status=config.BUILD_STATUS['FAILED'],
                    grade=config.GRADING_SCALE['BUILD_FAILURE'],
                    feedback="Dependency installation failed. Check package.json and dependencies.",
                    build_errors=f"Install stdout: {install_stdout}\nInstall stderr: {install_stderr}"
                )
                
                # Cleanup
                if config.CLEANUP_AFTER_PROCESSING:
                    self.repo_cloner.cleanup_repository(local_path)
                
                return False
            
            # Step 4: Build project
            if self.progress_callback:
                self.progress_callback(
                    student_name=student_name,
                    status="Building project",
                    current_index=index
                )
            
            logger.info(f"🔨 Building project for {student_name}...")
            build_success, build_stdout, build_stderr = self.build_checker.build_project(
                local_path, package_manager
            )
            
            if build_success:
                logger.info(f"✅ Project built successfully")
                if build_stdout:
                    logger.debug(f"Build stdout: {build_stdout[:500]}...")
            else:
                logger.error(f"❌ Project build failed")
                logger.error(f"Build stderr: {build_stderr}")
                logger.error(f"Build stdout: {build_stdout}")
            
            # Step 5: Analyze build output
            if self.progress_callback:
                self.progress_callback(
                    student_name=student_name,
                    status="Analyzing build results",
                    current_index=index
                )
            
            logger.info(f"📊 Analyzing build output for {student_name}...")
            build_output = self.build_checker.check_build_output(local_path)
            
            # Step 6: Functional Testing (End-to-End)
            if self.progress_callback:
                self.progress_callback(
                    student_name=student_name,
                    status="Testing functionality",
                    current_index=index
                )
            
            # Step 6: Run functional tests (End-to-End Testing)
            if self.progress_callback:
                self.progress_callback(
                    student_name=student_name,
                    status="Running functional tests (E2E testing)",
                    current_index=index
                )
            
            logger.info(f"🧪 Running end-to-end functional tests for {student_name}...")
            logger.info(f"🎯 Testing: button clicks, navigation, forms, and app functionality")
            
            # Run functional tests
            requirements = self.word_parser.get_requirements_list()
            functional_results = self.functional_tester.test_react_app_functionality(
                local_path, requirements, package_manager
            )
            
            # Log functional test results
            if functional_results:
                logger.info(f"🔬 Functional test summary:")
                logger.info(f"  📱 App loads: {functional_results.get('app_loads', False)}")
                logger.info(f"  🔘 Buttons work: {functional_results.get('buttons_work', False)}")
                logger.info(f"  🧭 Navigation works: {functional_results.get('navigation_works', False)}")
                logger.info(f"  📝 Forms work: {functional_results.get('forms_work', False)}")
                logger.info(f"  🎯 Functionality score: {functional_results.get('functionality_score', 0)}/100")
            else:
                logger.warning(f"⚠️ Functional tests could not be completed")
            
            # Step 7: Evaluate requirements and functionality (Enhanced Grading)
            if self.progress_callback:
                self.progress_callback(
                    student_name=student_name,
                    status="Evaluating requirements",
                    current_index=index
                )
            
            logger.info(f"📋 Evaluating requirements and functionality for {student_name}...")
            
            # Perform comprehensive evaluation (including functional test results)
            evaluation_result = self._evaluate_project_requirements(local_path, project_info, build_success, functional_results)
            
            # Step 8: Calculate grade and generate feedback
            logger.info(f"🎯 Calculating comprehensive grade for {student_name}...")
            build_result = {
                'success': build_success,
                'stdout': build_stdout,
                'stderr': build_stderr,
                'warnings': build_output.get('warnings', []),
                'errors': build_output.get('errors', []),
                'build_output': build_output,
                'evaluation': evaluation_result
            }
            
            has_warnings = len(build_result['warnings']) > 0
            
            # Enhanced grading based on requirements
            if len(self.word_parser.get_requirements_list()) > 0:
                grade, detailed_feedback = self.grader.calculate_requirements_based_grade(
                    build_result, evaluation_result, student_name
                )
                logger.info(f"📊 Requirements-based grading applied")
            else:
                grade, detailed_feedback = self.grader.calculate_basic_grade(build_success, has_warnings)
                logger.info(f"📊 Basic grading applied (no requirements document)")
            
            logger.info(f"📝 Grade calculated: {grade}/100 (Build success: {build_success}, Has warnings: {has_warnings})")
            feedback_lines = detailed_feedback.split('\n')
            logger.info(f"💬 Detailed feedback generated with {len(feedback_lines)} evaluation points")
            
            # Step 9: Update results
            if build_success:
                status = config.BUILD_STATUS['SUCCESS']
                if has_warnings:
                    status = config.BUILD_STATUS['WARNING']
            else:
                status = config.BUILD_STATUS['FAILED']
            
            logger.info(f"📊 Final status for {student_name}: {status}")
            
            build_errors = ""
            if not build_success:
                # Analyze errors for better reporting
                error_analysis = self.build_checker.analyze_build_errors(build_stderr, build_stdout)
                build_errors = f"Build stderr: {build_stderr}\nBuild stdout: {build_stdout}"
                
                if error_analysis.get('suggestions'):
                    build_errors += f"\nSuggestions: {'; '.join(error_analysis['suggestions'])}"
            
            logger.info(f"💾 Updating Excel results for {student_name}...")
            self.excel_handler.update_student_result(
                index=index,
                build_status=status,
                grade=grade,
                feedback=detailed_feedback,
                build_errors=build_errors
            )
            
            logger.info(f"✅ Successfully processed {student_name} - Grade: {grade}/100")
            
            # Step 10: Cleanup
            if config.CLEANUP_AFTER_PROCESSING:
                self.repo_cloner.cleanup_repository(local_path)
            
            if self.progress_callback:
                self.progress_callback(
                    student_name=student_name,
                    status=f"Completed - {status}",
                    current_index=index,
                    success=build_success
                )
            
            logger.info(f"Successfully processed {student_name}: Grade {grade}, Status {status}")
            return True
            
        except Exception as e:
            logger.error(f"💥 Unexpected error processing {student_name}: {str(e)}")
            logger.error(f"📊 Current progress state: student {index} of {self.total_students if hasattr(self, 'total_students') else 'unknown'}")
            
            # Make sure progress callback doesn't cause additional errors
            try:
                if self.progress_callback:
                    self.progress_callback(
                        student_name=student_name,
                        status="Error occurred",
                        current_index=index,
                        success=False
                    )
            except Exception as callback_error:
                logger.error(f"💥 Progress callback error: {str(callback_error)}")
            
            self.excel_handler.update_student_result(
                index=index,
                build_status=config.BUILD_STATUS['ERROR'],
                grade=0,
                feedback=f"Processing error: {str(e)}",
                build_errors=f"System error: {str(e)}"
            )
            
            return False
    
    def stop_processing(self):
        """Stop the current processing operation."""
        self.should_stop = True
        logger.info("Processing stop requested")
    
    def get_processing_status(self) -> Dict[str, any]:
        """
        Get current processing status.
        
        Returns:
            Dictionary with processing status information
        """
        return {
            'is_processing': self.is_processing,
            'should_stop': self.should_stop,
            'students_loaded': self.excel_handler.get_students_data() is not None,
            'requirements_loaded': len(self.word_parser.get_requirements_list()) > 0
        }
    
    def get_results_summary(self) -> Dict[str, any]:
        """
        Get summary of processing results.
        
        Returns:
            Dictionary with results summary
        """
        try:
            return self.excel_handler.get_summary_stats()
        except Exception as e:
            logger.error(f"Error getting results summary: {str(e)}")
            return {}
    
    def cleanup_all(self):
        """Clean up all temporary files and resources."""
        try:
            cleaned, errors = self.repo_cloner.cleanup_all_repositories()
            logger.info(f"Cleanup completed: {cleaned} directories cleaned, {errors} errors")
        except Exception as e:
            logger.error(f"Error during cleanup: {str(e)}")
    
    def validate_environment(self) -> Tuple[bool, Dict[str, any]]:
        """
        Validate the processing environment.
        
        Returns:
            Tuple of (is_valid, environment_info)
        """
        try:
            success, message = self.build_checker.verify_environment()
            
            if success:
                # Parse versions from message or get them separately
                env_info = {
                    'status': 'ready',
                    'message': message,
                    'node_version': 'Available',
                    'npm_version': 'Available',
                    'errors': []
                }
            else:
                env_info = {
                    'status': 'error',
                    'message': message,
                    'node_version': 'Not Found',
                    'npm_version': 'Not Found',
                    'errors': [message]
                }
            
            return success, env_info
            
        except Exception as e:
            logger.error(f"Error validating environment: {str(e)}")
            return False, {
                'status': 'error',
                'message': f"Environment validation failed: {str(e)}",
                'errors': [str(e)]
            }
    
    def get_excel_handler(self) -> ExcelHandler:
        """Get the Excel handler instance."""
        return self.excel_handler
    
    def get_word_parser(self) -> WordParser:
        """Get the Word parser instance."""
        return self.word_parser
