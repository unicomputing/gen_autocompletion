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

@add_document_property
def get_callable_names(self)->set[str]:
    #Returns the set of all callables in the current namespace
    #Right now this is more of an educated guess than anything else, since we don't have access to the python runtime
    import builtins
    output=set()
    output|=set(dir(builtins)) #int, list, etc are all functions and classes
    output|={name[:-1] for name in re.findall(r'\w+[\(]',self.text)} #If anywhere in our code we treat some name like a function (for example, if "flibber()" is somewhere in our code), then we assume that flibber is a function
    return output

@add_document_property
def python_tokens(self)->list:
    return split_python_tokens(self.text)

@add_document_property
def namespace(self)->set[str]:
    #Returns the set of all names in the current namespace
    #Right now this is more of an educated guess than anything else, since we don't have access to the python runtime
    import builtins
    output=set()
    output|=set(dir(builtins)) #int, list, etc are all functions and classes
    output|=set(self.delete_before_cursor(len(self.get_word_before_cursor())).python_tokens)
    return output


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

    def process(self,state:Document,*keystrokes:str,debug=False)->Document:
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
def space_to_function_call(state,keystroke):
    r"""
    Instead of pressing '(' to call a function, which you need the shift key for, you can use the spacebar
    |    ‹def f():›                 ‹def f():›    
    |    ‹    print(x)›    space    ‹    print(x)›
    |    ‹f¦›                       ‹f(¦)›        

    SHOULD_FAIL! If the word before the cursor is not a function, this rule should not be triggered
    |    ‹g¦›   space   ‹g(¦)›       

    SHOULD_FAIL! If we're declaring a function, we shouldn't treat it like a function call; def_to_args should take priority.
    |    ‹def f():pass›             ‹def f():pass›    
    |    ‹def f¦():›       space    ‹def f¦():›

    """
    if keystroke==' ':
        if state.get_word_before_cursor() in state.get_callable_names:
            return state.insert_text('()').cursor_left()

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

    SHOULD_FAIL! This shouldn't happen if d is a function, because space_to_function_call should take priority
    |   ‹def d():pass›           ‹def d():pass›
    |   ‹d¦›             space   ‹def ¦():›
    """
    if keystroke in ' \n' and state.current_line_before_cursor.lstrip()=='d' and not state.current_line_after_cursor:
        if keystroke==' ':
            return state.insert_text('ef ():').cursor_left(3)
        elif keystroke=='\n':
            return state.insert_text('ef _():\n'+state.leading_whitespace_in_current_line+'    ')

@engine.add_rule
def while_true(state,keystroke):
    """
    Default while loop
    |   ‹w›  enter  ‹while True:›
    |               ‹    ¦›
    ...
    |   ‹while ¦:›  enter  ‹while True:›
    |                      ‹    ¦›
    ...
    |   ‹while True:¦›  backspace  ‹while ¦:›

    """
    if keystroke=='\n' and state.current_line_before_cursor.lstrip()=='w':
        return engine.process(state.insert_text('hile True:'),'\n')
    if keystroke=='\n' and state.current_line_before_cursor.lstrip()=='while ' and state.current_line_after_cursor==':':
        return engine.process(state.insert_text('True'),'\n')
    if keystroke=='backspace' and state.current_line_before_cursor.endswith('while True:'):
        return state.cursor_left().delete_before_cursor(len('True'))

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
def enter_to_next_line(state,keystroke):
    r"""
    You don't always have to put your cursor to the end of the line before hitting the enter key.
    |    ‹def f():›                          ‹def f():›      
    |    ‹    print(x¦)›    enter            ‹    print(x)› 
    |                                        ‹    ¦›

    Notice how you can do the same thing while using the right arrow key:
    |    ‹def f():›                          ‹def f():›      
    |    ‹    print(x¦)›    enter   right    ‹    print(x)› 
    |                                        ‹    ¦›

    SHOULD_FAIL! This is what it would do without this completion:
    |    ‹def f():›                   ‹def f():›      
    |    ‹    print(x¦)›    enter     ‹    print(x› 
    |                                 ‹¦)›

    Integration test
    |                            ‹print(x)›
    |    p ␣ x ↵ p ␣ y ↵ p ␣ z   ‹print(y)›
    |                            ‹print(z¦)›

    Integration test: Should work on return, playing well with exit_block_on_enter
    |    ‹def f():›                  ‹def f():›       
    |    ‹    return g(¦)›   enter   ‹    return g()›
    |                                ‹¦›

    """
    if keystroke=='\n' and state.current_line_after_cursor and set(state.current_line_after_cursor)<=set(')]}'):
        return engine.process(state.cursor_end,'\n')


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

    Same with break and continue
    |   ‹while f():›                ‹while f():›      
    |   ‹    break¦›      enter     ‹    break›  
    |                               ‹¦›
    ... 
    |   ‹while f():›                ‹while f():›      
    |   ‹    continue¦›   enter     ‹    continue›  
    |                               ‹¦›
    """
    keywords='return break continue'.split()
    if keystroke=='\n':
        prefix=state.current_line_before_cursor.lstrip()
        if prefix in keywords or prefix.startswith('return '):
            whitespace=state.leading_whitespace_in_current_line
            desired_whitespace=whitespace[:-4]
            return state.insert_text('\n'+desired_whitespace)

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
def call_eight_to_vararg(state,keystroke):
    r"""
    Saves you from having to press the shift during function calls
    |   ‹print(x,¦)›     8 y     ‹print(x,*y¦)›
    ...
    |   ‹print(¦)›       8 x     ‹print(*x¦)›
    ...
    |   ‹print(x,¦)›     8 8 y     ‹print(x,**y¦)›
    ...
    |   ‹print(¦)›       8 8 x     ‹print(**x¦)›

    Here's how it works, step by step:
    |   ‹print(x,¦)›     8     ‹print(x,8¦)›     y   ‹print(x,*y¦)›
    ...
    |   ‹print(x,¦)›     8 8   ‹print(x,88¦)›    y   ‹print(x,**y¦)›
    """
    if re.fullmatch(r'[A-Za-z_\"\'\(\[\{]',keystroke) and state.char_after_cursor==')':
        if endswith_any(state.current_line_before_cursor,',8','(8'):
            return state.delete_before_cursor( ).insert_text('*'+keystroke)
        if endswith_any(state.current_line_before_cursor,',88','(88'):
            return state.delete_before_cursor(2).insert_text('**'+keystroke)



