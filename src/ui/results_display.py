"""
Results display components for the Streamlit UI.
"""
import streamlit as st
import pandas as pd
from typing import Dict, List, Optional
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
import config


class ResultsDisplay:
    """Handles display of grading results and analytics."""
    
    def __init__(self):
        """Initialize the results display component."""
        pass
    
    def render_results_overview(self, stats: Dict[str, any]) -> None:
        """
        Render high-level results overview.
        
        Args:
            stats: Statistics dictionary from grading process
        """
        st.header("📊 Grading Results Overview")
        
        # Main metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "Total Students", 
                stats.get('total_students', 0),
                help="Total number of student submissions processed"
            )
        
        with col2:
            success_count = stats.get('success', 0)
            total = stats.get('total_students', 1)
            success_rate = (success_count / total) * 100 if total > 0 else 0
            st.metric(
                "Success Rate", 
                f"{success_rate:.1f}%",
                delta=f"{success_count} successful builds",
                help="Percentage of projects that built successfully"
            )
        
        with col3:
            avg_grade = stats.get('average_grade', 0)
            st.metric(
                "Average Grade", 
                f"{avg_grade:.1f}/100",
                help="Average grade across all submissions"
            )
        
        with col4:
            failed_count = stats.get('failed', 0) + stats.get('errors', 0)
            st.metric(
                "Failed Builds", 
                failed_count,
                delta=f"{stats.get('failed', 0)} failed, {stats.get('errors', 0)} errors",
                delta_color="inverse",
                help="Number of projects that failed to build"
            )
    
    def render_grade_distribution(self, students_data: pd.DataFrame) -> None:
        """
        Render grade distribution visualization.
        
        Args:
            students_data: DataFrame with student grading results
        """
        st.subheader("🎓 Grade Distribution")
        
        if students_data.empty:
            st.info("No data available for grade distribution")
            return
        
        grade_col = config.EXCEL_COLUMNS['OUTPUT']['GRADE']
        
        if grade_col not in students_data.columns:
            st.warning("Grade column not found in data")
            return
        
        grades = students_data[grade_col].dropna()
        
        if grades.empty:
            st.info("No grades available")
            return
        
        # Create grade distribution chart
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # Histogram
            fig_hist = px.histogram(
                x=grades,
                nbins=10,
                title="Grade Distribution",
                labels={'x': 'Grade', 'y': 'Number of Students'},
                color_discrete_sequence=['#1f77b4']
            )
            fig_hist.update_layout(
                xaxis_title="Grade",
                yaxis_title="Number of Students",
                showlegend=False
            )
            st.plotly_chart(fig_hist, use_container_width=True)
        
        with col2:
            # Grade brackets
            brackets = {
                'A (90-100)': len(grades[grades >= 90]),
                'B (80-89)': len(grades[(grades >= 80) & (grades < 90)]),
                'C (70-79)': len(grades[(grades >= 70) & (grades < 80)]),
                'D (60-69)': len(grades[(grades >= 60) & (grades < 70)]),
                'F (0-59)': len(grades[grades < 60])
            }
            
            # Pie chart
            fig_pie = px.pie(
                values=list(brackets.values()),
                names=list(brackets.keys()),
                title="Grade Brackets"
            )
            st.plotly_chart(fig_pie, use_container_width=True)
        
        # Statistics summary
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Mean", f"{grades.mean():.1f}")
        with col2:
            st.metric("Median", f"{grades.median():.1f}")
        with col3:
            st.metric("Std Dev", f"{grades.std():.1f}")
        with col4:
            st.metric("Range", f"{grades.min():.0f} - {grades.max():.0f}")
    
    def render_build_status_overview(self, students_data: pd.DataFrame) -> None:
        """
        Render build status overview.
        
        Args:
            students_data: DataFrame with student grading results
        """
        st.subheader("🔧 Build Status Analysis")
        
        if students_data.empty:
            st.info("No data available for build status analysis")
            return
        
        status_col = config.EXCEL_COLUMNS['OUTPUT']['BUILD_STATUS']
        
        if status_col not in students_data.columns:
            st.warning("Build status column not found in data")
            return
        
        status_counts = students_data[status_col].value_counts()
        
        # Status overview
        col1, col2 = st.columns([1, 1])
        
        with col1:
            # Bar chart
            fig_bar = px.bar(
                x=status_counts.index,
                y=status_counts.values,
                title="Build Status Distribution",
                labels={'x': 'Status', 'y': 'Count'},
                color=status_counts.index,
                color_discrete_map={
                    'Success': '#90EE90',
                    'Failed': '#FFB6C1',
                    'Error': '#FFA07A',
                    'Warning': '#FFE4B5'
                }
            )
            st.plotly_chart(fig_bar, use_container_width=True)
        
        with col2:
            # Status breakdown
            st.write("**Status Breakdown:**")
            for status, count in status_counts.items():
                percentage = (count / len(students_data)) * 100
                
                if status == 'Success':
                    st.success(f"✅ {status}: {count} ({percentage:.1f}%)")
                elif status == 'Failed':
                    st.error(f"❌ {status}: {count} ({percentage:.1f}%)")
                elif status == 'Error':
                    st.error(f"🚫 {status}: {count} ({percentage:.1f}%)")
                else:
                    st.warning(f"⚠️ {status}: {count} ({percentage:.1f}%)")
    
    def render_detailed_results_table(self, students_data: pd.DataFrame) -> None:
        """
        Render detailed results table.
        
        Args:
            students_data: DataFrame with student grading results
        """
        st.subheader("📋 Detailed Results")
        
        if students_data.empty:
            st.info("No data available")
            return
        
        # Prepare display columns
        display_cols = []
        col_mapping = {}
        
        # Required columns
        required_cols = config.EXCEL_COLUMNS['REQUIRED']
        for key, col_name in required_cols.items():
            if col_name in students_data.columns:
                display_cols.append(col_name)
                col_mapping[col_name] = col_name
        
        # Output columns
        output_cols = config.EXCEL_COLUMNS['OUTPUT']
        for key, col_name in output_cols.items():
            if col_name in students_data.columns:
                display_cols.append(col_name)
                col_mapping[col_name] = col_name
        
        # Filter and display data
        display_data = students_data[display_cols].copy()
        
        # Style the dataframe
        def highlight_status(row):
            styles = [''] * len(row)
            
            if config.EXCEL_COLUMNS['OUTPUT']['BUILD_STATUS'] in row.index:
                status = row[config.EXCEL_COLUMNS['OUTPUT']['BUILD_STATUS']]
                if status == 'Success':
                    styles[row.index.get_loc(config.EXCEL_COLUMNS['OUTPUT']['BUILD_STATUS'])] = 'background-color: #90EE90'
                elif status == 'Failed':
                    styles[row.index.get_loc(config.EXCEL_COLUMNS['OUTPUT']['BUILD_STATUS'])] = 'background-color: #FFB6C1'
                elif status == 'Error':
                    styles[row.index.get_loc(config.EXCEL_COLUMNS['OUTPUT']['BUILD_STATUS'])] = 'background-color: #FFA07A'
            
            return styles
        
        # Apply styling
        styled_df = display_data.style.apply(highlight_status, axis=1)
        
        # Display table
        st.dataframe(styled_df, use_container_width=True, hide_index=True)
        
        # Add filtering options
        with st.expander("🔍 Filter Results"):
            col1, col2 = st.columns(2)
            
            with col1:
                if config.EXCEL_COLUMNS['OUTPUT']['BUILD_STATUS'] in students_data.columns:
                    status_filter = st.multiselect(
                        "Filter by Build Status",
                        options=students_data[config.EXCEL_COLUMNS['OUTPUT']['BUILD_STATUS']].unique(),
                        default=students_data[config.EXCEL_COLUMNS['OUTPUT']['BUILD_STATUS']].unique()
                    )
                    
                    if status_filter:
                        filtered_data = students_data[
                            students_data[config.EXCEL_COLUMNS['OUTPUT']['BUILD_STATUS']].isin(status_filter)
                        ]
                        st.write(f"Showing {len(filtered_data)} of {len(students_data)} students")
            
            with col2:
                if config.EXCEL_COLUMNS['OUTPUT']['GRADE'] in students_data.columns:
                    grade_range = st.slider(
                        "Filter by Grade Range",
                        min_value=0,
                        max_value=100,
                        value=(0, 100),
                        step=5
                    )
                    
                    filtered_by_grade = students_data[
                        (students_data[config.EXCEL_COLUMNS['OUTPUT']['GRADE']] >= grade_range[0]) &
                        (students_data[config.EXCEL_COLUMNS['OUTPUT']['GRADE']] <= grade_range[1])
                    ]
                    st.write(f"Grade range {grade_range[0]}-{grade_range[1]}: {len(filtered_by_grade)} students")
    
    def render_download_options(self, excel_handler, students_data: pd.DataFrame) -> None:
        """
        Render download options for results.
        
        Args:
            excel_handler: ExcelHandler instance
            students_data: DataFrame with results
        """
        st.subheader("💾 Download Results")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            # Download Excel file
            if st.button("📊 Download Excel Results", type="primary"):
                with st.spinner("Preparing Excel file..."):
                    success, file_path = excel_handler.save_results()
                    
                    if success:
                        try:
                            with open(file_path, 'rb') as f:
                                st.download_button(
                                    label="📥 Download Excel File",
                                    data=f.read(),
                                    file_name=Path(file_path).name,
                                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                                )
                            st.success(f"Excel file ready for download!")
                        except Exception as e:
                            st.error(f"Failed to prepare download: {str(e)}")
                    else:
                        st.error(f"Failed to save Excel file: {file_path}")
        
        with col2:
            # Download error log
            if st.button("📝 Download Error Log"):
                with st.spinner("Preparing error log..."):
                    success, file_path = excel_handler.export_error_log()
                    
                    if success:
                        try:
                            with open(file_path, 'r', encoding='utf-8') as f:
                                st.download_button(
                                    label="📥 Download Error Log",
                                    data=f.read(),
                                    file_name=Path(file_path).name,
                                    mime="text/plain"
                                )
                            st.success("Error log ready for download!")
                        except Exception as e:
                            st.error(f"Failed to prepare error log: {str(e)}")
                    else:
                        st.error(f"Failed to create error log: {file_path}")
        
        with col3:
            # Download summary report
            if st.button("📈 Download Summary Report"):
                with st.spinner("Generating summary report..."):
                    try:
                        summary = self._generate_summary_report(students_data)
                        
                        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                        filename = f"grading_summary_{timestamp}.txt"
                        
                        st.download_button(
                            label="📥 Download Summary",
                            data=summary,
                            file_name=filename,
                            mime="text/plain"
                        )
                        st.success("Summary report ready for download!")
                    except Exception as e:
                        st.error(f"Failed to generate summary: {str(e)}")
    
    def render_requirements_analysis(self, word_parser) -> None:
        """
        Render analysis of parsed requirements.
        
        Args:
            word_parser: WordParser instance with parsed requirements
        """
        st.subheader("📋 Requirements Analysis")
        
        requirements = word_parser.get_requirements_list()
        grading_criteria = word_parser.get_grading_criteria()
        point_values = word_parser.get_point_values()
        
        if not requirements:
            st.info("No requirements document was uploaded or parsed")
            return
        
        # Requirements summary
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total Requirements", len(requirements))
        with col2:
            st.metric("Grading Sections", len(grading_criteria))
        with col3:
            st.metric("Total Points", word_parser.get_total_points())
        
        # Detailed requirements
        if grading_criteria:
            st.write("**Grading Criteria by Section:**")
            
            for section, section_requirements in grading_criteria.items():
                points = point_values.get(section, 0)
                
                with st.expander(f"{section} ({points} points)"):
                    for req in section_requirements:
                        st.write(f"• {req}")
        else:
            st.write("**All Requirements:**")
            for req in requirements:
                st.write(f"• {req}")
    
    def _generate_summary_report(self, students_data: pd.DataFrame) -> str:
        """
        Generate a text summary report.
        
        Args:
            students_data: DataFrame with grading results
            
        Returns:
            Text summary report
        """
        report_lines = []
        
        # Header
        report_lines.append("ASSIGNMENT GRADING SUMMARY REPORT")
        report_lines.append("=" * 50)
        report_lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report_lines.append("")
        
        # Overview
        report_lines.append("OVERVIEW:")
        report_lines.append(f"Total Students: {len(students_data)}")
        
        if config.EXCEL_COLUMNS['OUTPUT']['BUILD_STATUS'] in students_data.columns:
            status_counts = students_data[config.EXCEL_COLUMNS['OUTPUT']['BUILD_STATUS']].value_counts()
            for status, count in status_counts.items():
                percentage = (count / len(students_data)) * 100
                report_lines.append(f"{status}: {count} ({percentage:.1f}%)")
        
        report_lines.append("")
        
        # Grade statistics
        if config.EXCEL_COLUMNS['OUTPUT']['GRADE'] in students_data.columns:
            grades = students_data[config.EXCEL_COLUMNS['OUTPUT']['GRADE']].dropna()
            
            if not grades.empty:
                report_lines.append("GRADE STATISTICS:")
                report_lines.append(f"Average: {grades.mean():.2f}")
                report_lines.append(f"Median: {grades.median():.2f}")
                report_lines.append(f"Standard Deviation: {grades.std():.2f}")
                report_lines.append(f"Range: {grades.min():.0f} - {grades.max():.0f}")
                report_lines.append("")
                
                # Grade brackets
                report_lines.append("GRADE DISTRIBUTION:")
                brackets = {
                    'A (90-100)': len(grades[grades >= 90]),
                    'B (80-89)': len(grades[(grades >= 80) & (grades < 90)]),
                    'C (70-79)': len(grades[(grades >= 70) & (grades < 80)]),
                    'D (60-69)': len(grades[(grades >= 60) & (grades < 70)]),
                    'F (0-59)': len(grades[grades < 60])
                }
                
                for bracket, count in brackets.items():
                    percentage = (count / len(grades)) * 100
                    report_lines.append(f"{bracket}: {count} ({percentage:.1f}%)")
                
                report_lines.append("")
        
        # Failed submissions
        if config.EXCEL_COLUMNS['OUTPUT']['BUILD_STATUS'] in students_data.columns:
            failed_students = students_data[
                students_data[config.EXCEL_COLUMNS['OUTPUT']['BUILD_STATUS']].isin(['Failed', 'Error'])
            ]
            
            if not failed_students.empty:
                report_lines.append("FAILED SUBMISSIONS:")
                name_col = config.EXCEL_COLUMNS['REQUIRED']['NAME']
                
                for _, row in failed_students.iterrows():
                    name = row.get(name_col, 'Unknown')
                    status = row.get(config.EXCEL_COLUMNS['OUTPUT']['BUILD_STATUS'], 'Unknown')
                    report_lines.append(f"- {name}: {status}")
                
                report_lines.append("")
        
        # Footer
        report_lines.append("=" * 50)
        report_lines.append("Report generated by Assignment Grading Agent")
        
        return "\n".join(report_lines)
