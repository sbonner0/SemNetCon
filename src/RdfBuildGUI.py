#Copyright 2016 John Brennan and Stephen Bonner
#This file is part of SEMNETCON.

#The Semantic Enabled Python Tool For The Construction Of Complex 
#Networks From Disperse Data Sources (SEMNETCON) 
#is free software: you can redistribute it and/or modify
#it under the terms of the GNU General Public License as published by
#the Free Software Foundation, either version 3 of the License, or
#(at your option) any later version.

#SEMNETCON is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#GNU General Public License for more details.

#You should have received a copy of the GNU General Public License
#along with SEMNETCON.  If not, see <http://www.gnu.org/licenses/>.
#Contact j.d.brennan@durham.ac.uk or s.a.r.bonner@durham.ac.uk

import sys, string, tkFileDialog, uuid, os
import Network_Constructor as NC
from rdflib import URIRef, BNode, Literal, Namespace, Graph
from rdflib.namespace import RDF, FOAF, NamespaceManager
from Tkinter import *
from os.path import expanduser
if TkVersion < 8.0 :
    print "\n" * 3
    print "*"*75
    print "Running Tk version:", TkVersion 
    print "You must be using Tk version 8.0 or greater to use EasyGui."
    print "Terminating."
    print "*"*75
    print "\n" * 3
    sys.exit(0)


# Adapted from http://www.ferg.org/easygui/epydoc/easygui-pysrc.html
# EasyGui version 0.97
# Copyright (c) 2014, Stephen Raymond Ferg
# All rights reserved.

rootWindowPosition = "+300+200"
DEFAULT_FONT_FAMILY   = ("MS", "Sans", "Serif")
MONOSPACE_FONT_FAMILY = ("Courier")
DEFAULT_FONT_SIZE     = 10
BIG_FONT_SIZE         = 12
SMALL_FONT_SIZE       =  9
CODEBOX_FONT_SIZE     =  9
TEXTBOX_FONT_SIZE     = DEFAULT_FONT_SIZE


#-------------------------------------------------------------------

def choicebox(message="Shall I continue?", title="Confirmation", choices=["Yes","No"]):
    """Display a option box.
    Return 1 if the OK was selected, otherwise return 0.
    """
    if title == None:
        if message == "Shall I continue?": title = "Confirmation"
        else: title = ""


    reply = buttonbox(message, title, choices)
    if reply == choices[0]: return 1
    else: return 0


#-------------------------------------------------------------------
# msgbox
#-------------------------------------------------------------------

def msgbox(message="Shall I continue?", title=""):
    """Display a with a simple OK button
    """
    choices = ["OK"]
    reply = buttonbox(message, title, choices)
    return reply


#-------------------------------------------------------------------
# buttonbox
#-------------------------------------------------------------------
def buttonbox(message="Shall I continue?", title="", choices = ["Button1", "Button2", "Button3"]):
    """Display a message, a title, and a set of buttons.
    The buttons are defined by the members of the choices list.
    Return the text of the button that the user selected.
    """

    global root, __replyButtonText, __a_button_was_clicked, __widgetTexts, buttonsFrame

    if title == None: title = ""
    if message == None: message = "This is a buttonbox."

    # __a_button_was_clicked will remain 0 if window is closed using the close button.
    # It will be changed to 1 if the event loop is exited by a click of one of the buttons.
    __a_button_was_clicked = 0

    # Initialize __replyButtonText to the first choice.
    # This is what will be used if the window is closed by the close button.
    __replyButtonText = choices[0]

    root = Tk()
    root.title(title)
    root.iconname('Dialog')
    root.geometry(rootWindowPosition)
    root.minsize(400, 100)

    # ------------- define the frames --------------------------------------------
    messageFrame = Frame(root)
    messageFrame.pack(side=TOP, fill=BOTH)

    buttonsFrame = Frame(root)
    buttonsFrame.pack(side=BOTTOM, fill=BOTH)

    # -------------------- place the widgets in the frames -----------------------
    messageWidget = Message(messageFrame, text=message, width=400)
    messageWidget.configure(font=(DEFAULT_FONT_FAMILY,DEFAULT_FONT_SIZE))
    messageWidget.pack(side=TOP, expand=YES, fill=X, padx='3m', pady='3m')

    __put_buttons_in_buttonframe(choices)

    # -------------- the action begins -----------
    # put the focus on the first button
    __firstWidget.focus_force()
    root.mainloop()
    if __a_button_was_clicked: root.destroy()
    return __replyButtonText


