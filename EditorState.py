# @prop text                               -> str:
# @prop cursor_position                    -> int:
# @prop current_char                       -> str:
# @prop char_before_cursor                 -> str:
# @prop text_before_cursor                 -> str:
# @prop text_after_cursor                  -> str:
# @prop current_line_before_cursor         -> str:
# @prop current_line_after_cursor          -> str:
# @prop lines                              -> List[str]:
# @prop lines_from_current                 -> List[str]:
# @prop line_count                         -> int:
# @prop current_line                       -> str:
# @prop leading_whitespace_in_current_line -> str:
# @prop on_first_line                      -> bool:
# @prop on_last_line                       -> bool:
# @prop cursor_position_row                -> int:
# @prop cursor_position_col                -> int:
# @prop is_cursor_at_the_end               -> bool:
# @prop is_cursor_at_the_end_of_line       -> bool:
# @prop selection                          -> Optional[SelectionState]:
# @prop _line_start_indexes                -> List[int]:

# char_before_cursor
# current_char
# current_line
# current_line_after_cursor
# current_line_before_cursor
# cursor_position
# cursor_position_col
# cursor_position_row
# cut_selection
# empty_line_count_at_the_end
# end_of_paragraph
# find
# find_all
# find_ backwards
# find_boundaries_of_current_word
# find_enclosing_bracket_left
# find_enclosing_bracket_right
# find_matching_bracket_position
# find_next_matching_line
# find_next_word_beginning
# find_next_word_ending
# find_previous_matching_line
# find_previous_word_beginning
# find_previous_word_ending
# find_start_of_previous_word
# get_column_cursor_position
# get_cursor_down_position
# get_cursor_left_position
# get_cursor_right_position
# get_cursor_up_position
# get_end_of_document_position
# get_end_of_line_position
# get_start_of_document_position
# get_start_of_line_position
# get_word_before_cursor
# get_word_under_cursor
# has_match_at_current_position
# insert_after
# insert_before
# is_cursor_at_the_end
# is_cursor_at_the_end_of_line
# last_non_blank_of_current_line_position
# leading_whitespace_in_current_line
# line_count
# lines
# lines_from_current
# on_first_line
# on_last_line
# paste_clipboard_data
# selection
# selection_range
# selection_range_at_line
# selection_ranges
# start_of_paragraph
# text
# text_after_cursor
# text_before_cursor
# translate_index_to_position
# translate_row_col_to_index


# def __init__(self, text='', cursor_position=None, selection=None):
# def _get_char_relative_to_cursor(self, offset=0):
# def _find_line_start_index(self, index):
# def translate_index_to_position(self, index):
# def translate_row_col_to_index(self, row, col):
# def has_match_at_current_position(self, sub):
# def find(self, sub, in_current_line=False, include_current_position=False, ignore_case=False, count=1):
# def find_all(self, sub, ignore_case=False):
# def find_backwards(self, sub, in_current_line=False, ignore_case=False, count=1):
# def get_word_before_cursor(self, WORD=False):
# def find_start_of_previous_word(self, count=1, WORD=False):
# def find_boundaries_of_current_word(self, WORD=False, include_leading_whitespace=False, include_trailing_whitespace=False):
# def get_regex(include_whitespace):
# def get_word_under_cursor(self, WORD=False):
# def find_next_word_beginning(self, count=1, WORD=False):
# def find_next_word_ending(self, include_current_position=False, count=1, WORD=False):
# def find_previous_word_beginning(self, count=1, WORD=False):
# def find_previous_word_ending(self, count=1, WORD=False):
# def find_next_matching_line(self, match_func, count=1):
# def find_previous_matching_line(self, match_func, count=1):
# def get_cursor_left_position(self, count=1):
# def get_cursor_right_position(self, count=1):
# def get_cursor_up_position(self, count=1, preferred_column=None):
# def get_cursor_down_position(self, count=1, preferred_column=None):
# def find_enclosing_bracket_right(self, left_ch, right_ch, end_pos=None):
# def find_enclosing_bracket_left(self, left_ch, right_ch, start_pos=None):
# def find_matching_bracket_position(self, start_pos=None, end_pos=None):
# def get_start_of_line_position(self, after_whitespace=False):
# def get_column_cursor_position(self, column):
# def selection_range_at_line(self, row):
# def paste_clipboard_data(self, data, paste_mode=PasteMode.EMACS, count=1):
# def start_of_paragraph(self, count=1, before=False):
# def match_func(text):
# def end_of_paragraph(self, count=1, after=False):
# def match_func(text):
# def insert_after(self, text):
# def insert_before(self, text):

from prompt_toolkit.document import Document
from prompt_toolkit.buffer import Buffer
from abc import ABC,abstractmethod,abstractproperty
import re
from rp import *

def add_document_method(method):
    #This method is a decorator that adds methods to the Document class.
    #We need this, as opposed to subclassing Document, because many Document methods are hard-wired to return a new Document object
    #These functions, by default, will not be memoized (because of the current implementation of rp.memoized, which isn't great for objects...)
    from prompt_toolkit.document import Document
    setattr(Document,method.__name__,method)

