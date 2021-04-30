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


#PREREQUISITES: pip install rp prompt_toolkit
from rp import *
from prompt_toolkit.document import Document
from prompt_toolkit.buffer import Buffer
from abc import ABC,abstractmethod,abstractproperty
import re

def add_document_method(method):
    #This method is a decorator that adds methods to the Document class.
    #We need this, as opposed to subclassing Document, because many Document methods are hard-wired to return a new Document object
    #These functions, by default, will not be memoized (because of the current implementation of rp.memoized, which isn't great for objects...)
    from prompt_toolkit.document import Document
    setattr(Document,method.__name__,method)

def add_document_property(method):
    #Properties will be memoized
    setattr(Document,method.__name__,property(method))

@add_document_method
def clamped_cursor(self,index:int)->int:
    return max(0,min(len(self.text),index)) #Clamps the cursor to the bounds of the Document to avoid errors

@add_document_method
def cursor_shift(self,count:int)->Document:
    return Document(self.text,self.clamped_cursor(self.cursor_position+count))

@add_document_method
def cursor_up   (self,count:int=1)->Document:
    buffer=Buffer(document=self)
    buffer.cursor_up(count)
    return buffer.document

@add_document_method
def cursor_down (self,count:int=1)->Document:
    buffer=Buffer(document=self)
    buffer.cursor_down(count)
    return buffer.document

@add_document_method
def cursor_left (self,count:int=1)->Document:
    r"""
    |    ‹Hello World¦›  left ‹Hello Worl¦d›   left   ‹Hello Wor¦ld›
    
    |    ‹¦Hello World›  left ‹¦Hello World›
    """
    buffer=Buffer(document=self)
    buffer.cursor_left(count)
    return buffer.document

@add_document_method
def cursor_right(self,count:int=1)->Document:
    buffer=Buffer(document=self)
    buffer.cursor_right(count)
    return buffer.document

@add_document_property
def cursor_home(self)->Document:
    return self.cursor_left(999999)

@add_document_property
def cursor_end(self)->Document:
    return self.cursor_right(999999)

@add_document_method
def delete_before_cursor(self,count:int=1)->Document:
    buffer=Buffer(document=self)
    buffer.delete_before_cursor(count)
    return buffer.document

@add_document_method
def delete(self,count:int=1)->Document:
    buffer=Buffer(document=self)
    buffer.delete(count)
    return buffer.document

@add_document_method
def insert_text(self,text:int=1)->Document:
    buffer=Buffer(document=self)
    buffer.insert_text(text)
    return buffer.document

@add_document_property
def char_after_cursor(self)->Document:
    return self.text_after_cursor[0] if self.text_after_cursor else ''

@add_document_property
def char_before_cursor(self)->Document:
    return self.text_before_cursor[-1] if self.text_before_cursor else ''

@add_document_property
def line_above_cursor(self)->str:
    #returns '' if not self.line_above_cursor_exists
    #else, returns the line above the cursor
    lines=self.text_before_cursor.splitlines()
    if len(lines)<=1:
        return ''
    return lines[-2]

@add_document_property
def line_above_cursor_exists(self)->bool:
    return number_of_lines(self.text_before_cursor)>1

@add_document_property
def new_block(self)->bool:
    return self.cursor_end.insert_text('\n'+self.leading_whitespace_in_current_line+'    ')


cursor_char='¦'

@add_document_property
def debug_view(self):
    return (fansi_syntax_highlighting('\u200b'+self.text[:self.cursor_position]+'\u200b') + fansi(cursor_char,'cyan','bold') + fansi_syntax_highlighting('\u200b'+self.text[self.cursor_position:]+'\u200b')).replace('\u200b','')

@add_document_property
def debug_view_plain(self):
    return self.text[:self.cursor_position] + cursor_char + self.text[self.cursor_position:]

class Engine:
    def __init__(self):
        self.rules=[]
        self.rules_last_used=[]

    def process(self,state:Document,*keystrokes:str,debug=True)->Document:
        #Processes a keystroke
        self.rules_last_used.clear()#Record every rule used while processing the keystroke
        debug_lines=[]
        for keystroke in keystrokes:
            assert isinstance(keystroke,str),'keystroke should be a string but got type '+repr(type(keystroke))
            for rule in self.rules:
                result=rule(state,keystroke)
                if result is not None:
                    self.rules_last_used.append(rule)

                    if debug:
                        debug_prefix="\t\tUsed Rule: "+rule.__name__
                        debug_view='‹'+result.debug_view_plain.replace('\n','↵')+'›'
                        debug_prefix=debug_prefix.ljust(max(len(rule.__name__) for rule in self.rules)+15)
                        print(fansi(debug_prefix,'magenta')+fansi(debug_view,'blue'))

                    assert isinstance(result,Document),"All rules must either None or a new state of type Document"   +repr(type(state   ))
                    state=result

                    break
        return state

    def add_rule(self,rule):
        self.rules.append(rule)

    def run_all_tests(self):
        run_all_engine_tests(self)

##########################################################################################


def startswith_any(string:str,*prefixes:str)->bool:
    return any(map(string.startswith,prefixes))

def endswith_any(string:str,*suffixes:str)->bool:
    return any(map(string.endswith,suffixes))


##########################################################################################

engine=Engine()