#-------------------------------------------------------------------
# formbox
#-------------------------------------------------------------------
def formbox(message="Enter something.", title="", argDefaultText=None, currentFile=""):
    """Show a form in which a user can enter details of files to be processed.
    Returns the text that the user entered, or None if he cancels the operation.
    """

    global root, __formboxText, __formboxDefaultText, __a_button_was_clicked, cancelButton, entryWidget
    global locationEntry, typeEntry, typeOption, nodeValEntry, nodeAttrEntry, edgeFromEntry, edgeToEntry
    global edgeAttrEntry, delimEntry, StartLineEntry, outputEntry, outputOption, okButton
    
    if title == None: title = ""
    choices = ["OK", "Cancel"]
    
    if argDefaultText == None:
        __formboxDefaultText = ""
    else:
        __formboxDefaultText = argDefaultText

    __formboxText = __formboxDefaultText

    # __a_button_was_clicked will remain 0 if window is closed using the close button]
    # will be changed to 1 if event-loop is quit by a click of one of the buttons.
    __a_button_was_clicked = 0

    root = Tk()
    root.title(title)
    root.iconname('Dialog')
    root.geometry(rootWindowPosition)
    root.bind("Escape", __formboxCancel)

    # -------------------- put subframes in the root --------------------
    main_frame = Frame(root)
    main_frame.grid(row=0)
    
    buttonsFrame = Frame(main_frame)
    buttonsFrame.grid(row=11,column=1,columnspan=2)

    
    #-------------------- the message widget ----------------------------
    Label(main_frame, text=message).grid(row=0, columnspan=3, pady=10)
    

    #-------------------- the info widget1 ----------------------------
    fileTypeInfo = Message(main_frame, text="File", width=80).grid(row=2, column=1, sticky=W)
    #-------------------- the info widget2 ----------------------------
    fileInfo = Message(main_frame, text="File Type", width=80).grid(row=1, column=1, sticky=W)
    #-------------------- the info widget3 ----------------------------
    nodeValInfo = Message(main_frame, text="Node Value", width=80).grid(row=3, column=1, sticky=W)
    #-------------------- the info widget4 ----------------------------
    nodeAttrInfo = Message(main_frame, text="Node Attrs", width=80).grid(row=4, column=1, sticky=W)
    #-------------------- the info widget5 ----------------------------
    edgeFromInfo = Message(main_frame, text="Edge Value From", width=80).grid(row=5, column=1, sticky=W)
    #-------------------- the info widget6 ----------------------------
    edgeToInfo = Message(main_frame, text="Edge Value To", width=80).grid(row=6, column=1, sticky=W)
    #-------------------- the info widget7 ----------------------------
    edgeAttrInfo = Message(main_frame, text="Edge Attrs", width=80).grid(row=7, column=1, sticky=W)
    #-------------------- the info widget8 ----------------------------
    delimInfo = Message(main_frame, text="Delimiter", width=80).grid(row=8, column=1, sticky=W)
    #-------------------- the info widget9 ----------------------------
    startLineInfo = Message(main_frame, text="Starting Line", width=80).grid(row=9, column=1, sticky=W)
    #-------------------- the info widget10 ----------------------------
    OutputInfo = Message(main_frame, text="Output Format", width=80).grid(row=10, column=1, sticky=W)

    # --------- locationEntry (File) ---------------------------------------------
    locationEntry = Entry(main_frame, width=40)
    locationEntry.configure(font=(DEFAULT_FONT_FAMILY,BIG_FONT_SIZE))
    locationEntry.grid(row=2, column=2, sticky=E, padx=10, pady=5)
    locationEntry.bind("<Return>", __formboxGetText)
    locationEntry.bind("<Escape>", __formboxCancel)
    # put text into the entryWidget
    locationEntry.insert(0,currentFile)
    locationEntry.configure(state=DISABLED)
    # --------- typeEntry (File Type) ---------------------------------------------
    typeChoices = ['csv', 'excel', 'json', 'xml']    
    typeOption = StringVar(root)
    typeOption.set(typeChoices[0])
    typeEntry = OptionMenu(main_frame, typeOption, *typeChoices)
    typeEntry.configure(font=(DEFAULT_FONT_FAMILY,BIG_FONT_SIZE),anchor=E, direction='flush')
    typeEntry.grid(row=1, column=2, sticky=W+E, padx=10, pady=5)
    typeEntry.bind("<Return>", __formboxGetText)
    typeEntry.bind("<Escape>", __formboxCancel)
    typeOption.trace('w', typeUpdate)
    # put text into the entryWidget
    #typeEntry.insert(0,"")
    # --------- nodeValEntry (Node Value) ---------------------------------------------
    nodeValEntry = Entry(main_frame, width=40)
    nodeValEntry.configure(font=(DEFAULT_FONT_FAMILY,BIG_FONT_SIZE))
    nodeValEntry.grid(row=3, column=2, sticky=E, padx=10, pady=5)
    nodeValEntry.bind("<Return>", __formboxGetText)
    nodeValEntry.bind("<Escape>", __formboxCancel)
    # put text into the entryWidget
    nodeValEntry.insert(0,"None")    
    # --------- nodeAttrEntry (Node Attrs) ---------------------------------------------
    nodeAttrEntry = Entry(main_frame, width=40)
    nodeAttrEntry.configure(font=(DEFAULT_FONT_FAMILY,BIG_FONT_SIZE))
    nodeAttrEntry.grid(row=4, column=2, sticky=E, padx=10, pady=5)
    nodeAttrEntry.bind("<Return>", __formboxGetText)
    nodeAttrEntry.bind("<Escape>", __formboxCancel)
    # put text into the entryWidget
    nodeAttrEntry.insert(0,"None")    
    # --------- edgeFromEntry (Edge From) ---------------------------------------------
    edgeFromEntry = Entry(main_frame, width=40)
    edgeFromEntry.configure(font=(DEFAULT_FONT_FAMILY,BIG_FONT_SIZE))
    edgeFromEntry.grid(row=5, column=2, sticky=E, padx=10, pady=5)
    edgeFromEntry.bind("<Return>", __formboxGetText)
    edgeFromEntry.bind("<Escape>", __formboxCancel)
    # put text into the entryWidget
    edgeFromEntry.insert(0,"None")
    
    # --------- edgeToEntry (Edge To) ---------------------------------------------
    edgeToEntry = Entry(main_frame, width=40)
    edgeToEntry.configure(font=(DEFAULT_FONT_FAMILY,BIG_FONT_SIZE))
    edgeToEntry.grid(row=6, column=2, sticky=E, padx=10, pady=5)
    edgeToEntry.bind("<Return>", __formboxGetText)
    edgeToEntry.bind("<Escape>", __formboxCancel)
    # put text into the entryWidget
    edgeToEntry.insert(0,"None")
    # --------- edgeAttrEntry (Edge Attrs) ---------------------------------------------
    edgeAttrEntry = Entry(main_frame, width=40)
    edgeAttrEntry.configure(font=(DEFAULT_FONT_FAMILY,BIG_FONT_SIZE))
    edgeAttrEntry.grid(row=7, column=2, sticky=E, padx=10, pady=5)
    edgeAttrEntry.bind("<Return>", __formboxGetText)
    edgeAttrEntry.bind("<Escape>", __formboxCancel)
    # put text into the entryWidget
    edgeAttrEntry.insert(0,"None")    
    # --------- delimEntry (Delimter) ---------------------------------------------
    delimEntry = Entry(main_frame, width=40)
    delimEntry.configure(font=(DEFAULT_FONT_FAMILY,BIG_FONT_SIZE))
    delimEntry.grid(row=8, column=2, sticky=E, padx=10, pady=5)
    delimEntry.bind("<Return>", __formboxGetText)
    delimEntry.bind("<Escape>", __formboxCancel)
    # put text into the entryWidget
    delimEntry.insert(0,"None")    
    # --------- StartLineEntry (Starting Line) ---------------------------------------------
    StartLineEntry = Entry(main_frame, width=40)
    StartLineEntry.configure(font=(DEFAULT_FONT_FAMILY,BIG_FONT_SIZE))
    StartLineEntry.grid(row=9, column=2, sticky=E, padx=10, pady=5)
    StartLineEntry.bind("<Return>", __formboxGetText)
    StartLineEntry.bind("<Escape>", __formboxCancel)
    # put text into the entryWidget
    StartLineEntry.insert(0,"None")
     # --------- outputEntry (File Type) ---------------------------------------------
    outputChoices = ['gml', 'adj', 'mladj', 'graphml','pajek']    
    outputOption = StringVar(root)
    outputOption.set(outputChoices[0])
    outputEntry = OptionMenu(main_frame, outputOption, *outputChoices)
    
    outputEntry.configure(font=(DEFAULT_FONT_FAMILY,BIG_FONT_SIZE),anchor=E, direction='flush')
    outputEntry.grid(row=10, column=2, sticky=W+E, padx=10, pady=5)
    outputEntry.bind("<Return>", __formboxGetText)
    outputEntry.bind("<Escape>", __formboxCancel)       

    # ------------------ ok button -------------------------------
    okButton = Button(buttonsFrame, takefocus=1, text="OK")
    okButton.pack(expand=1, side=LEFT, padx='3m', pady='3m', ipadx='2m', ipady='1m')
    okButton.bind("<Return>", __formboxGetText)
    okButton.bind("<Button-1>", __formboxGetText)

    # ------------------ cancel button -------------------------------
    cancelButton = Button(buttonsFrame, takefocus=1, text="Cancel")
    cancelButton.pack(expand=1, side=RIGHT, padx='3m', pady='3m', ipadx='2m', ipady='1m')
    cancelButton.bind("<Return>", __formboxCancel)
    cancelButton.bind("<Button-1>", __formboxCancel)

    # ------------------- time for action! -----------------
    locationEntry.focus_force()    # put the focus on the entryWidget
    root.mainloop()  # run it!

    # -------- after the run has completed ----------------------------------
    if __a_button_was_clicked:
        root.destroy()  # button_click didn't destroy root, so we do it now
        return __formboxText
    else:
        # No button was clicked, so we know the OK button was not clicked
        __formboxText = None
        return __formboxText

