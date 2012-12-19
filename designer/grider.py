###############################################################################
# UI FRAMEWORK FOR CONSTRUCT 3 DESIGNER
# VERSION: Proof of concept 0.1 (Late night edition)
# DATE: 2012-06-02
# AUTHOR: Jan Costermans
# LICENSE: COPYLEFT
#
# PLANNED UI DESIGN (BRAINSTORM)
#
# Start app -> only the girder frame opens
# User can open a project which loads the girder frame with all the constructs,
# containers, pcap files (for testing), perhaps some network settings for real-
# time monitoring, adapters, and other stuff
# OR User can choose to work without project and just open other frames and do
# stuff.
#
# Several frames can be openend from within the central girder frame. These are
#     1. An editor frame to insert python code (construct or container).
#        A tool palette should be openend along with this frame.
#        This editor can switch between code view and graphical view.
#        The graphical view will support drag-and-drop functionality.
#        Multiple editor frames can be open at the same time.
#     2.
# Enable these lines for pubsub v1.x / disable for pusub >= 3.0
# from wx.lib.pubsub import setupv1
# from wx.lib.pubsub import Publisher as pub
# Disable these lines for pubsub v1.x / enable for pusub >= 3.0
# from wx.lib.pubsub import setuparg1
###############################################################################
import wx
import wx.lib.pubsub.setupkwargs
from wx.lib.pubsub import pub

# TODO PUT ALL WX ID's OVER HERE
ID_SEARCH_BOX = wx.NewId()

###############################################################################
class SomeReceiver(object):
    """The pubsub receiver class. http://pubsub.sourceforge.net/"""
    def __init__(self):
        # The app creates 1 object of this class to handle all messages.
        #
        pub.subscribe(self.__onObjectAdded, 'object.added')

    # All message handlers go here
    # Larger functions go into some other module and are called from here.

    def __onObjectAdded(self, msg):
        # data passed with your message is put in msg.data.
        # Any object can be passed to subscribers this way.
        print "Object", repr(msg), "is added"
        pub.sendMessage("completed", msg="HELLO!")


###############################################################################
class constructApp(wx.App):
    """Construct designer application"""
    def __init__(self, redirect=True, filename=None):
        print "App __init__"
        wx.App.__init__(self, redirect, filename)

    def OnInit(self):
        self.frame = girderFrame(None,
                               title="Girder")
        self.SetTopWindow(self.frame)
        self.frame.Show()
        return True

class girderFrame(wx.Frame):
    """Main Frame holding the Panel."""
    def __init__(self, *args, **kwargs):
        """Create the girderFrame."""
        wx.Frame.__init__(self, *args, **kwargs)

        # Add the Widget Panel
        self.Panel = girderPanel(self)

        # Change the Size of the Frame
        self.Fit()

class girderPanel(wx.Panel):
    """This Panel holds two simple buttons, but doesn't really do anything."""
    def __init__(self, parent, *args, **kwargs):
        """Create the girderPanel."""
        wx.Panel.__init__(self, parent, *args, **kwargs)

        self.parent = parent


        # subscribe the girderPanel to some pubsub messages:
        pub.subscribe(self.onCompleted, 'completed')