@engine.add_rule
def d_to_def(state,keystroke):
    r"""
    Shortcut for creating a function definition
    |   ‹d¦›   ␣   ‹def ¦():›

    Works on indented lines too
    |   ‹    d¦›   ␣   ‹    def ¦():›

    Full usage demo
    |  d ␣ f ␣ x ␣ y ␣ z ↵    ‹def f(x,y,z):›
    |                         ‹    ¦›

    Add a defualt function name with no args if we press enter
    |   ‹d¦›   enter   ‹def _():›
    |                  ‹    ¦›
    """
    if keystroke in ' \n' and state.current_line_before_cursor.lstrip()=='d' and not state.current_line_after_cursor:
        if keystroke==' ':
            return state.insert_text('ef ():').cursor_left(3)
        elif keystroke=='\n':
            return state.insert_text('ef _():\n'+state.leading_whitespace_in_current_line+'    ')

@engine.add_rule
def def_to_args(state,keystroke):
    r"""
    Jumps to argument area
    |   ‹def f¦():›   ␣   ‹def f(¦):›

    Also works on indented def's
    |   ‹    def f¦():›   ␣   ‹    def f(¦):›
    """
    if keystroke==' ' and state.current_line_after_cursor=='():' and re.fullmatch(r'def \w+',state.current_line_before_cursor.lstrip()):
        return state.cursor_right(1)

@engine.add_rule
def def_enter(state,keystroke):
    r"""
    Gets rid of comma
    |   ‹def f(x,¦):›   enter   ‹def f(x):›
    |                           ‹    ¦›    

    Works with no trailing comma too
    |   ‹def f(x¦):›    enter    ‹def f(x):›
    |                            ‹    ¦›

    Works with functions with no args too
    |   ‹def f¦():›    enter    ‹def f():›
    |                           ‹    ¦›

    Indents nested functions properly
    |   ‹def f():›                 ‹def f():›
    |   ‹    def g¦():›    enter   ‹    def g():›
    |                              ‹        ¦›

    Integration test: Nested funcitons
    |                              ‹def f():›
    |   d ␣ f enter d ␣ g enter    ‹    def g():›
    |                              ‹        ¦›

    Spacebar: Gets rid of comma, only works with comma
    |   ‹def f(x,¦):›   space   ‹def f(x):¦›

    Spacebar: If there are no arguments, immediately enters the func body
    |   ‹def f(¦):›   space   ‹def f():¦›

    Add a default function name if none is given
    |   ‹def ¦():›    enter    ‹def _():›
    |                          ‹    ¦›

    """
    if state.current_line_before_cursor.lstrip()=='def ' and state.current_line_after_cursor=='():':
        state=state.insert_text('_')
    if keystroke in '\n ' and state.current_line_before_cursor.lstrip().startswith('def '):
        if keystroke==' ' and state.current_line_after_cursor=='):':
            if state.current_line_before_cursor.endswith(','):
                return state.delete_before_cursor().cursor_end
            elif  state.char_before_cursor=='(':
                return state.cursor_end
        if keystroke=='\n':
            if state.current_line_before_cursor.endswith(','):
                state=state.delete_before_cursor()
            return state.new_block


@engine.add_rule
def def_backspce(state,keystroke):
    r"""
    On backspace, delete the function name...
    |   ‹def func(¦):›   backspace   ‹def fun¦():›

    When there's no function name and no function args, delete the function...
    |   ‹def ¦():›    backspace    ‹›

    Integration test: Here's the intention...it's backspacing the action of the spacebar
    |   d ␣   ‹def ¦():›  backspace  ‹›
    """
    if keystroke == 'backspace' and state.current_line_before_cursor.lstrip().startswith('def ') and state.current_line_before_cursor.endswith('(') and state.current_line_after_cursor=='):':
        return state.cursor_left().delete_before_cursor()
    if keystroke == 'backspace' and state.current_line_before_cursor.lstrip()=='def ' and state.current_line_after_cursor=='():':
        return state.delete(3).delete_before_cursor(4)

def process_simple_arrow_key(state,keystroke):
    if keystroke=='right':
        return state.cursor_right()
    if keystroke=='left':
        return state.cursor_left()
    if keystroke=='up':
        return state.cursor_up()
    if keystroke=='down':
        return state.cursor_down()


@engine.add_rule
def def_type(state,keystroke):
    r"""
    Add the -> to a function when we put the cursor in the right place
    |   ‹def func(¦):›   right   ‹def func()->¦:›
    ...
    |   ‹def func():¦›   left    ‹def func()->¦:›


    Take the -> away if we move the cursor away again
    |   ‹def func()->¦:›   right       ‹def func():¦›
    ...
    |   ‹def func()->¦:›   left        ‹def func(¦):›
    ...
    |   ‹def func()->¦:›   backspace   ‹def func(¦):›

    """
    arrow_keys='left right up down'.split()
    if keystroke not in arrow_keys and keystroke!='backspace':
        return
    if state.current_line_before_cursor.lstrip().startswith('def '):
        if state.current_line_before_cursor.endswith(')->') and state.current_line_after_cursor==':':
            if keystroke=='backspace':
                keystroke='left'
            state=state.delete_before_cursor(2)
            if keystroke in arrow_keys:
                return process_simple_arrow_key(state,keystroke)
        else:
            if keystroke in arrow_keys:
                state = process_simple_arrow_key(state,keystroke)
            if state.char_before_cursor==')' and state.current_line_after_cursor==':':
                return state.insert_text('->')



@engine.add_rule
def enter_new_block(state,keystroke):
    r"""
    When entering a new block of code , add an indent
    |   ‹if True:¦›   enter   ‹if True:›
    |                         ‹    ¦›
    ...
    |   ‹def f(x):¦›    enter    ‹def f(x):›
    |                            ‹    ¦›
    ...
    |   ‹for x in y:¦›   enter   ‹for x in y:›
    |                            ‹    ¦›

    Also works when the cursor is right before the :
    |   ‹for x in y¦:›   enter   ‹for x in y:›
    |                            ‹    ¦›
    """
    if keystroke=='\n' and (not state.current_line_after_cursor and state.char_before_cursor==':' or state.current_line_after_cursor==':'):
        return state.cursor_end.insert_text('\n'+state.leading_whitespace_in_current_line+'    ')

