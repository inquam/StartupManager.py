import os
import sys
import shutil
import platform
from pathlib import Path
import subprocess


class StartupManager:
    """
    A cross-platform class to manage application startup entries.
    Supports Windows, macOS, and Linux.
    """

    def __init__(self, app_name, app_path):
        """
        Initialize the StartupManager with the application name and path.
        
        Args:
            app_name (str): The name of your application
            app_path (str): The full path to your executable or script
        """
        self.app_name = app_name
        self.app_path = os.path.abspath(app_path)
        self.system = platform.system()
        
        # Validate that the app path exists
        if not os.path.exists(self.app_path):
            raise FileNotFoundError(f"Application path not found: {self.app_path}")

    def _get_startup_location(self):
        """
        Get the appropriate startup location based on the operating system.
        
        Returns:
            Path: The path to the startup directory or file
        """
        if self.system == "Windows":
            # Windows startup folder
            startup_path = Path(os.path.expandvars("%APPDATA%\\Microsoft\\Windows\\Start Menu\\Programs\\Startup"))
            return startup_path
            
        elif self.system == "Darwin":  # macOS
            # macOS LaunchAgents directory
            launch_agents = Path.home() / "Library" / "LaunchAgents"
            os.makedirs(launch_agents, exist_ok=True)
            plist_path = launch_agents / f"{self.app_name}.plist"
            return plist_path
            
        elif self.system == "Linux":
            # Linux autostart directory
            autostart_dir = Path.home() / ".config" / "autostart"
            os.makedirs(autostart_dir, exist_ok=True)
            desktop_path = autostart_dir / f"{self.app_name}.desktop"
            return desktop_path
            
        else:
            raise NotImplementedError(f"Unsupported operating system: {self.system}")

    def is_enabled(self):
        """
        Check if the application is set to run at startup.
        
        Returns:
            bool: True if enabled, False otherwise
        """
        startup_location = self._get_startup_location()
        
        if self.system == "Windows":
            shortcut_path = startup_location / f"{self.app_name}.lnk"
            return shortcut_path.exists()
            
        elif self.system == "Darwin":  # macOS
            return startup_location.exists()
            
        elif self.system == "Linux":
            return startup_location.exists()

    def enable(self):
        """
        Enable the application to run at startup.
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            startup_location = self._get_startup_location()
            
            if self.system == "Windows":
                # Create a shortcut in the Windows startup folder
                shortcut_path = startup_location / f"{self.app_name}.lnk"
                
                # Use PowerShell to create the shortcut
                ps_command = f"""
                $WshShell = New-Object -comObject WScript.Shell
                $Shortcut = $WshShell.CreateShortcut('{shortcut_path}')
                $Shortcut.TargetPath = '{self.app_path}'
                $Shortcut.Save()
                """
                
                subprocess.run(["powershell", "-Command", ps_command], 
                               check=True, capture_output=True)
                
            elif self.system == "Darwin":  # macOS
                # Create a plist file for macOS LaunchAgents
                plist_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>{self.app_name}</string>
    <key>ProgramArguments</key>
    <array>
        <string>{self.app_path}</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
</dict>
</plist>
"""
                with open(startup_location, 'w') as f:
                    f.write(plist_content)
                
                # Set proper permissions
                os.chmod(startup_location, 0o644)
                
                # Load the agent
                subprocess.run(["launchctl", "load", startup_location], 
                               check=True, capture_output=True)
                
            elif self.system == "Linux":
                # Create a .desktop file for the Linux autostart directory
                desktop_content = f"""[Desktop Entry]
Type=Application
Name={self.app_name}
Exec={self.app_path}
Terminal=false
X-GNOME-Autostart-enabled=true
"""
                with open(startup_location, 'w') as f:
                    f.write(desktop_content)
                
                # Make it executable
                os.chmod(startup_location, 0o755)
                
            return True
            
        except Exception as e:
            print(f"Error enabling startup: {e}")
            return False

    def disable(self):
        """
        Disable the application from running at startup.
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            startup_location = self._get_startup_location()
            
            if self.system == "Darwin":  # macOS
                if startup_location.exists():
                    # Unload the agent before removing
                    subprocess.run(["launchctl", "unload", startup_location], 
                                   check=True, capture_output=True)
                    os.remove(startup_location)
            elif self.system == "Windows":
                shortcut_path = startup_location / f"{self.app_name}.lnk"
                if shortcut_path.exists():
                    os.remove(shortcut_path)
            elif self.system == "Linux":
                if startup_location.exists():
                    os.remove(startup_location)
                
            return True
            
        except Exception as e:
            print(f"Error disabling startup: {e}")
            return False