def typeUpdate(*args):
    """
    Monitor option box entry and enable or disable fields as appropriate
    """
    if typeOption.get() == 'csv' or typeOption.get() == 'excel':
        delimEntry.configure(state=NORMAL)
        StartLineEntry.configure(state=NORMAL)
    else:
        delimEntry.configure(state=DISABLED)
        StartLineEntry.configure(state=DISABLED)

def __formboxGetText(event):
    """
    Get user entered text from form box
    """
    global root, __formboxText, entryWidget, __a_button_was_clicked
    __formboxText = locationEntry.get() + "," + typeOption.get() + "," + nodeValEntry.get() + "," + nodeAttrEntry.get() + "," + edgeFromEntry.get() + "," + edgeToEntry.get() + "," + edgeAttrEntry.get() + "," + delimEntry.get() + "," + StartLineEntry.get() + "," + outputOption.get()
    __a_button_was_clicked = 1
    root.quit()

def __formboxCancel(event):
    """
    Cancel text entry of form box and kill window
    """
    global root,  __formboxDefaultText, __formboxText, __a_button_was_clicked
    __formboxText = None
    __a_button_was_clicked = 1
    root.quit()


#-------------------------------------------------------------------
# filesavebox
#-------------------------------------------------------------------
def filesavebox(msg=None, title=None, startpos=None):
    """A file to get the name of a file to save.
    Returns the name of a file, or None if user chose to cancel.
    """
    root = Tk()
    root.withdraw()
    f = tkFileDialog.asksaveasfilename(parent=root, title=title)
    if f == "": return None
    return f