@engine.add_rule
def exit_block_on_enter(state,keystroke):
    r"""
    When pressing enter after the return keyword, exit the current block
    |   ‹def f(x):›        enter   ‹def f(x):›      
    |   ‹    return x¦›            ‹    return x›  
    |                              ‹¦›
    ...
    |   ‹def f(x):›        enter   ‹def f(x):›      
    |   ‹    return¦›              ‹    return›  
    |                              ‹¦›
    """
    if keystroke=='\n':
        prefix=state.current_line_before_cursor.lstrip()
        if prefix=='return' or prefix.startswith('return '):
            whitespace=state.leading_whitespace_in_current_line
            desired_whitespace=whitespace[:-4]
            return state.insert_text('\n'+desired_whitespace)


@engine.add_rule
def def_arg_commas(state,keystroke):
    r"""
    Adds commas between args
    |   ‹def f(x¦):›   ␣   ‹def f(x,¦):›

    Also works with classes for multi-inheritance
    |   ‹class C(x¦):›   ␣   ‹class C(x,¦):›

    Integration test
    |   d ␣ f ␣ x ␣ y ␣ z  ‹def f(x,y,z¦):›
    """
    if keystroke==' ' and state.current_line_after_cursor=='):' and startswith_any(state.current_line_before_cursor.lstrip(),'def ','class '):
        return state.insert_text(',')

@engine.add_rule
def def_eight_to_vararg(state,keystroke):
    r"""
    Saves you from having to press the shift key, because "def f(8):" is invalid syntax
    |   ‹def f(¦):›     8   ‹def f(*¦):›
    ...
    |   ‹def f(x,¦):›   8   ‹def f(x,*¦):›   8   ‹def f(x,**¦):›

    SHOULD_FAIL!
    |   ‹def f(x¦):›    8   ‹def f(x*¦):›
    ...
    |   ‹def f(x=¦):›   8   ‹def f(x=*¦):›

    Integration test
    |   d ␣ f ␣ 8 a r g s    ‹def f(*args¦):›    ␣ 8 8 k w a r g s     ‹def f(*args,**kwargs¦):›
    """
    if keystroke=='8' and state.current_line_after_cursor=='):' and startswith_any(state.current_line_before_cursor.lstrip(),'def ') and endswith_any(state.current_line_before_cursor,'*',',','('):
        return state.insert_text('*')


@engine.add_rule
def r_to_return(state,keystroke):
    r"""
    TODO: Add the ability for this rule to detect if the cursor is currently in a function, like rp does
    TODO: When r is a variable, don't turn r into return when pressing the spacebar


    Adds the return keyword.
    |   ‹def f(x):›    space    ‹def f(x):›
    |   ‹    r¦›                ‹    return ¦›

    Also works with the enter key to return nothing
    |   ‹def f(x):›             ‹def f(x):›
    |   ‹    r¦›       enter    ‹    return›
    |                           ‹¦›
    ...
    |   ‹def f(x):›             ‹def f(x):›           
    |   ‹    if x:›    enter    ‹    if x:›           
    |   ‹        r¦›            ‹        return›
    |                           ‹    ¦›           

    Getting rid of return
    |   ‹def f(x):›      backspace    ‹def f(x):›
    |   ‹    return ¦›                ‹    ¦›
    ...
    |   ‹def f(x):›      backspace    ‹def f(x):›
    |   ‹    return¦›                 ‹    ¦›

    Integration test
    |   d ␣ f ␣ x enter r ␣ x   ‹def f(x):›
    |                           ‹    return x¦›
    """
    if keystroke in '\n ' and state.current_line_before_cursor.lstrip()=='r' and not state.current_line_after_cursor:
        return engine.process(state.insert_text('eturn'),keystroke,debug=False)
    if keystroke=='backspace' and state.current_line_before_cursor.strip()=='return':
        return state.delete_before_cursor(len(state.current_line_before_cursor)).insert_text(state.leading_whitespace_in_current_line)

@engine.add_rule
def add_matching_bracket(state,keystroke):
    r"""
    Inserting [ also inserts ]
    |   ‹¦›   [   ‹[¦]›   [    ‹[[¦]]›

    Inserting ( also inserts )
    |   ‹¦›   (   ‹(¦)›   (    ‹((¦))›

    Inserting { also inserts }
    |   ‹¦›   {   ‹{¦}›   {    ‹{{¦}}›
    """

    bracket_match={
        '{':'}',
        '(':')',
        '[':']',
    }

    if keystroke in bracket_match:
        return state.insert_text(keystroke+bracket_match[keystroke]).cursor_left()

@engine.add_rule
def backspace_matching_bracket(state,keystroke):
    r"""
    Backspacing [ also deletes ]
    |   ‹[[¦]]›   backspace   ‹[¦]›  backspace   ‹¦›

    Backspacing ( also deletes )
    |   ‹((¦))›   backspace   ‹(¦)›  backspace   ‹¦›

    Backspacing { also deletes }
    |   ‹{{¦}}›   backspace   ‹{¦}›  backspace   ‹¦›
    """

    bracket_match={
        '{':'}',
        '(':')',
        '[':']',
    }

    if keystroke == 'backspace':
        if state.char_before_cursor in bracket_match and state.char_after_cursor==bracket_match[state.char_before_cursor]:
            return state.delete_before_cursor().delete()

