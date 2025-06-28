"""
React build validation utilities for the Assi                logger.info(f"Installing dependencies with {package_manager} in {project_path}")
                
                # Run the install command
                result = subprocess.run(
                    command,
                    capture_output=True,
                    text=True,
                    timeout=self.install_timeout,
                    shell=True if sys.platform == "win32" else False
                )
                
                success = result.returncode == 0
                
                if success:
                    logger.info(f"✅ Dependencies installed successfully: {project_path}")
                else:
                    logger.error(f"❌ Dependency installation failed with exit code {result.returncode}: {project_path}")
                    logger.error(f"🔍 Install stderr: {result.stderr}")
                    logger.error(f"🔍 Install stdout: {result.stdout}")
                
                return success, result.stdout, result.stderr
import os
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from loguru import logger
import config


class BuildChecker:
    """Handles React application build validation and testing."""
    
    def __init__(self):
        """Initialize the build checker."""
        self.build_timeout = config.BUILD_TIMEOUT_SECONDS
        self.install_timeout = config.INSTALL_TIMEOUT_SECONDS
    
    def install_dependencies(self, project_path: str, package_manager: str = 'npm') -> Tuple[bool, str, str]:
        """
        Install project dependencies.
        
        Args:
            project_path: Path to the React project
            package_manager: Package manager to use (npm, yarn, pnpm)
            
        Returns:
            Tuple of (success, stdout, stderr)
        """
        try:
            project_dir = Path(project_path)
            if not project_dir.exists():
                return False, "", "Project directory does not exist"
            
            # Change to project directory
            original_cwd = os.getcwd()
            os.chdir(project_dir)
            
            try:
                # Determine install command
                install_commands = {
                    'npm': ['npm', 'install'],
                    'yarn': ['yarn', 'install'],
                    'pnpm': ['pnpm', 'install']
                }
                
                command = install_commands.get(package_manager, ['npm', 'install'])
                
                logger.info(f"Installing dependencies with {package_manager} in {project_path}")
                
                # Run the install command
                result = subprocess.run(
                    command,
                    capture_output=True,
                    text=True,
                    timeout=self.install_timeout,
                    shell=True if sys.platform == "win32" else False
                )
                
                success = result.returncode == 0
                
                if success:
                    logger.info(f"Dependencies installed successfully for {project_path}")
                else:
                    logger.error(f"Dependency installation failed for {project_path}")
                
                return success, result.stdout, result.stderr
                
            finally:
                # Always restore original working directory
                os.chdir(original_cwd)
                
        except subprocess.TimeoutExpired:
            logger.error(f"Dependency installation timed out for {project_path}")
            return False, "", f"Installation timed out after {self.install_timeout} seconds"
        except Exception as e:
            logger.error(f"Unexpected error during dependency installation: {str(e)}")
            return False, "", f"Installation failed: {str(e)}"
    
    def build_project(self, project_path: str, package_manager: str = 'npm') -> Tuple[bool, str, str]:
        """
        Build the React project.
        
        Args:
            project_path: Path to the React project
            package_manager: Package manager to use (npm, yarn, pnpm)
            
        Returns:
            Tuple of (success, stdout, stderr)
        """
        try:
            project_dir = Path(project_path)
            if not project_dir.exists():
                return False, "", "Project directory does not exist"
            
            # Change to project directory
            original_cwd = os.getcwd()
            os.chdir(project_dir)
            
            try:
                # Determine build command
                build_commands = {
                    'npm': ['npm', 'run', 'build'],
                    'yarn': ['yarn', 'build'],
                    'pnpm': ['pnpm', 'run', 'build']
                }
                
                command = build_commands.get(package_manager, ['npm', 'run', 'build'])
                
                logger.info(f"Building project with {package_manager} in {project_path}")
                
                # Run the build command
                result = subprocess.run(
                    command,
                    capture_output=True,
                    text=True,
                    timeout=self.build_timeout,
                    shell=True if sys.platform == "win32" else False
                )
                
                success = result.returncode == 0
                
                if success:
                    logger.info(f"Project built successfully: {project_path}")
                else:
                    logger.error(f"Project build failed: {project_path}")
                
                return success, result.stdout, result.stderr
                
            finally:
                # Always restore original working directory
                os.chdir(original_cwd)
                
        except subprocess.TimeoutExpired:
            logger.error(f"Build timed out for {project_path}")
            return False, "", f"Build timed out after {self.build_timeout} seconds"
        except Exception as e:
            logger.error(f"Unexpected error during build: {str(e)}")
            return False, "", f"Build failed: {str(e)}"
    
    def check_build_output(self, project_path: str) -> Dict[str, any]:
        """
        Check the build output directory and analyze results.
        
        Args:
            project_path: Path to the React project
            
        Returns:
            Dictionary with build output information
        """
        try:
            project_dir = Path(project_path)
            build_info = {
                'has_build_dir': False,
                'build_size_mb': 0,
                'file_count': 0,
                'has_index_html': False,
                'has_js_files': False,
                'has_css_files': False,
                'warnings': [],
                'errors': []
            }
            
            # Common build directories
            build_dirs = [
                project_dir / 'build',
                project_dir / 'dist',
                project_dir / 'out'
            ]
            
            build_dir = None
            for dir_path in build_dirs:
                if dir_path.exists():
                    build_dir = dir_path
                    build_info['has_build_dir'] = True
                    break
            
            if not build_dir:
                build_info['errors'].append("No build output directory found")
                return build_info
            
            # Analyze build directory
            try:
                # Calculate size and count files
                total_size = 0
                file_count = 0
                
                for file_path in build_dir.rglob('*'):
                    if file_path.is_file():
                        file_count += 1
                        total_size += file_path.stat().st_size
                        
                        # Check for specific file types
                        if file_path.name == 'index.html':
                            build_info['has_index_html'] = True
                        elif file_path.suffix == '.js':
                            build_info['has_js_files'] = True
                        elif file_path.suffix == '.css':
                            build_info['has_css_files'] = True
                
                build_info['build_size_mb'] = round(total_size / (1024 * 1024), 2)
                build_info['file_count'] = file_count
                
                # Validate essential files
                if not build_info['has_index_html']:
                    build_info['warnings'].append("No index.html found in build output")
                
                if not build_info['has_js_files']:
                    build_info['warnings'].append("No JavaScript files found in build output")
                
                if file_count == 0:
                    build_info['errors'].append("Build directory is empty")
                elif file_count < 3:
                    build_info['warnings'].append(f"Very few files in build output ({file_count})")
                
                logger.debug(f"Build output analysis for {project_path}: {build_info}")
                
            except Exception as e:
                build_info['errors'].append(f"Failed to analyze build directory: {str(e)}")
            
            return build_info
            
        except Exception as e:
            logger.error(f"Error checking build output for {project_path}: {str(e)}")
            return {'errors': [f"Build output check failed: {str(e)}"]}
    
    def validate_node_environment(self) -> Tuple[bool, Dict[str, str]]:
        """
        Validate that Node.js and npm are available and compatible.
        
        Returns:
            Tuple of (is_valid, environment_info)
        """
        env_info = {
            'node_version': None,
            'npm_version': None,
            'yarn_version': None,
            'node_path': None,
            'npm_path': None,
            'errors': []
        }
        
        try:
            # Check Node.js
            try:
                result = subprocess.run(['node', '--version'], capture_output=True, text=True, timeout=10, shell=True)
                if result.returncode == 0:
                    env_info['node_version'] = result.stdout.strip()
                    
                    # Get Node.js path - use PowerShell on Windows for better compatibility
                    if sys.platform == "win32":
                        path_result = subprocess.run(
                            ['powershell', '-Command', 'Get-Command node | Select-Object -ExpandProperty Source'], 
                            capture_output=True, text=True, timeout=10, shell=True
                        )
                    else:
                        path_result = subprocess.run(['which', 'node'], capture_output=True, text=True, timeout=10)
                    
                    if path_result.returncode == 0:
                        env_info['node_path'] = path_result.stdout.strip()
                else:
                    env_info['errors'].append("Node.js not found or not working")
            except (subprocess.TimeoutExpired, FileNotFoundError) as e:
                env_info['errors'].append(f"Node.js not found in PATH: {str(e)}")
            
            # Check npm
            try:
                result = subprocess.run(['npm', '--version'], capture_output=True, text=True, timeout=10, shell=True)
                if result.returncode == 0:
                    env_info['npm_version'] = result.stdout.strip()
                    
                    # Get npm path - use PowerShell on Windows for better compatibility  
                    if sys.platform == "win32":
                        path_result = subprocess.run(
                            ['powershell', '-Command', 'Get-Command npm | Select-Object -ExpandProperty Source'], 
                            capture_output=True, text=True, timeout=10, shell=True
                        )
                    else:
                        path_result = subprocess.run(['which', 'npm'], capture_output=True, text=True, timeout=10)
                    
                    if path_result.returncode == 0:
                        env_info['npm_path'] = path_result.stdout.strip()
                else:
                    env_info['errors'].append("npm not found or not working")
            except (subprocess.TimeoutExpired, FileNotFoundError) as e:
                env_info['errors'].append(f"npm not found in PATH: {str(e)}")
            
            # Check yarn (optional)
            try:
                result = subprocess.run(['yarn', '--version'], capture_output=True, text=True, timeout=10, shell=True)
                if result.returncode == 0:
                    env_info['yarn_version'] = result.stdout.strip()
            except (subprocess.TimeoutExpired, FileNotFoundError):
                pass  # Yarn is optional
            
            # Validate Node.js version
            if env_info['node_version']:
                try:
                    version_str = env_info['node_version'].lstrip('v')
                    major_version = int(version_str.split('.')[0])
                    if major_version < 16:
                        env_info['errors'].append(f"Node.js version {env_info['node_version']} is too old. Minimum required: v16.0.0")
                except (ValueError, IndexError):
                    env_info['errors'].append(f"Could not parse Node.js version: {env_info['node_version']}")
            
            is_valid = len(env_info['errors']) == 0 and env_info['node_version'] and env_info['npm_version']
            
            if is_valid:
                logger.info(f"Node.js environment validated: Node {env_info['node_version']}, npm {env_info['npm_version']}")
            else:
                logger.error(f"Node.js environment validation failed: {env_info['errors']}")
            
            return is_valid, env_info
            
        except Exception as e:
            env_info['errors'].append(f"Environment validation failed: {str(e)}")
            logger.error(f"Error validating Node.js environment: {str(e)}")
            return False, env_info
    
    def analyze_build_errors(self, stderr: str, stdout: str = "") -> Dict[str, List[str]]:
        """
        Analyze build error output to categorize common issues.
        
        Args:
            stderr: Standard error output
            stdout: Standard output (may contain warnings)
            
        Returns:
            Dictionary with categorized errors and warnings
        """
        analysis = {
            'dependency_errors': [],
            'compilation_errors': [],
            'typescript_errors': [],
            'eslint_warnings': [],
            'general_errors': [],
            'suggestions': []
        }
        
        combined_output = f"{stderr}\n{stdout}".lower()
        
        # Dependency-related errors
        dependency_patterns = [
            'module not found',
            'cannot resolve module',
            'npm err!',
            'yarn error',
            'package not found',
            'enoent'
        ]
        
        for pattern in dependency_patterns:
            if pattern in combined_output:
                analysis['dependency_errors'].append(f"Dependency issue detected: {pattern}")
        
        # TypeScript errors
        typescript_patterns = [
            'typescript error',
            'ts error',
            'type error',
            '.ts(',
            '.tsx('
        ]
        
        for pattern in typescript_patterns:
            if pattern in combined_output:
                analysis['typescript_errors'].append("TypeScript compilation errors found")
                break
        
        # ESLint warnings
        if 'eslint' in combined_output or 'warning' in combined_output:
            analysis['eslint_warnings'].append("Code quality warnings detected")
        
        # Compilation errors
        compilation_patterns = [
            'syntax error',
            'unexpected token',
            'parse error',
            'compilation failed'
        ]
        
        for pattern in compilation_patterns:
            if pattern in combined_output:
                analysis['compilation_errors'].append(f"Compilation issue: {pattern}")
        
        # Generate suggestions based on errors
        if analysis['dependency_errors']:
            analysis['suggestions'].append("Try deleting node_modules and package-lock.json, then run npm install")
        
        if analysis['typescript_errors']:
            analysis['suggestions'].append("Check TypeScript configuration and type definitions")
        
        if analysis['compilation_errors']:
            analysis['suggestions'].append("Review code syntax and fix compilation errors")
        
        if not any(analysis.values()):
            analysis['general_errors'].append("Build failed with unknown error")
            analysis['suggestions'].append("Check the full error output for more details")
        
        return analysis
