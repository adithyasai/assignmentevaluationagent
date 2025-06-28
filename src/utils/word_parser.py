"""
Word document parsing utilities for extracting assignment requirements.
"""
from docx import Document
from typing import Dict, List, Optional, Tuple
from loguru import logger
import re


class WordParser:
    """Parses Word documents to extract assignment requirements and grading criteria."""
    
    def __init__(self):
        """Initialize the Word parser."""
        self.requirements: List[str] = []
        self.grading_criteria: Dict[str, List[str]] = {}
        self.point_values: Dict[str, int] = {}
        self.total_points: int = 100
    
    def parse_requirements_document(self, file_path: str) -> Tuple[bool, str]:
        """
        Parse a Word document to extract assignment requirements.
        
        Args:
            file_path: Path to the Word document
            
        Returns:
            Tuple of (success, message)
        """
        try:
            doc = Document(file_path)
            self.requirements.clear()
            self.grading_criteria.clear()
            self.point_values.clear()
            
            current_section = "General"
            current_requirements = []
            
            for paragraph in doc.paragraphs:
                text = paragraph.text.strip()
                
                if not text:
                    continue
                
                # Check if this is a section header (contains points value)
                header_match = self._extract_section_header(text)
                if header_match:
                    # Save previous section if it exists
                    if current_requirements:
                        self.grading_criteria[current_section] = current_requirements.copy()
                    
                    # Start new section
                    current_section = header_match['section']
                    self.point_values[current_section] = header_match['points']
                    current_requirements.clear()
                    continue
                
                # Check if this is a requirement bullet point
                requirement = self._extract_requirement(text)
                if requirement:
                    self.requirements.append(requirement)
                    current_requirements.append(requirement)
            
            # Save the last section
            if current_requirements:
                self.grading_criteria[current_section] = current_requirements.copy()
            
            # Calculate total points
            self.total_points = sum(self.point_values.values()) if self.point_values else 100
            
            logger.info(f"Parsed {len(self.requirements)} requirements from {file_path}")
            logger.info(f"Found {len(self.grading_criteria)} grading sections with {self.total_points} total points")
            
            return True, f"Successfully parsed {len(self.requirements)} requirements"
            
        except Exception as e:
            logger.error(f"Failed to parse Word document: {str(e)}")
            return False, f"Failed to parse Word document: {str(e)}"
    
    def _extract_section_header(self, text: str) -> Optional[Dict[str, any]]:
        """
        Extract section header with point values.
        
        Args:
            text: Text to analyze
            
        Returns:
            Dictionary with section name and points, or None if not a header
        """
        # Pattern to match headers like "Technical Requirements (40 points):"
        patterns = [
            r'^(.+?)\s*\((\d+)\s*points?\):\s*$',
            r'^(.+?)\s*\((\d+)\s*pts?\):\s*$',
            r'^(.+?)\s*-\s*(\d+)\s*points?\s*$',
            r'^(.+?)\s*:\s*(\d+)\s*points?\s*$'
        ]
        
        for pattern in patterns:
            match = re.match(pattern, text, re.IGNORECASE)
            if match:
                section_name = match.group(1).strip()
                points = int(match.group(2))
                return {'section': section_name, 'points': points}
        
        # Check for simple headers (without points)
        if text.endswith(':') and len(text.split()) <= 5:
            return {'section': text[:-1].strip(), 'points': 0}
        
        return None
    
    def _extract_requirement(self, text: str) -> Optional[str]:
        """
        Extract individual requirement from text.
        
        Args:
            text: Text to analyze
            
        Returns:
            Clean requirement text or None if not a requirement
        """
        # Common bullet point patterns
        bullet_patterns = [
            r'^[•·▪▫‣⁃]\s*(.+)$',  # Unicode bullets
            r'^[-*+]\s*(.+)$',      # ASCII bullets
            r'^\d+\.\s*(.+)$',      # Numbered lists
            r'^[a-zA-Z]\.\s*(.+)$', # Lettered lists
        ]
        
        for pattern in bullet_patterns:
            match = re.match(pattern, text)
            if match:
                return match.group(1).strip()
        
        # If no bullet pattern but seems like a requirement (contains "must", "should", etc.)
        requirement_keywords = ['must', 'should', 'need', 'require', 'include', 'use', 'implement', 'create']
        if any(keyword in text.lower() for keyword in requirement_keywords):
            return text.strip()
        
        return None
    
    def get_requirements_list(self) -> List[str]:
        """
        Get the list of all parsed requirements.
        
        Returns:
            List of requirement strings
        """
        return self.requirements.copy()
    
    def get_grading_criteria(self) -> Dict[str, List[str]]:
        """
        Get the structured grading criteria by section.
        
        Returns:
            Dictionary mapping section names to lists of requirements
        """
        return self.grading_criteria.copy()
    
    def get_point_values(self) -> Dict[str, int]:
        """
        Get the point values for each section.
        
        Returns:
            Dictionary mapping section names to point values
        """
        return self.point_values.copy()
    
    def get_total_points(self) -> int:
        """
        Get the total points for the assignment.
        
        Returns:
            Total points value
        """
        return self.total_points
    
    def generate_requirements_summary(self) -> str:
        """
        Generate a formatted summary of the parsed requirements.
        
        Returns:
            Formatted string with requirements summary
        """
        if not self.requirements:
            return "No requirements found in the document."
        
        summary = f"Assignment Requirements Summary\n"
        summary += f"Total Requirements: {len(self.requirements)}\n"
        summary += f"Total Points: {self.total_points}\n\n"
        
        if self.grading_criteria:
            for section, requirements in self.grading_criteria.items():
                points = self.point_values.get(section, 0)
                summary += f"{section}"
                if points > 0:
                    summary += f" ({points} points)"
                summary += ":\n"
                
                for req in requirements:
                    summary += f"  • {req}\n"
                summary += "\n"
        else:
            summary += "All Requirements:\n"
            for req in self.requirements:
                summary += f"  • {req}\n"
        
        return summary
    
    def search_requirements(self, keywords: List[str]) -> List[str]:
        """
        Search for requirements containing specific keywords.
        
        Args:
            keywords: List of keywords to search for
            
        Returns:
            List of matching requirements
        """
        matching_requirements = []
        
        for requirement in self.requirements:
            requirement_lower = requirement.lower()
            if any(keyword.lower() in requirement_lower for keyword in keywords):
                matching_requirements.append(requirement)
        
        return matching_requirements
    
    def export_requirements_json(self) -> Dict[str, any]:
        """
        Export requirements data as JSON-serializable dictionary.
        
        Returns:
            Dictionary with all requirements data
        """
        return {
            'requirements': self.requirements,
            'grading_criteria': self.grading_criteria,
            'point_values': self.point_values,
            'total_points': self.total_points,
            'sections_count': len(self.grading_criteria),
            'requirements_count': len(self.requirements)
        }