#-------------------------------------------------------------------
# fileopenbox
#-------------------------------------------------------------------
def fileopenbox(msg=None, title=None, startpos=None):
    """A dialog to get a file name.
    Returns the name of a file, or None if user chose to cancel.
    """
    root = Tk()
    root.withdraw()
    f = tkFileDialog.askopenfilename(parent=root,title=title)
    if f == "": return None
    return f


#-------------------------------------------------------------------
# utility routines
#-------------------------------------------------------------------
# These routines are used by several other functions

def __buttonEvent(event):
    """Handle an event that is generated by a person clicking a button.
    """
    global  root, __a_button_was_clicked, __widgetTexts, __replyButtonText
    __replyButtonText = __widgetTexts[event.widget]
    __a_button_was_clicked = 1
    root.quit() # quit the main loop


def __put_buttons_in_buttonframe(choices):
    """Put the buttons in the buttons frame
    """
    global __widgetTexts, __firstWidget, buttonsFrame

    __widgetTexts = {}
    i = 0

    for buttonText in choices:
        tempButton = Button(buttonsFrame, takefocus=1, text=buttonText)
        tempButton.pack(expand=YES, side=LEFT, padx='1m', pady='1m', ipadx='2m', ipady='1m')

        # remember the text associated with this widget
        __widgetTexts[tempButton] = buttonText

        # remember the first widget, so we can put the focus there
        if i == 0:
            __firstWidget = tempButton
            i = 1

        # bind the keyboard events to the widget
        tempButton.bind("<Return>", __buttonEvent)
        tempButton.bind("<Button-1>", __buttonEvent)


#-------------------------------------------------------------------
# Main
#-------------------------------------------------------------------

