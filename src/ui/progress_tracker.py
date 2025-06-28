"""
Progress tracking components for the Streamlit UI.
"""
import streamlit as st
import time
from typing import Dict, List, Optional
from datetime import datetime


class ProgressTracker:
    """Handles progress tracking and display during the grading process."""
    
    def __init__(self):
        """Initialize the progress tracker."""
        self.total_students = 0
        self.current_student = 0
        self.start_time = None
        self.status_history = []
        self.current_status = "Ready"
        self.detailed_logs = []  # Store detailed logs for display
    
    def initialize(self, total_students: int):
        """
        Initialize progress tracking for a batch of students.
        
        Args:
            total_students: Total number of students to process
        """
        self.total_students = total_students
        self.current_student = 0
        self.start_time = datetime.now()
        self.status_history = []
        self.current_status = "Starting..."
        
    def render_progress_header(self) -> Dict[str, st.empty]:
        """
        Render the main progress tracking header.
        
        Returns:
            Dictionary of streamlit empty containers for updates
        """
        st.subheader("🎯 Grading Progress")
        
        # Create containers for dynamic updates
        containers = {
            'progress_bar': st.empty(),
            'status': st.empty(),
            'stats': st.empty(),
            'current_student': st.empty(),
            'time_info': st.empty()
        }
        
        return containers
    
    def update_progress(self, containers: Dict[str, st.empty], student_name: str, 
                       status: str, success: Optional[bool] = None, current_index: int = None):
        """
        Update the progress display.
        
        Args:
            containers: Dictionary of streamlit containers
            student_name: Name of current student being processed
            status: Current processing status
            success: Whether the current operation was successful (optional)
            current_index: Current student index (0-based)
        """
        # Use provided index or increment (but don't double increment)
        if current_index is not None:
            self.current_student = current_index + 1  # Convert to 1-based for display
        
        self.current_status = status
        
        # Add to history
        self.status_history.append({
            'student': student_name,
            'status': status,
            'success': success,
            'timestamp': datetime.now()
        })
        
        # Update progress bar - ensure progress never exceeds 1.0
        progress = min(self.current_student / self.total_students, 1.0) if self.total_students > 0 else 0
        containers['progress_bar'].progress(progress, text=f"Processing {self.current_student}/{self.total_students} students")
        
        # Update current status
        containers['status'].info(f"🔄 **Current:** {status} - {student_name}")
        
        # Update current student info
        containers['current_student'].markdown(f"""
        **Processing:** {student_name}  
        **Step:** {status}  
        **Progress:** {self.current_student}/{self.total_students} ({progress:.1%})
        """)
        
        # Update time information
        if self.start_time:
            elapsed = datetime.now() - self.start_time
            elapsed_seconds = elapsed.total_seconds()
            
            if self.current_student > 0:
                avg_time_per_student = elapsed_seconds / self.current_student
                estimated_remaining = avg_time_per_student * (self.total_students - self.current_student)
                
                containers['time_info'].markdown(f"""
                **Elapsed:** {self._format_duration(elapsed_seconds)}  
                **Estimated Remaining:** {self._format_duration(estimated_remaining)}  
                **Avg per Student:** {self._format_duration(avg_time_per_student)}
                """)
    
    def update_statistics(self, containers: Dict[str, st.empty], stats: Dict[str, int]):
        """
        Update the statistics display.
        
        Args:
            containers: Dictionary of streamlit containers
            stats: Statistics dictionary
        """
        col1, col2, col3, col4 = containers['stats'].columns(4)
        
        with col1:
            st.metric("✅ Success", stats.get('success', 0))
        with col2:
            st.metric("❌ Failed", stats.get('failed', 0))
        with col3:
            st.metric("🚫 Errors", stats.get('errors', 0))
        with col4:
            st.metric("📊 Processed", stats.get('processed', 0))
    
    def render_live_log(self, max_entries: int = 10) -> st.container:
        """
        Render live processing log.
        
        Args:
            max_entries: Maximum number of log entries to display
            
        Returns:
            Streamlit container for log updates
        """
        st.subheader("📜 Processing Log")
        log_container = st.container()
        
        with log_container:
            # Show recent entries
            recent_entries = self.status_history[-max_entries:] if self.status_history else []
            
            for entry in reversed(recent_entries):  # Show most recent first
                timestamp = entry['timestamp'].strftime('%H:%M:%S')
                student = entry['student']
                status = entry['status']
                success = entry.get('success')
                
                # Choose emoji based on success status
                if success is True:
                    emoji = "✅"
                elif success is False:
                    emoji = "❌"
                else:
                    emoji = "🔄"
                
                st.write(f"`{timestamp}` {emoji} **{student}** - {status}")
        
        return log_container
    
    def render_detailed_progress(self, student_results: List[Dict]) -> None:
        """
        Render detailed progress table.
        
        Args:
            student_results: List of student processing results
        """
        st.subheader("📋 Detailed Results")
        
        if not student_results:
            st.info("No results yet...")
            return
        
        # Create results table
        import pandas as pd
        
        table_data = []
        for result in student_results:
            table_data.append({
                'Student': result.get('name', 'Unknown'),
                'Status': result.get('status', 'Pending'),
                'Grade': result.get('grade', 0),
                'Build Time': result.get('build_time', 'N/A'),
                'Processed': result.get('processed_at', 'N/A')
            })
        
        df = pd.DataFrame(table_data)
        
        # Style the dataframe
        def style_status(val):
            if val == 'Success':
                return 'background-color: #90EE90'
            elif val == 'Failed':
                return 'background-color: #FFB6C1'
            elif val == 'Error':
                return 'background-color: #FFA07A'
            else:
                return ''
        
        styled_df = df.style.applymap(style_status, subset=['Status'])
        st.dataframe(styled_df, use_container_width=True)
    
    def render_summary_stats(self, final_stats: Dict[str, any]) -> None:
        """
        Render final summary statistics.
        
        Args:
            final_stats: Final processing statistics
        """
        st.subheader("📈 Final Statistics")
        
        # Main metrics
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            st.metric("Total Students", final_stats.get('total_students', 0))
        with col2:
            st.metric("Successful Builds", final_stats.get('success', 0))
        with col3:
            st.metric("Failed Builds", final_stats.get('failed', 0))
        with col4:
            st.metric("Errors", final_stats.get('errors', 0))
        with col5:
            success_rate = 0
            if final_stats.get('total_students', 0) > 0:
                success_rate = (final_stats.get('success', 0) / final_stats.get('total_students', 1)) * 100
            st.metric("Success Rate", f"{success_rate:.1f}%")
        
        # Grade statistics
        if 'average_grade' in final_stats:
            st.subheader("🎓 Grade Distribution")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Average Grade", f"{final_stats.get('average_grade', 0):.1f}")
            with col2:
                st.metric("Highest Grade", final_stats.get('max_grade', 0))
            with col3:
                st.metric("Lowest Grade", final_stats.get('min_grade', 0))
        
        # Processing time
        if self.start_time:
            total_time = datetime.now() - self.start_time
            total_seconds = total_time.total_seconds()
            
            st.subheader("⏱️ Processing Time")
            col1, col2 = st.columns(2)
            
            with col1:
                st.metric("Total Time", self._format_duration(total_seconds))
            with col2:
                if final_stats.get('total_students', 0) > 0:
                    avg_time = total_seconds / final_stats['total_students']
                    st.metric("Avg per Student", self._format_duration(avg_time))
    
    def render_error_summary(self, error_details: List[Dict]) -> None:
        """
        Render summary of errors encountered.
        
        Args:
            error_details: List of error detail dictionaries
        """
        if not error_details:
            return
        
        st.subheader("🚨 Error Summary")
        
        with st.expander(f"View {len(error_details)} Error(s)"):
            for i, error in enumerate(error_details, 1):
                st.write(f"**{i}. {error.get('student', 'Unknown Student')}**")
                st.write(f"Status: {error.get('status', 'Unknown')}")
                st.write(f"Error: {error.get('error_message', 'No details available')}")
                
                if error.get('build_errors'):
                    with st.expander("Build Error Details"):
                        st.code(error['build_errors'])
                
                st.divider()
    
    def _format_duration(self, seconds: float) -> str:
        """
        Format duration in seconds to human-readable string.
        
        Args:
            seconds: Duration in seconds
            
        Returns:
            Formatted duration string
        """
        if seconds < 60:
            return f"{seconds:.1f}s"
        elif seconds < 3600:
            minutes = seconds / 60
            return f"{minutes:.1f}m"
        else:
            hours = seconds / 3600
            return f"{hours:.1f}h"
    
    def get_processing_summary(self) -> Dict[str, any]:
        """
        Get a summary of the processing session.
        
        Returns:
            Dictionary with processing summary
        """
        if not self.start_time:
            return {}
        
        total_time = datetime.now() - self.start_time
        
        successful = len([h for h in self.status_history if h.get('success') is True])
        failed = len([h for h in self.status_history if h.get('success') is False])
        
        return {
            'total_students': self.total_students,
            'processed': len(self.status_history),
            'successful': successful,
            'failed': failed,
            'total_time_seconds': total_time.total_seconds(),
            'start_time': self.start_time.isoformat(),
            'end_time': datetime.now().isoformat()
        }