@engine.add_rule 
def if_else_inline(state,keystroke):
    """
    If/else on space
    |    ‹x=y if¦›    space   ‹x=y if ¦ else›    y space    ‹x=y if y else ¦›
    ...
    |    ‹[x if¦]›    space   ‹[x if ¦ else]›    y space    ‹[x if y else ¦]›

    If/else on backspace
    |    ‹[x if y else ¦]›    backspace    ‹[x if ¦ else]›    backspace    ‹[x¦]›
    """
    #Todo: If we can detect that we're in a list comprehension, we can trigger this upon pressing 'f' (like we do in rp)
    if keystroke==' ':
        if state.current_line_before_cursor.endswith(' if') and state.current_line_before_cursor[-2:].strip():
            return state.insert_text('  else').cursor_left(len(' else'))
        if state.current_line_after_cursor.rstrip()==' else' or startswith_any(state.current_line_after_cursor,' else]',' else)',' else}',' else,',' else:',' else;',' else#'):
            return state.cursor_right(len(' else')).insert_text(' ')


@engine.add_rule
def uncomma_binary_keyword(state,keystroke):
    """
    This rule should come before space_to_function_arg
    |    ‹print(x,and¦)›    space   ‹print(x and ¦)›
    """
    if keystroke==' ':
        keywords='is and or if for'.split()
        for keyword in keywords:
            if state.current_line_before_cursor.endswith(','+keyword):
                return state.delete_before_cursor(len(','+keyword)).insert_text(' '+keyword+' ')    

