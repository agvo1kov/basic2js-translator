import re
import json
from tkinter import *
from tkinter.font import Font
from tkinter import filedialog, ttk
# from lab1 import resultFromFile
# from lab2 import toOpz, convertToSymb
# from lab3 import goToCPP
# from lab4 import isMistakes
import subprocess

# для корретной работы
operations = ['+', '-', '*', '/', '^', '<', '>', '=', '<>', '<=', '>=']
separators = [' ', ',', '..', ':', ';', '(', ')', '[', ']', '{', '}']
result = ''
index = 0
opzResult = ''
constants = []
identifiers = []


# для интерфейса
def clearForNewFile():
    global index, token, result, program, identifiers, constants
    sourseText.delete(1.0, END)
    resultLexicalText.delete(1.0, END)
    resultOpzText.delete(1.0, END)
    resultCppText.delete(1.0, END)
    result = ''
    program = ''
    index = 0
    opzResult = ''
    constants = []
    identifiers = []


def openFile():
    global result, identifiers, constants
    file_dir = filedialog.askopenfilename(filetypes=(
        ('Basic File', '*.bas'), ('All files', '*.*')))
    # try:
    data = open(file_dir, 'r').read()
    clearForNewFile()
    sourseText.insert(1.0, data)
    # result = resultFromFile(file_dir)
    # constants = result['tables']['constants']
    # identifiers = result['tables']['identifiers']
    with open('./prog.bas', 'w') as outfile:
        outfile.write(data)
    # subprocess.run(["python", "lab1.py"]) 
    # subprocess.run(["python", "lab2.py"])
    subprocess.run(["python", "lab3.py"])
    subprocess.run(["python", "lab4.py"])
    stepButton['state'] = NORMAL
    fullButton['state'] = NORMAL
    opzBUTTON['state'] = DISABLED
    syntaxBUTTON['state'] = DISABLED
    toCppBUTTON['state'] = DISABLED

    for tag in sourseText.tag_names():
        sourseText.tag_delete(tag)


def fullProgram():
    resultLexicalText.delete(1.0, END)
    resultLexicalText.insert(1.0, open('./lab1.txt', 'r').read())
    stepButton['state'] = DISABLED
    fullButton['state'] = DISABLED
    opzBUTTON['state'] = NORMAL
    syntaxBUTTON['state'] = NORMAL


def nextStep():
    pass


def toOpzNormal():
    resultOpzText.delete(1.0, END)
    resultOpzText.insert(1.0, open('./lab2.txt', 'r').read())
    toCppBUTTON['state'] = NORMAL


def toCPP():
    resultCppText.delete(1.0, END)
    resultCppText.insert(1.0, open('./result.js', 'r').read())


def checkErrors():
    mistake = open('./checked.txt', 'r').read()
    if mistake == '':
        syntaxBUTTON['state'] = DISABLED
        print('ошибок нет')
        new = Tk()
        new.title("Ошибок нет")
        Label(new, text="Ошибок нет", font=fontForText).pack(side=TOP, padx=20, pady=40)
        # syntaxBUTTON['state'] = DISABLED
        # opzBUTTON['state'] = DISABLED
        sourseText.tag_add("error", "{}.0".format(mistake[1]), "{}.{}".format(mistake[1], END))
        sourseText.tag_config("error", background="red")
        sourseText.see("{}.0".format(mistake[1]))
    else:
        new = Tk()
        new.title("Ошибка")
        Label(new, text=mistake, font=fontForText).pack(side=TOP, padx=20, pady=40)
        syntaxBUTTON['state'] = DISABLED
        opzBUTTON['state'] = DISABLED
        sourseText.tag_add("error", "{}.0".format(mistake[1]), "{}.{}".format(mistake[1], END))
        sourseText.tag_config("error", background="red")
        sourseText.see("{}.0".format(mistake[1]))


# Интерфейс
root = Tk()
root.title("Транслятор")
root.configure(bg="#c9c9c9")
fontForButtons = Font(family="Helvetica", size=18)
fontForText = Font(family="Helvetica", size=17)

# тулбар
toolbar = Frame(root, bg="#c9c9c9")
toolbar.grid(row=0, column=0, columnspan=3, sticky="W")
Button(toolbar, text="Open", command=openFile, font=fontForButtons).pack(
    side=LEFT, padx=20, pady=20)

stepButton = Button(toolbar, text=">", command=nextStep, font=fontForButtons, state=DISABLED)
stepButton.pack(side=LEFT, padx=20, pady=20)
fullButton = Button(toolbar, text=">>", command=fullProgram, font=fontForButtons, state=DISABLED)
fullButton.pack(side=LEFT, padx=(0, 20), pady=20)

syntaxBUTTON = Button(toolbar, text="Проверить", command=checkErrors,
                      font=fontForButtons, state=DISABLED)
syntaxBUTTON.pack(side=LEFT, padx=20, pady=20)

opzBUTTON = Button(toolbar, text="ОПЗ", command=toOpzNormal, font=fontForButtons, state=DISABLED)
opzBUTTON.pack(side=LEFT, padx=20, pady=20)

toCppBUTTON = Button(toolbar, text="в JavaScript", command=toCPP, font=fontForButtons, state=DISABLED)
toCppBUTTON.pack(side=LEFT, padx=20, pady=20)
# конец тулбара

sourseText = Text(root, font=fontForText, width=26, height=20)
sourseText.grid(row=1, column=0, padx=20, pady=20)
resultLexicalText = Text(root, font=fontForText, width=26, height=20)
resultLexicalText.grid(row=1, column=1, padx=20, pady=20)
resultOpzText = Text(root, font=fontForText, width=26, height=20)
resultOpzText.grid(row=1, column=2, padx=20, pady=20)
resultCppText = Text(root, font=fontForText, width=26, height=20)
resultCppText.grid(row=1, column=3, padx=20, pady=20)


root.resizable(0, 0)
root.mainloop()
