import yattag
import os
import io
import re
from WebPageTools.WebPageEnums import WebPageEnums
from WebPageTools.WebPageStateManager import WebPageStateManager
from WebStructures.WebTable import WebTable
from Utilities.TextProcessor import TextProcessor
from WebStructures.SimpleHTML import SimpleHTML
from Utilities.Core import *
    
class WebPage_Slides:
    def __init__(self):

        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
        self.SlideTagToIdNumber = {}
        self.SlideTagSlideCounter = {}
        self.NextSlideTagIdNumber = 0

    def AddSlideShow(self, Input, State, Interface, Data, IsKey=False):

        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
        if State['slides_group'][0] not in self.SlideTagToIdNumber:
            self.SlideTagToIdNumber[State['slides_group'][0]] = self.NextSlideTagIdNumber
            self.SlideTagSlideCounter[State['slides_group'][0]] = 0
            self.NextSlideTagIdNumber += 1
        else:
            self.SlideTagSlideCounter[State['slides_group'][0]] = 0
        self.Doc.stag('div', self.DCTS, self.Style(State), self.Class(State, 'slideshow-container', 'slideshow-container-instance{}'.format(self.SlideTagToIdNumber[State['slides_group'][0]])))
        with self.Tag('p', self.Style(State), self.Class(State, 'slideshow-control-spacer', 'slideshow-control-spacer-instance{}'.format(self.SlideTagToIdNumber[State['slides_group'][0]]))):
            self.Text('slideshow-control-spacer-instance{}'.format(self.SlideTagToIdNumber[State['slides_group'][0]]))
        with self.Tag('a', 'onclick="plusSlides({}, -1)"'.format(self.SlideTagToIdNumber[State['slides_group'][0]]), self.Style(State), self.Class(State, 'slideshow-control-spacer', 'prev', 'waves-effect', 'waves-light', 'btn')):
            self.Text(self.PreProcessText('&#10094;'))
        with self.Tag('a', 'onclick="plusSlides({}, 1)"'.format(self.SlideTagToIdNumber[State['slides_group'][0]]), self.Style(State), self.Class(State, 'slideshow-control-spacer', 'next', 'waves-effect', 'waves-light', 'btn')):
            self.Text(self.PreProcessText('&#10095;'))
        State.GlobalState['in_slide_show'] = True
        #FlushPrintUTF8('Start Slide Show', State['slides_group'][0], self.SlideTagToIdNumber[State['slides_group'][0]])
        #FlushPrintUTF8('{}[{}]: '.format(State['slides_group'][0], self.SlideTagToIdNumber[State['slides_group'][0]]), end='')

    def AddSlide(self, Input, State, Interface, Data, IsKey=False):

        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
        self.Doc.stag('div', self.DCTS, self.Style(State), self.Class(State, 'slide', 'slide-instance{}'.format(self.SlideTagSlideCounter[State['slides_group'][0]])))
        State['mode'] = WebPageEnums.SlideContent
        State['slide_depth'] = 1
        State.GlobalState['in_slide'] = True
        #FlushPrintUTF8('  -- Start Slide', State['slides_group'][0], self.SlideTagSlideCounter[State['slides_group'][0]])
        self.SlideTagSlideCounter[State['slides_group'][0]] += 1
        #FlushPrintUTF8('{},'.format(self.SlideTagSlideCounter[State['slides_group'][0]]), end='')
        return self.LoadItem(Input, State, Interface, Data=Data, IsKey=IsKey)

    def CloseSlide(self, Input, State, Interface):

        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
        self.Doc.stag('/div', self.DCTS)
        State.GlobalState['in_slide'] = False
        State['mode'] = WebPageEnums.Slides
        #FlushPrintUTF8('  -- End Slide')

    def CloseSlideShow(self, Input, State, Interface):

        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
        self.Doc.stag('/div', self.DCTS)
        State.GlobalState['in_slide_show'] = False
        #FlushPrintUTF8('End Slide Show')
        #FlushPrintUTF8('')

    def WebPageSlidesAddJS(self):
        
        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
        slidesFunctionality = []
        slidesFunctionality += ['$(document).ready(function() {{']
        slidesFunctionality += ['    initSlides({});']
        #for Index in range(self.NextSlideTagIdNumber):
        #    slidesFunctionality += ['    showSlides(0, {});'.format(Index)]
        slidesFunctionality += ['}});']
        slidesFunctionality = '\n'.join(slidesFunctionality)

        self.Text(self.PreProcessText(Format(slidesFunctionality, self.NextSlideTagIdNumber - 1)))