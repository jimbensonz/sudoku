# Sudoku Solver 


It is a Python program to solve Sudoku problems. 

The program can accept either ``csv`` file or image as the input. The examples of both data types can be found in the ``data/`` folder.

All the exercises are taken from [Web Sudoku](https://www.websudoku.com/).

-----------

## Image Recognition


To recognize the image of sudoku puzzle, I do the following procedures to process the image:

1. Read the image in grey mode and invert the color (To fit in with the model)
2. Remove the borders in black line 
3. Split the image into 9x9 sub-images
4. Centerize digit in the sub-images
4. Use the model to classify each sub-image and create the sudoku

-----------

## Data Structure


``Cell.py`` and ``Sudoku.py`` are the object files.

There are 9x9 Cells in the Sudoku, and each Cell stores the position, value, and potential candidates. 

All the primary functions are in the ``Sudoku.py``, and calling ``solve()`` function can solve the sudoku puzzle.
