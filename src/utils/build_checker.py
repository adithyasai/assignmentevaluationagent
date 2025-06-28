"""
React build validation utilities for the Assignment Agent.
"""
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
                logger.error(f"❌ Project directory does not exist: {project_path}")
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
                
                logger.info(f"📦 Installing dependencies with {package_manager} in {project_path}")
                logger.debug(f"🔧 Command: {' '.join(command)}")
                
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
                    if result.stdout:
                        logger.debug(f"📄 Install stdout (first 300 chars): {result.stdout[:300]}...")
                else:
                    logger.error(f"❌ Dependency installation failed with exit code {result.returncode}: {project_path}")
                    logger.error(f"🔍 Install stderr: {result.stderr}")
                    if result.stdout:
                        logger.error(f"🔍 Install stdout: {result.stdout}")
                
                return success, result.stdout, result.stderr
                
            finally:
                # Always restore original working directory
                os.chdir(original_cwd)
                
        except subprocess.TimeoutExpired:
            logger.error(f"⏰ Install timed out for {project_path}")
            return False, "", f"Install timed out after {self.install_timeout} seconds"
        except Exception as e:
            logger.error(f"💥 Unexpected error during install: {str(e)}")
            return False, "", f"Install failed: {str(e)}"
    
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
                logger.error(f"❌ Project directory does not exist: {project_path}")
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
                
                logger.info(f"🔨 Building project with {package_manager} in {project_path}")
                logger.debug(f"🔧 Command: {' '.join(command)}")
                
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
                    logger.info(f"✅ Project built successfully: {project_path}")
                    if result.stdout:
                        logger.debug(f"📄 Build stdout (first 300 chars): {result.stdout[:300]}...")
                else:
                    logger.error(f"❌ Project build failed with exit code {result.returncode}: {project_path}")
                    logger.error(f"🔍 Build stderr: {result.stderr}")
                    if result.stdout:
                        logger.error(f"🔍 Build stdout: {result.stdout}")
                
                return success, result.stdout, result.stderr
                
            finally:
                # Always restore original working directory
                os.chdir(original_cwd)
                
        except subprocess.TimeoutExpired:
            logger.error(f"⏰ Build timed out for {project_path}")
            return False, "", f"Build timed out after {self.build_timeout} seconds"
        except Exception as e:
            logger.error(f"💥 Unexpected error during build: {str(e)}")
            return False, "", f"Build failed: {str(e)}"
    
    def check_build_output(self, project_path: str) -> Dict[str, any]:
        """
        Check the build output directory and analyze results.
        
        Args:
            project_path: Path to the React project
            
        Returns:
            Dictionary with build analysis results
        """
        try:
            project_dir = Path(project_path)
            build_dir = project_dir / "build"
            dist_dir = project_dir / "dist"
            
            analysis = {
                'has_build_folder': False,
                'build_size': 0,
                'file_count': 0,
                'warnings': [],
                'errors': [],
                'assets': []
            }
            
            # Check for build output directories
            output_dir = None
            if build_dir.exists() and build_dir.is_dir():
                output_dir = build_dir
                analysis['has_build_folder'] = True
                logger.info(f"📁 Found build directory: {build_dir}")
            elif dist_dir.exists() and dist_dir.is_dir():
                output_dir = dist_dir
                analysis['has_build_folder'] = True
                logger.info(f"📁 Found dist directory: {dist_dir}")
            else:
                logger.warning(f"⚠️ No build output directory found in {project_path}")
                return analysis
            
            # Analyze build output
            if output_dir:
                try:
                    files = list(output_dir.rglob("*"))
                    file_files = [f for f in files if f.is_file()]
                    
                    analysis['file_count'] = len(file_files)
                    analysis['build_size'] = sum(f.stat().st_size for f in file_files)
                    
                    # Categorize files
                    for file_path in file_files:
                        analysis['assets'].append({
                            'name': file_path.name,
                            'size': file_path.stat().st_size,
                            'extension': file_path.suffix
                        })
                    
                    logger.info(f"📊 Build analysis: {analysis['file_count']} files, {analysis['build_size']} bytes")
                    
                except Exception as e:
                    logger.error(f"💥 Error analyzing build output: {str(e)}")
                    analysis['errors'].append(f"Error analyzing build output: {str(e)}")
            
            return analysis
            
        except Exception as e:
            logger.error(f"💥 Error checking build output: {str(e)}")
            return {
                'has_build_folder': False,
                'build_size': 0,
                'file_count': 0,
                'warnings': [],
                'errors': [f"Error checking build output: {str(e)}"],
                'assets': []
            }
    
    def verify_environment(self) -> Tuple[bool, str]:
        """
        Verify that the required build environment is available.
        
        Returns:
            Tuple of (success, message)
        """
        try:
            logger.info("🔍 Verifying build environment...")
            
            # Check Node.js
            try:
                node_result = subprocess.run(
                    ['node', '--version'],
                    capture_output=True,
                    text=True,
                    timeout=10,
                    shell=True if sys.platform == "win32" else False
                )
                
                if node_result.returncode == 0:
                    node_version = node_result.stdout.strip()
                    logger.info(f"✅ Node.js found: {node_version}")
                else:
                    logger.error("❌ Node.js not found or not accessible")
                    return False, "Node.js is not installed or not in PATH"
                    
            except (subprocess.TimeoutExpired, FileNotFoundError):
                logger.error("❌ Node.js not found or not accessible")
                return False, "Node.js is not installed or not in PATH"
            
            # Check npm
            try:
                npm_result = subprocess.run(
                    ['npm', '--version'],
                    capture_output=True,
                    text=True,
                    timeout=10,
                    shell=True if sys.platform == "win32" else False
                )
                
                if npm_result.returncode == 0:
                    npm_version = npm_result.stdout.strip()
                    logger.info(f"✅ npm found: {npm_version}")
                else:
                    logger.error("❌ npm not found or not accessible")
                    return False, "npm is not installed or not in PATH"
                    
            except (subprocess.TimeoutExpired, FileNotFoundError):
                logger.error("❌ npm not found or not accessible")
                return False, "npm is not installed or not in PATH"
            
            logger.info("✅ Build environment verification successful")
            return True, "Build environment is ready"
            
        except Exception as e:
            logger.error(f"💥 Error verifying environment: {str(e)}")
            return False, f"Environment verification failed: {str(e)}"
    
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
        
        # Check for dependency issues
        if any(term in combined_output for term in ['module not found', 'cannot resolve', 'package not found']):
            analysis['dependency_errors'].append("Missing or unresolved dependencies")
            analysis['suggestions'].append("Run npm install to ensure all dependencies are installed")
        
        # Check for TypeScript errors
        if any(term in combined_output for term in ['typescript', 'ts(', '.ts(']):
            analysis['typescript_errors'].append("TypeScript compilation errors")
            analysis['suggestions'].append("Check TypeScript configuration and fix type errors")
        
        # Check for ESLint warnings
        if 'eslint' in combined_output or 'warning' in combined_output:
            analysis['eslint_warnings'].append("Code quality warnings detected")
            analysis['suggestions'].append("Review and fix ESLint warnings for better code quality")
        
        # Check for compilation errors
        if any(term in combined_output for term in ['syntax error', 'unexpected token', 'parse error']):
            analysis['compilation_errors'].append("JavaScript/JSX syntax errors")
            analysis['suggestions'].append("Review code syntax and fix compilation errors")
        
        if not any(analysis.values()):
            analysis['general_errors'].append("Build failed with unknown error")
            analysis['suggestions'].append("Check the full error output for more details")
        
        return analysis
