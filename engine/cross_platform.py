import os
import platform
import subprocess
import webbrowser
import logging
from typing import Optional, List
from engine.config import PLATFORM_CONFIG

class CrossPlatformManager:
    def __init__(self):
        self.system = platform.system().lower()
        self.logger = logging.getLogger(__name__)
        self.setup_platform_specifics()
    
    def setup_platform_specifics(self):
        """Setup platform-specific configurations"""
        if self.system == 'windows':
            self.path_separator = '\\'
            self.default_browser = 'chrome'
        elif self.system == 'darwin':  # macOS
            self.path_separator = '/'
            self.default_browser = 'safari'
        elif self.system == 'linux':
            self.path_separator = '/'
            self.default_browser = 'firefox'
        else:
            self.path_separator = '/'
            self.default_browser = 'chrome'
    
    def get_path_separator(self) -> str:
        """Get the appropriate path separator for the current platform"""
        return self.path_separator
    
    def normalize_path(self, path: str) -> str:
        """Normalize path for current platform"""
        if self.system == 'windows':
            return path.replace('/', '\\')
        else:
            return path.replace('\\', '/')
    
    def open_application(self, app_name: str) -> bool:
        """Open application cross-platform"""
        try:
            if self.system == 'windows':
                return self._open_app_windows(app_name)
            elif self.system == 'darwin':
                return self._open_app_macos(app_name)
            elif self.system == 'linux':
                return self._open_app_linux(app_name)
            else:
                return self._open_app_generic(app_name)
        except Exception as e:
            self.logger.error(f"Error opening application {app_name}: {e}")
            return False
    
    def _open_app_windows(self, app_name: str) -> bool:
        """Open application on Windows"""
        try:
            # Try using start command
            subprocess.run(['start', app_name], shell=True, check=True)
            return True
        except subprocess.CalledProcessError:
            try:
                # Try using os.startfile
                os.startfile(app_name)
                return True
            except Exception:
                return False
    
    def _open_app_macos(self, app_name: str) -> bool:
        """Open application on macOS"""
        try:
            subprocess.run(['open', '-a', app_name], check=True)
            return True
        except subprocess.CalledProcessError:
            return False
    
    def _open_app_linux(self, app_name: str) -> bool:
        """Open application on Linux"""
        try:
            subprocess.run([app_name], check=True)
            return True
        except subprocess.CalledProcessError:
            try:
                subprocess.run(['xdg-open', app_name], check=True)
                return True
            except subprocess.CalledProcessError:
                return False
    
    def _open_app_generic(self, app_name: str) -> bool:
        """Generic application opening"""
        try:
            subprocess.Popen([app_name])
            return True
        except Exception:
            return False
    
    def open_url(self, url: str, browser: Optional[str] = None) -> bool:
        """Open URL in browser cross-platform"""
        try:
            if browser and browser != 'auto':
                return self._open_url_specific_browser(url, browser)
            else:
                return self._open_url_default_browser(url)
        except Exception as e:
            self.logger.error(f"Error opening URL {url}: {e}")
            return False
    
    def _open_url_specific_browser(self, url: str, browser: str) -> bool:
        """Open URL in specific browser"""
        try:
            if self.system == 'windows':
                subprocess.run(['start', browser, url], shell=True, check=True)
            elif self.system == 'darwin':
                subprocess.run(['open', '-a', browser, url], check=True)
            elif self.system == 'linux':
                subprocess.run([browser, url], check=True)
            else:
                webbrowser.get(browser).open(url)
            return True
        except Exception:
            return False
    
    def _open_url_default_browser(self, url: str) -> bool:
        """Open URL in default browser"""
        try:
            webbrowser.open(url)
            return True
        except Exception:
            return False
    
    def get_system_info(self) -> dict:
        """Get detailed system information"""
        return {
            'system': self.system,
            'platform': platform.platform(),
            'architecture': platform.architecture()[0],
            'processor': platform.processor(),
            'python_version': platform.python_version(),
            'path_separator': self.path_separator,
            'default_browser': self.default_browser
        }
    
    def check_dependencies(self) -> dict:
        """Check if required dependencies are available"""
        dependencies = {
            'python': self._check_python_version(),
            'pip': self._check_pip(),
            'git': self._check_git(),
            'ffmpeg': self._check_ffmpeg(),
            'chrome': self._check_chrome(),
            'firefox': self._check_firefox(),
            'safari': self._check_safari()
        }
        return dependencies
    
    def _check_python_version(self) -> bool:
        """Check Python version"""
        try:
            version = platform.python_version()
            major, minor, _ = map(int, version.split('.'))
            return major >= 3 and minor >= 8
        except Exception:
            return False
    
    def _check_pip(self) -> bool:
        """Check if pip is available"""
        try:
            subprocess.run(['pip', '--version'], capture_output=True, check=True)
            return True
        except Exception:
            return False
    
    def _check_git(self) -> bool:
        """Check if git is available"""
        try:
            subprocess.run(['git', '--version'], capture_output=True, check=True)
            return True
        except Exception:
            return False
    
    def _check_ffmpeg(self) -> bool:
        """Check if ffmpeg is available"""
        try:
            subprocess.run(['ffmpeg', '-version'], capture_output=True, check=True)
            return True
        except Exception:
            return False
    
    def _check_chrome(self) -> bool:
        """Check if Chrome is available"""
        try:
            if self.system == 'windows':
                subprocess.run(['chrome', '--version'], capture_output=True, check=True)
            elif self.system == 'darwin':
                subprocess.run(['/Applications/Google Chrome.app/Contents/MacOS/Google Chrome', '--version'], 
                             capture_output=True, check=True)
            elif self.system == 'linux':
                subprocess.run(['google-chrome', '--version'], capture_output=True, check=True)
            return True
        except Exception:
            return False
    
    def _check_firefox(self) -> bool:
        """Check if Firefox is available"""
        try:
            if self.system == 'windows':
                subprocess.run(['firefox', '--version'], capture_output=True, check=True)
            elif self.system == 'darwin':
                subprocess.run(['/Applications/Firefox.app/Contents/MacOS/firefox', '--version'], 
                             capture_output=True, check=True)
            elif self.system == 'linux':
                subprocess.run(['firefox', '--version'], capture_output=True, check=True)
            return True
        except Exception:
            return False
    
    def _check_safari(self) -> bool:
        """Check if Safari is available (macOS only)"""
        if self.system == 'darwin':
            try:
                subprocess.run(['/Applications/Safari.app/Contents/MacOS/Safari', '--version'], 
                             capture_output=True, check=True)
                return True
            except Exception:
                return False
        return False
    
    def install_dependency(self, dependency: str) -> bool:
        """Install a dependency using the appropriate package manager"""
        try:
            if self.system == 'windows':
                return self._install_windows(dependency)
            elif self.system == 'darwin':
                return self._install_macos(dependency)
            elif self.system == 'linux':
                return self._install_linux(dependency)
            else:
                return False
        except Exception as e:
            self.logger.error(f"Error installing {dependency}: {e}")
            return False
    
    def _install_windows(self, dependency: str) -> bool:
        """Install dependency on Windows"""
        try:
            # Try using winget first
            subprocess.run(['winget', 'install', dependency], check=True)
            return True
        except subprocess.CalledProcessError:
            try:
                # Try using chocolatey
                subprocess.run(['choco', 'install', dependency], check=True)
                return True
            except subprocess.CalledProcessError:
                return False
    
    def _install_macos(self, dependency: str) -> bool:
        """Install dependency on macOS"""
        try:
            # Try using Homebrew
            subprocess.run(['brew', 'install', dependency], check=True)
            return True
        except subprocess.CalledProcessError:
            return False
    
    def _install_linux(self, dependency: str) -> bool:
        """Install dependency on Linux"""
        try:
            # Try using apt (Ubuntu/Debian)
            subprocess.run(['sudo', 'apt', 'install', dependency], check=True)
            return True
        except subprocess.CalledProcessError:
            try:
                # Try using yum (CentOS/RHEL)
                subprocess.run(['sudo', 'yum', 'install', dependency], check=True)
                return True
            except subprocess.CalledProcessError:
                return False
    
    def get_available_browsers(self) -> List[str]:
        """Get list of available browsers on the system"""
        browsers = []
        
        if self._check_chrome():
            browsers.append('chrome')
        if self._check_firefox():
            browsers.append('firefox')
        if self._check_safari():
            browsers.append('safari')
        
        return browsers 