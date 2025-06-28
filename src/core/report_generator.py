"""
Report generation utilities for the Assignment Agent.
"""
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
import pandas as pd
from loguru import logger
import config


class ReportGenerator:
    """Generates comprehensive reports and analytics for grading results."""
    
    def __init__(self):
        """Initialize the report generator."""
        self.output_dir = config.DATA_DIR
    
    def generate_html_report(self, students_data: pd.DataFrame, 
                           summary_stats: Dict[str, any],
                           requirements_info: Optional[Dict[str, any]] = None) -> str:
        """
        Generate comprehensive HTML report.
        
        Args:
            students_data: DataFrame with grading results
            summary_stats: Summary statistics dictionary
            requirements_info: Optional requirements information
            
        Returns:
            Path to generated HTML file
        """
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = config.OUTPUT_FILE_PATTERNS['HTML_REPORT'].format(timestamp=timestamp)
            output_path = self.output_dir / filename
            
            # Generate HTML content
            html_content = self._build_html_content(students_data, summary_stats, requirements_info)
            
            # Write to file
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            logger.info(f"HTML report generated: {output_path}")
            return str(output_path)
            
        except Exception as e:
            logger.error(f"Failed to generate HTML report: {str(e)}")
            raise
    
    def _build_html_content(self, students_data: pd.DataFrame, 
                           summary_stats: Dict[str, any],
                           requirements_info: Optional[Dict[str, any]] = None) -> str:
        """
        Build HTML content for the report.
        
        Args:
            students_data: DataFrame with grading results
            summary_stats: Summary statistics
            requirements_info: Optional requirements information
            
        Returns:
            HTML content string
        """
        # HTML template
        html_template = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Assignment Grading Report</title>
    <style>
        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 0; padding: 20px; background-color: #f5f5f5; }}
        .container {{ max-width: 1200px; margin: 0 auto; background-color: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        .header {{ text-align: center; margin-bottom: 30px; padding-bottom: 20px; border-bottom: 2px solid #007bff; }}
        .header h1 {{ color: #007bff; margin: 0; font-size: 2.5em; }}
        .header p {{ color: #666; margin: 10px 0 0 0; font-size: 1.1em; }}
        .summary {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin-bottom: 30px; }}
        .metric {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 8px; text-align: center; }}
        .metric h3 {{ margin: 0 0 10px 0; font-size: 1.1em; }}
        .metric .value {{ font-size: 2em; font-weight: bold; }}
        .section {{ margin-bottom: 30px; }}
        .section h2 {{ color: #333; border-bottom: 2px solid #007bff; padding-bottom: 10px; }}
        table {{ width: 100%; border-collapse: collapse; margin-top: 15px; }}
        th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }}
        th {{ background-color: #007bff; color: white; font-weight: bold; }}
        tr:nth-child(even) {{ background-color: #f9f9f9; }}
        .status-success {{ background-color: #d4edda !important; color: #155724; }}
        .status-failed {{ background-color: #f8d7da !important; color: #721c24; }}
        .status-error {{ background-color: #fff3cd !important; color: #856404; }}
        .grade-a {{ background-color: #d1ecf1 !important; color: #0c5460; }}
        .grade-b {{ background-color: #d1ecf1 !important; color: #0c5460; }}
        .grade-c {{ background-color: #fff3cd !important; color: #856404; }}
        .grade-d {{ background-color: #f8d7da !important; color: #721c24; }}
        .grade-f {{ background-color: #f8d7da !important; color: #721c24; }}
        .requirements {{ background-color: #f8f9fa; padding: 15px; border-radius: 5px; }}
        .footer {{ text-align: center; margin-top: 30px; padding-top: 20px; border-top: 1px solid #ddd; color: #666; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🤖 Assignment Grading Report</h1>
            <p>Generated on {generation_time}</p>
        </div>
        
        <div class="summary">
            {summary_metrics}
        </div>
        
        {requirements_section}
        
        <div class="section">
            <h2>📊 Grade Distribution</h2>
            {grade_distribution_table}
        </div>
        
        <div class="section">
            <h2>🔧 Build Status Overview</h2>
            {build_status_table}
        </div>
        
        <div class="section">
            <h2>📋 Detailed Results</h2>
            {detailed_results_table}
        </div>
        
        <div class="footer">
            <p>Report generated by Assignment Grading Agent v{version}</p>
            <p>Processing completed at {generation_time}</p>
        </div>
    </div>
</body>
</html>
        '''
        
        # Build components
        generation_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # Summary metrics
        summary_metrics = self._build_summary_metrics_html(summary_stats)
        
        # Requirements section
        requirements_section = ""
        if requirements_info:
            requirements_section = self._build_requirements_section_html(requirements_info)
        
        # Grade distribution
        grade_distribution_table = self._build_grade_distribution_html(students_data)
        
        # Build status
        build_status_table = self._build_build_status_html(students_data)
        
        # Detailed results
        detailed_results_table = self._build_detailed_results_html(students_data)
        
        # Fill template
        html_content = html_template.format(
            generation_time=generation_time,
            summary_metrics=summary_metrics,
            requirements_section=requirements_section,
            grade_distribution_table=grade_distribution_table,
            build_status_table=build_status_table,
            detailed_results_table=detailed_results_table,
            version=config.APP_VERSION
        )
        
        return html_content
    
    def _build_summary_metrics_html(self, summary_stats: Dict[str, any]) -> str:
        """Build HTML for summary metrics."""
        metrics = [
            ("Total Students", summary_stats.get('total_students', 0)),
            ("Success Rate", f"{((summary_stats.get('success', 0) / max(summary_stats.get('total_students', 1), 1)) * 100):.1f}%"),
            ("Average Grade", f"{summary_stats.get('average_grade', 0):.1f}"),
            ("Failed Builds", summary_stats.get('failed', 0) + summary_stats.get('errors', 0))
        ]
        
        html_parts = []
        for label, value in metrics:
            html_parts.append(f'''
            <div class="metric">
                <h3>{label}</h3>
                <div class="value">{value}</div>
            </div>
            ''')
        
        return ''.join(html_parts)
    
    def _build_requirements_section_html(self, requirements_info: Dict[str, any]) -> str:
        """Build HTML for requirements section."""
        if not requirements_info:
            return ""
        
        html = '''
        <div class="section">
            <h2>📋 Assignment Requirements</h2>
            <div class="requirements">
        '''
        
        requirements = requirements_info.get('requirements', [])
        grading_criteria = requirements_info.get('grading_criteria', {})
        point_values = requirements_info.get('point_values', {})
        
        if grading_criteria:
            for section, section_requirements in grading_criteria.items():
                points = point_values.get(section, 0)
                html += f'<h3>{section} ({points} points)</h3><ul>'
                
                for req in section_requirements:
                    html += f'<li>{req}</li>'
                
                html += '</ul>'
        else:
            html += '<h3>General Requirements</h3><ul>'
            for req in requirements:
                html += f'<li>{req}</li>'
            html += '</ul>'
        
        html += '''
            </div>
        </div>
        '''
        
        return html
    
    def _build_grade_distribution_html(self, students_data: pd.DataFrame) -> str:
        """Build HTML for grade distribution."""
        if students_data.empty or config.EXCEL_COLUMNS['OUTPUT']['GRADE'] not in students_data.columns:
            return "<p>No grade data available</p>"
        
        grades = students_data[config.EXCEL_COLUMNS['OUTPUT']['GRADE']].dropna()
        
        if grades.empty:
            return "<p>No grades to display</p>"
        
        # Calculate distribution
        brackets = {
            'A (90-100)': len(grades[grades >= 90]),
            'B (80-89)': len(grades[(grades >= 80) & (grades < 90)]),
            'C (70-79)': len(grades[(grades >= 70) & (grades < 80)]),
            'D (60-69)': len(grades[(grades >= 60) & (grades < 70)]),
            'F (0-59)': len(grades[grades < 60])
        }
        
        html = '''
        <table>
            <thead>
                <tr>
                    <th>Grade Range</th>
                    <th>Count</th>
                    <th>Percentage</th>
                </tr>
            </thead>
            <tbody>
        '''
        
        total_students = len(grades)
        for grade_range, count in brackets.items():
            percentage = (count / total_students * 100) if total_students > 0 else 0
            grade_class = f"grade-{grade_range[0].lower()}"
            
            html += f'''
                <tr class="{grade_class}">
                    <td>{grade_range}</td>
                    <td>{count}</td>
                    <td>{percentage:.1f}%</td>
                </tr>
            '''
        
        html += '''
            </tbody>
        </table>
        '''
        
        return html
    
    def _build_build_status_html(self, students_data: pd.DataFrame) -> str:
        """Build HTML for build status overview."""
        if students_data.empty or config.EXCEL_COLUMNS['OUTPUT']['BUILD_STATUS'] not in students_data.columns:
            return "<p>No build status data available</p>"
        
        status_counts = students_data[config.EXCEL_COLUMNS['OUTPUT']['BUILD_STATUS']].value_counts()
        
        html = '''
        <table>
            <thead>
                <tr>
                    <th>Build Status</th>
                    <th>Count</th>
                    <th>Percentage</th>
                </tr>
            </thead>
            <tbody>
        '''
        
        total_students = len(students_data)
        for status, count in status_counts.items():
            percentage = (count / total_students * 100) if total_students > 0 else 0
            status_class = f"status-{status.lower()}"
            
            html += f'''
                <tr class="{status_class}">
                    <td>{status}</td>
                    <td>{count}</td>
                    <td>{percentage:.1f}%</td>
                </tr>
            '''
        
        html += '''
            </tbody>
        </table>
        '''
        
        return html
    
    def _build_detailed_results_html(self, students_data: pd.DataFrame) -> str:
        """Build HTML for detailed results table."""
        if students_data.empty:
            return "<p>No student data available</p>"
        
        # Select columns to display
        display_columns = []
        column_headers = []
        
        required_cols = config.EXCEL_COLUMNS['REQUIRED']
        output_cols = config.EXCEL_COLUMNS['OUTPUT']
        
        # Add required columns
        for key, col_name in required_cols.items():
            if col_name in students_data.columns:
                display_columns.append(col_name)
                column_headers.append(col_name)
        
        # Add key output columns
        key_output_cols = ['BUILD_STATUS', 'GRADE', 'PROCESSED_AT']
        for key in key_output_cols:
            col_name = output_cols[key]
            if col_name in students_data.columns:
                display_columns.append(col_name)
                column_headers.append(col_name)
        
        html = '''
        <table>
            <thead>
                <tr>
        '''
        
        for header in column_headers:
            html += f'<th>{header}</th>'
        
        html += '''
                </tr>
            </thead>
            <tbody>
        '''
        
        # Add data rows
        for _, row in students_data.iterrows():
            html += '<tr>'
            
            for col in display_columns:
                value = row.get(col, 'N/A')
                cell_class = ""
                
                # Apply special styling
                if col == output_cols['BUILD_STATUS']:
                    if str(value).lower() == 'success':
                        cell_class = "status-success"
                    elif str(value).lower() == 'failed':
                        cell_class = "status-failed"
                    elif str(value).lower() == 'error':
                        cell_class = "status-error"
                elif col == output_cols['GRADE']:
                    try:
                        grade_val = float(value)
                        if grade_val >= 90:
                            cell_class = "grade-a"
                        elif grade_val >= 80:
                            cell_class = "grade-b"
                        elif grade_val >= 70:
                            cell_class = "grade-c"
                        elif grade_val >= 60:
                            cell_class = "grade-d"
                        else:
                            cell_class = "grade-f"
                    except (ValueError, TypeError):
                        pass
                
                html += f'<td class="{cell_class}">{value}</td>'
            
            html += '</tr>'
        
        html += '''
            </tbody>
        </table>
        '''
        
        return html
    
    def generate_json_summary(self, students_data: pd.DataFrame, 
                            summary_stats: Dict[str, any],
                            processing_info: Optional[Dict[str, any]] = None) -> str:
        """
        Generate JSON summary file.
        
        Args:
            students_data: DataFrame with grading results
            summary_stats: Summary statistics
            processing_info: Optional processing information
            
        Returns:
            Path to generated JSON file
        """
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = config.OUTPUT_FILE_PATTERNS['SUMMARY_STATS'].format(timestamp=timestamp)
            output_path = self.output_dir / filename
            
            # Build summary data
            summary_data = {
                'metadata': {
                    'generated_at': datetime.now().isoformat(),
                    'generator': 'Assignment Grading Agent',
                    'version': config.APP_VERSION
                },
                'summary_statistics': summary_stats,
                'processing_info': processing_info or {},
                'student_results': []
            }
            
            # Add student results
            if not students_data.empty:
                required_cols = config.EXCEL_COLUMNS['REQUIRED']
                output_cols = config.EXCEL_COLUMNS['OUTPUT']
                
                for _, row in students_data.iterrows():
                    student_result = {}
                    
                    # Add required fields
                    for key, col_name in required_cols.items():
                        if col_name in row:
                            student_result[key.lower()] = row[col_name]
                    
                    # Add output fields
                    for key, col_name in output_cols.items():
                        if col_name in row:
                            student_result[key.lower()] = row[col_name]
                    
                    summary_data['student_results'].append(student_result)
            
            # Write JSON file
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(summary_data, f, indent=2, ensure_ascii=False, default=str)
            
            logger.info(f"JSON summary generated: {output_path}")
            return str(output_path)
            
        except Exception as e:
            logger.error(f"Failed to generate JSON summary: {str(e)}")
            raise
    
    def generate_csv_export(self, students_data: pd.DataFrame) -> str:
        """
        Generate CSV export of results.
        
        Args:
            students_data: DataFrame with grading results
            
        Returns:
            Path to generated CSV file
        """
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"grading_results_{timestamp}.csv"
            output_path = self.output_dir / filename
            
            # Export to CSV
            students_data.to_csv(output_path, index=False, encoding='utf-8')
            
            logger.info(f"CSV export generated: {output_path}")
            return str(output_path)
            
        except Exception as e:
            logger.error(f"Failed to generate CSV export: {str(e)}")
            raise
    
    def cleanup_old_reports(self, keep_days: int = 7):
        """
        Clean up old report files.
        
        Args:
            keep_days: Number of days to keep reports
        """
        try:
            cutoff_time = datetime.now().timestamp() - (keep_days * 24 * 3600)
            
            report_patterns = ['grading_report_*.html', 'summary_stats_*.json', 'grading_results_*.csv']
            cleaned_count = 0
            
            for pattern in report_patterns:
                for file_path in self.output_dir.glob(pattern):
                    if file_path.stat().st_mtime < cutoff_time:
                        file_path.unlink()
                        cleaned_count += 1
                        logger.debug(f"Cleaned up old report: {file_path}")
            
            if cleaned_count > 0:
                logger.info(f"Cleaned up {cleaned_count} old report files")
            
        except Exception as e:
            logger.error(f"Error cleaning up old reports: {str(e)}")