@engine.add_rule
def increment_decrement(state,keystroke):
    r"""
    Adds the ++ and -- operators to python
    |   ‹x›   + +   ‹x+=1›
    ...
    |   ‹x›   - -   ‹x-=1›

    Works with array_augmented_assignment
    |   ‹a[x¦]›   + +   ‹a[x]+=1¦›

    Integration test
    |   a [ ; - -   ‹a[:]-=1›
    """

    if keystroke in '+-' and state.char_before_cursor==keystroke:
        return engine.process(state,'=','1',debug=False)

@engine.add_rule
def spaces_not_tabs(state,keystroke):
    r"""
    Tab adds four spaces
    |   ‹›   tab   ‹    ›   tab   ‹        ›

    SHOULD_FAIL! Tab does not add a tab character
    |   ‹›   tab   ‹\t›
    """

    if keystroke == '\t':
        return state.insert_text('    ')

@engine.add_rule
def f_to_for_loop(state,keystroke):
    r"""
    Upon pressing space
    |    ‹fo›   space   ‹for ¦ in :›   x ␣ y  ‹for x in y¦:›
    ...
    |    ‹f›    space   ‹for ¦ in :›

    Backspacing for loops
    |    ‹for ¦ in :›   backspace   ‹›
    ...
    |    ‹for x in ¦:›   backspace   ‹for x¦ in :›


    """

    prefix=state.current_line_before_cursor.lstrip()
    if keystroke==' ' and not state.current_line_after_cursor and (prefix=='fo' or prefix=='f'):
        return state.insert_text('for  in :'[len(prefix):]).cursor_left(len(' in :'))
    if keystroke==' ' and state.current_line_after_cursor==' in :':
        return state.cursor_right(4)
    if keystroke=='backspace' and state.current_line_before_cursor.lstrip()=='for ' and state.current_line_after_cursor==' in :':
        return state.delete_before_cursor(len('for ')).delete(len(' in :'))
    if keystroke=='backspace' and state.current_line_before_cursor.lstrip().startswith('for ') and state.current_line_before_cursor.endswith(' in ') and state.current_line_after_cursor==':':
        return state.cursor_left(4)



@engine.add_rule
def i_to_import(state,keystroke):
    r"""
    Upon pressing space, 'i' or 'im' turns into 'import '
    |    ‹i›  space  ‹import ›
    ...
    |    ‹im›  space  ‹import ›

    SHOULD_FAIL! If the indent isn't 0, requires that we have at least 'im' (because i could also mean if, and people don't normally import in indented blocks)
    |    ‹    i›  space  ‹    import ›
    """

    prefix=state.current_line_before_cursor.lstrip()
    if keystroke==' ' and not state.current_line_after_cursor and (prefix=='im' or prefix=='i' and not state.leading_whitespace_in_current_line):
        return state.insert_text('import '[len(prefix):])

@engine.add_rule
def p_to_print(state,keystroke):
    r"""
    Upon pressing space, 'p' turns into print (assuming variable p doesn't exist)
    |    ‹p›  space  ‹print(¦)›
    """
    prefix=state.current_line_before_cursor.lstrip()
    if keystroke==' ' and prefix=='p' and not state.current_line_after_cursor:
        return state.insert_text('print()'[len(prefix):]).cursor_left()

@engine.add_rule
def import_as(state,keystroke):
    r"""
    Upon pressing space when doing imports, try to do "import x as y"
    |    ‹import thing›  space  ‹import thing as ›

    Integration test
    |    i ␣ n u m p y ␣ n p ‹import numpy as np›

    SHOULD_FAIL! Won't do anything if we haven't imported anything
    |    ‹import ¦› space ‹import  as ¦›
    """

    prefix=state.current_line_before_cursor.lstrip()
    if keystroke==' ' and prefix.startswith('import ') and not prefix.strip()=='import':
        return state.insert_text(' as ')

@engine.add_rule
def new_colon_block(state,keystroke):
    r"""
    Automatically adds the missing ':'
    |    ‹if›      space  ‹if ¦:›
    ...
    |    ‹while›   space  ‹while ¦:›
    ...
    |    ‹elif›    space  ‹elif ¦:›
    ...
    |    ‹with›    space  ‹with ¦:›
    ...
    |    ‹except›  space  ‹except ¦:›


    Enters the block in-line upon pressing space
    |    ‹if True ¦:›           space  ‹if True:¦›        
    ...
    |    ‹while True ¦:›        space  ‹while True:¦›     
    ...
    |    ‹elif True ¦:›         space  ‹elif True:¦›      
    ...
    |    ‹with thingy ¦:›       space  ‹with thingy:¦›    
    ...
    |    ‹except Exception ¦:›  space  ‹except Exception:¦›


    Backspace destroys the block header
    |    ‹if ¦:›       backspace  ‹›
    ...
    |    ‹while ¦:›    backspace  ‹›
    ...
    |    ‹elif ¦:›     backspace  ‹›
    ...
    |    ‹with ¦:›     backspace  ‹›
    ...
    |    ‹except ¦:›   backspace  ‹›
    """

    if keystroke==' ':
        keywords='if elif except with while'.split()
        prefix=state.current_line_before_cursor.lstrip()
        if prefix in keywords and not state.current_line_after_cursor:
            return state.insert_text(' :').cursor_left()
        if startswith_any(prefix,*keywords) and state.current_line_after_cursor==':' and state.char_before_cursor==' ':
            return state.delete_before_cursor().cursor_right()
    if keystroke=='backspace':
        keywords='if elif except with while'.split()
        prefix=state.current_line_before_cursor.lstrip()
        if prefix.endswith(' ') and prefix[:-1] in keywords and state.current_line_after_cursor==':':
            return state.delete_before_cursor(len(prefix)).delete()