def run_rdfCreate():
    """
    Main function to drive GUI process, write rdf to file and invoke Network Constructor.
    """
    global saveFile
    currentFile = None
    cont = 1
    saveFile = None
    formDataMap = {}
    fileProcessed = False
    rdfString = ""
    title = "Data Ingestion RDF Builder"
    msg = "Please enter the number of data files to be ingested."
    g = Graph()
    network = Namespace("http://www.semanticweb.org/stephenbonner/ontologies/2015/8/networkIngestion#")
    namespace_manager = NamespaceManager(Graph())
    namespace_manager.bind('network', network, override=False)
    g.namespace_manager = namespace_manager


    while 1: # do forever
        about = 1
        if fileProcessed == False:
            about = choicebox(message="Welcome to RDF Bulider Please Click OK to Begin Processing Input Files", title="Welcome", choices=["OK","About"])
            #msgbox("Welcome to RDF Bulider Please Click OK to Begin Processing Input Files")
            if about == 0:
                msgbox("SEMNETCON Copyright (C) 2016 John Brennan and Stephen Bonner.\n\
                This program comes with ABSOLUTELY NO WARRANTY.\n\
                This is free software, and you are welcome to redistribute it\n\
                under certain conditions.")
            else:
                #pass
                currentFile = fileopenbox("", "Please Select file to Process", expanduser("~"))
        if currentFile == None and fileProcessed == False and about == 1: 
            msgbox("Thank you for using 'Data Ingestion RDF Builder'.", title)
            break
        else:
            formData = None
            if currentFile != None:
                formData = formbox("Please insert required information",title, None, currentFile)
                
            #Form Processing ---------------------------------------------------------------------
            if formData is not None:
                formData = formData.split(",")
                fileName = formData[0].split(os.sep)
                fileName = fileName[len(fileName)-1]
                
                formDataMap = {'location':formData[0],
                    'filetype':formData[1],
                    'nodeinfo':formData[2],
                    'nodeattr':formData[3],
                    'edgefrom':formData[4],
                    'edgeto':formData[5],
                    'edgeattr':formData[6],
                    'dlim':formData[7],
                    'sl':formData[8],
                    'outputtype':formData[9]}
                   
                fileDescription = URIRef(str(uuid.uuid4()))
                nodeDescription = URIRef(str(uuid.uuid4()))
                edgeDescription = URIRef(str(uuid.uuid4()))

                # Build RDF Graph using Network namespace
                g.add( (fileDescription, network.fileName, Literal( fileName ) ) )
                g.add( (fileDescription, network.filePath, Literal( formDataMap['location'] ) ) )
                g.add( (fileDescription, network.fileType, Literal( formDataMap['filetype'] ) ) )
                g.add( (fileDescription, network.delimData, Literal( formDataMap['dlim'] ) ) )
                g.add( (fileDescription, network.startingLine, Literal(formDataMap['sl']) ) )
                g.add( (fileDescription, network.node, nodeDescription ) )
                g.add( (fileDescription, network.edge, edgeDescription ) )
                
                g.add( (nodeDescription, network.hasValue, Literal( formDataMap['nodeinfo'] ) ) )
                g.add( (nodeDescription, network.nodeAttributes, Literal( formDataMap['nodeattr'] ) ) )
                
                g.add( (edgeDescription, network.hasValueFrom, Literal( formDataMap['edgefrom'] ) ) )
                g.add( (edgeDescription, network.hasValueTo, Literal( formDataMap['edgeto'] ) ) )
                g.add( (edgeDescription, network.edgeAttributes, Literal( formDataMap['edgeattr'] ) ) )
                
                fileProcessed = True
            if about != 0:
                cont = choicebox("Do you have further files to process?",title)
            if cont == 0:
                if fileProcessed == True:
                    save = choicebox("Would you like to save the generated RDF?", title)
                    if save == 1:
                        rdfString = g.serialize()
                        saveFile = filesavebox("","Select File to Save Data")
                        if saveFile != None:
                            f = open(saveFile + ".rdf",'w')
                            f.write(str(rdfString))
                            f.close()
                            msgbox("Thank you for using 'Data Ingestion RDF Builder'.", title)
                            break
                        else:
                            msgbox("ERROR: NO FILE SELECTED.", title)
                            msgbox("Thank you for using 'Data Ingestion RDF Builder'.", title)
                            break                            
                    else:
                        msgbox("Thank you for using 'Data Ingestion RDF Builder'.", title)
                        break                        
                else:
                    msgbox("Thank you for using 'Data Ingestion RDF Builder'.", title)
                    break                    
    if fileProcessed == True:          
        NC.main(g.serialize(), formDataMap['outputtype'])

if __name__ == '__main__':
    run_rdfCreate()

