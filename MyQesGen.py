# -*- coding: cp936 -*- 

###########################################################################
## Python code generated with wxFormBuilder (version Jun 17 2015) 
## Last update: 2017-01-04
## version 1.22
###########################################################################

# section imports -----------------------------
import wx
import wx.richtext
import itertools
import re
import random
import math
import os, sys
import threading
import lovemath
from add_brackets import main
from kidsmode import isExpValid
import codecs
from configobj import ConfigObj
from wx.html import HtmlEasyPrinting
# ---------------------------------------------

# define consts -------------------------------
OPS = ['+', '-', '*', '/']
# bad patterns
BAD_PATTERN_1 = '\d+\/\d+\/'
BAD_PATTERN_2 = '(\d+)\/(\d+)'
SIGNS =[ u"( )", u"□", u"?", u"__" ]
VER = 'v1.22' # software version
BUILD = 'Build 170204'
AUTHOR = 'Quinn Song'
TITLE = 'Love Math'
PANEL_BKCOLOR = wx.Colour(234,234,234)
# ---------------------------------------------

# defined for threading events
myEVT_COUNT = wx.NewEventType()
EVT_COUNT = wx.PyEventBinder(myEVT_COUNT, 1)

# get exe path
EXE_PATH = unicode(os.path.dirname(sys.path[0]), 'cp936')

# HtmlEasyPrinting solution from:
# https://www.daniweb.com/programming/software-development/threads/453413/printing-in-wxpython
class Printer(HtmlEasyPrinting):
    def __init__(self):
        global frame
        HtmlEasyPrinting.__init__(self,name="Printing", parentWindow=None)

    def PreviewText(self, text, doc_name):
        self.SetHeader(doc_name)
        try:
            HtmlEasyPrinting.PreviewText(self, text)
        except: pass

    def Print(self, text, doc_name):
         self.SetHeader(doc_name)
         self.PrintText(text, doc_name)  

class CountEvent(wx.PyCommandEvent):
    """Event to signal that a count value is ready"""
    def __init__(self, etype, eid, value=None):
        """Creates the event object"""
        wx.PyCommandEvent.__init__(self, etype, eid)
        self._value = value

    def GetValue(self):
        """Returns the value from the event.
        @return: the value of this event

        """
        return self._value


class CountingThread(threading.Thread):
    def __init__(self, parent, value):
        """
        @param parent: The gui object that should recieve the value
        @param value: value to 'calculate' to
        """
        threading.Thread.__init__(self)
        self._parent = parent
        self._value = value

    def run(self):
        """Overrides Thread.run. Don't call this directly its called internally
        when you call Thread.start().
        """
        self._parent.run_thread()
        evt = CountEvent(myEVT_COUNT, -1, self._value)
        wx.PostEvent(self._parent, evt)


###########################################################################
## Class ExpressionGenerator
###########################################################################