@engine.add_rule
def space_to_function_arg(state,keystroke):
    r"""
    You can use the spacebar instead of the comma key
    |    ‹max(¦)›   ␣   ‹max ¦›
    ...
    |    ‹max(x¦)›   ␣   ‹max(x,¦)›
    ...
    |    ‹max(x,¦)›   ␣   ‹max(x)¦›
    ...
    |    ‹max(x,min¦)›   ␣   ‹max(x,min(¦))›
    ...
    |    ‹map(int¦)›   ␣   ‹map(int(¦))›   ␣   ‹map(int,¦)›
    ...
    |    ‹zip(map(x,y¦))›   ␣   ‹zip(map(x,y,¦))›   ␣   ‹zip(map(x,y),¦)›  z ␣   ‹zip(map(x,y),z,¦)›  ␣  ‹zip(map(x,y),z)¦›

    Integration test
    |    ‹def f():pass›                                  ‹def f():pass›
    |    ‹¦›               f ␣ f ␣ a ␣ b ␣ ␣ f ␣ c ␣ d   ‹f(f(a,b),f(c,d¦))›
    """
    if keystroke==' ':
        if state.char_before_cursor=='(':
            if state.current_line_after_cursor.startswith('))'):
                return state.delete_before_cursor().delete().insert_text(',')
            if  state.char_after_cursor==')':
                return state.delete_before_cursor().delete().insert_text(' ')
        if state.char_after_cursor==')':
            if state.char_before_cursor==',':
                if state.current_line_after_cursor.startswith('))'):
                    return state.delete_before_cursor().cursor_right().insert_text(',')
                return state.delete_before_cursor().cursor_right()
            return state.insert_text(',')

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
def backspace_through_bracket(state,keystroke):
    """
    Backspacing through brackets can be faster than just backspacing the bracket because of backspace_matching_bracket
    |    ‹f(x)¦›   backspace  ‹f(¦)›
    ...
    |    ‹f((x))¦›   backspace  ‹f((¦))›
    
    Integration test with backspace_matching_bracket
    |    ‹[[1],[2]]¦›   ⌫   ‹[[1],[¦]]›   ⌫ ⌫  ‹[[1]¦]›  ⌫   ‹[[¦]]›   ⌫   ‹[¦]›   ⌫   ‹¦› 
    """
    if keystroke=='backspace' and state.char_before_cursor in set('])}'):
        while state.char_before_cursor in set('])}'):
            state=state.cursor_left()
        return engine.process(state,'backspace')

