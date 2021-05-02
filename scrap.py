#Don't mind this python file, this is just for my own reference when writing some of the completions. It outlines methods specified by the Document and Buffer classes from prompt_toolkit.

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