@engine.add_rule
def backspace_through_colon(state,keystroke):
    """
    Backspace outside the block header enters it, for faster deletion
    |    ‹if True:¦›           backspace  ‹if True¦:›        
    ...
    |    ‹while True:¦›        backspace  ‹while True¦:›     
    ...
    |    ‹elif True:¦›         backspace  ‹elif True¦:›      
    ...
    |    ‹with thingy:¦›       backspace  ‹with thingy¦:›    
    ...
    |    ‹except Exception:¦›  backspace  ‹except Exception¦:›
    
    For functions and other things with parenthesis
    |    ‹def f():¦›  backspace  ‹def f(¦):›
    ...
    |    ‹if f(x):¦›  backspace  ‹if f(x¦):›
    """
    if keystroke=='backspace' and not state.current_line_after_cursor:
        if state.current_line_before_cursor.endswith('):'):
            return state.cursor_left(2)
        if state.current_line_before_cursor.endswith(':'):
            return state.cursor_left()

# def auto_pass(state,keystroke):

@engine.add_rule
def dot_equals(state,keystroke):
    r"""
    The .= operator activates upon pressing =
    |   ‹matrix.¦›   =  ‹matrix=matrix.¦›

    Integration test: The .= operator is good for numpy operations, for example
    |   ‹matrix¦› . = a b s ( ‹matrix=matrix.abs(¦)›
    
    SHOULD_FAIL! Index assignment and function calls are out of the scope of this rule
    |   ‹a[b.¦]›   =   ‹a[b=a[b.¦]›
    ...
    |   ‹f(x.¦)›   =   ‹f(x=f(x.¦)›

    Whitespace after the variable is OK
    |   ‹matrix.¦    ›   =   ‹matrix=matrix.¦    ›

    TODO: Allow comments in addition to whitespace, or anything after a semicolon - because these should be OK. With a better semantic understaning of python, a lot more can be done...

    SHOULD_FAIL! ...but if there's anything on this line after the cursor, it should not trigger this rule...
    |   ‹matrix.¦    thing›   =   ‹matrix=matrix.¦    thing›
    """

    if keystroke == '=' and state.char_before_cursor=='.' and not state.current_line_after_cursor.strip():
        return state.delete_before_cursor().insert_text('='+state.current_line_before_cursor.strip()[:-1]+'.')


@engine.add_rule
def semicolon_to_colon_slices(state,keystroke):
    r"""
    This rule saves you from having to reach for the shift key when specifying array slices...
    |    ‹a[¦]›   ;  ‹a[:¦]›

    Integration test: Especially useful for numpy...
    |    a [ ; , 1 * = 0    ‹a[:,1]*=0›
    """
    if keystroke==';' and state.char_after_cursor==']':
        return state.insert_text(':')


@engine.add_rule
def semicolon_arg_type(state,keystroke):
    r"""
    This rule saves you from having to reach for the shift key when specifying argument types in a function declaration...
    |    ‹def f(x¦):›    ;   ‹def f(x:¦):›

    Integration test
    |    d ␣ f ␣ x ; i n t    ‹def f(x:int¦):›
    """
    if keystroke==';' and state.current_line_before_cursor.lstrip().startswith('def ') and state.current_line_after_cursor=='):':
        return state.insert_text(':')


@engine.add_rule
def array_assignment(state,keystroke):
    r"""
    Easy setting index-values
    |    ‹array[i¦]›  = x  ‹array[i]=x¦›

    What happens, step by step...
    |    ‹array[i¦]›  =  ‹array[i=¦]›  x  ‹array[i]=x¦›

    SHOULD_FAIL! This shouldn't happen if we're using == or != as the index
    |    ‹array[i==¦]›  x  ‹array[i=]=x¦›
    ...
    |    ‹array[i!=¦]›  x  ‹array[i!]=x¦›

    Instead, this should happen...
    |    ‹array[i==¦]›  x  ‹array[i==x¦]›
    ...
    |    ‹array[i!=¦]›  x  ‹array[i!=x¦]›

    Nevertheless, this should still be possible...
    |    ‹array[a==b=¦]›  c  ‹array[a==b]=c¦›

    SHOULD_FAIL! This rule should not handle the dot_equals functionality - that's done in another rule
    |    ‹a[i.=¦]›   x   ‹a[i.]=x¦›

    Integration test
    |    a [ i = x   ‹a[i]=x›
    """
    if re.fullmatch(r'[A-Za-z_0-9]',keystroke) and state.char_before_cursor=='=' and not state.current_line_before_cursor.endswith('.=') and not state.current_line_before_cursor.endswith('==') and not state.current_line_before_cursor.endswith('!=') and state.current_line_after_cursor==']':
        return state.delete_before_cursor().cursor_end.insert_text('='+keystroke)

@engine.add_rule
def array_augmented_assignment(state,keystroke):
    r"""
    Similar to array_assignment, except it handles +=, -=, @=, *=, &=, ^=, %=, /=, etc
    |    ‹array[i¦]› + =  ‹array[i]+=¦›

    Works with -=, *=, %=, etc
    |    ‹array[i-¦]›  =  ‹array[i]-=¦›
    ...
    |    ‹array[i*¦]›  =  ‹array[i]*=¦›
    ...
    |    ‹array[i%¦]›  =  ‹array[i]%=¦›

    Also works with function calls, since += corresponds to the __iadd__ function, which can mutate objects like numpy arrays...
    |    ‹f(x¦)› + =  ‹f(x)+=¦›

    Integration test...note how we never needed to press the arrow keys to do any of this
    |    f ( x - = y   ‹f(x)-=y›

    Integration test...an application for numpy arrays
    |    a [ : 2 - = 1   ‹a[:2]-=1›
    """
    operators=set('+-*/%@&|^')
    if keystroke=='=' and state.char_before_cursor in operators and state.current_line_after_cursor in {')',']'}:
        return state.delete_before_cursor().cursor_end.insert_text(state.char_before_cursor+'=')
    