# @engine.add_rule
# def backspace_into_def(state,keystroke):
#     """
#     Don't backspace the :, its not useful to do that. Backspace what's inside instead, and this will save time.
#     |    ‹def f(x):¦›   backspace  ‹def f(¦):›
#     """
#     if keystroke=='backspace' and not state.current_line_after_cursor and state.current_line_before_cursor.endswith('):') and startswith_any(state.current_line_before_cursor.lstrip(),'def '):
#         return engine.process(state.cursor_left(2),'backspace')

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
        return engine.process(state,'=','1')

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
    ...
    |    ‹for›  space   ‹for ¦ in :›

    Backspacing for loops
    |    ‹for ¦ in :›   backspace   ‹›
    ...
    |    ‹for x in ¦:›   backspace   ‹for x¦ in :›
    """

    valid_prefixes='f fo for'.split()
    prefix=state.current_line_before_cursor.lstrip()
    if prefix in state.namespace:
        return
    if keystroke==' ' and not state.current_line_after_cursor and prefix in valid_prefixes:
        return state.insert_text('for  in :'[len(prefix):]).cursor_left(len(' in :'))
    if keystroke==' ' and state.current_line_after_cursor==' in :':
        return state.cursor_right(4)
    if keystroke=='backspace' and state.current_line_before_cursor.lstrip()=='for ' and state.current_line_after_cursor==' in :':
        return state.delete_before_cursor(len('for ')).delete(len(' in :'))
    if keystroke=='backspace' and state.current_line_before_cursor.lstrip().startswith('for ') and state.current_line_before_cursor.endswith(' in ') and state.current_line_after_cursor==':':
        return state.cursor_left(4)

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


@engine.add_rule
def backspace_keyword_space(state,keystroke):
    """
    Backspacing a space after a keyword deletes the whole keyword in one stroke
    |    ‹import ¦›  backspace  ‹›
    ...
    |    ‹a=b and ¦› backspace ‹a=b ¦›
    ...
    |    ‹a=b is ¦› backspace ‹a=b ¦›
    ...
    ‹def f():›                   ‹def f():›
    ‹    global ¦›  backspace    ‹    ¦›
    ...
    ‹def f():›                   ‹def f():›
    ‹    global ¦›  backspace    ‹    ¦›
    """
    keywords="and as assert break class continue def del elif else except False finally for from global if import in is lambda None nonlocal not or pass raise return True try while with yield".split()
    if keystroke=='backspace' and state.char_before_cursor==' ':
        state=state.delete_before_cursor()
        word=state.get_word_before_cursor()
        if word in keywords:
            state=state.delete_before_cursor(len(word))
            return state

def get_all_word_prefixes(word):
    output=[]
    for i in range(len(word)):
        output.append(word[:i+1])
    return output

@engine.add_rule #This rule is now obsolete because of space_to_keyword
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
def space_to_keyword(state,keystroke):
    """
    ...
    |    ‹t¦›     space   ‹try:¦›
    ...
    |    ‹a¦›     space   ‹assert ¦›
    ...
    |    ‹g¦›     space   ‹global ¦›
    ...
    |    ‹n¦›     space   ‹nonlocal ¦›
    ...
    |    ‹i¦›     space   ‹import ¦›
    ...
    |    ‹y¦›     space   ‹yield ¦›
    ...
    |    ‹w¦›     space   ‹while ¦:›
    ...
    |    ‹if¦›     space   ‹if ¦:›
    ...
    |    ‹pa¦›    space   ‹pass¦›
    ...
    |    ‹co¦›    space   ‹continue¦›
    ...
    |    ‹while True:›          ‹while True:›
    |    ‹    bre¦›     space   ‹    break¦›
    ...
    |    ‹tr¦›    space   ‹try:¦›
    ...
    |    ‹try¦›   space   ‹try:¦›
    ...
    |    ‹as¦›    space   ‹assert ¦›
    ...
    |    ‹del¦›    space   ‹del ¦›
    ...
    |    ‹ra¦›    space   ‹raise ¦›
    """
    #Higher priority keywords come first in the list
    if keystroke==' ':
        keywords=['if :','elif :','while :']+"else: except: finally: try: assert break continue del global import nonlocal pass return raise yield".split()
        no_space='break continue pass'.split()
        full_words={}
        for keyword in keywords[::-1]:
            for prefix in get_all_word_prefixes(keyword):
                full_words[prefix]=keyword
        prefix=state.current_line_before_cursor.lstrip()

        if prefix in full_words:
            state=state.delete_before_cursor(len(prefix)).insert_text(full_words[prefix])
            if not full_words[prefix].endswith(':') and not full_words[prefix] in no_space:
                state=state.insert_text(' ')
            if full_words[prefix].endswith(' :'):
                state=state.cursor_left()
            return state

@engine.add_rule
def space_enter_to_keyword_colon(state,keystroke):
    if keystroke in '\n ':
        keywords="else: except: finally: try:".split()
        full_words={}
        for keyword in keywords[::-1]:
            for prefix in get_all_word_prefixes(keyword):
                full_words[prefix]=keyword
        prefix=state.current_line_before_cursor.lstrip()

        if prefix in full_words:
            state=state.delete_before_cursor(len(prefix)).insert_text(full_words[prefix])
            if keystroke=='\n':
                return engine.process(state,'\n')

@engine.add_rule
def backspace_keyword_colon(state,keystroke):
    """
    Backspacing a keyword with just a colon deletes both
    |    ‹if True:pass›               ‹if True:pass›  
    |    ‹else:¦›         backspace   ‹¦›
    ...
    |    ‹try:¦›   backspace   ‹¦›
    """
    keywords="else: except: finally: try:".split()
    prefix=state.current_line_before_cursor.lstrip()
    if keystroke=='backspace' and prefix in keywords:
        return state.delete_before_cursor(len(prefix))

@engine.add_rule
def unindent_on_enter(state,keystroke):
    """
    If on a blank line, unindent
    |    ‹def f():›                  ‹def f():›    
    |    ‹    if True:›    enter     ‹    if True:›
    |    ‹        pass›              ‹        pass›
    |    ‹        ¦›                 ‹    ¦›   
    """
    if keystroke=='\n' and state.current_line and not state.current_line.strip():
        return engine.process(state,'shift_tab')





# @engine.add_rule #This rule is now obsolete because of space_to_keyword
# def r_to_return(state,keystroke):
#     r"""
#     TODO: Add the ability for this rule to detect if the cursor is currently in a function, like rp does
#     TODO: When r is a variable, don't turn r into return when pressing the spacebar
#     Adds the return keyword.
#     |   ‹def f(x):›    space    ‹def f(x):›
#     |   ‹    r¦›                ‹    return ¦›
#     Also works with the enter key to return nothing
#     |   ‹def f(x):›             ‹def f(x):›
#     |   ‹    r¦›       enter    ‹    return›
#     |                           ‹¦›
#     ...
#     |   ‹def f(x):›             ‹def f(x):›           
#     |   ‹    if x:›    enter    ‹    if x:›           
#     |   ‹        r¦›            ‹        return›
#     |                           ‹    ¦›           
#     Getting rid of return
#     |   ‹def f(x):›      backspace    ‹def f(x):›
#     |   ‹    return ¦›                ‹    ¦›
#     ...
#     |   ‹def f(x):›      backspace    ‹def f(x):›
#     |   ‹    return¦›                 ‹    ¦›
#     Integration test
#     |   d ␣ f ␣ x enter r ␣ x   ‹def f(x):›
#     |                           ‹    return x¦›
#     """
#     if keystroke in '\n ' and state.current_line_before_cursor.lstrip()=='r' and not state.current_line_after_cursor:
#         return engine.process(state.insert_text('eturn'),keystroke)
#     if keystroke=='backspace' and state.current_line_before_cursor.strip()=='return':
#         return state.delete_before_cursor(len(state.current_line_before_cursor)).insert_text(state.leading_whitespace_in_current_line)


