#!/usr/bin/python
###
#	copyright (2015) Zachary King
#	Pyrite
#	Beta v1.0.2
###

import wx
import wx.lib.dialogs
import wx.stc as stc
import keyword
import os
from xml.dom.minidom import parse
import xml.dom.minidom

# Font face data depending on OS
if wx.Platform == '__WXMSW__':
    faces = { 'times': 'Times New Roman',
              'mono' : 'Courier New',
              'helv' : 'Arial',
              'other': 'Comic Sans MS',
              'size' : 10,
              'size2': 8,
             }
elif wx.Platform == '__WXMAC__':
    faces = { 'times': 'Times New Roman',
              'mono' : 'Monaco',
              'helv' : 'Arial',
              'other': 'Comic Sans MS',
              'size' : 12,
              'size2': 10,
             }
else:
    faces = { 'times': 'Times',
              'mono' : 'Courier',
              'helv' : 'Helvetica',
              'other': 'new century schoolbook',
              'size' : 12,
              'size2': 10,
             }

# Application Framework
class MainWindow(wx.Frame):
	def __init__(self, parent, title):
		# variables for file i/o
		self.dirname = ''
		self.filename = ''
		self.normalStylesFore = dict()
		self.normalStylesBack = dict()
		self.pythonStylesFore = dict()
		self.pythonStylesBack = dict()

		# editor options
		self.foldSymbols = 2
		self.lineNumbersEnabled = True
		self.leftMarginWidth = 25

		# Initialize the application Frame and create the Styled Text Control
		wx.Frame.__init__(self, parent, title=title, size=(800, 600))
		self.control = stc.StyledTextCtrl(self, style=wx.TE_MULTILINE | wx.TE_WORDWRAP)

		# Bind Ctrl + '=' and Ctrl + '-' to zooming in and out or making the text bigger/smaller
		self.control.CmdKeyAssign(ord('='), stc.STC_SCMOD_CTRL, stc.STC_CMD_ZOOMIN) # Ctrl + = to zoom in
		self.control.CmdKeyAssign(ord('-'), stc.STC_SCMOD_CTRL, stc.STC_CMD_ZOOMOUT) # Ctrl + - to zoom out

		# Set up the Python keywords for syntax highlighting
		self.control.SetLexer(stc.STC_LEX_PYTHON)
		self.control.SetKeyWords(0, " ".join(keyword.kwlist))

		# Set some properties of the text control
		self.control.SetViewWhiteSpace(False)
		self.control.SetProperty("fold", "1")
		self.control.SetProperty("tab.timmy.whinge.level", "1")

		# Set margins
		self.control.SetMargins(5,0) # 5px margin on left inside of text control
		self.control.SetMarginType(1, stc.STC_MARGIN_NUMBER) # line numbers column
		self.control.SetMarginWidth(1, self.leftMarginWidth) # width of line numbers column

		# Set foldSymbols style based off the instance variable self.foldSymbols
		if self.foldSymbols == 0:
			# Arrow pointing right for contracted folders, arrow pointing down for expanded
			self.control.MarkerDefine(stc.STC_MARKNUM_FOLDEROPEN,    stc.STC_MARK_ARROWDOWN, "black", "black")
			self.control.MarkerDefine(stc.STC_MARKNUM_FOLDER,        stc.STC_MARK_ARROW, "black", "black")
			self.control.MarkerDefine(stc.STC_MARKNUM_FOLDERSUB,     stc.STC_MARK_EMPTY, "black", "black")
			self.control.MarkerDefine(stc.STC_MARKNUM_FOLDERTAIL,    stc.STC_MARK_EMPTY, "black", "black")
			self.control.MarkerDefine(stc.STC_MARKNUM_FOLDEREND,     stc.STC_MARK_EMPTY, "white", "black")
			self.control.MarkerDefine(stc.STC_MARKNUM_FOLDEROPENMID, stc.STC_MARK_EMPTY, "white", "black")
			self.control.MarkerDefine(stc.STC_MARKNUM_FOLDERMIDTAIL, stc.STC_MARK_EMPTY, "white", "black")

		elif self.foldSymbols == 1:
			# Plus for contracted folders, minus for expanded
			self.control.MarkerDefine(stc.STC_MARKNUM_FOLDEROPEN,    stc.STC_MARK_MINUS, "white", "black")
			self.control.MarkerDefine(stc.STC_MARKNUM_FOLDER,        stc.STC_MARK_PLUS,  "white", "black")
			self.control.MarkerDefine(stc.STC_MARKNUM_FOLDERSUB,     stc.STC_MARK_EMPTY, "white", "black")
			self.control.MarkerDefine(stc.STC_MARKNUM_FOLDERTAIL,    stc.STC_MARK_EMPTY, "white", "black")
			self.control.MarkerDefine(stc.STC_MARKNUM_FOLDEREND,     stc.STC_MARK_EMPTY, "white", "black")
			self.control.MarkerDefine(stc.STC_MARKNUM_FOLDEROPENMID, stc.STC_MARK_EMPTY, "white", "black")
			self.control.MarkerDefine(stc.STC_MARKNUM_FOLDERMIDTAIL, stc.STC_MARK_EMPTY, "white", "black")

		elif self.foldSymbols == 2:
			# Like a flattened tree control using circular headers and curved joins
			self.control.MarkerDefine(stc.STC_MARKNUM_FOLDEROPEN,    stc.STC_MARK_CIRCLEMINUS,          "white", "#404040")
			self.control.MarkerDefine(stc.STC_MARKNUM_FOLDER,        stc.STC_MARK_CIRCLEPLUS,           "white", "#404040")
			self.control.MarkerDefine(stc.STC_MARKNUM_FOLDERSUB,     stc.STC_MARK_VLINE,                "white", "#404040")
			self.control.MarkerDefine(stc.STC_MARKNUM_FOLDERTAIL,    stc.STC_MARK_LCORNERCURVE,         "white", "#404040")
			self.control.MarkerDefine(stc.STC_MARKNUM_FOLDEREND,     stc.STC_MARK_CIRCLEPLUSCONNECTED,  "white", "#404040")
			self.control.MarkerDefine(stc.STC_MARKNUM_FOLDEROPENMID, stc.STC_MARK_CIRCLEMINUSCONNECTED, "white", "#404040")
			self.control.MarkerDefine(stc.STC_MARKNUM_FOLDERMIDTAIL, stc.STC_MARK_TCORNERCURVE,         "white", "#404040")

		elif self.foldSymbols == 3:
			# Like a flattened tree control using square headers
			self.control.MarkerDefine(stc.STC_MARKNUM_FOLDEROPEN,    stc.STC_MARK_BOXMINUS,          "white", "#808080")
			self.control.MarkerDefine(stc.STC_MARKNUM_FOLDER,        stc.STC_MARK_BOXPLUS,           "white", "#808080")
			self.control.MarkerDefine(stc.STC_MARKNUM_FOLDERSUB,     stc.STC_MARK_VLINE,             "white", "#808080")
			self.control.MarkerDefine(stc.STC_MARKNUM_FOLDERTAIL,    stc.STC_MARK_LCORNER,           "white", "#808080")
			self.control.MarkerDefine(stc.STC_MARKNUM_FOLDEREND,     stc.STC_MARK_BOXPLUSCONNECTED,  "white", "#808080")
			self.control.MarkerDefine(stc.STC_MARKNUM_FOLDEROPENMID, stc.STC_MARK_BOXMINUSCONNECTED, "white", "#808080")
			self.control.MarkerDefine(stc.STC_MARKNUM_FOLDERMIDTAIL, stc.STC_MARK_TCORNER,           "white", "#808080")

		# Create the status bar at the bottom
		self.CreateStatusBar()
		self.UpdateLineCol(self) # show the line #, row # in status bar
		self.StatusBar.SetBackgroundColour((220,220,220))

		# Setting up the file menu
		filemenu = wx.Menu()
		menuNew = filemenu.Append(wx.ID_NEW, "&New", " Create a new document (Ctrl+N)")
		menuOpen = filemenu.Append(wx.ID_OPEN, "&Open", " Open an existing document (Ctrl+O)")
		menuSave = filemenu.Append(wx.ID_SAVE, "&Save", " Save the current document (Ctrl+S)")
		menuSaveAs = filemenu.Append(wx.ID_SAVEAS, "Save &As", " Save a new document (Alt+S)")
		filemenu.AppendSeparator()
		menuClose = filemenu.Append(wx.ID_EXIT, "&Close", " Close the application (Ctrl+W)")

		# Setting up the Edit menu
		editmenu = wx.Menu()
		menuUndo = editmenu.Append(wx.ID_UNDO, "&Undo", " Undo last action (Ctrl+Z)")
		menuRedo = editmenu.Append(wx.ID_REDO, "&Redo", " Redo last action (Ctrl+Y)")
		editmenu.AppendSeparator()
		menuSelectAll = editmenu.Append(wx.ID_SELECTALL, "&Select All", " Select the entire document (Ctrl+A)")
		menuCopy = editmenu.Append(wx.ID_COPY, "&Copy", " Copy selected text (Ctrl+C)")
		menuCut = editmenu.Append(wx.ID_CUT, "C&ut", " Cut selected text (Ctrl+X)")
		menuPaste = editmenu.Append(wx.ID_PASTE, "&Paste", " Pasted text from the clipboard (Ctrl+V)")

		# Setting up the Preferences menu
		prefmenu = wx.Menu()
		menuLineNumbers = prefmenu.Append(wx.ID_ANY, "Toggle &Line Numbers", " Show/Hide the line numbers column")

		# Setting up the help menu
		helpmenu = wx.Menu()
		menuHowTo = helpmenu.Append(wx.ID_ANY, "&How To...", " Get help using the text editor (F1)")
		helpmenu.AppendSeparator()
		menuAbout = helpmenu.Append(wx.ID_ABOUT, "&About", " Read about the text editor and it's making (F2)")

		# Creating the menubar
		menuBar = wx.MenuBar()
		menuBar.Append(filemenu, "&File")
		menuBar.Append(editmenu, "&Edit")
		menuBar.Append(prefmenu, "&Preferences")
		menuBar.Append(helpmenu, "&Help")
		self.SetMenuBar(menuBar)

		# File events
		self.Bind(wx.EVT_MENU, self.OnNew, menuNew)
		self.Bind(wx.EVT_MENU, self.OnOpen, menuOpen)
		self.Bind(wx.EVT_MENU, self.OnSave, menuSave)
		self.Bind(wx.EVT_MENU, self.OnSaveAs, menuSaveAs)
		self.Bind(wx.EVT_MENU, self.OnClose, menuClose)

		# Edit events
		self.Bind(wx.EVT_MENU, self.OnUndo, menuUndo)
		self.Bind(wx.EVT_MENU, self.OnRedo, menuRedo)
		self.Bind(wx.EVT_MENU, self.OnSelectAll, menuSelectAll)
		self.Bind(wx.EVT_MENU, self.OnCopy, menuCopy)
		self.Bind(wx.EVT_MENU, self.OnCut, menuCut)
		self.Bind(wx.EVT_MENU, self.OnPaste, menuPaste)

		# Preference events
		self.Bind(wx.EVT_MENU, self.OnToggleLineNumbers, menuLineNumbers)

		# Help events
		self.Bind(wx.EVT_MENU, self.OnHowTo, menuHowTo)
		self.Bind(wx.EVT_MENU, self.OnAbout, menuAbout)

		# Key bindings
		self.control.Bind(wx.EVT_CHAR, self.OnCharEvent)
		self.control.Bind(wx.EVT_KEY_UP, self.UpdateLineCol)
		self.control.Bind(stc.EVT_STC_UPDATEUI, self.OnUpdateUI)
		self.control.Bind(stc.EVT_STC_MARGINCLICK, self.OnMarginClick)
		self.control.Bind(wx.EVT_KEY_DOWN, self.OnKeyPressed)
		self.control.Bind(wx.EVT_LEFT_UP, self.OnLeftUp)

		# go ahead and display the application
		self.Show()

		# defaulting the style
		self.control.StyleSetSpec(stc.STC_STYLE_DEFAULT, "face:%(helv)s,size:%(size)d" % faces)
		self.control.StyleClearAll() # reset all to be like default

		# global default styles for all languages
		self.control.StyleSetSpec(stc.STC_STYLE_DEFAULT, "face:%(helv)s,size:%(size)d" % faces)
		self.control.StyleSetSpec(stc.STC_STYLE_LINENUMBER, "back:#C0C0C0,face:%(helv)s,size:%(size2)d" % faces)
		self.control.StyleSetSpec(stc.STC_STYLE_CONTROLCHAR, "face:%(other)s" % faces)
		self.control.StyleSetSpec(stc.STC_STYLE_BRACELIGHT, "fore:#FFFFFF,back:#0000FF,bold")
		self.control.StyleSetSpec(stc.STC_STYLE_BRACEBAD, "fore:#000000,back:#FF0000,bold")

		# Set all the theme settings
		self.ReadThemeSettings()
		self.ParseSettings("settings.xml")
		self.SetStyling()

	# Setting the styles
	def SetStyling(self):
		# Set the general foreground and background for normal and python styles
		pSFore = self.pythonStylesFore
		pSBack = self.pythonStylesBack
		nSFore = self.normalStylesFore
		nSBack = self.normalStylesBack

		# Python styles
		self.control.StyleSetBackground(stc.STC_STYLE_DEFAULT, nSBack["Main"])
		self.control.SetSelBackground(True, "#333333")

		# Default
		self.control.StyleSetSpec(stc.STC_P_DEFAULT, "fore:%s,back:%s" % (pSFore["Default"], pSBack["Default"]))
		self.control.StyleSetSpec(stc.STC_P_DEFAULT, "face:%(helv)s,size:%(size)d" % faces)

		# Comments
		self.control.StyleSetSpec(stc.STC_P_COMMENTLINE, "fore:%s,back:%s" % (pSFore["Comment"], pSBack["Comment"]))
		self.control.StyleSetSpec(stc.STC_P_COMMENTLINE, "face:%(other)s,size:%(size)d" % faces)

		# Number
		self.control.StyleSetSpec(stc.STC_P_NUMBER, "fore:%s,back:%s" % (pSFore["Number"], pSBack["Number"]))
		self.control.StyleSetSpec(stc.STC_P_NUMBER, "size:%(size)d" % faces)

		# String
		self.control.StyleSetSpec(stc.STC_P_STRING, "fore:%s,back:%s" % (pSFore["String"], pSBack["Number"]))
		self.control.StyleSetSpec(stc.STC_P_STRING, "face:%(helv)s,size:%(size)d" % faces)

		# Single-quoted string
		self.control.StyleSetSpec(stc.STC_P_CHARACTER, "fore:%s,back:%s" % (pSFore["SingleQuoteString"], pSBack["SingleQuoteString"]))
		self.control.StyleSetSpec(stc.STC_P_CHARACTER, "face:%(helv)s,size:%(size)d" % faces)

		# Keyword
		self.control.StyleSetSpec(stc.STC_P_WORD, "fore:%s,back:%s" % (pSFore["Keyword"], pSBack["Keyword"]))
		self.control.StyleSetSpec(stc.STC_P_WORD, "bold,size:%(size)d" % faces)

		# Triple quotes
		self.control.StyleSetSpec(stc.STC_P_TRIPLE, "fore:%s,back:%s" % (pSFore["TripleQuote"], pSBack["TripleQuote"]))
		self.control.StyleSetSpec(stc.STC_P_TRIPLE, "size:%(size)d" % faces)

		# Triple double quotes
		self.control.StyleSetSpec(stc.STC_P_TRIPLEDOUBLE, "fore:%s,back:%s" % (pSFore["TripleDoubleQuote"], pSBack["TripleDoubleQuote"]))
		self.control.StyleSetSpec(stc.STC_P_TRIPLEDOUBLE, "size:%(size)d" % faces)

		# Class name definition
		self.control.StyleSetSpec(stc.STC_P_CLASSNAME, "fore:%s,back:%s" % (pSFore["ClassName"], pSBack["ClassName"]))
		self.control.StyleSetSpec(stc.STC_P_CLASSNAME, "bold,underline,size:%(size)d" % faces)

		# Function name definition
		self.control.StyleSetSpec(stc.STC_P_DEFNAME, "fore:%s,back:%s" % (pSFore["FunctionName"], pSBack["FunctionName"]))
		self.control.StyleSetSpec(stc.STC_P_DEFNAME, "bold,size:%(size)d" % faces)

		# Operators
		self.control.StyleSetSpec(stc.STC_P_OPERATOR, "fore:%s,back:%s" % (pSFore["Operator"], pSBack["Operator"]))
		self.control.StyleSetSpec(stc.STC_P_OPERATOR, "bold,size:%(size)d" % faces)

		# Identifiers
		self.control.StyleSetSpec(stc.STC_P_IDENTIFIER, "fore:%s,back:%s" % (pSFore["Identifier"], pSBack["Identifier"]))
		self.control.StyleSetSpec(stc.STC_P_IDENTIFIER, "face:%(helv)s,size:%(size)d" % faces)

		# Comment blocks
		self.control.StyleSetSpec(stc.STC_P_COMMENTBLOCK, "fore:%s,back:%s" % (pSFore["CommentBlock"], pSBack["CommentBlock"]))
		self.control.StyleSetSpec(stc.STC_P_COMMENTBLOCK, "size:%(size)d" % faces)

		# End of line where string is not closed
		self.control.StyleSetSpec(stc.STC_P_STRINGEOL, "fore:%s,back:%s" % (pSFore["StringEOL"], pSBack["StringEOL"]))
		self.control.StyleSetSpec(stc.STC_P_STRINGEOL, "face:%(mono)s,eol,size:%(size)d" % faces)

		# Caret/Insertion Point
		self.control.SetCaretForeground(pSFore["Caret"])
		self.control.SetCaretLineBackground(pSBack["CaretLine"])
		self.control.SetCaretLineVisible(True)

	# New document menu action
	def OnNew(self, e):
		# Empty the instance variable for current filename, and the main text box's content
		self.filename = ""
		self.control.SetValue("")

	# Open existing document menu action
	def OnOpen(self, e):
		# First try opening the existing file; if it fails, the file doesn't exist most likely
		try:
			dlg = wx.FileDialog(self, "Choose a file", self.dirname, "", "*.*", wx.FD_OPEN)
			if (dlg.ShowModal() == wx.ID_OK):
				self.filename = dlg.GetFilename()
				self.dirname = dlg.GetDirectory()
				f = open(os.path.join(self.dirname, self.filename), 'r')
				self.control.SetValue(f.read())
				f.close()
			dlg.Destroy()
		except:
			dlg = wx.MessageDialog(self, " Couldn't open file", "Error 009", wx.ICON_ERROR)
			dlg.ShowModal()
			dlg.Destroy()

	# Save the document menu action
	def OnSave(self, e):
		# First try just saving the existing file, but if that file doesn't 
		# exist it will fail, and the except will launch the Save As.
		try:
			f = open(os.path.join(self.dirname, self.filename), 'w')
			f.write(self.control.GetValue())
			f.close()
		except:
			try:
				# If regular save fails, try the Save As method.
				dlg = wx.FileDialog(self, "Save file as", self.dirname, "Untitled", "*.*", wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT)
				if (dlg.ShowModal() == wx.ID_OK):
					self.filename = dlg.GetFilename()
					self.dirname = dlg.GetDirectory()
					f = open(os.path.join(self.dirname, self.filename), 'w')
					f.write(self.control.GetValue())
					f.close()
				dlg.Destroy()
			except:
				pass

	# Save a new document menu action
	def OnSaveAs(self, e):
		try:
			dlg = wx.FileDialog(self, "Save file as", self.dirname, self.filename, "*.*", wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT)
			if (dlg.ShowModal() == wx.ID_OK):
				self.filename = dlg.GetFilename()
				self.dirname = dlg.GetDirectory()
				f = open(os.path.join(self.dirname, self.filename), 'w')
				f.write(self.control.GetValue())
				f.close()
			dlg.Destroy()
		except:
			pass

	# Terminate the program menu action
	def OnClose(self, e):
		self.Close(True)

	# Undo event menu action
	def OnUndo(self, e):
		self.control.Undo()

	# Redo event menu action
	def OnRedo(self, e):
		self.control.Redo()

	# Select All text menu action
	def OnSelectAll(self, e):
		self.control.SelectAll()

	# Copy selected text menu action
	def OnCopy(self, e):
		self.control.Copy()

	# Cut selected text menu action
	def OnCut(self, e):
		self.control.Cut()

	# Paste text from clipboard menu action
	def OnPaste(self, e):
		self.control.Paste()

	# Toggle Line numbers menu action
	def OnToggleLineNumbers(self, e):
		if (self.lineNumbersEnabled):
			self.control.SetMarginWidth(1,0)
			self.lineNumbersEnabled = False
		else:
			self.control.SetMarginWidth(1, self.leftMarginWidth)
			self.lineNumbersEnabled = True

	# Show How To menu action
	def OnHowTo(self, e):
		# Simple display the How To from HowTo.txt in a modal window
		f = open("HowTo.txt", "r")
		msg = f.read()
		f.close()
		dlg = wx.lib.dialogs.ScrolledMessageDialog(self, msg, "How To:", size=(400, 500))
		dlg.ShowModal()
		dlg.Destroy()

	# Show About menu action
	def OnAbout(self, e):
		# Simple display a modal window telling about the application
		dlg = wx.MessageDialog(self, "An elegant, yet simple, text editor made with Python and wxPython.\nCreated by Zachary King.\n02/1/2015\nVersion 1.0.5\n", "About My Text Editor", wx.OK)
		dlg.ShowModal()
		dlg.Destroy()

	# Update the Line/Col in status bar
	def UpdateLineCol(self, e):
		line = self.control.GetCurrentLine() + 1
		col = self.control.GetColumn(self.control.GetCurrentPos())
		stat = "Line %s, Column %s" % (line, col)
		self.StatusBar.SetStatusText(stat, 0)

	# Left mouse up
	def OnLeftUp(self, e):
		# This way if you click on another position in the text box
		# it will update the line/col number in the status bar (like it should)
		self.UpdateLineCol(self)
		e.Skip()

	# Char event
	def OnCharEvent(self, e):
		# These are keyboard shortcuts.
		# Some of these are very unstable and
		# may only work on Windows currently.
		keycode = e.GetKeyCode()
		controlDown = e.CmdDown()
		altDown = e.AltDown()
		shiftDown = e.ShiftDown()
		#print(keycode) # helps with testing
		if (keycode == 14): # Ctrl + N
			self.OnNew(self)
		elif (keycode == 15): # Ctrl + O
			self.OnOpen(self)
		elif (keycode == 19): # Ctrl + S
			self.OnSave(self)
		elif (altDown and (keycode == 115)): # Alt + S
			self.OnSaveAs(self)
		elif (keycode == 23): # Ctrl + W
			self.OnClose(self)
		elif (keycode == 1): # Ctrl + A
			self.OnSelectAll(self)
		elif (keycode == 340): # F1
			self.OnHowTo(self)
		elif (keycode == 341): # F2
			self.OnAbout(self)
		else:
			e.Skip()

	# Update the user interface 
	def OnUpdateUI(self, e):
		# check for matching braces
		braceAtCaret = -1
		braceOpposite = -1
		charBefore = None
		caretPos = self.control.GetCurrentPos()

		if (caretPos > 0):
			charBefore = self.control.GetCharAt(caretPos - 1)
			styleBefore = self.control.GetStyleAt(caretPos - 1)

		# check before
		if (charBefore and chr(charBefore) in "[]{}()" and styleBefore == stc.STC_P_OPERATOR):
			braceAtCaret = caretPos - 1

		# check after
		if (braceAtCaret < 0):
			charAfter = self.control.GetCharAt(caretPos)
			styleAfter = self.control.GetStyleAt(caretPos)

			if (charAfter and chr(charAfter) in "[]{}()" and styleAfter == stc.STC_P_OPERATOR):
				braceAtCaret = caretPos

		if (braceAtCaret >= 0):
			braceOpposite = self.control.BraceMatch(braceAtCaret)

		if (braceAtCaret != -1 and braceOpposite == -1):
			self.control.BraceBadLight(braceAtCaret)
		else:
			self.control.BraceHighlight(braceAtCaret,braceOpposite) 

	# Handles when the margin is clicked (folding)
	def OnMarginClick(self, e):
		# fold and unfold as needed
		if (e.GetMargin() == 2):
			if (e.GetShift() and e.GetControl()):
				self.control.FoldAll()
			else:
				lineClicked = self.control.LineFromPosition(e.GetPosition())

				if (self.control.GetFoldLevel(lineClicked) & stc.STC_P_FOLDLEVELHEADERFLAG):
					if (e.GetShift()):
						self.control.SetFoldExpanded(lineClicked, True)
						self.control.Expand(lineClicked, True, True, -1)
					elif (e.GetControl()):
						if (self.control.GetFoldExpaned(lineClicked)):
							self.control.SetFoldExpanded(lineClicked, False)
							self.control.Expand(lineClicked, False, True, 0)
						else:
							self.control.SetFoldExpanded(lineClicked, True)
							self.control.Expand(lineClicked, True, True, 100)
					else:
						self.control.ToggleFold(lineClicked)

	# Folds all the blocks of code
	def FoldAll(self):
		lineCount = self.control.GetLineCount()
		expanding = True

		# find out if we are folding or unfolding
		for lineNum in range(lineCount):
			if self.GetFoldLevel(lineNum) & stc.STC_FOLDLEVELHEADERFLAG:
				expanding = not self.GetFoldExpanded(lineNum)
				break

		lineNum = 0

		while lineNum < lineCount:
			level = self.GetFoldLevel(lineNum)
			if level & stc.STC_FOLDLEVELHEADERFLAG and \
				(level & stc.STC_FOLDLEVELNUMBERMASK) == stc.STC_FOLDLEVELBASE:

				if expanding:
					self.SetFoldExpanded(lineNum, True)
					lineNum = self.Expand(lineNum, True)
					lineNum = lineNum - 1
				else:
					lastChild = self.GetLastChild(lineNum, -1)
					self.SetFoldExpanded(lineNum, False)

					if lastChild > lineNum:
						self.HideLines(lineNum+1, lastChild)

		lineNum = lineNum + 1

	# Helper method for expanding a block of code
	def Expand(self, line, doExpand, force=False, visLevels=0, level=-1):
		lastChild = self.GetLastChild(line, level)
		line = line + 1

		while line <= lastChild:
			if force:
				if visLevels > 0:
					self.ShowLines(line, line)
				else:
					self.HideLines(line, line)
			else:
				if doExpand:
					self.ShowLines(line, line)

			if level == -1:
				level = self.GetFoldLevel(line)

			if level & stc.STC_FOLDLEVELHEADERFLAG:
				if force:
					if visLevels > 1:
						self.SetFoldExpanded(line, True)
					else:
						self.SetFoldExpanded(line, False)

					line = self.Expand(line, doExpand, force, visLevels-1)

				else:
					if doExpand and self.GetFoldExpanded(line):
						line = self.Expand(line, True, force, visLevels-1)
					else:
						line = self.Expand(line, False, force, visLevels-1)
			else:
				line = line + 1

		return line

	# Key press event bindings
	def OnKeyPressed(self, e):
		# if the tip is already up, hide it
		if (self.control.CallTipActive()):
			self.control.CallTipCancel()
		key = e.GetKeyCode()

		# Ctrl + Space for autocomplete
		if (key == 32 and e.ControlDown()):
			pos = self.control.GetCurrentPos()

			# Small tool tip box
			if (e.ShiftDown()):
				self.control.CallTipSetBackground("yellow")
				self.control.CallTipShow(pos, "Press <Ctrl> + <Space> for code completion")
			# Code completion
			else:
				kw = keyword.kwlist[:]
				kw.sort() # Case-sensitive
				self.control.AutoCompSetIgnoreCase(False) # so this needs to match
				self.control.AutoCompShow(0, " ".join(kw))
		else:
			e.Skip()

	# Parses an XML settings file for styling and configuring the text editor
	def ParseSettings(self, settings_file):
		# Open XML document using minidom parser
		DOMTree = xml.dom.minidom.parse(settings_file)
		collection = DOMTree.documentElement # Root element
		
		# Get all the styles in the collection
		styles = collection.getElementsByTagName("style")
		for s in styles:
			item = s.getElementsByTagName("item")[0].childNodes[0].data
			color = s.getElementsByTagName("color")[0].childNodes[0].data
			side = s.getElementsByTagName("side")[0].childNodes[0].data
			sType = s.getAttribute("type")
			if sType == "normal":
				if side == "Back": # background
					self.normalStylesBack[str(item)] = str(color)
				else:
					self.normalStylesFore[str(item)] = str(color)
			elif sType == "python":
				if side == "Back":
					self.pythonStylesBack[str(item)] = str(color)
				else:
					self.pythonStylesFore[str(item)] = str(color)


app = wx.App(False)
frame = MainWindow(None, "Pyrite (beta)")
app.MainLoop()