@engine.add_rule
def array_assignment_dot_equals(state,keystroke):
    r"""
    This rule is a natural combination of the array_assignment and dot_equals rules
    |    ‹array[i¦]›  . = x  ‹array[i]=array[i].x¦›

    Step by step...
    |    ‹array[i¦]›  . =    ‹array[i.=¦]›  x  ‹array[i]=array[i].x¦›
    """
    if re.fullmatch(r'[A-Za-z_0-9]',keystroke) and state.current_line_before_cursor.endswith('.=') and state.current_line_after_cursor==']':
        return state.delete_before_cursor(2).cursor_end.insert_text('='+state.current_line_before_cursor.strip()[:-2]+'].'+keystroke)
    

@engine.add_rule
def f_to_for_in_if(state,keystroke):
    r"""
    List and set comprehensions
    |    ‹[x ¦]›   f   ‹[x for ¦ in]›   x ␣ y   ‹[x for x in y¦]›   ␣ i f x  ‹[x for x in y if x¦]›
    ...
    |    ‹{x ¦}›   f   ‹{x for ¦ in}›   x ␣ y   ‹{x for x in y¦}›   ␣ i f x  ‹{x for x in y if x¦}›
    
    Backspacing the list comprehension
    |    ‹[x for ¦ in]›          backspace   ‹[x¦]›
    ...
    |    ‹[x for x in ¦]›        backspace   ‹[x for x¦ in]›
    ...
    |    ‹[x for x in y if ¦]›   backspace   ‹[x for x in y¦]›

    """
    if keystroke=='f' and state.char_before_cursor==' ' and state.char_after_cursor in set(']})'):
        return state.insert_text('for  in').cursor_left(3)
    if keystroke==' ' and startswith_any(state.current_line_after_cursor,' in]',' in}',' in)'):
        return state.cursor_right(3).insert_text(' ')
    if keystroke=='backspace' and state.current_line_before_cursor.endswith(' for ') and startswith_any(state.current_line_after_cursor,' in]',' in}',' in)'):
        return state.delete_before_cursor(len(' for ')).delete(len(' in'))
    if keystroke=='backspace' and state.current_line_before_cursor.endswith(' in ') and state.char_after_cursor in set(']})'):
        return state.delete_before_cursor().cursor_left(len(' in'))
    if keystroke=='f' and state.current_line_before_cursor.endswith(' i') and state.char_after_cursor in set(']})'):
        return state.insert_text('f ')
    if keystroke=='backspace' and state.current_line_before_cursor.endswith(' if ') and state.char_after_cursor in set(']})'):
        return state.delete_before_cursor(len(' if '))

@engine.add_rule
def backspace_whitespace(state,keystroke):
    if keystroke=='backspace' and state.leading_whitespace_in_current_line==state.current_line_before_cursor:
        return state.delete_before_cursor(len(state.leading_whitespace_in_current_line)).delete_before_cursor()

@engine.add_rule
def unindent(state,keystroke):
    if keystroke=='shift_tab':
        prefix=state.current_line_before_cursor.lstrip()
        whitespace=state.leading_whitespace_in_current_line
        return state.delete_before_cursor(len(state.current_line_before_cursor)).insert_text(whitespace[4:]+prefix)

###############NORMAL RULES

@engine.add_rule
def cursor_right(state,keystroke):
    return process_simple_arrow_key(state,keystroke)

@engine.add_rule
def cursor_left(state,keystroke):
    return process_simple_arrow_key(state,keystroke)

@engine.add_rule
def cursor_up(state,keystroke):
    return process_simple_arrow_key(state,keystroke)

@engine.add_rule
def cursor_down(state,keystroke):
    return process_simple_arrow_key(state,keystroke)
@engine.add_rule
def preserve_indent(state,keystroke):
    r"""
    Hitting enter can preserve the indent
    |   ‹def f():›               ‹def f():›
    |   ‹    print()¦›   enter   ‹    print()›
    |                            ‹    ¦›

    SHOULD_FAIL! Hitting enter doesn't simple go to the beginning of the line with this rule
    |   ‹def f():›               ‹def f():›
    |   ‹    print()¦›   enter   ‹    print()›
    |                            ‹¦›
    """
    if keystroke=='\n' and not state.current_line_after_cursor:
        return state.insert_text('\n'+state.leading_whitespace_in_current_line)


@engine.add_rule
def backspace(state,keystroke):
    r"""
    Pressing the delete key deletes the character before the cursor
    |   ‹abc¦def›   backspace  ‹ab¦def›   backspace   ‹a¦def›  backspace  ‹¦def›

    Pressing the delete key deletes the character before the cursor
    |   ‹abc¦def›   backspace  backspace ‹a¦def›

    Deleting doesn't do anything when there are no characters before the cursor
    |   ‹¦abc›   backspace   ‹¦abc›
    """
    if keystroke=='backspace':
        return state.delete_before_cursor()

@engine.add_rule
def delete(state,keystroke):
    r"""
    Pressing the delete key deletes the character after the cursor
    |   ‹abc¦def›   delete   ‹abc¦ef›   delete   ‹abc¦f›  delete  ‹abc¦›

    Deleting doesn't do anything when there are no characters after the cursor
    |   ‹abc¦›   delete   ‹abc¦›
    """
    if keystroke=='delete':
        return state.delete()

