"""
Advanced grade calculation logic for the Assignment Agent.
"""
from typing import Dict, List, Optional, Tuple
import statistics
from loguru import logger


class GradeCalculator:
    """Advanced grade calculation with multiple criteria and weighting."""
    
    def __init__(self):
        """Initialize the grade calculator."""
        self.weights = {
            'build_success': 0.4,      # 40% - Does it build?
            'code_quality': 0.3,       # 30% - Code structure and quality
            'requirements': 0.2,       # 20% - Requirements compliance
            'best_practices': 0.1      # 10% - React best practices
        }
        self.max_grade = 100
    
    def set_grading_weights(self, weights: Dict[str, float]):
        """
        Set custom grading weights.
        
        Args:
            weights: Dictionary with weight values (should sum to 1.0)
        """
        total_weight = sum(weights.values())
        if abs(total_weight - 1.0) > 0.01:
            logger.warning(f"Grading weights sum to {total_weight}, not 1.0. Normalizing...")
            weights = {k: v / total_weight for k, v in weights.items()}
        
        self.weights.update(weights)
        logger.info(f"Updated grading weights: {self.weights}")
    
    def calculate_build_score(self, build_result: Dict[str, any]) -> Tuple[float, str]:
        """
        Calculate score based on build success and quality.
        
        Args:
            build_result: Dictionary with build results
            
        Returns:
            Tuple of (score_0_to_100, feedback)
        """
        if build_result.get('success', False):
            base_score = 100
            feedback_parts = ["✅ Project builds successfully"]
            
            # Deduct points for warnings
            warnings = build_result.get('warnings', [])
            if warnings:
                warning_penalty = min(len(warnings) * 5, 20)  # Max 20 points penalty
                base_score -= warning_penalty
                feedback_parts.append(f"⚠️ {len(warnings)} warning(s) found (-{warning_penalty} points)")
            
            # Check build output quality
            build_output = build_result.get('build_output', {})
            if build_output.get('has_index_html', False):
                feedback_parts.append("✅ index.html generated")
            else:
                base_score -= 10
                feedback_parts.append("❌ No index.html found (-10 points)")
            
            if build_output.get('has_js_files', False):
                feedback_parts.append("✅ JavaScript files generated")
            else:
                base_score -= 5
                feedback_parts.append("❌ No JavaScript files found (-5 points)")
            
            # Check build size (very large builds might indicate issues)
            build_size = build_output.get('build_size_mb', 0)
            if build_size > 50:  # Unusually large build
                base_score -= 5
                feedback_parts.append(f"⚠️ Large build size ({build_size}MB) (-5 points)")
            
            return max(base_score, 0), " | ".join(feedback_parts)
        else:
            return 0, "❌ Project failed to build"
    
    def calculate_code_quality_score(self, project_info: Dict[str, any]) -> Tuple[float, str]:
        """
        Calculate score based on code structure and quality.
        
        Args:
            project_info: Dictionary with project analysis
            
        Returns:
            Tuple of (score_0_to_100, feedback)
        """
        score = 0
        feedback_parts = []
        
        # Project structure (40 points)
        if project_info.get('has_src_folder', False):
            score += 15
            feedback_parts.append("✅ Good project structure (src folder)")
        else:
            feedback_parts.append("❌ Missing src folder structure")
        
        if project_info.get('has_public_folder', False):
            score += 10
            feedback_parts.append("✅ Public folder present")
        else:
            feedback_parts.append("❌ Missing public folder")
        
        if project_info.get('has_package_json', False):
            score += 15
            feedback_parts.append("✅ Valid package.json")
        else:
            feedback_parts.append("❌ Missing or invalid package.json")
        
        # Dependencies and configuration (30 points)
        if project_info.get('has_react_dependency', False):
            score += 20
            feedback_parts.append("✅ React dependency configured")
        else:
            feedback_parts.append("❌ React dependency not found")
        
        if project_info.get('build_script', True):
            score += 10
            feedback_parts.append("✅ Build script available")
        else:
            score -= 5
            feedback_parts.append("❌ No build script found")
        
        # Code organization (30 points)
        # This would require more advanced analysis in the future
        # For now, give partial credit based on basic indicators
        if project_info.get('has_src_folder', False):
            score += 15  # Assume good organization if src folder exists
            feedback_parts.append("✅ Organized code structure")
        
        if project_info.get('react_version'):
            # Check if using reasonably recent React version
            try:
                version_str = project_info['react_version'].lstrip('^~')
                major_version = int(version_str.split('.')[0])
                if major_version >= 17:
                    score += 15
                    feedback_parts.append(f"✅ Modern React version ({project_info['react_version']})")
                else:
                    score += 10
                    feedback_parts.append(f"⚠️ Older React version ({project_info['react_version']})")
            except (ValueError, IndexError):
                score += 5
                feedback_parts.append("⚠️ Could not verify React version")
        
        return min(score, 100), " | ".join(feedback_parts)
    
    def calculate_requirements_score(self, requirements_met: List[str], 
                                   total_requirements: List[str]) -> Tuple[float, str]:
        """
        Calculate score based on requirements compliance.
        
        Args:
            requirements_met: List of requirements that were satisfied
            total_requirements: List of all requirements
            
        Returns:
            Tuple of (score_0_to_100, feedback)
        """
        if not total_requirements:
            return 100, "No specific requirements to check"
        
        met_count = len(requirements_met)
        total_count = len(total_requirements)
        score = (met_count / total_count) * 100
        
        feedback_parts = [
            f"Requirements met: {met_count}/{total_count} ({score:.1f}%)"
        ]
        
        if requirements_met:
            feedback_parts.append("✅ Met: " + ", ".join(requirements_met))
        
        missing = [req for req in total_requirements if req not in requirements_met]
        if missing:
            feedback_parts.append("❌ Missing: " + ", ".join(missing))
        
        return score, " | ".join(feedback_parts)
    
    def calculate_best_practices_score(self, project_info: Dict[str, any], 
                                     build_result: Dict[str, any]) -> Tuple[float, str]:
        """
        Calculate score based on React best practices.
        
        Args:
            project_info: Dictionary with project analysis
            build_result: Dictionary with build results
            
        Returns:
            Tuple of (score_0_to_100, feedback)
        """
        score = 0
        feedback_parts = []
        
        # Package manager best practices (20 points)
        package_manager = project_info.get('package_manager', 'npm')
        if package_manager in ['npm', 'yarn', 'pnpm']:
            score += 20
            feedback_parts.append(f"✅ Using {package_manager}")
        
        # Build optimization (30 points)
        build_output = build_result.get('build_output', {})
        if build_output.get('has_css_files', False):
            score += 15
            feedback_parts.append("✅ CSS files generated (styling included)")
        
        if build_output.get('file_count', 0) > 5:
            score += 15
            feedback_parts.append("✅ Multiple files generated (good structure)")
        
        # Error-free build (30 points)
        if not build_result.get('errors', []):
            score += 30
            feedback_parts.append("✅ Clean build (no errors)")
        else:
            error_count = len(build_result.get('errors', []))
            penalty = min(error_count * 5, 30)
            score += max(30 - penalty, 0)
            feedback_parts.append(f"⚠️ {error_count} error(s) found")
        
        # Modern React features (20 points)
        # This would require code analysis - placeholder for now
        if project_info.get('has_react_dependency', False):
            score += 20
            feedback_parts.append("✅ React framework usage")
        
        return min(score, 100), " | ".join(feedback_parts)
    
    def calculate_comprehensive_grade(self, build_result: Dict[str, any], 
                                    project_info: Dict[str, any],
                                    requirements_met: Optional[List[str]] = None,
                                    total_requirements: Optional[List[str]] = None) -> Tuple[int, str]:
        """
        Calculate comprehensive grade using all criteria.
        
        Args:
            build_result: Dictionary with build results
            project_info: Dictionary with project analysis
            requirements_met: Optional list of requirements satisfied
            total_requirements: Optional list of all requirements
            
        Returns:
            Tuple of (final_grade, detailed_feedback)
        """
        # Calculate individual scores
        build_score, build_feedback = self.calculate_build_score(build_result)
        quality_score, quality_feedback = self.calculate_code_quality_score(project_info)
        best_practices_score, practices_feedback = self.calculate_best_practices_score(
            project_info, build_result
        )
        
        # Requirements score
        if requirements_met is not None and total_requirements is not None:
            req_score, req_feedback = self.calculate_requirements_score(
                requirements_met, total_requirements
            )
        else:
            req_score, req_feedback = 100, "No specific requirements provided"
        
        # Calculate weighted final grade
        final_grade = (
            build_score * self.weights['build_success'] +
            quality_score * self.weights['code_quality'] +
            req_score * self.weights['requirements'] +
            best_practices_score * self.weights['best_practices']
        )
        
        # Round to nearest integer
        final_grade = round(min(final_grade, self.max_grade))
        
        # Generate detailed feedback
        feedback_sections = [
            f"FINAL GRADE: {final_grade}/100",
            "",
            f"BUILD SUCCESS ({self.weights['build_success']*100:.0f}%): {build_score:.1f}/100",
            build_feedback,
            "",
            f"CODE QUALITY ({self.weights['code_quality']*100:.0f}%): {quality_score:.1f}/100",
            quality_feedback,
            "",
            f"REQUIREMENTS ({self.weights['requirements']*100:.0f}%): {req_score:.1f}/100",
            req_feedback,
            "",
            f"BEST PRACTICES ({self.weights['best_practices']*100:.0f}%): {best_practices_score:.1f}/100",
            practices_feedback
        ]
        
        detailed_feedback = "\n".join(feedback_sections)
        
        logger.debug(f"Comprehensive grade calculated: {final_grade}/100")
        return final_grade, detailed_feedback
    
    def calculate_class_statistics(self, grades: List[int]) -> Dict[str, any]:
        """
        Calculate statistics for a class of grades.
        
        Args:
            grades: List of grades
            
        Returns:
            Dictionary with class statistics
        """
        if not grades:
            return {}
        
        stats = {
            'count': len(grades),
            'mean': round(statistics.mean(grades), 2),
            'median': statistics.median(grades),
            'mode': None,
            'std_dev': round(statistics.stdev(grades) if len(grades) > 1 else 0, 2),
            'min': min(grades),
            'max': max(grades),
            'range': max(grades) - min(grades),
            'quartiles': {},
            'grade_distribution': {}
        }
        
        # Calculate mode (most common grade)
        try:
            stats['mode'] = statistics.mode(grades)
        except statistics.StatisticsError:
            stats['mode'] = None  # No unique mode
        
        # Calculate quartiles
        sorted_grades = sorted(grades)
        n = len(sorted_grades)
        
        stats['quartiles'] = {
            'Q1': sorted_grades[n // 4] if n >= 4 else sorted_grades[0],
            'Q2': stats['median'],
            'Q3': sorted_grades[3 * n // 4] if n >= 4 else sorted_grades[-1]
        }
        
        # Grade distribution
        stats['grade_distribution'] = {
            'A (90-100)': len([g for g in grades if g >= 90]),
            'B (80-89)': len([g for g in grades if 80 <= g < 90]),
            'C (70-79)': len([g for g in grades if 70 <= g < 80]),
            'D (60-69)': len([g for g in grades if 60 <= g < 70]),
            'F (0-59)': len([g for g in grades if g < 60])
        }
        
        return stats
    
    def suggest_grade_adjustments(self, stats: Dict[str, any]) -> List[str]:
        """
        Suggest grade adjustments based on class statistics.
        
        Args:
            stats: Class statistics dictionary
            
        Returns:
            List of suggestions
        """
        suggestions = []
        
        if not stats:
            return suggestions
        
        mean_grade = stats.get('mean', 0)
        std_dev = stats.get('std_dev', 0)
        
        # Mean-based suggestions
        if mean_grade < 60:
            suggestions.append("Class average is low - consider reviewing assignment difficulty")
        elif mean_grade > 95:
            suggestions.append("Class average is very high - assignment might be too easy")
        
        # Standard deviation suggestions
        if std_dev > 20:
            suggestions.append("High grade variation - some students may need additional help")
        elif std_dev < 5:
            suggestions.append("Low grade variation - consistent performance across class")
        
        # Distribution suggestions
        distribution = stats.get('grade_distribution', {})
        failure_rate = distribution.get('F (0-59)', 0) / stats.get('count', 1)
        
        if failure_rate > 0.3:
            suggestions.append("High failure rate (>30%) - consider providing additional support")
        elif failure_rate == 0:
            suggestions.append("No failures - excellent class performance!")
        
        return suggestions
    
    def export_grading_scheme(self) -> Dict[str, any]:
        """
        Export the current grading scheme configuration.
        
        Returns:
            Dictionary with grading scheme details
        """
        return {
            'weights': self.weights,
            'max_grade': self.max_grade,
            'criteria': {
                'build_success': {
                    'description': 'Project builds successfully without errors',
                    'max_points': 100,
                    'factors': ['Build success', 'Warning penalties', 'Output quality']
                },
                'code_quality': {
                    'description': 'Code structure, organization, and dependencies',
                    'max_points': 100,
                    'factors': ['Project structure', 'Dependencies', 'Organization']
                },
                'requirements': {
                    'description': 'Compliance with assignment requirements',
                    'max_points': 100,
                    'factors': ['Requirements met', 'Feature implementation']
                },
                'best_practices': {
                    'description': 'React best practices and modern development',
                    'max_points': 100,
                    'factors': ['Package management', 'Build optimization', 'Modern features']
                }
            }
        }
