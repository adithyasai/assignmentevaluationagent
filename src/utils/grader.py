"""
Grading logic and score calculation for the Assignment Agent.
"""
from typing import Dict, List, Optional, Tuple
from datetime import datetime
from loguru import logger
import config
import os
import json
import re
from pathlib import Path


class Grader:
    """Handles grading logic and score calculation for React assignments."""
    
    def __init__(self):
        """Initialize the grader with default settings."""
        self.grading_scale = config.GRADING_SCALE.copy()
        self.requirements = []
        self.grading_criteria = {}
        self.point_values = {}
        self.total_possible_points = 100
    
    def set_requirements(self, requirements: List[str], point_values: Optional[Dict[str, int]] = None):
        """
        Set the assignment requirements for grading.
        
        Args:
            requirements: List of requirement strings
            point_values: Optional dictionary mapping requirements to point values
        """
        self.requirements = requirements.copy()
        if point_values:
            self.point_values = point_values.copy()
            self.total_possible_points = sum(point_values.values())
        logger.info(f"Set {len(requirements)} requirements for grading")
        logger.info(f"Point distribution: {self.point_values}")
    
    def set_grading_criteria(self, grading_criteria: Dict[str, List[str]]):
        """
        Set detailed grading criteria organized by sections.
        
        Args:
            grading_criteria: Dictionary mapping section names to requirement lists
        """
        self.grading_criteria = grading_criteria.copy()
        logger.info(f"Set grading criteria for {len(grading_criteria)} sections")
    
    def calculate_requirements_based_grade(self, local_path: str, build_result: Dict[str, any], 
                                         project_info: Dict[str, any]) -> Tuple[int, str, Dict[str, any]]:
        """
        Calculate grade based on requirements document and functional testing.
        
        Args:
            local_path: Path to the cloned repository
            build_result: Build results dictionary
            project_info: Project analysis information
            
        Returns:
            Tuple of (grade, detailed_feedback, evaluation_details)
        """
        logger.info("🔍 Starting requirements-based grading evaluation...")
        
        evaluation_details = {
            'sections_evaluated': {},
            'total_points_earned': 0,
            'total_points_possible': self.total_possible_points,
            'build_score': 0,
            'functionality_score': 0,
            'code_quality_score': 0,
            'requirements_met': [],
            'requirements_missed': []
        }
        
        # Base score from build success (30% of total grade)
        build_score = self._evaluate_build_quality(build_result)
        evaluation_details['build_score'] = build_score
        
        # Evaluate each requirements section
        total_earned = 0
        total_possible = 0
        
        for section_name, section_requirements in self.grading_criteria.items():
            section_points = self.point_values.get(section_name, 20)  # Default 20 points per section
            
            logger.info(f"📋 Evaluating section: {section_name} ({section_points} points)")
            
            section_score, section_details = self._evaluate_requirements_section(
                local_path, section_name, section_requirements, build_result, project_info
            )
            
            earned_points = int((section_score / 100) * section_points)
            total_earned += earned_points
            total_possible += section_points
            
            evaluation_details['sections_evaluated'][section_name] = {
                'score_percentage': section_score,
                'points_earned': earned_points,
                'points_possible': section_points,
                'details': section_details
            }
            
            # Track requirements
            evaluation_details['requirements_met'].extend(section_details.get('met', []))
            evaluation_details['requirements_missed'].extend(section_details.get('missed', []))
        
        # Calculate final grade
        if total_possible > 0:
            final_grade = min(100, int((total_earned / total_possible) * 100))
        else:
            # Fallback to basic grading if no requirements
            final_grade = build_score
        
        evaluation_details['total_points_earned'] = total_earned
        evaluation_details['functionality_score'] = final_grade
        
        # Generate detailed feedback
        detailed_feedback = self._generate_requirements_feedback(evaluation_details, local_path)
        
        logger.info(f"🎯 Final requirements-based grade: {final_grade}/100 ({total_earned}/{total_possible} points)")
        
        return final_grade, detailed_feedback, evaluation_details
    
    def calculate_requirements_based_grade(self, build_result: Dict[str, any], evaluation_result: Dict[str, any], student_name: str) -> Tuple[int, str]:
        """
        Calculate grade based on comprehensive evaluation results.
        
        Args:
            build_result: Build results from assignment processor
            evaluation_result: Evaluation results from project analysis
            student_name: Name of the student
            
        Returns:
            Tuple of (grade, detailed_feedback)
        """
        logger.info(f"🎯 Calculating requirements-based grade for {student_name}...")
        
        # Use the total score from evaluation
        final_grade = min(100, max(0, evaluation_result.get('total_score', 0)))
        
        # Generate comprehensive feedback
        feedback_lines = [
            f"🎓 Comprehensive Evaluation Report for {student_name}",
            f"📊 Final Grade: {final_grade}/100",
            "",
            "📋 Evaluation Breakdown:",
        ]
        
        # Add detailed analysis
        for analysis_point in evaluation_result.get('detailed_analysis', []):
            feedback_lines.append(f"  • {analysis_point}")
        
        feedback_lines.extend([
            "",
            "🔍 Component Scores:",
            f"  • File Structure: {evaluation_result.get('file_structure_score', 0)}/20 points",
            f"  • Code Quality: {evaluation_result.get('code_quality_score', 0)}/20 points", 
            f"  • Build & Basic Functionality: {evaluation_result.get('build_score', 0)}/20 points",
            f"  • End-to-End Functionality: {evaluation_result.get('e2e_functionality_score', 0)}/25 points",
            f"  • Requirements Matching: {evaluation_result.get('requirements_score', 0)}/15 points",
        ])
        
        # Add build information
        if build_result.get('success'):
            feedback_lines.append("\n✅ Build Status: Successful")
        else:
            feedback_lines.append("\n❌ Build Status: Failed")
            if build_result.get('stderr'):
                feedback_lines.append(f"Build Errors: {build_result['stderr'][:200]}...")
        
        # Add requirements status
        if evaluation_result.get('requirements_met'):
            feedback_lines.append(f"\n✅ Requirements Met: {len(evaluation_result['requirements_met'])}")
        
        if evaluation_result.get('requirements_failed'):
            feedback_lines.append(f"❌ Requirements Not Met: {len(evaluation_result['requirements_failed'])}")
        
        # Grade interpretation
        if final_grade >= 90:
            feedback_lines.append("\n🌟 Excellent work! Your project meets all requirements with high quality implementation.")
        elif final_grade >= 75:
            feedback_lines.append("\n👍 Good work! Your project meets most requirements with some areas for improvement.")
        elif final_grade >= 60:
            feedback_lines.append("\n📝 Satisfactory work. Your project meets basic requirements but needs significant improvements.")
        else:
            feedback_lines.append("\n🔧 Your project needs substantial work to meet the assignment requirements.")
        
        detailed_feedback = "\n".join(feedback_lines)
        
        logger.info(f"✅ Requirements-based grade calculated: {final_grade}/100")
        return final_grade, detailed_feedback
    
    def calculate_basic_grade(self, build_success: bool, has_warnings: bool = False) -> Tuple[int, str]:
        """
        Calculate basic grade based on build success (Phase 1 implementation).
        
        Args:
            build_success: Whether the project built successfully
            has_warnings: Whether there were build warnings
            
        Returns:
            Tuple of (grade, feedback)
        """
        logger.info(f"🎯 Calculating grade - Build success: {build_success}, Has warnings: {has_warnings}")
        
        if build_success:
            if has_warnings:
                grade = self.grading_scale['BUILD_WITH_WARNINGS']
                feedback = "Project builds successfully but with warnings. Consider addressing the warnings for better code quality."
                logger.info(f"📊 Grade: {grade}/100 (Build with warnings)")
            else:
                grade = self.grading_scale['BUILD_SUCCESS']
                feedback = "Excellent! Project builds successfully without errors or warnings."
                logger.info(f"📊 Grade: {grade}/100 (Perfect build)")
        else:
            grade = self.grading_scale['BUILD_FAILURE']
            feedback = "Project failed to build. Please fix the compilation errors and ensure all dependencies are properly configured."
            logger.info(f"📊 Grade: {grade}/100 (Build failed)")
        
        logger.debug(f"💬 Feedback: {feedback}")
        return grade, feedback
    
    def calculate_comprehensive_grade(self, build_result: Dict[str, any], 
                                    project_analysis: Dict[str, any],
                                    requirements_met: Optional[List[str]] = None) -> Tuple[int, str]:
        """
        Calculate comprehensive grade based on multiple criteria (Future Phase 2).
        
        Args:
            build_result: Dictionary with build results
            project_analysis: Dictionary with project structure analysis
            requirements_met: Optional list of requirements that were met
            
        Returns:
            Tuple of (grade, detailed_feedback)
        """
        # This is a placeholder for future advanced grading logic
        # For now, fall back to basic grading
        build_success = build_result.get('success', False)
        has_warnings = len(build_result.get('warnings', [])) > 0
        
        base_grade, base_feedback = self.calculate_basic_grade(build_success, has_warnings)
        
        # Add bonus points for good project structure
        bonus_points = 0
        bonus_feedback = []
        
        if project_analysis.get('has_src_folder'):
            bonus_points += 2
            bonus_feedback.append("Good project structure with src folder")
        
        if project_analysis.get('has_public_folder'):
            bonus_points += 2
            bonus_feedback.append("Proper public folder structure")
        
        if project_analysis.get('has_readme'):
            bonus_points += 3
            bonus_feedback.append("Documentation provided with README")
        
        if project_analysis.get('has_tests'):
            bonus_points += 5
            bonus_feedback.append("Unit tests included")
        
        final_grade = min(base_grade + bonus_points, 100)
        
        detailed_feedback = base_feedback
        if bonus_feedback:
            detailed_feedback += f"\n\nBonus points earned (+{bonus_points}):\n" + "\n".join(f"• {fb}" for fb in bonus_feedback)
        
        logger.debug(f"Comprehensive grade calculated: {final_grade}/100 (base: {base_grade}, bonus: {bonus_points})")
        return final_grade, detailed_feedback
    
    def generate_detailed_feedback(self, student_name: str, build_result: Dict[str, any], 
                                 project_info: Dict[str, any], grade: int) -> str:
        """
        Generate detailed feedback for a student's submission.
        
        Args:
            student_name: Name of the student
            build_result: Build results dictionary
            project_info: Project analysis information
            grade: Calculated grade
            
        Returns:
            Detailed feedback string
        """
        feedback_parts = []
        
        # Header
        feedback_parts.append(f"Grading Report for {student_name}")
        feedback_parts.append(f"Grade: {grade}/100")
        feedback_parts.append(f"Processed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        feedback_parts.append("-" * 50)
        
        # Build Results
        feedback_parts.append("BUILD RESULTS:")
        if build_result.get('success'):
            feedback_parts.append("✅ Project builds successfully")
        else:
            feedback_parts.append("❌ Project failed to build")
        
        if build_result.get('warnings'):
            feedback_parts.append(f"⚠️  {len(build_result['warnings'])} warnings found")
        
        if build_result.get('errors'):
            feedback_parts.append(f"🚫 {len(build_result['errors'])} errors found")
        
        # Project Structure Analysis
        feedback_parts.append("\nPROJECT STRUCTURE:")
        
        structure_items = [
            ("package.json", project_info.get('has_package_json', False)),
            ("React dependency", project_info.get('has_react_dependency', False)),
            ("src/ folder", project_info.get('has_src_folder', False)),
            ("public/ folder", project_info.get('has_public_folder', False)),
            ("Build script", project_info.get('build_script', True))
        ]
        
        for item_name, has_item in structure_items:
            status = "✅" if has_item else "❌"
            feedback_parts.append(f"{status} {item_name}")
        
        # React Version Info
        if project_info.get('react_version'):
            feedback_parts.append(f"📦 React version: {project_info['react_version']}")
        
        if project_info.get('package_manager'):
            feedback_parts.append(f"📦 Package manager: {project_info['package_manager']}")
        
        # Build Output Analysis
        if 'build_output' in build_result:
            build_output = build_result['build_output']
            feedback_parts.append("\nBUILD OUTPUT:")
            
            if build_output.get('has_build_dir'):
                feedback_parts.append(f"✅ Build directory created")
                feedback_parts.append(f"📁 {build_output.get('file_count', 0)} files generated")
                feedback_parts.append(f"💾 Build size: {build_output.get('build_size_mb', 0)} MB")
                
                if build_output.get('has_index_html'):
                    feedback_parts.append("✅ index.html generated")
                if build_output.get('has_js_files'):
                    feedback_parts.append("✅ JavaScript files generated")
                if build_output.get('has_css_files'):
                    feedback_parts.append("✅ CSS files generated")
            else:
                feedback_parts.append("❌ No build output directory found")
        
        # Error Details
        if build_result.get('stderr') and not build_result.get('success'):
            feedback_parts.append("\nERROR DETAILS:")
            error_lines = build_result['stderr'].split('\n')[:10]  # First 10 lines
            for line in error_lines:
                if line.strip():
                    feedback_parts.append(f"  {line}")
            
            if len(build_result['stderr'].split('\n')) > 10:
                feedback_parts.append("  ... (additional errors truncated)")
        
        # Recommendations
        recommendations = self._generate_recommendations(build_result, project_info, grade)
        if recommendations:
            feedback_parts.append("\nRECOMMENDATIONS:")
            for rec in recommendations:
                feedback_parts.append(f"💡 {rec}")
        
        return "\n".join(feedback_parts)
    
    def _generate_recommendations(self, build_result: Dict[str, any], 
                                project_info: Dict[str, any], grade: int) -> List[str]:
        """
        Generate recommendations based on the grading results.
        
        Args:
            build_result: Build results dictionary
            project_info: Project analysis information
            grade: Calculated grade
            
        Returns:
            List of recommendation strings
        """
        recommendations = []
        
        # Build-related recommendations
        if not build_result.get('success'):
            recommendations.append("Fix compilation errors to get your project building")
            
            if 'dependency' in str(build_result.get('stderr', '')).lower():
                recommendations.append("Check your package.json dependencies and run 'npm install'")
            
            if 'typescript' in str(build_result.get('stderr', '')).lower():
                recommendations.append("Review TypeScript configuration and type definitions")
        
        # Structure recommendations
        if not project_info.get('has_src_folder'):
            recommendations.append("Organize your code in a 'src' folder for better structure")
        
        if not project_info.get('has_public_folder'):
            recommendations.append("Include a 'public' folder with your index.html")
        
        if not project_info.get('build_script'):
            recommendations.append("Add a 'build' script to your package.json")
        
        # Performance recommendations
        if grade < 70:
            recommendations.append("Focus on getting your basic React app building and running")
        elif grade < 90:
            recommendations.append("Consider adding better project structure and documentation")
        else:
            recommendations.append("Great work! Consider adding unit tests and optimizing performance")
        
        return recommendations
    
    def get_grade_distribution(self, grades: List[int]) -> Dict[str, any]:
        """
        Calculate grade distribution statistics.
        
        Args:
            grades: List of grades
            
        Returns:
            Dictionary with distribution statistics
        """
        if not grades:
            return {}
        
        import statistics
        
        distribution = {
            'count': len(grades),
            'average': round(statistics.mean(grades), 2),
            'median': statistics.median(grades),
            'min': min(grades),
            'max': max(grades),
            'std_dev': round(statistics.stdev(grades) if len(grades) > 1 else 0, 2)
        }
        
        # Grade brackets
        distribution['grade_brackets'] = {
            'A (90-100)': len([g for g in grades if g >= 90]),
            'B (80-89)': len([g for g in grades if 80 <= g < 90]),
            'C (70-79)': len([g for g in grades if 70 <= g < 80]),
            'D (60-69)': len([g for g in grades if 60 <= g < 70]),
            'F (0-59)': len([g for g in grades if g < 60])
        }
        
        return distribution
    
    def update_grading_scale(self, new_scale: Dict[str, int]):
        """
        Update the grading scale.
        
        Args:
            new_scale: New grading scale dictionary
        """
        self.grading_scale.update(new_scale)
        logger.info(f"Updated grading scale: {self.grading_scale}")
    
    def export_grading_rubric(self) -> Dict[str, any]:
        """
        Export the current grading rubric.
        
        Returns:
            Dictionary with grading rubric information
        """
        return {
            'grading_scale': self.grading_scale,
            'requirements': self.requirements,
            'total_possible_points': self.total_possible_points,
            'criteria': {
                'build_success': 'Project must build without errors',
                'project_structure': 'Proper React project organization',
                'code_quality': 'Clean, readable code following best practices',
                'requirements_met': 'Assignment requirements fulfilled'
            }
        }
    
    def _evaluate_build_quality(self, build_result: Dict[str, any]) -> int:
        """
        Evaluate build quality and assign base score.
        
        Args:
            build_result: Build results dictionary
            
        Returns:
            Build quality score (0-100)
        """
        if not build_result.get('success', False):
            logger.info("❌ Build failed - 0 points for build quality")
            return 0
        
        has_warnings = len(build_result.get('warnings', [])) > 0
        has_errors = len(build_result.get('errors', [])) > 0
        
        if has_errors:
            logger.info("⚠️ Build has errors - 60 points for build quality") 
            return 60
        elif has_warnings:
            logger.info("⚠️ Build has warnings - 85 points for build quality")
            return 85
        else:
            logger.info("✅ Clean build - 100 points for build quality")
            return 100
    
    def _evaluate_requirements_section(self, local_path: str, section_name: str, 
                                     requirements: List[str], build_result: Dict[str, any],
                                     project_info: Dict[str, any]) -> Tuple[int, Dict[str, any]]:
        """
        Evaluate a specific requirements section.
        
        Args:
            local_path: Path to project
            section_name: Name of the requirements section
            requirements: List of requirements to check
            build_result: Build results
            project_info: Project information
            
        Returns:
            Tuple of (score_percentage, evaluation_details)
        """
        logger.info(f"🔍 Evaluating section: {section_name}")
        
        section_details = {
            'met': [],
            'missed': [],
            'partial': [],
            'checks_performed': []
        }
        
        total_requirements = len(requirements)
        if total_requirements == 0:
            return 100, section_details
        
        # Different evaluation strategies based on section type
        if 'technical' in section_name.lower() or 'functionality' in section_name.lower():
            score = self._evaluate_functional_requirements(local_path, requirements, section_details)
        elif 'ui' in section_name.lower() or 'design' in section_name.lower():
            score = self._evaluate_ui_requirements(local_path, requirements, section_details)
        elif 'code' in section_name.lower() or 'quality' in section_name.lower():
            score = self._evaluate_code_quality_requirements(local_path, requirements, section_details)
        else:
            # General requirements evaluation
            score = self._evaluate_general_requirements(local_path, requirements, section_details)
        
        logger.info(f"📊 Section '{section_name}' score: {score}%")
        logger.info(f"✅ Met: {len(section_details['met'])}, ❌ Missed: {len(section_details['missed'])}")
        
        return score, section_details
    
    def _evaluate_functional_requirements(self, local_path: str, requirements: List[str], 
                                        details: Dict[str, any]) -> int:
        """
        Evaluate functional/technical requirements by checking project structure and code.
        
        Args:
            local_path: Path to project
            requirements: List of requirements
            details: Details dictionary to populate
            
        Returns:
            Score percentage (0-100)
        """
        met_count = 0
        
        for req in requirements:
            req_lower = req.lower()
            check_name = f"Functional: {req[:50]}..."
            details['checks_performed'].append(check_name)
            
            if self._check_react_component_requirement(local_path, req):
                details['met'].append(req)
                met_count += 1
                logger.debug(f"✅ Met: {req[:50]}...")
            elif self._check_npm_package_requirement(local_path, req):
                details['met'].append(req)
                met_count += 1
                logger.debug(f"✅ Met (package): {req[:50]}...")
            elif self._check_file_structure_requirement(local_path, req):
                details['met'].append(req)
                met_count += 1
                logger.debug(f"✅ Met (structure): {req[:50]}...")
            else:
                details['missed'].append(req)
                logger.debug(f"❌ Missed: {req[:50]}...")
        
        return int((met_count / len(requirements)) * 100) if requirements else 100
    
    def _evaluate_ui_requirements(self, local_path: str, requirements: List[str], 
                                details: Dict[str, any]) -> int:
        """
        Evaluate UI/design requirements.
        
        Args:
            local_path: Path to project
            requirements: List of requirements
            details: Details dictionary to populate
            
        Returns:
            Score percentage (0-100)
        """
        met_count = 0
        
        for req in requirements:
            check_name = f"UI: {req[:50]}..."
            details['checks_performed'].append(check_name)
            
            if self._check_css_styling_requirement(local_path, req):
                details['met'].append(req)
                met_count += 1
                logger.debug(f"✅ Met UI: {req[:50]}...")
            elif self._check_responsive_design_requirement(local_path, req):
                details['met'].append(req)
                met_count += 1
                logger.debug(f"✅ Met responsive: {req[:50]}...")
            else:
                details['missed'].append(req)
                logger.debug(f"❌ Missed UI: {req[:50]}...")
        
        return int((met_count / len(requirements)) * 100) if requirements else 100
    
    def _evaluate_code_quality_requirements(self, local_path: str, requirements: List[str], 
                                          details: Dict[str, any]) -> int:
        """
        Evaluate code quality requirements.
        
        Args:
            local_path: Path to project
            requirements: List of requirements
            details: Details dictionary to populate
            
        Returns:
            Score percentage (0-100)
        """
        met_count = 0
        
        for req in requirements:
            check_name = f"Quality: {req[:50]}..."
            details['checks_performed'].append(check_name)
            
            if self._check_code_quality_requirement(local_path, req):
                details['met'].append(req)
                met_count += 1
                logger.debug(f"✅ Met quality: {req[:50]}...")
            else:
                details['missed'].append(req)
                logger.debug(f"❌ Missed quality: {req[:50]}...")
        
        return int((met_count / len(requirements)) * 100) if requirements else 100
    
    def _evaluate_general_requirements(self, local_path: str, requirements: List[str], 
                                     details: Dict[str, any]) -> int:
        """
        Evaluate general requirements.
        
        Args:
            local_path: Path to project
            requirements: List of requirements
            details: Details dictionary to populate
            
        Returns:
            Score percentage (0-100)
        """
        met_count = 0
        
        for req in requirements:
            check_name = f"General: {req[:50]}..."
            details['checks_performed'].append(check_name)
            
            # Check multiple criteria for general requirements
            if (self._check_file_structure_requirement(local_path, req) or
                self._check_react_component_requirement(local_path, req) or
                self._check_npm_package_requirement(local_path, req) or
                self._check_documentation_requirement(local_path, req)):
                details['met'].append(req)
                met_count += 1
                logger.debug(f"✅ Met general: {req[:50]}...")
            else:
                details['missed'].append(req)
                logger.debug(f"❌ Missed general: {req[:50]}...")
        
        return int((met_count / len(requirements)) * 100) if requirements else 100
    
    def _check_react_component_requirement(self, local_path: str, requirement: str) -> bool:
        """
        Check if a React component requirement is met.
        
        Args:
            local_path: Path to the project
            requirement: Requirement string (e.g., "Header component")
            
        Returns:
            True if the requirement is met, False otherwise
        """
        # Example check: Look for a specific file or folder
        component_name = requirement.split()[0]  # Get the component name (e.g., "Header")
        component_path = os.path.join(local_path, 'src', f"{component_name}.js")
        
        return os.path.isfile(component_path)
    
    def _check_npm_package_requirement(self, local_path: str, requirement: str) -> bool:
        """
        Check if an npm package requirement is met.
        
        Args:
            local_path: Path to the project
            requirement: Requirement string (e.g., "axios")
            
        Returns:
            True if the requirement is met, False otherwise
        """
        # Example check: Look for the package in package.json
        package_json_path = os.path.join(local_path, 'package.json')
        
        if not os.path.isfile(package_json_path):
            return False
        
        with open(package_json_path, 'r') as f:
            package_json = json.load(f)
            dependencies = package_json.get('dependencies', {})
            dev_dependencies = package_json.get('devDependencies', {})
            
            return (requirement in dependencies) or (requirement in dev_dependencies)
    
    def _check_file_structure_requirement(self, local_path: str, requirement: str) -> bool:
        """
        Check if a file structure requirement is met.
        
        Args:
            local_path: Path to the project
            requirement: Requirement string (e.g., "src/ folder")
            
        Returns:
            True if the requirement is met, False otherwise
        """
        # Example check: Ensure the src/ folder exists
        if requirement == "src/ folder":
            return os.path.isdir(os.path.join(local_path, 'src'))
        elif requirement == "public/ folder":
            return os.path.isdir(os.path.join(local_path, 'public'))
        elif requirement == "package.json":
            return os.path.isfile(os.path.join(local_path, 'package.json'))
        elif requirement == "Build script":
            # Check for a build script in package.json
            package_json_path = os.path.join(local_path, 'package.json')
            
            if not os.path.isfile(package_json_path):
                return False
            
            with open(package_json_path, 'r') as f:
                package_json = json.load(f)
                return 'build' in package_json.get('scripts', {})
        
        return False
    
    def _check_css_styling_requirement(self, local_path: str, requirement: str) -> bool:
        """
        Check if a CSS styling requirement is met.
        
        Args:
            local_path: Path to the project
            requirement: Requirement string (e.g., "Header has correct styles")
            
        Returns:
            True if the requirement is met, False otherwise
        """
        # Example check: Look for specific CSS rules in the main CSS file
        css_file_path = os.path.join(local_path, 'src', 'index.css')
        
        if not os.path.isfile(css_file_path):
            return False
        
        with open(css_file_path, 'r') as f:
            css_content = f.read()
            
            # Check for specific rules (this is a simplified example)
            if "header {" in css_content and "color:" in css_content:
                return True
        
        return False
    
    def _check_responsive_design_requirement(self, local_path: str, requirement: str) -> bool:
        """
        Check if a responsive design requirement is met.
        
        Args:
            local_path: Path to the project
            requirement: Requirement string (e.g., "App is responsive")
            
        Returns:
            True if the requirement is met, False otherwise
        """
        # Example check: Look for meta viewport tag in index.html
        html_file_path = os.path.join(local_path, 'public', 'index.html')
        
        if not os.path.isfile(html_file_path):
            return False
        
        with open(html_file_path, 'r') as f:
            html_content = f.read()
            
            # Check for meta viewport tag
            if '<meta name="viewport"' in html_content:
                return True
        
        return False
    
    def _check_code_quality_requirement(self, local_path: str, requirement: str) -> bool:
        """
        Check if a code quality requirement is met.
        
        Args:
            local_path: Path to the project
            requirement: Requirement string (e.g., "No console logs")
            
        Returns:
            True if the requirement is met, False otherwise
        """
        # Example check: Look for specific patterns in the code
        pattern = re.compile(r'console\.log|debugger')
        
        for dirpath, _, filenames in os.walk(os.path.join(local_path, 'src')):
            for filename in filenames:
                file_path = os.path.join(dirpath, filename)
                
                if file_path.endswith('.js') or file_path.endswith('.jsx'):
                    with open(file_path, 'r') as f:
                        file_content = f.read()
                        
                        if pattern.search(file_content):
                            return False  # Console log or debugger found
        
        return True  # No issues found
    
    def _check_documentation_requirement(self, local_path: str, requirement: str) -> bool:
        """
        Check if a documentation requirement is met.
        
        Args:
            local_path: Path to the project
            requirement: Requirement string (e.g., "README.md exists")
            
        Returns:
            True if the requirement is met, False otherwise
        """
        # Example check: Ensure README.md exists
        if requirement == "README.md exists":
            return os.path.isfile(os.path.join(local_path, 'README.md'))
        
        return False