@engine.add_rule
def insert_character(state,keystroke):
    r"""
    Typing letters
    |    H e l l o ␣ W o r l d ‹Hello World›

    """

    if len(keystroke)==1:
        return state.insert_text(keystroke)

@engine.add_rule
def integration_tests(state,keystroke):
    r"""
    This rule doesn't do actually anything, it's just here for testing purposes
    
    ...
    |   d ␣ f ␣ x ␣ y ␣ z enter ‹def f(x,y,z):›
    |                           ‹    ¦›
    ...
    |                                                             ‹def f(x:int)->int:›
    |   d ␣ f ␣ x ; i n t right i n t enter x + + enter r ␣ x     ‹    x+=1›
    |                                                             ‹    return x¦›
    ...
    |   ‹def f(¦):›   right   ‹def f()->¦:›   right    ‹def f():¦›
    ...
    |                             ‹def _():›
    |   d enter d enter d enter   ‹    def _():›
    |                             ‹        def _():›
    |                             ‹            ¦›
    ...
    |   x [ i + +     ‹x[i]+=1›
    ...
    |   x [ i = y     ‹x[i]=y›
    ...
    |   x . = y       ‹x=x.y›
    ...
    |   [ x ␣ f x ␣ y ␣ i f x    ‹[x for x in y if x¦]›
    ...
    |   i ␣ n u m p y ␣ n p   ‹import numpy as np›
    ...
    |                                               ‹def f(x):›
    |   d ␣ f ␣ x ↵ f ␣ y ␣ x ↵ i f ␣ y ↵ p ␣ y     ‹    for y in x:›
    |                                               ‹        if y:›
    |                                               ‹            print(y¦)›


    BELOW: Behaviours that can be implemented in the future. Most of these probably fail right now. All of these things currently work in rp.

    TODO: Get rid of the ->
    |   ‹def f()->¦:›  enter   ‹def f():›
    |                          ‹    ¦›

    SHOULD_FAIL! TODO: Detect if we're in a string before applying rules
    |   ‹'''›           ‹'''› 
    |   ‹d¦›     space  ‹def ¦():›  
    |   ‹'''›           ‹'''› 

    SHOULD_FAIL! It's not really important whether this fails or not, because "return x++" is invalid syntax anyway, but then again so is "return x+=1"
    |   ‹def f():›                ‹def f():›        
    |   ‹    return x+¦›    +     ‹    return x+=1¦›

    SHOULD_FAIL! It would be better if 'f' made 'if', because what it currently does is invalid syntax
    |   ‹[x for x in y ¦]›    f    ‹[x for x in y for ¦ in]›

    """
    pass



keystroke_translations={
    '\x1b[A' :'up',
    '\x1b[B' :'down',
    '\x1b[D' :'left',
    '\x1b[C' :'right',
    '\x7f'   :'backspace',
    '\x1b[3~':'delete',
    '\x1b'   :'escape',
    '\x1b[Z' :'shift_tab',
    '\r'     :'\n',
    '\x03'   :'^c',
    '\x1a'   :'^z',
}

keystroke_testing_translations={
    'enter':'\n',
    'space':' ',
    '␣':' ',
    '↵':'\n',
    'tab':'\t',
}

negation_prefix='SHOULD_FAIL' #Add this to the beginning of a rule doc if we WANT it to fail
ditto_header='...' #Add this to the beginning of a rule doc if we WANT it to fail


def _get_groups(ans:str):
    #ans=r"""
        #Gets rid of comma
        #|   ‹def f(x,¦):›   enter   ‹def f(x):›
        #|                           ‹    ¦›
    #
        #Works with no trailing comma too
        #|   ‹def f(x¦):›    enter    ‹def f(x):›
        #|                            ‹    ¦›
        #"""
    ans=ans.splitlines()
    ans=ans[::-1]
    groups=[]
    group=[]
    for x in ans:
        if not x.strip():
            continue
        x=x.strip()
        if x.startswith('|'):
            group.append(x)
        else:
            group.append(x)
            groups.append(line_join(group[::-1]))
            group.clear()
    ans=groups
    return ans
def _tokenize(line):
    #EXAMPLE:
    #     >>> _tokenize('  |  ‹def f(x,¦):›   enter   ‹def f(x):›')
    #    ans = [('‹def f(x¦):›', 'state', 0), ('    ', 'whitespace', 12), ('enter', 'keystroke', 16), ('    ', 'whitespace', 21), ('‹def f(x):›', 'state', 25)]
    line=line.strip()
    if line.startswith('|'):
        line=line[1:]
    #line=line.strip()
    import re
    regex=re.compile(r'([^‹›\s]+)|(‹[^‹›]*›)|(\s+)')
    ans=regex.findall(line)
    c=0
    o=[]
    for x in ans:
        s=''.join(x)
        w={0:'keystroke',1:'state',2:'whitespace'}[max_valued_index(x)]
        o.append((s,w,c))
        c+=len(s)
    return o
def _get_keystroke_indices(group):
    out=set()
    for line in line_split(group)[1:]:
        out|={index for text,type,index in _tokenize(line) if type=='keystroke'}
    return sorted(out)
