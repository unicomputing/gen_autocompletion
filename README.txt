Ryan Burgert CSE526 Final Project

This project demonstrates a new way to write python code, using what I call "microcompletions". Microcompletions are a set of behaviours that a text editor can implement to make writing code more efficient for a given language, dramatically reducing the effort it takes to type a given piece of code.

How to run my code:
    To run my code, you need to install two python libraries:
        "python3.9 -m pip install rp prompt_toolkit"
    Please note: You must be using at least python3.8 to get the right version of prompt_toolkit
    To run the code, use "python3.9 microcompletion_engine.py"
    Note: I haven't tested this on a Windows terminal yet; right now I can confirm this works correctly on Ubuntu and Mac though.


This testing framework allows me to add more rules more efficiently. Many times when you add a rule, it might have unintentional side effects in other rules. Having a suite of unit tests that check if you've made such a mistake makes adding rules much easier, because then you don't have to test all the edge cases manually. This came in handy many times while designing rules in this demo (numbering over 30). Note that even something as subtle as changing the order of the rules can have a significant effect on the output.

The testing framework also simultaneously as documentation in the source code, contained in docstrings in the function corresponding to each rule.

The best way to understand how the test suite works is to run the code in a terminal, because this will give you a color-highlighted output. But in case for some reason you can't do this, I've also included Example_Output.txt


Each test consists of a list of states separated by keystrokes.
A state consists of both a string surrounded by ‹ and ›, and a cursor position, represented by the ¦ character.
For example, ‹Hello¦ World!› represents a an editor state where the editor text is "Hello World!" and the cursor position is at index 5.



Here is a simple example test, demonstrating what happens when we press the W key
|   ‹Hello ¦›    W    ‹Hello W¦›

Tests can chain more than one keystroke/state pair at a time
|   ‹Hello ¦›    W    ‹Hello W¦›   o    ‹Hello Wo¦›

You can have more than one keystroke between states
|   ‹Hello ¦›    W    ‹Hello W¦›   o    ‹Hello Wo¦›  r l d  ‹Hello World¦› 

Some keys, like the left arrow key are represented with words
|   ‹Hello World¦›    left     ‹Hello Worl¦d›    backspace   ‹Hello Wor¦d›


Each test implies that a state will be run through the microcompletion engine with the given keystrokes, and compared to the desired state to determine if it's getting the proper result.


When we add SHOULD_FAIL to the beginning of a test header, it means that it's good if the test fails.

SHOULD_FAIL! Here's a negative-test, where the test should fail. It says that Q should not be added when we press the W key
|   ‹Hello ¦›    W    ‹Hello Q¦›


Some keystrokes have special characters that can be used to make reading the tests easier

For example, 'space' and '␣' both mean the same thing
|   ‹¦›    space   ‹ ¦›    ␣    ‹  ¦›


keystroke_testing_translations={
    'space':' ',
    '␣'    :' ',
    'enter':'\n',
    '↵'    :'\n',
    'tab':'\t',
    '⌫':'backspace'
}





