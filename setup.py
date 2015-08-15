import sys
from cx_Freeze import setup, Executable

# Dependencies are automatically detected, but it might need fine tuning.
build_exe_options = {"packages": ["os", "wx", "wx.lib.dialogs", "wx.stc", "keyword", "xml.dom.minidom"], "excludes": ["tkinter"], "include_files": ["HowTo.txt", "settings.xml", "README.md"]}

# GUI applications require a different base on Windows
# the default is for a console application
base = None
if sys.platform == "win32":
	base = "Win32GUI"

setup( 	name = "Pyrite - The Python Text Editor",
	 	version = "1.0.5",
	 	description = "A Simple Python text editor made by Zachary King",
	 	options = {"build_exe": build_exe_options},
	 	executables = [Executable("Pyrite.py", base=base)])