def _get_states(group):
    #EXAMPLE:
    #    >>> _get_states("""    Gets rid of comma
    #      2     |   ‹def f(x,¦):›   enter   ‹def f(x):›  chump  ‹bagger›
    #      3     |                           ‹    ¦›             ‹dagger›""")
    #   ic| regions: [(0, 19), (19, 40), (40, 999999)]
    #   ans = ['‹def f(x,¦):›', '‹def f(x):›\n‹    ¦›', '‹bagger›\n‹dagger›']
    states=[]
    keystroke_indices=sorted(set(_get_keystroke_indices(group))|{0,999999})
    body_lines=line_split(group)[1:]
    regions= list(zip(keystroke_indices[:-1],keystroke_indices[1:]))
    # ic(regions)
    for index_start,index_end in regions:
        state_lines=[]
        for line in body_lines:
            tokens=_tokenize(line)
            state_line=''.join([text for text,type,index in tokens if type=='state' and index_start<=index<index_end])
            state_line=state_line.strip()
            if state_line:
                state_lines.append(state_line)
        states.append(line_join(state_lines))

    def _process_state(ans):
        #Raw state is like  '‹bagger›\n‹dagger›'
        ans=line_split(ans)
        ans=[x.strip() for x in ans]
        ans=[x[1:-1] for x in ans]
        ans=line_join(ans)
        cursor_index=ans.find('¦')
        ans=ans.replace('¦','')
        from prompt_toolkit.document import Document
        output=Document(ans,cursor_index)
        return output
    return list(map(_process_state,states))
def _get_keystrokes(group):
    out=set()
    for line in line_split(group)[1:]:
        out|={(index,text) for text,type,index in _tokenize(line) if type=='keystroke'}
    return [x[1] for x in sorted(out)]
def _get_tests(group):
    states=_get_states(group)
    keystrokes=_get_keystrokes(group)
    return _merge_tests(list(zip(states[:-1],keystrokes,states[1:])))

def _run_engine_test(engine,test)->bool:
    before_state,keystrokes,after_state=test
    new_state=before_state
    for keystroke in keystrokes.split():
        if keystroke in keystroke_testing_translations:
            keystroke=keystroke_testing_translations[keystroke]
        new_state=engine.process(new_state,keystroke)
    return after_state==new_state
def _test_group(engine,group)->bool:
    return all(_run_engine_test(engine,test) for test in _get_tests(group))

def _merge_tests(tests):
    #EXAMPLE:
    #        ans = [(Document('', -1), 'backspace', Document('', -1)), (Document('', -1), 'backspace', Document('abdef', 2)), (Document('abdef', 2), 'backspace', Document('adef', 1)), (Document('adef', 1), 'backspace', Document('def', 0))]
    #     >>> _merge_tests(ans)
    #    ans = [[Document('', -1), 'backspace backspace', Document('abdef', 2)], [Document('abdef', 2), 'backspace', Document('adef', 1)], [Document('adef', 1), 'backspace', Document('def', 0)]]
    tests=list(map(list,tests))
    nulldoc=Document('', -1)
    def index_pairs(l):
        # 2 -> [(0, 1), (1, 2)]
        return zip(range(l-1),range(1,l))
    for _ in range(len(tests)):
        for x,y in index_pairs(len(tests)):
            if tests[x][-1]==tests[y][0]==nulldoc:
                tests[x][1]+=' '+tests[y][1]
                tests[x][2]=tests[y][2]
                del tests[y]
                break
    if tests and tests[0][0]==nulldoc:
        tests[0][0]=Document('',0)
    for test in tests:
        for x in test:
            if isinstance(x,Document) and x.cursor_position==-1:
                x._cursor_position=max(0,len(x.text))

    return tests


def run_all_engine_tests(engine):
    print("Running Tests")
    for i,rule in enumerate(engine.rules):
        if hasattr(rule,'__doc__') and isinstance(rule.__doc__,str):
            print()
            fansi_print("RULE #%i: "%i+ rule.__name__,'magenta','bold')
            should_fail=False #This the default incase the first group header is "..."
            for group in _get_groups(rule.__doc__)[::-1]:
                group_title=group.splitlines()[0].strip()
                group_body='\n'.join(group.splitlines()[1:])
                if group_title!=ditto_header: #This means to continue from the previous title
                    print()
                if group_body.strip()=='':
                    fansi_print(indentify(group_title),'blue') #It's a comment
                    continue
                fansi_print(indentify(group_title),'yellow','bold')
                fansi_print(indentify(group_body),'yellow')
                passed=_test_group(engine,group)
                if group_title!=ditto_header:
                    should_fail=group.splitlines()[0].strip().startswith(negation_prefix)

                if passed:
                    print('  '+fansi(indentify(('BAD: ' if should_fail else 'GOOD: ') + 'PASSED'),'red' if should_fail else 'green','bold'))
                else:
                    print('  '+fansi(indentify(('GOOD: ' if should_fail else 'BAD: ') + 'FAILED'),'green' if should_fail else 'red','bold'))


engine.run_all_tests()


state=Document()
def test_engine(engine):
    global state
    while True:
        keystroke=input_keypress()
        if keystroke=='q':
            break
        if keystroke in keystroke_translations:
            keystroke=keystroke_translations[keystroke]
        fansi_print("========================================================",'magenta','bold')
        fansi_print("Processing "+keystroke,'magenta')
        state=engine.process(state,keystroke)
        # fansi_print("-----------------------------------",'magenta')
        print(state.debug_view)

print("Start typing code into the terminal, and press q when your're done.")
test_engine(engine)



#Having the engine able to call itself recursively is a blessing that rp doesn't have. It makes augmented array assignment much simpler, for example.
#Being able to debug when things fail with unit tests and explanations of exactly what happens each time you press a character is also very useful.
#It also opens the door to using these microcompletions on apps over sockets, instead of being bound to the terminal
#When you count the shift key as a keypress, the number of keypresses saved is much more apparent. Not that its not allready...
#Also keep in mind that holding down a key is easier than switching between multiple keys, that the spacebar is the easiest key to press, etc...