@engine.add_rule
def backspace_through_colon(state,keystroke):
    """
    Backspace outside the block header enters it, for faster deletion
    |    ‹if condition:¦›           backspace  ‹if conditio¦:›        
    ...
    |    ‹while condition:¦›        backspace  ‹while conditio¦:›     
    ...
    |    ‹elif condition:¦›         backspace  ‹elif conditio¦:›      
    ...
    |    ‹with thingy:¦›       backspace  ‹with thing¦:›    
    ...
    |    ‹except Exception:¦›  backspace  ‹except Exceptio¦:›
    
    For functions and other things with parenthesis
    |    ‹def f():¦›  backspace  ‹def ¦():›
    ...
    |    ‹if f(x):¦›  backspace  ‹if f(¦):›
    """
    if keystroke=='backspace' and not state.current_line_after_cursor:
        if state.current_line_before_cursor.endswith('):'):
            return engine.process(state.cursor_left(2),'backspace')
        if state.current_line_before_cursor.endswith(':'):
            return engine.process(state.cursor_left(),'backspace')

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
    |                                               ‹def g(x):›
    |   d ␣ g ␣ x ↵ f ␣ y ␣ x ↵ i ␣ y ↵ p ␣ y     ‹    for y in x:›
    |                                               ‹        if y:›
    |                                               ‹            print(y¦)›
    ...
    |  ‹if x[7]:¦›   ⌫   ‹if x[¦]:›   ⌫   ‹if x¦:›   ⌫   ‹if ¦:›   ⌫   ‹¦›
    ...
    |                                       ‹def f(x):›
    |  d ␣ f ␣ x ↵ w ␣ x ↵ p ␣ x ↵ x - -    ‹    while x:›
    |                                       ‹        print(x)›
    |                                       ‹        x-=1¦›
    ...
    |  l i s t ␣ m a p ␣ i n t ␣ ␣ x     ‹list(map(int,x¦))›

    Fibbonacci
    |                                                                     ‹def f(x):›
    |  d ␣ f ␣ x ↵ i ␣ x < 2 ↵ r ␣ 1 ↵ r ␣ f ␣ x - 1 ␣ ␣ + f ␣ x - 2      ‹    if x<2:›
    |                                                                     ‹        return 1›
    |                                                                     ‹    return f(x-1)+f(x-2¦)›

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

    TODO: Make space_to_function_call and def_to_args play together more nicely
    |   ‹def f(x=print¦):›    space    ‹def f(x=print(¦)):›


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
    '⌫':'backspace'
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
        new_state=engine.process(new_state,keystroke,debug=True)
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
        state=engine.process(state,keystroke,debug=True)
        # fansi_print("-----------------------------------",'magenta')
        print(state.debug_view)

print("Start typing code into the terminal, and press q when your're done.")
test_engine(engine)



#Having the engine able to call itself recursively is a blessing that rp doesn't have. It makes augmented array assignment much simpler, for example.
#Being able to debug when things fail with unit tests and explanations of exactly what happens each time you press a character is also very useful.
#It also opens the door to using these microcompletions on apps over sockets, instead of being bound to the terminal
#When you count the shift key as a keypress, the number of keypresses saved is much more apparent. Not that its not allready...
#Also keep in mind that holding down a key is easier than switching between multiple keys, that the spacebar is the easiest key to press, etc...