###############################################################################
# MORE BRAINSTORM
# 1. Search box for searching buttons, recently used constructs, containers,...
# 2. Constructs (collapsible pane)
# 2.1. Create new construct ... ( and adapters ?? ) -> opens an 'editor' frame
# 2.2. Open/Load existing construct
# 2.3. list of recently used constructs, perhaps also favourites, projects, ...
# 3. Containers
# 3.1. Create new Container ...
# 3.2. Open/Load existing Container
# 3.3. list of recently used containers, perhaps also favourites, projects, ...
# 4. Open pcap file / real-time sniffing with pcapy module ??
# ?? where does the encode/decode frame belong?

    # GIRDER - SEARCH BOX
        self.searchbox = ExtendedSearchCtrl(self,
                                       id=ID_SEARCH_BOX,
                                       style=wx.TE_PROCESS_ENTER)
    # GIRDER - COLLAPSIBLEPANE
    # probably need some kind of list here to make it easy to add stuff
    # also needs drag-n-drop for dropping files
    # perhaps needs some virtual folders (like code::blocks)

        self.cp = cp = wx.CollapsiblePane(self,
                                          label="colpane",
                                 style=wx.CP_DEFAULT_STYLE | wx.CP_NO_TLW_RESIZE)
        self.Bind(wx.EVT_COLLAPSIBLEPANE_CHANGED, self.OnPaneChanged, cp)
        # self.MakePaneContent(cp.GetPane())



        self.newConstructBtn = wx.Button(self,
                                         id= -1,
                                         label="Create new Struct...")
        self.Bind(wx.EVT_BUTTON, self.OnnewConstructBtn, self.newConstructBtn)


        self.newValueBtn = wx.Button(self, id= -1, label="Request new value")
        self.Bind(wx.EVT_BUTTON, self.OnBtn, self.newValueBtn)
       # self.newValueBtn.Bind(wx.EVT_BUTTON, self.OnBtn)

        self.displayLbl = wx.StaticText(self, id= -1, label="Value goes here")

        Sizer = wx.BoxSizer(wx.VERTICAL)
        Sizer.Add(self.searchbox, 0, wx.ALIGN_LEFT | wx.ALL, 5)
        Sizer.Add(self.newConstructBtn, 0, wx.ALIGN_CENTER | wx.ALL, 5)
        Sizer.Add(self.newValueBtn, 0, wx.ALIGN_CENTER | wx.ALL, 5)
        Sizer.Add(self.displayLbl, 0, wx.ALL | wx.CENTER, 5)

        self.SetSizerAndFit(Sizer)

###############################################################################
###           EVENT HANDLING - ALL EVENTS ARE MAPPED TO PUBSUB MESSAGES     ###
###############################################################################

    def OnnewConstructBtn(self, msg):
       pass

    def onCompleted(self, msg):
        # data passed with your message is put in message.data.
        # Any object can be passed to subscribers this way.
        print 'pubsub', repr(msg), "this works"
        self.newValueBtn.Enable()  # doesn't work
        self.newValueBtn.SetLabel("This Works")
        self.displayLbl.SetLabel("This also works")

    def OnBtn(self, event=None):

        self.displayLbl.SetLabel("Requesting...")
        # self.newValueBtn = event.GetEventObject()
        self.newValueBtn.Disable()
        pub.sendMessage("object.added", msg="HELLO WORLD")

    def OnPaneChanged(self):
        pass


###############################################################################
class ExtendedSearchCtrl(wx.SearchCtrl):
    """Extended Search Control. Based on a snip from Cody Precord. (thanks) """
    def __init__(self, parent, id, value='', pos=wx.DefaultPosition,
                 size=wx.DefaultSize, style=wx.TE_PROCESS_ENTER):
        wx.SearchCtrl.__init__(self, parent, id, value, pos, size)
        self.Bind(wx.EVT_TEXT_ENTER, self.SearchHandler)
        self.Bind(wx.EVT_KEY_UP, self.SearchHandler)
        self.Show()

    def SearchHandler(self, event):
        print "Searching...."
        eventType = event.GetEventType()
        searchQuery = self.GetValue()
        if eventType == wx.wxEVT_COMMAND_TEXT_ENTER:
            # TODO Do we need to check for this event?
            print "COMMAND_TEXT is looking for" + searchQuery
        elif eventType == wx.wxEVT_KEY_UP:
            # SEARCH FUNCTIONALITY GOES HERE
            print "Looking for: " + searchQuery
            # program a filter on this --> USE PUBSUB !!
        else:
            event.Skip()


# TODO ADD THREADING SUPPORT HERE
if __name__ == '__main__':
    a = SomeReceiver()
    # change redirect to False to use the console for stout and stderr
    app = constructApp(redirect=False, filename="mypylog")

    app.MainLoop()


