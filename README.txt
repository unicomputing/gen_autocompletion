Ryan Burgert CSE526 Final Project

This project demonstrates a new way to write python code, using what I call "microcompletions". Microcompletions are a set of behaviours that a text editor can implement to make writing code more efficient for a given language, dramatically reducing the effort it takes to type a given piece of code.

How to run my code:
    To run my code, you need to install two python libraries:
        "python3.9 -m pip install rp prompt_toolkit"
    Please note: You must be using at least python3.8 to get the right version of prompt_toolkit
    To run the code, use "python3.9 microcompletion_engine.py"
    Note: I haven't tested this on a Windows terminal yet; right now I can confirm this works correctly on Ubuntu and Mac though.

keystroke_testing_translations={
    'enter':'\n',
    'space':' ',
    '␣':' ',
    '↵':'\n',
    'tab':'\t',
    '⌫':'backspace'
}

This testing framework allows me to add more rules more efficiently. Many times when you add a rule, it might have unintentional side effects in other rules. Having a suite of unit tests that check if you've made such a mistake makes adding rules much easier, because then you don't have to test all the edge cases manually. This came in handy many times while designing rules in this demo (numbering over 30). Note that even something as subtle as changing the order of the rules can have a significant effect on the output.

The testing framework also simultaneously as documentation in the source code, contained in docstrings in the function corresponding to each rule.

The best way to understand how the test suite works is to run the code in a terminal, because this will give you a color-highlighted output. But in case for some reason you can't do this, I've also included Example_Output.txt