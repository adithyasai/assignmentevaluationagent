"""
File validation utilities for the Assignment Agent.
"""
import os
import pandas as pd
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from loguru import logger
import config


class FileValidator:
    """Validates uploaded files for format and content requirements."""
    
    def __init__(self):
        """Initialize the file validator."""
        self.errors: List[str] = []
        self.warnings: List[str] = []
    
    def validate_excel_file(self, file_path: str) -> Tuple[bool, List[str], List[str]]:
        """
        Validate Excel file format and required columns.
        
        Args:
            file_path: Path to the Excel file
            
        Returns:
            Tuple of (is_valid, errors, warnings)
        """
        self.errors.clear()
        self.warnings.clear()
        
        try:
            # Check file existence
            if not os.path.exists(file_path):
                self.errors.append(f"File not found: {file_path}")
                return False, self.errors, self.warnings
            
            # Check file extension
            file_ext = Path(file_path).suffix.lower()
            if file_ext not in config.SUPPORTED_EXCEL_EXTENSIONS:
                self.errors.append(f"Unsupported file extension: {file_ext}. Supported: {config.SUPPORTED_EXCEL_EXTENSIONS}")
                return False, self.errors, self.warnings
            
            # Check file size
            file_size_mb = os.path.getsize(file_path) / (1024 * 1024)
            if file_size_mb > config.MAX_FILE_SIZE_MB:
                self.errors.append(f"File too large: {file_size_mb:.1f}MB. Maximum allowed: {config.MAX_FILE_SIZE_MB}MB")
                return False, self.errors, self.warnings
            
            # Try to read the Excel file
            try:
                df = pd.read_excel(file_path)
            except Exception as e:
                self.errors.append(f"Failed to read Excel file: {str(e)}")
                return False, self.errors, self.warnings
            
            # Check if file is empty
            if df.empty:
                self.errors.append("Excel file is empty")
                return False, self.errors, self.warnings
            
            # Check required columns
            required_cols = list(config.EXCEL_COLUMNS['REQUIRED'].values())
            missing_cols = [col for col in required_cols if col not in df.columns]
            
            if missing_cols:
                self.errors.append(f"Missing required columns: {missing_cols}")
                return False, self.errors, self.warnings
            
            # Check for empty required columns
            for col_key, col_name in config.EXCEL_COLUMNS['REQUIRED'].items():
                if df[col_name].isna().all():
                    self.errors.append(f"Required column '{col_name}' is empty")
                    return False, self.errors, self.warnings
                
                empty_rows = df[df[col_name].isna()].index.tolist()
                if empty_rows:
                    self.warnings.append(f"Column '{col_name}' has empty values in rows: {empty_rows}")
            
            # Validate GitHub URLs
            github_col = config.EXCEL_COLUMNS['REQUIRED']['GITHUB_URL']
            invalid_urls = []
            
            for idx, url in df[github_col].items():
                if pd.isna(url):
                    continue
                    
                url_str = str(url).strip()
                if not self._is_valid_github_url(url_str):
                    invalid_urls.append(f"Row {idx + 2}: {url_str}")
            
            if invalid_urls:
                self.warnings.append(f"Invalid GitHub URLs found: {invalid_urls}")
            
            # Check for duplicate entries
            name_col = config.EXCEL_COLUMNS['REQUIRED']['NAME']
            duplicates = df[df.duplicated(subset=[name_col], keep=False)]
            if not duplicates.empty:
                dup_names = duplicates[name_col].tolist()
                self.warnings.append(f"Duplicate student names found: {dup_names}")
            
            logger.info(f"Excel file validation completed: {len(self.errors)} errors, {len(self.warnings)} warnings")
            return len(self.errors) == 0, self.errors, self.warnings
            
        except Exception as e:
            logger.error(f"Unexpected error during Excel validation: {str(e)}")
            self.errors.append(f"Validation failed: {str(e)}")
            return False, self.errors, self.warnings
    
    def validate_word_file(self, file_path: str) -> Tuple[bool, List[str], List[str]]:
        """
        Validate Word document format and content.
        
        Args:
            file_path: Path to the Word document
            
        Returns:
            Tuple of (is_valid, errors, warnings)
        """
        self.errors.clear()
        self.warnings.clear()
        
        try:
            # Check file existence
            if not os.path.exists(file_path):
                self.errors.append(f"File not found: {file_path}")
                return False, self.errors, self.warnings
            
            # Check file extension
            file_ext = Path(file_path).suffix.lower()
            if file_ext not in config.SUPPORTED_WORD_EXTENSIONS:
                self.errors.append(f"Unsupported file extension: {file_ext}. Supported: {config.SUPPORTED_WORD_EXTENSIONS}")
                return False, self.errors, self.warnings
            
            # Check file size
            file_size_mb = os.path.getsize(file_path) / (1024 * 1024)
            if file_size_mb > config.MAX_FILE_SIZE_MB:
                self.errors.append(f"File too large: {file_size_mb:.1f}MB. Maximum allowed: {config.MAX_FILE_SIZE_MB}MB")
                return False, self.errors, self.warnings
            
            # Try to read the Word document
            try:
                from docx import Document
                doc = Document(file_path)
                
                # Check if document has content
                has_content = False
                for paragraph in doc.paragraphs:
                    if paragraph.text.strip():
                        has_content = True
                        break
                
                if not has_content:
                    self.warnings.append("Word document appears to be empty or contains no readable text")
                
            except Exception as e:
                self.errors.append(f"Failed to read Word document: {str(e)}")
                return False, self.errors, self.warnings
            
            logger.info(f"Word file validation completed: {len(self.errors)} errors, {len(self.warnings)} warnings")
            return len(self.errors) == 0, self.errors, self.warnings
            
        except Exception as e:
            logger.error(f"Unexpected error during Word validation: {str(e)}")
            self.errors.append(f"Validation failed: {str(e)}")
            return False, self.errors, self.warnings
    
    def _is_valid_github_url(self, url: str) -> bool:
        """
        Check if the URL is a valid GitHub repository URL.
        
        Args:
            url: URL to validate
            
        Returns:
            True if valid GitHub URL, False otherwise
        """
        if not url:
            return False
        
        url = url.strip().lower()
        
        # Basic GitHub URL patterns
        valid_patterns = [
            'https://github.com/',
            'http://github.com/',
            'github.com/'
        ]
        
        if not any(url.startswith(pattern) for pattern in valid_patterns):
            return False
        
        # Check if URL has at least owner/repo structure
        try:
            if url.startswith('http'):
                path_part = url.split('github.com/', 1)[1]
            else:
                path_part = url.split('github.com/', 1)[1]
            
            path_parts = path_part.strip('/').split('/')
            
            # Should have at least owner and repo name
            if len(path_parts) < 2:
                return False
            
            # Check for empty owner or repo name
            if not path_parts[0] or not path_parts[1]:
                return False
            
            return True
            
        except (IndexError, AttributeError):
            return False
    
    def get_file_info(self, file_path: str) -> Dict[str, str]:
        """
        Get basic information about a file.
        
        Args:
            file_path: Path to the file
            
        Returns:
            Dictionary with file information
        """
        try:
            if not os.path.exists(file_path):
                return {"error": "File not found"}
            
            stat = os.stat(file_path)
            return {
                "name": Path(file_path).name,
                "size": f"{stat.st_size / (1024 * 1024):.2f} MB",
                "extension": Path(file_path).suffix,
                "modified": str(pd.to_datetime(stat.st_mtime, unit='s'))
            }
            
        except Exception as e:
            return {"error": f"Failed to get file info: {str(e)}"}
