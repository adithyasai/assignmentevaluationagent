"""
GitHub repository cloning utilities for the Assignment Agent.
"""
import os
import shutil
import subprocess
import stat
import time
from pathlib import Path
from typing import Optional, Tuple
from git import Repo, GitCommandError
from loguru import logger
import config


class RepoCloner:
    """Handles GitHub repository cloning operations."""
    
    def __init__(self):
        """Initialize the repository cloner."""
        self.repos_dir = config.REPOS_DIR
        self.clone_timeout = config.GITHUB_CLONE_TIMEOUT
    
    def clone_repository(self, github_url: str, student_name: str) -> Tuple[bool, str, Optional[str]]:
        """
        Clone a GitHub repository for a specific student.
        
        Args:
            github_url: GitHub repository URL
            student_name: Student name (used for directory naming)
            
        Returns:
            Tuple of (success, message, local_path)
        """
        try:
            # Clean student name for directory naming
            safe_name = self._sanitize_directory_name(student_name)
            local_path = self.repos_dir / safe_name
            
            logger.info(f"📁 Target directory: {local_path}")
            
            # Remove existing directory if it exists with better Windows handling
            if local_path.exists():
                logger.info(f"🗑️ Removing existing directory: {local_path}")
                self._force_remove_directory(local_path)
            
            # Ensure parent directory exists
            local_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Clone the repository
            logger.info(f"Cloning {github_url} to {local_path}")
            
            try:
                # Use GitPython for cloning (shallow clone for faster downloads)
                logger.info(f"📥 Starting shallow clone of {github_url}...")
                repo = Repo.clone_from(
                    github_url,
                    str(local_path),
                    depth=1  # Shallow clone for faster downloads - removed timeout as it's not supported
                )
                
                logger.info(f"✅ Successfully cloned repository for {student_name}")
                return True, f"Repository cloned successfully", str(local_path)
                
            except GitCommandError as e:
                logger.error(f"Git command failed for {student_name}: {str(e)}")
                
                # Try to get more specific error information
                error_msg = str(e)
                if "repository not found" in error_msg.lower():
                    return False, "Repository not found (may be private or deleted)", None
                elif "permission denied" in error_msg.lower():
                    return False, "Permission denied (repository may be private)", None
                elif "timeout" in error_msg.lower():
                    return False, "Clone operation timed out", None
                else:
                    return False, f"Git error: {error_msg}", None
            
        except Exception as e:
            logger.error(f"Unexpected error cloning repository for {student_name}: {str(e)}")
            return False, f"Clone failed: {str(e)}", None
    
    def verify_react_project(self, local_path: str) -> Tuple[bool, str, dict]:
        """
        Verify that the cloned repository is a valid React project.
        
        Args:
            local_path: Path to the cloned repository
            
        Returns:
            Tuple of (is_react_project, message, project_info)
        """
        try:
            project_path = Path(local_path)
            project_info = {
                'has_package_json': False,
                'has_react_dependency': False,
                'has_src_folder': False,
                'has_public_folder': False,
                'package_manager': 'npm',
                'react_version': None,
                'build_script': True
            }
            
            # Check for package.json
            package_json_path = project_path / 'package.json'
            if not package_json_path.exists():
                return False, "No package.json found - not a Node.js project", project_info
            
            project_info['has_package_json'] = True
            
            # Parse package.json
            try:
                import json
                with open(package_json_path, 'r', encoding='utf-8') as f:
                    package_data = json.load(f)
                
                # Check for React dependency
                dependencies = package_data.get('dependencies', {})
                dev_dependencies = package_data.get('devDependencies', {})
                all_deps = {**dependencies, **dev_dependencies}
                
                if 'react' in all_deps:
                    project_info['has_react_dependency'] = True
                    project_info['react_version'] = all_deps['react']
                else:
                    return False, "React dependency not found in package.json", project_info
                
                # Check for build script
                scripts = package_data.get('scripts', {})
                if 'build' not in scripts:
                    project_info['build_script'] = False
                    logger.warning(f"No build script found in {local_path}")
                
                # Detect package manager
                if (project_path / 'yarn.lock').exists():
                    project_info['package_manager'] = 'yarn'
                elif (project_path / 'pnpm-lock.yaml').exists():
                    project_info['package_manager'] = 'pnpm'
                
            except (json.JSONDecodeError, UnicodeDecodeError) as e:
                logger.error(f"Failed to parse package.json in {local_path}: {str(e)}")
                return False, f"Invalid package.json: {str(e)}", project_info
            
            # Check for typical React project structure
            project_info['has_src_folder'] = (project_path / 'src').exists()
            project_info['has_public_folder'] = (project_path / 'public').exists()
            
            # Determine if this looks like a complete React project
            if project_info['has_react_dependency']:
                if project_info['has_src_folder'] or project_info['has_public_folder']:
                    return True, "Valid React project detected", project_info
                else:
                    return True, "React dependency found (minimal project structure)", project_info
            else:
                return False, "Not a React project", project_info
                
        except Exception as e:
            logger.error(f"Error verifying React project at {local_path}: {str(e)}")
            return False, f"Verification failed: {str(e)}", {}
    
    def cleanup_repository(self, local_path: str) -> bool:
        """
        Clean up a cloned repository directory.
        
        Args:
            local_path: Path to the repository directory
            
        Returns:
            True if cleanup successful, False otherwise
        """
        try:
            path_obj = Path(local_path)
            if path_obj.exists():
                return self._force_remove_directory(path_obj)
            return True
            
        except Exception as e:
            logger.error(f"Failed to cleanup repository at {local_path}: {str(e)}")
            return False
    
    def cleanup_all_repositories(self) -> Tuple[int, int]:
        """
        Clean up all cloned repositories.
        
        Returns:
            Tuple of (cleaned_count, error_count)
        """
        if not self.repos_dir.exists():
            return 0, 0
        
        cleaned_count = 0
        error_count = 0
        
        try:
            for item in self.repos_dir.iterdir():
                if item.is_dir():
                    if self._force_remove_directory(item):
                        cleaned_count += 1
                        logger.debug(f"Cleaned up {item}")
                    else:
                        logger.error(f"Failed to cleanup {item}")
                        error_count += 1
            
            logger.info(f"Cleanup completed: {cleaned_count} directories cleaned, {error_count} errors")
            
        except Exception as e:
            logger.error(f"Error during cleanup: {str(e)}")
            error_count += 1
        
        return cleaned_count, error_count
    
    def get_repository_info(self, local_path: str) -> dict:
        """
        Get information about a cloned repository.
        
        Args:
            local_path: Path to the repository
            
        Returns:
            Dictionary with repository information
        """
        try:
            repo_path = Path(local_path)
            info = {
                'exists': repo_path.exists(),
                'size_mb': 0,
                'file_count': 0,
                'last_commit': None,
                'branch': None
            }
            
            if not repo_path.exists():
                return info
            
            # Calculate directory size
            total_size = sum(f.stat().st_size for f in repo_path.rglob('*') if f.is_file())
            info['size_mb'] = round(total_size / (1024 * 1024), 2)
            
            # Count files
            info['file_count'] = len([f for f in repo_path.rglob('*') if f.is_file()])
            
            # Get git information
            try:
                repo = Repo(str(repo_path))
                if not repo.bare:
                    info['branch'] = repo.active_branch.name
                    if repo.head.commit:
                        info['last_commit'] = {
                            'hash': repo.head.commit.hexsha[:8],
                            'message': repo.head.commit.message.strip(),
                            'author': repo.head.commit.author.name,
                            'date': repo.head.commit.committed_datetime.isoformat()
                        }
            except Exception as e:
                logger.debug(f"Could not get git info for {local_path}: {str(e)}")
            
            return info
            
        except Exception as e:
            logger.error(f"Failed to get repository info for {local_path}: {str(e)}")
            return {'exists': False, 'error': str(e)}
    
    def _sanitize_directory_name(self, name: str) -> str:
        """
        Sanitize a string to be safe for use as a directory name.
        
        Args:
            name: Original name string
            
        Returns:
            Sanitized directory name
        """
        # Remove or replace invalid characters
        invalid_chars = '<>:"/|?*\\ '  # Added space to invalid chars
        sanitized = name
        
        # Replace spaces and invalid characters with underscores
        for char in invalid_chars:
            sanitized = sanitized.replace(char, '_')
        
        # Remove multiple consecutive underscores
        while '__' in sanitized:
            sanitized = sanitized.replace('__', '_')
        
        # Trim underscores from start and end
        sanitized = sanitized.strip('_')
        
        # Ensure it's not empty and not too long
        if not sanitized:
            sanitized = "unnamed_student"
        
        if len(sanitized) > 30:  # Shorter for better Windows compatibility
            sanitized = sanitized[:30]
        
        # Make it lowercase for consistency
        sanitized = sanitized.lower()
        
        return sanitized
    
    def _force_remove_directory(self, directory_path: Path) -> bool:
        """
        Force remove a directory on Windows, handling file permission issues.
        
        Args:
            directory_path: Path to the directory to remove
            
        Returns:
            True if removal successful, False otherwise
        """
        try:
            if not directory_path.exists():
                return True
            
            logger.debug(f"🗑️ Attempting to remove directory: {directory_path}")
            
            # First attempt: regular removal
            try:
                shutil.rmtree(directory_path)
                logger.debug(f"✅ Directory removed successfully: {directory_path}")
                return True
            except PermissionError:
                logger.debug(f"⚠️ Permission error, trying forced removal...")
            
            # Second attempt: make everything writable first
            try:
                self._make_writable_recursive(directory_path)
                shutil.rmtree(directory_path)
                logger.debug(f"✅ Directory removed after making writable: {directory_path}")
                return True
            except Exception as e:
                logger.debug(f"⚠️ Still failed: {e}, trying Windows-specific approach...")
            
            # Third attempt: Windows-specific with retries
            try:
                # Close any Git processes that might be holding locks
                if os.name == 'nt':  # Windows
                    self._kill_git_processes()
                    time.sleep(0.5)  # Give processes time to close
                
                # Use Windows rmdir command as fallback
                if os.name == 'nt':
                    cmd = f'rmdir /s /q "{directory_path}"'
                    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
                    if result.returncode == 0:
                        logger.debug(f"✅ Directory removed using Windows rmdir: {directory_path}")
                        return True
                    else:
                        logger.debug(f"Windows rmdir failed: {result.stderr}")
                
                # Final attempt with multiple retries
                for attempt in range(3):
                    try:
                        self._make_writable_recursive(directory_path)
                        shutil.rmtree(directory_path, onerror=self._handle_remove_readonly)
                        logger.debug(f"✅ Directory removed on attempt {attempt + 1}: {directory_path}")
                        return True
                    except Exception as e:
                        if attempt == 2:  # Last attempt
                            logger.warning(f"❌ Failed to remove directory after 3 attempts: {directory_path}: {e}")
                            return False
                        else:
                            logger.debug(f"Attempt {attempt + 1} failed, retrying...")
                            time.sleep(1)  # Wait before retry
                
            except Exception as e:
                logger.error(f"❌ All removal attempts failed for {directory_path}: {e}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Unexpected error in _force_remove_directory: {e}")
            return False
        
        return False
    
    def _make_writable_recursive(self, directory_path: Path):
        """Make all files and directories writable recursively."""
        try:
            for root, dirs, files in os.walk(directory_path):
                # Make directories writable
                for dir_name in dirs:
                    dir_path = os.path.join(root, dir_name)
                    try:
                        os.chmod(dir_path, stat.S_IWRITE | stat.S_IREAD | stat.S_IEXEC)
                    except Exception:
                        pass  # Ignore individual failures
                
                # Make files writable
                for file_name in files:
                    file_path = os.path.join(root, file_name)
                    try:
                        os.chmod(file_path, stat.S_IWRITE | stat.S_IREAD)
                    except Exception:
                        pass  # Ignore individual failures
                        
                # Make the root directory itself writable
                try:
                    os.chmod(root, stat.S_IWRITE | stat.S_IREAD | stat.S_IEXEC)
                except Exception:
                    pass
                    
        except Exception as e:
            logger.debug(f"Error making directory writable: {e}")
    
    def _handle_remove_readonly(self, func, path, exc):
        """Error handler for shutil.rmtree to handle readonly files."""
        try:
            os.chmod(path, stat.S_IWRITE)
            func(path)
        except Exception:
            pass  # If we can't fix it, just ignore
    
    def _kill_git_processes(self):
        """Kill any Git processes that might be holding file locks (Windows)."""
        try:
            if os.name == 'nt':  # Windows only
                subprocess.run(['taskkill', '/f', '/im', 'git.exe'], 
                             capture_output=True, text=True)
                subprocess.run(['taskkill', '/f', '/im', 'git-upload-pack.exe'], 
                             capture_output=True, text=True)
                subprocess.run(['taskkill', '/f', '/im', 'git-receive-pack.exe'], 
                             capture_output=True, text=True)
        except Exception:
            pass  # Ignore errors - this is best effort