def add_document_property(method):
    #Properties will be memoized
    property_name='_'+method.__name__
    def memoized_property(self):
        return method(self)
        if not hasattr(self._cache,property_name):
            setattr(self._cache,property_name,method(self))
        return getattr(self._cache,property_name)
    memoized_property.__name__+=method.__name__
    memoized_property=property(memoized_property)
    setattr(Document,method.__name__,memoized_property)

@add_document_method
def clamped_cursor(self,index:int)->int:
    return max(0,min(len(self.text),index)) #Clamps the cursor to the bounds of the Document to avoid errors

@add_document_method
def cursor_shift(self,count:int)->Document:
    return Document(self.text,self.clamped_cursor(self.cursor_position+count))

@add_document_method
def cursor_up   (self,count:int=1)->Document:
    buffer=Buffer(document=Document(self.text,self.cursor_position))
    buffer.cursor_up(count)
    return buffer.document

@add_document_method
def cursor_down (self,count:int=1)->Document:
    buffer=Buffer(document=Document(self.text,self.cursor_position))
    buffer.cursor_down(count)
    return buffer.document

@add_document_method
def cursor_left (self,count:int=1)->Document:
    buffer=Buffer(document=Document(self.text,self.cursor_position))
    buffer.cursor_left(count)
    return buffer.document

@add_document_method
def cursor_right(self,count:int=1)->Document:
    buffer=Buffer(document=Document(self.text,self.cursor_position))
    buffer.cursor_right(count)
    return buffer.document

@add_document_method
def delete_before_cursor(self,count:int=1)->Document:
    return Document(self.text[:-count],self.clamped_cursor(self.cursor_position-count))

@add_document_method
def delete_after_cursor(self,count:int=1)->Document:
    return Document(self.text[:self.cursor_position]+self.text[self.cursor_position+count:],self.cursor_position)



cursor_char='¦'

@add_document_property
def debug_view(self):
    print('POST:',self.cursor_position)
    print("AOSIDAOISDIJOASDJOIASOIJDAIJOSDIJOASDJIOA")
    return fansi(self.text[:self.cursor_position],'gray') + fansi(cursor_char,'cyan','bold') + fansi(self.text[self.cursor_position:],'gray')

# @add_document_property
# def as_state(self):
#     return Document.from_document(self)

# class Document(Document):
#     @staticmethod
#     def from_document(document:Document):
#         return Document(document.text,document.cursor_position)

class Engine:
    def __init__(self,state=None):
        self.state=Document()
        self.rules=[]

    def process(self,keystroke:str):
        #Mutates the Engine's state, returns the engine
        assert isinstance(keystroke,str),'keystroke should be a string but got type '+repr(type(keystroke))
        for rule in self.rules:
            result=rule(self.state,keystroke)
            if result is None:
                terminal=False
            else:
                print('Applying Rule: '+rule.__name__)
                assert isinstance(result,tuple)
                assert len(result)==2
                new_state,terminal=result
                assert isinstance(terminal,bool    ),"All rules must return (state:Document,terminal:bool) tuples - but the terminal value returned was of type "+repr(type(terminal))
                assert isinstance(new_state,Document),"All rules must return (state:Document,terminal:bool) tuples - but the state value returned was of type "   +repr(type(state   ))
                self.state=new_state
            if terminal:
                break

    def add_rule(self,rule):
        self.rules.append(rule)

python_engine=Engine()

@python_engine.add_rule
def cursor_right(state,keystroke):
    if keystroke=='right':
        return state.cursor_right(),True

@python_engine.add_rule
def cursor_left(state,keystroke):
    if keystroke=='left':
        return state.cursor_left(),True

@python_engine.add_rule
def cursor_up(state,keystroke):
    print("DOOBLY")
    if keystroke=='up':
        return state.cursor_up(),True

@python_engine.add_rule
def cursor_down(state,keystroke):
    if keystroke=='down':
        return state.cursor_down(),True

@python_engine.add_rule
def backspace(state,keystroke):
    if keystroke=='backspace':
        return state.delete_before_cursor(),True

@python_engine.add_rule
def delete(state,keystroke):
    if keystroke=='delete':
        return state.delete_after_cursor(),True

@python_engine.add_rule
def insert_character(state,keystroke):
    if len(keystroke)==1:
        return state.insert_before(keystroke),True

keystroke_translations={
    '\x1b[A' :'up',
    '\x1b[B' :'down',
    '\x1b[D' :'left',
    '\x1b[C' :'right',
    '\x7f'   :'backspace',
    '\x1b[3~':'delete',
}

while True:
    keystroke=input_keypress()
    if keystroke=='q':
        break
    if keystroke in keystroke_translations:
        keystroke=keystroke_translations[keystroke]
    python_engine.process(keystroke)
    print("========================================================")
    print("Processing "+keystroke)
    print("-----------------------------------")
    print(python_engine.state.debug_view)