class ExpressionGenerator ( wx.Dialog ):
        
        def __init__( self, parent ):
                wx.Dialog.__init__ ( self, parent, id = wx.ID_ANY, title = u"%s %s" % (TITLE, VER), pos = wx.DefaultPosition, size = wx.Size( 1024,650 ), style = wx.DEFAULT_DIALOG_STYLE|wx.MINIMIZE_BOX|wx.RESIZE_BORDER|wx.MAXIMIZE_BOX )
                
                self.SetSizeHintsSz ((900, 550), wx.DefaultSize )
                # init icons
                self.preview_ico = lovemath.previewIcon.GetBitmap()
                self.save32_ico = lovemath.save32Icon.GetBitmap()
                self.close32_ico = lovemath.closeIcon.GetBitmap()
                self.print_ico = lovemath.printIcon.GetBitmap()
                self.icon = lovemath.heart.GetIcon()
                self.refresh_ico = lovemath.refreshIcon.GetBitmap()
                self.setup_ico = lovemath.setup.GetBitmap()
                self.qa_ico = lovemath.qa.GetBitmap()
                self.q_ico = lovemath.q.GetBitmap()
                self.me_ico = lovemath.me.GetBitmap()
                self.SetIcon(self.icon)
                
                # define variables
                self.max_steps = 1
                self.exclude_zero = False
                self.row_exp = True  ## False for vertical Format
                self.adjust_value = None
                self.check_every_step = True
                self.have_remainder = False
                self.max_num = 10
                self.allow_minus = False
                self.items_per_row = 1
                self.total_items = 10
                self.opers = []
                self.questions = []
                self.answers = []
                self.x_list = []
                self.qx_list = []
                self.show_answer = False
                self.ques_width = None
                self.progress_dlg = None
                self.cancel = False
                self.use_threading = None
                self.check_bracket = False
                self.size = (1024, 650)
                self.save_answer_under = False
                self.hide_ques_index = False
                self.line_spacing = 1
                self.use_sign = False
                self.sign_selected = 0
                
                # default header and footer
                self.footer = u"="*45 + u"\r\nThank you for using Love Math! ^O^"
                self.header = u"Here are the arithmetic expressions:\r\n" + u"="*45
                # font settings
                self.font_bold = False
                self.font_name = 'Courier New'
                self.font_size =  10 #wx.NORMAL_FONT.GetPointSize()
                self.default_font = None
                self.m_comboBoxFontChoices = [u'Courier New', u'Fixedsys', u'Lucida Console']
                
                # program config file
                self.config = None
                self.configfile = os.path.join(EXE_PATH, 'LoveMath.ini')
                
                # get user doc dir
                path = wx.StandardPaths.Get()
                UserDocDir = path.GetDocumentsDir()
                
                # init background and font color
                self.bg_color = 'white'
                self.fg_color = 'black'
                
                # init text file path for user settings
                self.ques_path = os.path.join(UserDocDir, u'questions.txt')
                self.answ_path = os.path.join(UserDocDir, u'questions_answers.txt')
                self.is_dash = None
                
                # read program config file
                self.readFile()
                
                # set window size
                if self.size != (1200, 650):
                    self.SetSize(self.size)

                self.m_notebookGlobal = wx.Notebook( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.NB_FIXEDWIDTH)
                self.m_panelGen = wx.Panel( self.m_notebookGlobal, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
                self.m_panelGen.SetBackgroundColour(PANEL_BKCOLOR)
                bSizerGen = wx.BoxSizer( wx.VERTICAL )
                
                self.m_richTextWindow = wx.richtext.RichTextCtrl( self.m_panelGen, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0|wx.VSCROLL|wx.HSCROLL|wx.NO_BORDER|wx.WANTS_CHARS )
                bSizerGen.Add( self.m_richTextWindow, 10, wx.EXPAND |wx.ALL, 5 )

                self.default_font = self.m_richTextWindow.GetFont()
                self.m_richTextWindow.SetBackgroundColour(self.bg_color)
                self.m_richTextWindow.BeginTextColour(self.fg_color)
                self.default_font.SetFaceName(self.font_name)
                #self.default_font.MakeBold()
                self.default_font.SetPointSize(self.font_size)
                #self.default_font.SetWeight(wx.FONTWEIGHT_BOLD if self.font_bold else wx.FONTWEIGHT_NORMAL)
                self.m_richTextWindow.SetFont(self.default_font)

                self.m_richTextWindow.ApplyAlignmentToSelection(wx.TEXT_ALIGNMENT_CENTER)
                
                bSizerBtns = wx.BoxSizer( wx.HORIZONTAL )

                self.m_buttonBold = wx.ToggleButton( self.m_panelGen, wx.ID_ANY, u"B", wx.DefaultPosition, wx.Size( -1,-1 ), wx.BU_EXACTFIT|wx.NO_BORDER )
                bSizerBtns.Add( self.m_buttonBold, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )
                self.m_buttonBold.SetToolTipString(u'Bold')
                f = self.m_buttonBold.GetFont()
                f.SetWeight(wx.FONTWEIGHT_BOLD)
                self.m_buttonBold.SetFont( f)      
                
                #self.m_comboBoxFontChoices = self.get_fixed_fonts() # disable this for now
                self.m_comboBoxFont = wx.ComboBox( self.m_panelGen, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, self.m_comboBoxFontChoices, wx.NO_BORDER )
                self.m_comboBoxFont.SetToolTipString( u"Font Name" )
                self.m_comboBoxFont.SetValue(self.font_name)
                bSizerBtns.Add( self.m_comboBoxFont, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )
                
                m_comboBoxFontSizeChoices = ['8','9','10','11','12','14','16','18', '20','22','24','26','28','36']
                self.m_comboBoxFontSize = wx.ComboBox( self.m_panelGen, wx.ID_ANY, u"Size", wx.DefaultPosition, wx.Size( 60,-1 ), m_comboBoxFontSizeChoices, wx.CB_READONLY|wx.NO_BORDER )
                self.m_comboBoxFontSize.SetSelection(m_comboBoxFontSizeChoices.index(str(self.font_size)))
                self.m_comboBoxFontSize.SetToolTipString( u"Font Size" )
                bSizerBtns.Add( self.m_comboBoxFontSize, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )
                
                self.m_btnBg = wx.Button( self.m_panelGen, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.Size( 22,22 ), 0|wx.NO_BORDER )
                bSizerBtns.Add( self.m_btnBg, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )
                self.m_btnBg.SetBackgroundColour( self.bg_color) 
                self.m_btnBg.SetToolTipString(u'Background Color')
                
                self.m_btnFg = wx.Button( self.m_panelGen, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.Size( 22,22 ), 0|wx.NO_BORDER )
                bSizerBtns.Add( self.m_btnFg, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )
                self.m_btnFg.SetBackgroundColour( self.fg_color) 
                self.m_btnFg.SetToolTipString(u'Font Color')
                
                self.anw_ico = self.q_ico if self.show_answer else self.qa_ico
                self.m_btnAnswer = wx.BitmapButton( self.m_panelGen, wx.ID_ANY, self.anw_ico, wx.DefaultPosition, wx.Size(32, 32), wx.NO_BORDER|wx.BU_EXACTFIT  )
                bSizerBtns.Add( self.m_btnAnswer, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )
                self.m_btnAnswer.SetToolTipString(u'Hide Answer' if self.show_answer else u'Show Answer')
                
                bSizerBtns.AddSpacer( ( 0, 0), 5, wx.EXPAND, 5 )
                # add print icons
                self.m_btnPageSetup = wx.BitmapButton( self.m_panelGen, wx.ID_ANY, self.setup_ico, wx.DefaultPosition, wx.Size(32, 32), wx.NO_BORDER|wx.BU_EXACTFIT  )
                bSizerBtns.Add( self.m_btnPageSetup, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 0 )
                self.m_btnPageSetup.SetToolTipString(u'Page Setup')
                
                self.m_btnPreview = wx.BitmapButton( self.m_panelGen, wx.ID_ANY, self.preview_ico, wx.DefaultPosition, wx.Size(48, 48), wx.NO_BORDER|wx.BU_EXACTFIT  )
                bSizerBtns.Add( self.m_btnPreview, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 0 )
                self.m_btnPreview.SetToolTipString(u'Preview')
                
                self.m_btnPrint = wx.BitmapButton( self.m_panelGen, wx.ID_ANY, self.print_ico, wx.DefaultPosition, wx.Size(32, 32), wx.NO_BORDER|wx.BU_EXACTFIT  )
                bSizerBtns.Add( self.m_btnPrint, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 0 )
                self.m_btnPrint.SetToolTipString(u'Print')
                
                bSizerBtns.AddSpacer( ( 0, 0), 5, wx.EXPAND, 5 )
                
                self.m_btnGen = wx.BitmapButton( self.m_panelGen, wx.ID_ANY, self.refresh_ico, wx.DefaultPosition, wx.Size(32, 32), wx.NO_BORDER|wx.BU_EXACTFIT  )

                bSizerBtns.Add( self.m_btnGen, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )
                self.m_btnGen.SetToolTipString(u'Generate')
                
                self.m_btnSave = wx.BitmapButton( self.m_panelGen, wx.ID_ANY, self.save32_ico, wx.DefaultPosition, wx.Size(32, 32), wx.NO_BORDER|wx.BU_EXACTFIT ) 
                bSizerBtns.Add( self.m_btnSave, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )
                self.m_btnSave.SetToolTipString(u'Save to text file')
                
                self.m_btnExit = wx.BitmapButton( self.m_panelGen, wx.ID_ANY, self.close32_ico, wx.DefaultPosition, wx.Size(32, 32), wx.NO_BORDER|wx.BU_EXACTFIT ) 
                bSizerBtns.Add( self.m_btnExit, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )
                self.m_btnExit.SetToolTipString(u'Exit')                
                
                bSizerGen.Add( bSizerBtns, 0, wx.ALIGN_RIGHT|wx.EXPAND, 5 )
                
                self.m_staticline1 = wx.StaticLine( self.m_panelGen, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LI_HORIZONTAL )
                bSizerGen.Add( self.m_staticline1, 0, wx.EXPAND |wx.ALL, 5 )            
                
                bSizerGen.AddSpacer( (-1, 20))

                bSizerAuthorLine = wx.BoxSizer( wx.HORIZONTAL )
                
                self.m_bitmapMe = wx.StaticBitmap( self.m_panelGen, wx.ID_ANY, self.me_ico, wx.DefaultPosition, wx.DefaultSize, 0 )
                bSizerAuthorLine.Add( self.m_bitmapMe, 0, wx.ALIGN_CENTER, 5 )
                self.m_bitmapMe.SetToolTipString(u"My Photo")
                
                self.m_staticTextAuthor = wx.StaticText( self.m_panelGen, wx.ID_ANY, AUTHOR, wx.DefaultPosition, wx.DefaultSize, 0 )
                self.m_staticTextAuthor.Wrap( -1 )
                self.m_staticTextAuthor.Enable( False )
                
                bSizerAuthorLine.Add( self.m_staticTextAuthor, 1, wx.ALIGN_CENTER|wx.ALL, 5 )
                bSizerGen.Add( bSizerAuthorLine, 0, wx.ALIGN_CENTER_HORIZONTAL, 5 )
                
                self.m_panelGen.SetSizer( bSizerGen )
                self.m_panelGen.Layout()
                #bSizerGen.Fit( self.m_panelGen )
                self.m_notebookGlobal.AddPage( self.m_panelGen, "Main", False )
                self.m_panelSettings = wx.Panel( self.m_notebookGlobal, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
                self.m_panelSettings.SetBackgroundColour(PANEL_BKCOLOR)
                bSizerMain = wx.BoxSizer( wx.VERTICAL )
                
                gSizerMain = wx.FlexGridSizer( 0, 4, 0, 0 )
                
                sbSizerMultiStep = wx.StaticBoxSizer( wx.StaticBox( self.m_panelSettings, wx.ID_ANY, u"Steps Count" ), wx.HORIZONTAL )
                
                self.m_spinCtrlSteps = wx.SpinCtrl( sbSizerMultiStep.GetStaticBox(), wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.Size( 65,-1 ), wx.SP_ARROW_KEYS, 1, 50, self.max_steps )
                sbSizerMultiStep.Add( self.m_spinCtrlSteps, 0, wx.ALL, 5 )      
                
                gSizerMain.Add( sbSizerMultiStep, 1, wx.EXPAND, 5 )     
                
                sbSizerRange = wx.StaticBoxSizer( wx.StaticBox( self.m_panelSettings, wx.ID_ANY, u"Operation Range" ), wx.HORIZONTAL )
                
                m_comboBoxRangeChoices = [ u"5", u"10", u"50", u"100", u"1000", u"10000" ]
                self.m_comboBoxRange = wx.ComboBox( sbSizerRange.GetStaticBox(), wx.ID_ANY, str(self.max_num), wx.DefaultPosition, wx.Size( 60,-1 ), m_comboBoxRangeChoices, 0 )
                sbSizerRange.Add( self.m_comboBoxRange, 0, wx.ALL, 5 )                
              
                self.m_checkBoxZeroOut = wx.CheckBox( sbSizerRange.GetStaticBox(), wx.ID_ANY, u"Nonzero", wx.DefaultPosition, wx.DefaultSize, 0 )
                sbSizerRange.Add( self.m_checkBoxZeroOut, 0, wx.ALL, 10 )
                self.m_checkBoxZeroOut.SetValue(self.exclude_zero)
                
                self.m_checkBoxCheckEveryStep = wx.CheckBox( sbSizerRange.GetStaticBox(), wx.ID_ANY, u"Watch Each Step", wx.DefaultPosition, wx.DefaultSize, 0 )
                sbSizerRange.Add( self.m_checkBoxCheckEveryStep, 0, wx.ALL, 10 )
                self.m_checkBoxCheckEveryStep.SetValue(self.check_every_step)
                self.m_checkBoxCheckEveryStep.SetToolTipString('Validate Each Step')                
            
                gSizerMain.Add( sbSizerRange, 1, wx.EXPAND, 5 )
                
                m_radioBoxLeftChoices = [ u"No", u"Yes" ]
                self.m_radioBoxLeft = wx.RadioBox( self.m_panelSettings, wx.ID_ANY, u"Allow Remainder in Division?", wx.DefaultPosition, wx.DefaultSize, m_radioBoxLeftChoices, 1, wx.RA_SPECIFY_ROWS )
                self.m_radioBoxLeft.SetSelection( 0 )
                self.m_radioBoxLeft.Enable( False )
                gSizerMain.Add( self.m_radioBoxLeft, 0, wx.ALL|wx.EXPAND, 0 )
                
                m_radioBoxLeftRowCol = [ u"Horizontal", u"Vertical" ]
                self.m_radioBoxRowCol = wx.RadioBox( self.m_panelSettings, wx.ID_ANY, u"Expression Format", wx.DefaultPosition, wx.DefaultSize, m_radioBoxLeftRowCol, 1, wx.RA_SPECIFY_ROWS )
                self.m_radioBoxRowCol.SetSelection( int(not self.row_exp) )                
                gSizerMain.Add( self.m_radioBoxRowCol, 0, wx.ALL|wx.EXPAND, 0 )
                
                m_radioBoxMinusChoices = [ u"No", u"Yes" ]
                self.m_radioBoxMinus = wx.RadioBox( self.m_panelSettings, wx.ID_ANY, u"Accept Negtive Answer?", wx.DefaultPosition, wx.DefaultSize, m_radioBoxMinusChoices, 1, wx.RA_SPECIFY_ROWS )
                self.m_radioBoxMinus.SetSelection( self.allow_minus)
                gSizerMain.Add( self.m_radioBoxMinus, 0, wx.ALL|wx.EXPAND, 0 )
                
                sbSizerOper = wx.StaticBoxSizer( wx.StaticBox( self.m_panelSettings, wx.ID_ANY, u"Operators" ), wx.HORIZONTAL )
                
                self.m_checkBoxAdd = wx.CheckBox( sbSizerOper.GetStaticBox(), wx.ID_ANY, u"+", wx.DefaultPosition, wx.DefaultSize, 0 )
                self.m_checkBoxAdd.SetValue('+' in self.opers) 
                sbSizerOper.Add( self.m_checkBoxAdd, 0, wx.ALL, 10 )
                
                self.m_checkBoxMinus = wx.CheckBox( sbSizerOper.GetStaticBox(), wx.ID_ANY, u"-", wx.DefaultPosition, wx.DefaultSize, 0 )
                sbSizerOper.Add( self.m_checkBoxMinus, 0, wx.ALL, 10 )
                self.m_checkBoxMinus.SetValue('-' in self.opers) 
                
                self.m_checkBoxMulti = wx.CheckBox( sbSizerOper.GetStaticBox(), wx.ID_ANY, u"*", wx.DefaultPosition, wx.DefaultSize, 0 )
                sbSizerOper.Add( self.m_checkBoxMulti, 0, wx.ALL, 10 )
                self.m_checkBoxMulti.SetValue('*' in self.opers) 
                
                self.m_checkBoxDiv = wx.CheckBox( sbSizerOper.GetStaticBox(), wx.ID_ANY, u"/", wx.DefaultPosition, wx.DefaultSize, 0 )
                sbSizerOper.Add( self.m_checkBoxDiv, 0, wx.ALL, 10 )
                self.m_checkBoxDiv.SetValue('/' in self.opers) 
                
                self.m_checkBoxBra = wx.CheckBox( sbSizerOper.GetStaticBox(), wx.ID_ANY, u"( )", wx.DefaultPosition, wx.DefaultSize, 0 )
                sbSizerOper.Add( self.m_checkBoxBra, 0, wx.ALL, 10 )
                self.m_checkBoxBra.SetValue(self.check_bracket)
                
                self.opers_mod = [self.m_checkBoxAdd, self.m_checkBoxMinus, self.m_checkBoxMulti, self.m_checkBoxDiv ]
                
                gSizerMain.Add( sbSizerOper, 1, wx.EXPAND, 5 )
                
                sbSizerTotalQues = wx.StaticBoxSizer( wx.StaticBox( self.m_panelSettings, wx.ID_ANY, u"Number of Questions" ), wx.VERTICAL )
                
                self.m_spinCtrlTotalQues = wx.SpinCtrl( sbSizerTotalQues.GetStaticBox(), wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.SP_ARROW_KEYS, 1, 1000, self.total_items )
                sbSizerTotalQues.Add( self.m_spinCtrlTotalQues, 0, wx.ALL, 5 )                
                
                gSizerMain.Add( sbSizerTotalQues, 1, wx.EXPAND, 5 )
                
                sbSizerPlaceHolder = wx.StaticBoxSizer( wx.StaticBox( self.m_panelSettings, wx.ID_ANY, u"Fill-in-the-Blank Equations" ), wx.HORIZONTAL )
                
                self.m_checkBoxUse = wx.CheckBox( sbSizerPlaceHolder.GetStaticBox(), wx.ID_ANY, u"Use Variable", wx.DefaultPosition, wx.DefaultSize, 0 )
                sbSizerPlaceHolder.Add( self.m_checkBoxUse, 0, wx.LEFT|wx.TOP, 8 )
                self.m_checkBoxUse.SetValue(self.use_sign)
                
                m_choiceSpaceHolderChoices = [ u"Round Brackets ( )", u"Square Box □", u"Question Mark ?", u"Underline __" ]
                self.m_choiceSpaceHolder = wx.Choice( sbSizerPlaceHolder.GetStaticBox(), wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, m_choiceSpaceHolderChoices, 0 )
                self.m_choiceSpaceHolder.SetSelection( 3 )
                sbSizerPlaceHolder.Add( self.m_choiceSpaceHolder, 0, wx.RIGHT|wx.BOTTOM|wx.TOP, 5 )

                self.OnToggleRowCol(None) # To check if init settings are vertical format
                
                gSizerMain.Add( sbSizerPlaceHolder, 1, wx.EXPAND, 5 )
                
                bSizerMain.Add( gSizerMain, 0, wx.EXPAND, 5 )
                
                sbSizerPrint = wx.StaticBoxSizer( wx.StaticBox( self.m_panelSettings, wx.ID_ANY, u"Custom Printing" ), wx.VERTICAL )
                
                bSizerTxtStart = wx.BoxSizer( wx.HORIZONTAL )
                
                self.m_staticTextStart = wx.StaticText( sbSizerPrint.GetStaticBox(), wx.ID_ANY, u"Header Text", wx.DefaultPosition, wx.DefaultSize, 0 )
                self.m_staticTextStart.Wrap( -1 )
                bSizerTxtStart.Add( self.m_staticTextStart, 0, wx.ALL, 5 )
                
                self.m_textCtrlStart = wx.TextCtrl( sbSizerPrint.GetStaticBox(), wx.ID_ANY, self.header, wx.DefaultPosition, wx.Size(-1, 60), wx.TE_MULTILINE )
                bSizerTxtStart.Add( self.m_textCtrlStart, 1, wx.ALL, 5 )
                
                
                sbSizerPrint.Add( bSizerTxtStart, 1, wx.EXPAND, 0 )
                
                bSizerQuesRow = wx.BoxSizer( wx.HORIZONTAL )
                
                self.m_staticTextPrintRow = wx.StaticText( sbSizerPrint.GetStaticBox(), wx.ID_ANY, u"Questions Per Row", wx.DefaultPosition, wx.DefaultSize, 0 )
                self.m_staticTextPrintRow.Wrap( -1 )
                bSizerQuesRow.Add( self.m_staticTextPrintRow, 0, wx.ALL, 5 )
                
                self.m_spinCtrlPrint = wx.SpinCtrl( sbSizerPrint.GetStaticBox(), wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.SP_ARROW_KEYS, 1, 10, self.items_per_row )
                bSizerQuesRow.Add( self.m_spinCtrlPrint, 1, wx.ALL, 5 )
                
                bSizerQuesRow.AddSpacer((20, -1))
                
                self.m_checkBoxHideQuesIndex = wx.CheckBox( sbSizerPrint.GetStaticBox(), wx.ID_ANY, u"Hide Question No.", wx.DefaultPosition, wx.DefaultSize, 0 )
                bSizerQuesRow.Add( self.m_checkBoxHideQuesIndex, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )
                self.m_checkBoxHideQuesIndex.SetValue(self.hide_ques_index)
                bSizerQuesRow.AddSpacer((20, -1))                
                                
                self.m_staticTextSpacing = wx.StaticText( sbSizerPrint.GetStaticBox(), wx.ID_ANY, u"Line Spacing", wx.DefaultPosition, wx.DefaultSize, 0 )
                bSizerQuesRow.Add( self.m_staticTextSpacing, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 0 )
                
                m_choiceSpacingChoices = [ u"1", u"2", u"3" ]
                self.m_choiceSpacing = wx.ComboBox( sbSizerPrint.GetStaticBox(), wx.ID_ANY, str(self.line_spacing), wx.DefaultPosition, wx.Size( 80,-1 ), m_choiceSpacingChoices, 0 )
                self.m_choiceSpacing.SetValue(str(self.line_spacing).strip('.0'))
                bSizerQuesRow.Add( self.m_choiceSpacing, 0, wx.ALL, 5 )
                
                bSizerQuesRow.AddSpacer((20, -1))
                
                self.m_checkBoxAnswerUnder = wx.CheckBox( sbSizerPrint.GetStaticBox(), wx.ID_ANY, u"Move Answer to the End", wx.DefaultPosition, wx.DefaultSize, 0 )
                bSizerQuesRow.Add( self.m_checkBoxAnswerUnder, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )
                self.m_checkBoxAnswerUnder.SetValue(self.save_answer_under)             
                sbSizerPrint.Add( bSizerQuesRow, 0, wx.ALL, 0 )
                
                bSizerEnd = wx.BoxSizer( wx.HORIZONTAL )
                
                self.m_staticTextEnd = wx.StaticText( sbSizerPrint.GetStaticBox(), wx.ID_ANY, u"Footer Text", wx.DefaultPosition, wx.DefaultSize, 0 )
                self.m_staticTextEnd.Wrap( -1 )
                bSizerEnd.Add( self.m_staticTextEnd, 0, wx.ALL, 5 )
                
                self.m_textCtrlEnd = wx.TextCtrl( sbSizerPrint.GetStaticBox(), wx.ID_ANY, self.footer, wx.DefaultPosition, wx.Size(-1, 60), wx.TE_MULTILINE )
                bSizerEnd.Add( self.m_textCtrlEnd, 1, wx.ALL, 5 )
                
                
                sbSizerPrint.Add( bSizerEnd, 1, wx.EXPAND, 0 )  
                bSizerMain.Add( sbSizerPrint, 0, wx.EXPAND, 0 )
                
                sbSizerSavePath = wx.StaticBoxSizer( wx.StaticBox( self.m_panelSettings, wx.ID_ANY, u"Save Path" ), wx.VERTICAL )
                
                bSizerTxtQuesPath = wx.BoxSizer( wx.HORIZONTAL )
                
                self.m_staticTextQuesPath = wx.StaticText( sbSizerSavePath.GetStaticBox(), wx.ID_ANY, u"Questions", wx.DefaultPosition, wx.DefaultSize, 0 )
                self.m_staticTextQuesPath.Wrap( -1 )
                bSizerTxtQuesPath.Add( self.m_staticTextQuesPath, 0, wx.ALL, 10 )
                
                self.m_filePickerQues = wx.FilePickerCtrl( sbSizerSavePath.GetStaticBox(), wx.ID_ANY, self.ques_path, u"Please choose a text file", u"*.txt", wx.DefaultPosition, wx.DefaultSize, wx.FLP_DEFAULT_STYLE|wx.FLP_SMALL )
                bSizerTxtQuesPath.Add( self.m_filePickerQues, 1, wx.ALL, 5 )            
                
                sbSizerSavePath.Add( bSizerTxtQuesPath, 0, wx.EXPAND, 5 )
                
                bSizerAnswerPath = wx.BoxSizer( wx.HORIZONTAL )
                
                self.m_staticTextAnswerPath = wx.StaticText( sbSizerSavePath.GetStaticBox(), wx.ID_ANY, u"Answers", wx.DefaultPosition, wx.DefaultSize, 0 )
                self.m_staticTextAnswerPath.Wrap( -1 )
                bSizerAnswerPath.Add( self.m_staticTextAnswerPath, 0, wx.ALL, 10 )
                
                self.m_filePickerAnswer = wx.FilePickerCtrl( sbSizerSavePath.GetStaticBox(), wx.ID_ANY, self.answ_path, u"Please choose a text file", u"*.txt", wx.DefaultPosition, wx.DefaultSize, wx.FLP_DEFAULT_STYLE|wx.FLP_SMALL )
                bSizerAnswerPath.Add( self.m_filePickerAnswer, 1, wx.ALL, 5 )
                
                
                sbSizerSavePath.Add( bSizerAnswerPath, 0, wx.EXPAND, 5 )        
                
                bSizerMain.Add( sbSizerSavePath, 0, wx.EXPAND, 5 )              
                
                bSizerMain.AddSpacer( ( 0, 0), 0, wx.EXPAND, 5 )                
                
                self.m_panelSettings.SetSizer( bSizerMain )
                self.m_panelSettings.Layout()
                self.m_notebookGlobal.AddPage( self.m_panelSettings, u"Settings", True )
                
                # add about tab
                self.m_panelAbout = wx.Panel( self.m_notebookGlobal, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
                self.m_panelAbout.SetBackgroundColour(PANEL_BKCOLOR)
                bSizerAbout = wx.BoxSizer( wx.VERTICAL )
                
                logo = lovemath.LoveMath.GetBitmap()
                
                self.m_bitmapLogo = wx.StaticBitmap( self.m_panelAbout, wx.ID_ANY, logo, wx.DefaultPosition, wx.DefaultSize, 0 )
                bSizerAbout.Add( self.m_bitmapLogo, 0, wx.ALIGN_CENTER|wx.ALL, 5 )
                self.m_bitmapLogo.SetToolTipString(u'Visit My Cloud Storage')
                
                self.m_staticTextComments = wx.StaticText( self.m_panelAbout, wx.ID_ANY, u"%s %s %s" % (TITLE, VER, BUILD), wx.DefaultPosition, wx.DefaultSize, 0 )
                self.m_staticTextComments.Enable( False )
                
                self.m_staticTextContact = wx.StaticText( self.m_panelAbout, wx.ID_ANY, u"Author: Quinn Song", wx.DefaultPosition, wx.DefaultSize, 0 )
                self.m_staticTextContact.Enable( False )
                
                bSizerAbout.Add( self.m_staticTextComments, 0, wx.ALIGN_CENTER|wx.ALL, 10 )
                bSizerAbout.Add( self.m_staticTextContact, 0, wx.ALIGN_CENTER|wx.ALL, 10 )
                
                bSizerAbout.AddSpacer( ( 0, 0), 1, wx.EXPAND, 5 )               
                
                self.m_panelAbout.SetSizer( bSizerAbout )
                self.m_panelAbout.Layout()
                #bSizerAbout.Fit( self.m_panelAbout )
                self.m_notebookGlobal.AddPage( self.m_panelAbout, u"About", False )
                
                self.Layout()
                
                self.Centre( wx.BOTH )
                
                # Connect Events
                self.m_buttonBold.Bind( wx.EVT_TOGGLEBUTTON, self.UpdateWindow )
                self.m_comboBoxFont.Bind( wx.EVT_COMBOBOX, self.UpdateWindow )
                self.m_comboBoxFontSize.Bind( wx.EVT_COMBOBOX, self.UpdateWindow )
                self.m_btnPageSetup.Bind( wx.EVT_BUTTON, self.OnSetup )
                self.m_btnPreview.Bind( wx.EVT_BUTTON, self.file_printPreview )
                self.m_btnPrint.Bind( wx.EVT_BUTTON, self.file_print )
                self.m_btnGen.Bind( wx.EVT_BUTTON, self.OnGenerate )
                self.m_btnSave.Bind( wx.EVT_BUTTON, self.OnSave )
                self.m_btnExit.Bind( wx.EVT_BUTTON, self.OnExit )
                self.m_btnAnswer.Bind( wx.EVT_BUTTON, self.OnAnswer )
                self.m_notebookGlobal.Bind( wx.EVT_NOTEBOOK_PAGE_CHANGED , self.OnTabChanged)
                self.m_btnBg.Bind (wx.EVT_BUTTON, self.OnBgChange)
                self.m_btnFg.Bind (wx.EVT_BUTTON, self.OnFgChange)
                self.m_spinCtrlSteps.Bind( wx.EVT_SPINCTRL, self.OnStepChanged )
                self.m_bitmapLogo.Bind( wx.EVT_LEFT_DCLICK, self.OpenLink )
                self.m_comboBoxRange.Bind(wx.EVT_TEXT, self.OnRangeChanged)
                self.m_checkBoxHideQuesIndex.Bind(wx.EVT_CHECKBOX, self.OnHideQuesIndex )
                self.m_checkBoxAnswerUnder.Bind(wx.EVT_CHECKBOX, self.OnAnswerUnder )
                self.m_radioBoxRowCol.Bind(wx.EVT_RADIOBOX, self.OnToggleRowCol )
                # opers events
                self.m_checkBoxAdd.Bind(wx.EVT_CHECKBOX, self.OnToggleRowCol )
                self.m_checkBoxMinus.Bind(wx.EVT_CHECKBOX, self.OnToggleRowCol )
                self.m_checkBoxMulti.Bind(wx.EVT_CHECKBOX, self.OnToggleRowCol )
                self.m_checkBoxDiv.Bind(wx.EVT_CHECKBOX, self.OnToggleRowCol )
                self.m_checkBoxBra.Bind(wx.EVT_CHECKBOX, self.OnToggleRowCol )
                self.Bind(wx.EVT_CLOSE, self.OnExit)
                self.Bind(EVT_COUNT, self.OnCount)

                ##Printer Initialization (create PrintPreview & Print objects)
                self.html_printer=Printer()   #Works with PrintPreview
                #self.html_printer.SetFonts(normal_face = self.font_name, fixed_face = self.font_name)
                #Work with Print
                self.html_print=HtmlEasyPrinting(name="Printing", parentWindow=self.m_richTextWindow)
                
                self.ShowModal()
        
        def __del__( self ):
                pass
        
        def randomList(self, a):
                """ shuffle the list """
                b = []
                for i in range(len(a)):
                        element = random.choice(a)
                        a.remove(element)
                        b.append(element)
                return b        
        
        # Virtual event handlers, overide them in your derived class
        #def init_lst ( self ):
        #       return [str(x) for x in range(1, self.max_num)] + self.opers
        def UpdateWindow( self, event ):
                """ GUI refresh when font changes """
                # update toggle button font
                btn_font = self.m_buttonBold.GetFont()
                if self.m_buttonBold.GetValue():
                    btn_font.SetWeight(wx.FONTWEIGHT_NORMAL)
                    self.m_buttonBold.SetToolTipString('')
                else:
                    btn_font.SetWeight(wx.FONTWEIGHT_BOLD)
                    self.m_buttonBold.SetToolTipString(u'Bold')
                self.m_buttonBold.SetFont (btn_font)
                self.is_dash = False
                self.font_name = self.m_comboBoxFont.GetValue()
                self.font_size = int(self.m_comboBoxFontSize.GetValue())
                self.default_font.SetFaceName(self.font_name)
                self.default_font.SetPointSize(self.font_size)
                self.m_richTextWindow.SetFont(self.default_font)
                self.m_richTextWindow.BeginFont(self.default_font)
                self.font_bold = self.m_buttonBold.GetValue()
                if self.questions and self.answers:
                    if self.font_bold:
                        self.m_richTextWindow.BeginBold()
                    self.OnCount(None)
                    if self.font_bold:
                        self.m_richTextWindow.EndBold()
                if event: event.Skip()

        def get_fixed_fonts ( self ):
                """ Validate if list are all fixed-width fonts """
                fixed_fonts = []
                for name in self.m_comboBoxFontChoices:
                    f = self.m_richTextWindow.GetFont()
                    f.SetFaceName(name)
                    if f.IsOk() and f.IsFixedWidth():
                        fixed_fonts.append(name)
                    else: continue
                return fixed_fonts        
              
        def OpenLink( self, event ):
                """ Open the link for cloud storage """
                os.startfile('http://pan.baidu.com/s/1CNWlg')
                event.Skip()
                
        def OnHideQuesIndex (self, event):
                """ If hiding question no. """
                if self.m_checkBoxHideQuesIndex.GetValue() and self.m_checkBoxAnswerUnder.GetValue():
                    self.m_checkBoxAnswerUnder.SetValue(False)
                event.Skip()
                
        def OnAnswerUnder (self, event):
                """ Move answer to the end """
                if self.m_checkBoxAnswerUnder.GetValue() and self.m_checkBoxHideQuesIndex.GetValue():
                    self.m_checkBoxHideQuesIndex.SetValue(False)
                event.Skip()
                
        def OnSetup (self, event):
                """ Page Setup """
                self.html_printer.PageSetup()
                event.Skip()                
               
        def OnToggleRowCol ( self, event ):
                """
                For vertical format: +, - no step limit;
                                    *, /   one step only.
                """
                self.row_exp = self.m_radioBoxRowCol.GetSelection() == 0
                self.m_checkBoxUse.Enable(self.row_exp)
                self.m_choiceSpaceHolder.Enable(self.row_exp)
                if not self.row_exp:
                    self.get_opers()
                    if '+' in self.opers:
                        [x.SetValue(y) for x, y in zip(self.opers_mod[1:], [False, False, False])]                      
                    elif '-' in self.opers:
                        [x.SetValue(y) for x, y in zip(self.opers_mod[2:], [ False, False])]
                    elif '*' in self.opers:
                        [x.SetValue(y) for x, y in zip(self.opers_mod[3:], [ False])]
                        self.m_spinCtrlSteps.SetValue(1)
                    elif '/' in self.opers:
                        self.m_spinCtrlSteps.SetValue(1)
                    else: pass
                    self.m_checkBoxBra.SetValue(False)    
                    
                if event: event.Skip()
                
        def OnRangeChanged ( self, event ):
                """
                Make sure the input are digits
                """
                if not self.m_comboBoxRange.GetValue().isdigit():
                    self.m_comboBoxRange.SetValue(str(self.max_num))
                event.Skip()
                
        def writeFile(self):
                """
                Save user setting to a file
                """
                self.config = ConfigObj(encoding='cp936') #work with unicode
                self.config.filename = self.configfile
                try:
                        if not self.config.has_key('SETTINGS'):
                                self.config['SETTINGS'] = {}
                        self.config['SETTINGS']['STEP_LIMIT'] = str(self.max_steps)
                        self.config['SETTINGS']['NUM_RANGE'] = str(self.max_num)       
                        self.config['SETTINGS']['HEADER'] = self.header
                        self.config['SETTINGS']['FOOTER'] = self.footer
                        self.config['SETTINGS']['QTY_PER_ROW'] = str(self.items_per_row) 
                        
                        self.config['SETTINGS']['QUES_QTY'] = str(self.total_items )
                        self.config['SETTINGS']['ALLOW_NEGTIVE'] = self.allow_minus
                        self.config['SETTINGS']['ROW_EXP'] = self.row_exp
                        self.config['SETTINGS']['OPS_CHECKED'] = self.opers
                        self.config['SETTINGS']['BRA_CHECKED'] = self.check_bracket
                        self.config['SETTINGS']['USE_SIGN'] = self.use_sign
                        self.config['SETTINGS']['SIGN_SELECTED'] = self.sign_selected
                        self.config['SETTINGS']['QUES_PATH'] = self.ques_path
                        self.config['SETTINGS']['ANSW_PATH'] = self.answ_path
                        self.config['SETTINGS']['EXCLUDE_ZERO'] = self.exclude_zero
                        self.config['SETTINGS']['CHECK_EVERY_STEP'] = self.check_every_step
                        self.config['SETTINGS']['ANSW_SAVE_UNDER'] = self.save_answer_under
                        self.config['SETTINGS']['HIDE_QUES_INDEX'] = self.hide_ques_index
                        self.config['SETTINGS']['LINE_SPACING'] = str(self.line_spacing) 
                        
                        if not self.config.has_key('MAIN'):
                                self.config['MAIN'] = {}
                                self.config.comments['MAIN'].insert(0,'')
                        self.config['MAIN']['SHOW_ANSWER'] = self.show_answer
                        self.config['MAIN']['BG_COLOR'] = self.bg_color
                        self.config['MAIN']['FG_COLOR'] = self.fg_color
                        self.config['MAIN']['SIZE'] = self.size
                        self.config['MAIN']['FONTS'] = self.m_comboBoxFontChoices

                        self.config.write()
                except Exception, e: pass
                
        def readFile(self):
                """
                read user setting from a file
                """
                # does the config file exist?
                self.config = ConfigObj(encoding='cp936') # work with unicode
                if os.path.isfile(self.configfile):                        
                        try:
                                self.config = ConfigObj(self.configfile)             
                                self.max_steps =  int(self.config['SETTINGS']['STEP_LIMIT'])
                                self.max_num = int(self.config['SETTINGS']['NUM_RANGE'])
                                self.ques_path = unicode(self.config['SETTINGS']['QUES_PATH'], 'cp936')
                                self.answ_path = unicode(self.config['SETTINGS']['ANSW_PATH'], 'cp936')
                                self.header = unicode(self.config['SETTINGS']['HEADER'], 'cp936')
                                self.footer = unicode(self.config['SETTINGS']['FOOTER'], 'cp936')
                                self.items_per_row = int(self.config['SETTINGS']['QTY_PER_ROW'])
                                self.opers = self.config['SETTINGS']['OPS_CHECKED']                             
                                self.total_items = int(self.config['SETTINGS']['QUES_QTY'])
                                self.use_sign = (self.config['SETTINGS']['USE_SIGN'] == 'True' )
                                self.sign_selected = int(self.config['SETTINGS']['SIGN_SELECTED'])
                                
                                self.allow_minus = ( self.config['SETTINGS']['ALLOW_NEGTIVE'] == 'True' )
                                self.check_bracket = (self.config['SETTINGS']['BRA_CHECKED'] == 'True')
                                self.exclude_zero = (self.config['SETTINGS']['EXCLUDE_ZERO'] == 'True')
                                self.check_every_step = (self.config['SETTINGS']['CHECK_EVERY_STEP'] == 'True')
                                self.save_answer_under = (self.config['SETTINGS']['ANSW_SAVE_UNDER']  == 'True' ) 
                                self.hide_ques_index = (self.config['SETTINGS']['HIDE_QUES_INDEX'] == 'True')
                                self.row_exp = (self.config['SETTINGS']['ROW_EXP'] == 'True')
                                self.allow_minus = (self.config['SETTINGS']['ALLOW_NEGTIVE'] == 'True' )
                                self.line_spacing = int(self.config['SETTINGS']['LINE_SPACING'] )
                                
                                self.bg_color = self.config['MAIN']['BG_COLOR']
                                self.fg_color = self.config['MAIN']['FG_COLOR']
                                self.show_answer = ( self.config['MAIN']['SHOW_ANSWER'] == 'True' )
                                
                                self.size = tuple([int(s) for s in self.config['MAIN']['SIZE']])
                                B = self.config['MAIN']['FONTS']
                                self.m_comboBoxFontChoices = [unicode(s, 'cp936') for s in self.config['MAIN']['FONTS']]
                                
                        except Exception, e:
                                pass   
                
        def OnStepChanged( self, event ):
                """
                The event handler on steps change
                Rule: 1) Steps <= Max; 2) For vertical format,
                only one step is allowed for multiplication and division
                """
                if self.m_spinCtrlSteps.GetValue() > int(self.m_comboBoxRange.GetValue()):
                        self.m_spinCtrlSteps.SetValue(int(self.m_comboBoxRange.GetValue()))
                        wx.MessageBox( u'Steps Count cannot be greater than Operation Range', u'Reminder', wx.OK | wx.ICON_EXCLAMATION)
                if self.m_radioBoxRowCol.GetSelection() == 1 and (self.m_checkBoxMulti.GetValue() or self.m_checkBoxDiv.GetValue()):
                        self.m_spinCtrlSteps.SetValue(1)
                        wx.MessageBox( u'Only one step is allowed for (* /) in vertical format', u'Reminder', wx.OK | wx.ICON_EXCLAMATION)
                event.Skip()
                
        def ChooseColour ( self ):
                """ The event handler on picking a color """
                color = None
                dialog = wx.ColourDialog(self)
                dialog.GetColourData().SetChooseFull(True)
                if dialog.ShowModal() == wx.ID_OK:
                    data = dialog.GetColourData()
                    color = data.GetColour()
                dialog.Destroy()
                return color
                
        def OnBgChange ( self, event ):
                """ The event handler for background color changes """
                color = self.ChooseColour ()
                if color:
                        self.bg_color = color.GetAsString (wx.C2S_HTML_SYNTAX )
                        self.m_btnBg.SetBackgroundColour(color)
                        self.m_richTextWindow.SetBackgroundColour(color)
                        self.m_richTextWindow.Refresh()
                event.Skip()
                
        def OnFgChange ( self, event ):
                """ The event handler for font color changes """
                color = self.ChooseColour ()
                if color:
                        self.fg_color = color.GetAsString (wx.C2S_HTML_SYNTAX )
                        self.m_btnFg.SetBackgroundColour(color)
                        self.m_richTextWindow.BeginTextColour(color)
                        if self.questions and self.answers:
                            self.OnCount(None)
                event.Skip()
        
        def OnAnswer( self, event ):
                """ The event handler for show answer button """
                self.show_answer = not self.show_answer
                self.anw_ico = self.q_ico if self.show_answer else self.qa_ico
                self.m_btnAnswer.SetBitmap(self.anw_ico)
                self.m_btnAnswer.SetToolTipString(u'Hide Answer' if self.show_answer else u'Show Answer')
                if self.questions and self.answers:
                        self.UpdateWindow(None)
                if event: event.Skip()
        
        def OnGenerate( self, event ):
                """ The event handler """
                self.is_dash = False
                if self.use_threading:
                    worker = CountingThread(self, 1)
                    worker.start()
                else:
                    self.run_thread()
                    self.OnCount(None)                
                event.Skip()
                
        def run_thread ( self ):
                """
                Main function to generate good math expressions
                """
                # reset these lists  
                self.questions = []
                self.answers = []
                self.x_list = []
                self.qx_list = []
                
                dialog = wx.ProgressDialog( u"Processing...", u"Please wait", self.total_items, style=wx.PD_CAN_ABORT | wx.PD_ELAPSED_TIME | wx.PD_REMAINING_TIME | wx.PD_AUTO_HIDE)
                dialog.SetIcon(self.icon)
                count = 0
                self.cancel = False
                
                while (not self.cancel) and count < self.total_items:
                        op = self.randomList(self.max_steps * self.opers)

                        exp = ''.join( [ item for pair in zip([str(x) for x in random.sample( range(int(self.exclude_zero), self.max_num + 1), self.max_steps + 1)],  \
                            list(op) + [0]) for item in pair][:-1])
                        if re.findall(BAD_PATTERN_1, exp):
                                continue
                        if not self.have_remainder and  any(int(i)%int(j) != 0 for i,j in re.findall(BAD_PATTERN_2, exp) if int(j) != 0):
                                continue                        
                        try:
                                if self.check_bracket: exp = main(exp)
                                # remove brackets like '(1+2+3)'
                                exp = re.sub('^\((.*)\)$', '\g<1>', exp)
                                exp = re.sub('(.*)\((\d+)\)(.*)', '\g<1>\g<2>\g<3>', exp )
                                exp = re.sub('(.*)\(\((.*)\)\)(.*)', '\g<1>\g<2>\g<3>', exp )
                                
                                if self.check_every_step and ( not isExpValid(exp, self.max_num)): continue
                                
                                result = eval(exp)
                                if not self.allow_minus and result < 0:
                                        continue

                                self.questions.append('%i. %s' % (count + 1, exp) if not self.hide_ques_index else exp)
                                self.answers.append(str(result))
                                count = count + 1
                                self.cancel = not dialog.Update(count)[0]
                                
                        except: pass
                dialog.Destroy()
                
        def OnCount(self, evt):
                """
                Show result upon threading is finished
                """
                # clear richtext window first
                self.m_richTextWindow.Clear()
                if self.row_exp:
                        max_value_q = max(map(self.CalWidth, self.questions))
                        self.adjust_value = max_value_q/3 + 3
                        output = self.format_output()
                        self.m_richTextWindow.AppendText(output)
                else:
                        max_value_q = self.CalWidth('%s. + %s' % (self.total_items, self.max_num))
                        self.adjust_value = max_value_q/8 + 5           
        
                        output = self.format_output()
                        for b in xrange(0, len(output), 2):                    
                            self.m_richTextWindow.AppendText(output[b])
                            
                            if b + 1 < len(output):

                                frm_tos = [(m.start(0), m.end(0)) for m in re.finditer('[^\s\d]\s+\d+', output[b+1])]
                                last = self.m_richTextWindow.GetLastPosition()
                                self.m_richTextWindow.AppendText(output[b+1])
                                # set selection underlined
                                for frm,to in frm_tos:    
                                    self.m_richTextWindow.SetSelection(last+frm, last+to)
                                    self.m_richTextWindow.ApplyUnderlineToSelection()                        
                pos = self.m_richTextWindow.GetCaretPosition()
                self.m_richTextWindow.ScrollIntoView(pos, wx.WXK_END)
                if evt: evt.Skip()
                        
        def CalWidth(self, line):
                """
                get the width of a string in pixels
                """
                f = self.m_richTextWindow.GetFont()
                a = self.font_name
                f.SetFaceName('Courier New')
                dc = wx.WindowDC(self)
                dc.SetFont(f)
                line_width, height = dc.GetTextExtent(line)
                return line_width
            
        def convert_q (self, q_string):
                # find all positions of numbers in a question, and pick a random to replace
                pos = [(m.start(0), m.end(0)) for m in re.finditer('(?<!\d)\d+(?!\d*\.)', q_string)]
                a = random.choice(pos)
                x = q_string[a[0]:a[1]]
                self.x_list.append(x)                
                self.qx_list.append( re.sub('(?<!\d)' + x + '(?!\d|\.)', SIGNS[self.sign_selected], q_string) )
        
        def row_calculate (self, buf):
                """ Horizontal format """
                tmp_a, tmp_q = None, None
                if self.row_exp and self.use_sign:
                    # save to buffer
                    tmp_a = self.show_answer
                    self.show_answer = True
                    
                    if not self.x_list:
                        for q in self.questions:
                            self.convert_q(q)                    
                    if not tmp_a:
                        tmp_q = self.questions
                        self.questions = self.qx_list

                q_grp = [self.questions[x:x+self.items_per_row] for x in xrange(0, self.total_items, self.items_per_row)]
                a_grp = [self.answers[x:x+self.items_per_row] for x in xrange(0, self.total_items, self.items_per_row)]
                max_value_q = max(map(self.CalWidth, self.questions))

                for q_list, a_list in zip(q_grp, a_grp):
                        body = ''.join([('%s = %s' % (q, a_list[i] if self.show_answer and (not self.save_answer_under) else '') ).ljust(self.adjust_value)  for i,q in enumerate(q_list)])
                        buf = buf + body + ('\r\n' ) * self.line_spacing
                if tmp_a != None: self.show_answer = tmp_a
                if tmp_q: self.questions = tmp_q
                return buf          
        
        def col_calculate  (self, buf ):
                """ Vertical format """
                q_grp = [self.questions[x:x+self.items_per_row] for x in xrange(0, self.total_items, self.items_per_row)]
                a_grp = [self.answers[x:x+self.items_per_row] for x in xrange(0, self.total_items, self.items_per_row)]
                max_value_q = self.CalWidth('%s. + %s' % (self.total_items, self.max_num))
                bufs = []
                # define lambda functions for index alignment
                left_indent = len(str(self.max_num/10)) + 5
                f =lambda x: (x.split('.')[0]+ '.').rjust(left_indent) + x.split('.')[1].rjust(self.adjust_value - left_indent)
                s = lambda y: 1 if self.font_name == 'Fixedsys' and (y == '*' or y == '/') else 0

                for q_list, a_list in zip(q_grp, a_grp):
                        q_num_grp = [re.split('[+*/-]', q) for q in q_list]
                        for step in range(self.max_steps):
                            row = ''.join([ f(q_num[step]) if (not self.hide_ques_index and step == 0) else (q_num[step]).rjust(self.adjust_value) for q_num in q_num_grp])
                            buf = buf + row + ('\r\n' ) * self.line_spacing
                        bufs.append(buf)
                        buf = ''
                        row = ''.join([(self.opers[0]+' '.ljust(len(str(self.max_num))-len(q_num[-1]))+q_num[-1]).rjust(self.adjust_value - (s(self.opers[0]))) for q_num in q_num_grp])
                        bufs.append(row + ('\r\n' ) * self.line_spacing )
                        if self.is_dash:
                            dash_underline = ''.join([('-'* (len(str(self.max_num)) + 1)).rjust(self.adjust_value) for i in range(len(q_list))]) + ('\r\n' ) * self.line_spacing
                        else: dash_underline = ''
                        row_answer = ''.join(['%s' % (i if self.show_answer and (not self.save_answer_under) else '').rjust(self.adjust_value)  for i in a_list])
                        buf = buf + dash_underline + row_answer + '\r\n\r\n\r\n' # (add 3 new lines)

                return bufs, dash_underline + row_answer + '\r\n\r\n'                
                        
        
        def format_output ( self ):
                """
                Format the output
                """
                start = self.header.replace('\n', '\r\n')
                buf = start + ('\r\n') * self.line_spacing
                end = self.footer.replace('\n', '\r\n')

                if self.row_exp: # horizontal format
                        buf = self.row_calculate(buf)
                else:   # vertical format
                    bufs, buf = self.col_calculate(buf)

                # if show answer under page
                if self.show_answer and self.save_answer_under:
                        end = end + '\r\n\r\n' + '='*18 + u'ANSWERS:' + '='*18 + '=\r\n'
                        for x in xrange(0, self.total_items, self.items_per_row):
                            anw = ''.join([('%i. %s' % (x+i+1, a) ).ljust(self.adjust_value) for i,a in enumerate(self.answers[x:x+self.items_per_row]) ])
                            end = end + anw + '\r\n'
                
                if self.row_exp:  # horizontal format
                        return buf + '\r\n'+end
                else:   # Vertical format
                        bufs.append(buf + '\r\n'+end)
                        return bufs
        
        def get_file_out ( self):
                """ Prepare for output to file """
                if self.row_exp:
                        return self.format_output()    
                else:   return ''.join(self.format_output())
        
        def OnSave( self, event ):
                """ Handler for saving output to file """
                self.is_dash = True
                tmp = self.show_answer
                self.show_answer = False
                output_ques = self.get_file_out() 
                file_ques = self.ques_path
                with  codecs.open(file_ques, 'w', 'utf-8') as f: f.write(output_ques)
                
                self.show_answer = True
                output_answer = self.get_file_out()        
                file_answer = self.answ_path
                with  codecs.open(file_answer, 'w', 'utf-8') as f: f.write(output_answer)
                self.show_answer = tmp
                
                # open both files
                os.startfile(file_ques)
                os.startfile(file_answer)
                event.Skip()
        
        def OnExit( self, event ):
                """ Save user setting to file upon exit button is pressed """
                self.size = self.GetSizeTuple()
                self.writeFile()
                self.cancel = True
                self.Destroy()
                event.Skip()    
        
        def OnTabChanged ( self, event ):
                """ Save settings if the current tab is not Settings tab"""
                if self.m_notebookGlobal.GetPageText(event.GetSelection()) != u"Settings":
                        self.GetSettings()
                event.Skip()
                
        def get_opers ( self ):
                # get current checked ops (self.opers)
                self.opers = [ OPS[index] for index, op in enumerate(self.opers_mod) if op.IsChecked()]
        
        def GetSettings( self ):
                # get settings when leaving Settings tab
                self.max_steps = self.m_spinCtrlSteps.GetValue()
                self.have_remainder = self.m_radioBoxLeft.GetSelection() == 1
                self.max_num = int(self.m_comboBoxRange.GetValue())
                self.allow_minus = self.m_radioBoxMinus.GetSelection() == 1
                self.row_exp = self.m_radioBoxRowCol.GetSelection() == 0
                self.items_per_row = int(self.m_spinCtrlPrint.GetValue())
                self.total_items = self.m_spinCtrlTotalQues.GetValue()
                self.check_bracket = self.m_checkBoxBra.GetValue()
                self.use_sign = self.m_checkBoxUse.GetValue()
                self.sign_selected = self.m_choiceSpaceHolder.GetSelection()
                self.exclude_zero = self.m_checkBoxZeroOut.GetValue()
                self.check_every_step = self.m_checkBoxCheckEveryStep.GetValue()
                self.header = self.m_textCtrlStart.GetValue()
                self.footer = self.m_textCtrlEnd.GetValue()
                self.ques_path = self.m_filePickerQues.GetTextCtrlValue()
                self.answ_path = self.m_filePickerAnswer.GetTextCtrlValue()
                self.save_answer_under = self.m_checkBoxAnswerUnder.GetValue()
                self.hide_ques_index = self.m_checkBoxHideQuesIndex.GetValue()
                self.line_spacing = int(self.m_choiceSpacing.GetValue())
                self.get_opers()
                # in case no oper is checked, then default "+" is checked
                if not self.opers:
                    self.m_checkBoxAdd.SetValue(True)
                    self.opers = ['+']
                # write config
                self.writeFile()
                # if not use threading
                if self.opers == ['/']:
                        self.m_spinCtrlSteps.SetValue(1)
                        self.use_threading = False
                elif '/' in self.opers and len(self.opers) >= 2:
                    self.use_threading = True
                else:
                    self.use_threading = False

        def GetHtmlText(self,text):
            #"Simple conversion of text.  Use a more powerful version"
            if self.font_bold:
                text = '<strong>%s</strong>' % (text) # set font to bold
            html_font = self.get_font_size()
            text = '<font color="%s" face="%s" size="%s">'  % (self.fg_color, self.font_name, html_font) + text + '</font>'
            text = '<pre>' + text + '</pre>' 		# Preserve spacing
            text = re.sub (u'([×÷+-]\s+\d+)', '<U>\g<1></U>', text) # underline the missing part
            text = text.replace('\n\n','<P>')     	# Paragraphs
            html_text = text.replace('\n', '<BR>')     # Line breaks            
            return html_text 
        
        # From the Menu "File/Page Setup" allows user to make changes in printer settings
        def file_pageSetup(self, event):
            self.html_printer.PageSetup()
        
        # From the Menu "File/Print Preview" shows how text prints before printing
        def file_printPreview(self, event):
            global frame
            text = self.m_richTextWindow.GetValue()
            doc_name= '' #self.filename
            self.html_printer.PreviewText(self.GetHtmlText(text), doc_name)
        
        # From the Menu "File/Print"  actually prints the text to the printer     
        def file_print(self, event):
            global frame
            text = self.m_richTextWindow.GetValue()
            doc_name='' #self.filename
            self.html_printer.Print(self.GetHtmlText(text), doc_name)
        
        def get_font_size (self):
            # conversion from pixel size (7 - 72) to html font size (1 - 7)
            # refer link: http://jerekdain.com/fontconversion.html
            if self.font_size in range(7, 10): return 1
            elif self.font_size in range(10, 12): return 2
            elif self.font_size in range(12, 14): return 3
            elif self.font_size in range(14, 18): return 4
            elif self.font_size in range(18, 24): return 5
            elif self.font_size in range(24, 32): return 6
            else: return 7
        
        def GetErrorText():
           "Put your error text logic here.  See Python Cookbook for a useful example of error text."
           return "Some error occurred."
                
if __name__ == '__main__':
    app = wx.App(False)
    frame = ExpressionGenerator(None)
    app.MainLoop() 

        

