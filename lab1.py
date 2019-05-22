import re
import pprint
import json
# from IPython.display import display
from colorama import Fore, Back, Style
import re
import json
from tkinter import *
from tkinter.font import Font
from tkinter import filedialog, ttk

# In[2]:


service_words = ['stop', 'end', 'dim', 'goto', 'gosub', 'if', 'then', 'else', 'end if']
operations = ['+', '-', '*', '/', '^', '<', '>', '=', '<>', '<=', '>=']
separators = [' ', ',', ':', '(', ')', '[', ']', '\'', '"']


# In[22]:


def filter_program(text):
    formatted_text = []
    text = re.sub(r'[$%&!#]', '', text)
    lines = text.split('\n')
    for index, line in enumerate(lines):
        splitted_text = line.split('\'')
        even_flag = False
        for span in splitted_text:
            if not even_flag:
                formatted_span = re.sub(r'[\t\n]+', ' ', span)
                formatted_span = re.sub(r' +', ' ', formatted_span)
                formatted_span = re.sub(r'^[0-9]+ ', '', formatted_span)
                formatted_span = re.sub(r'REM.*', '', formatted_span)
                formatted_text.append({
                    'text': formatted_span.lower(),
                    'type': 'code',
                    'line': index + 1

                })
            else:
                formatted_text.append({
                    'text': span,
                    'type': 'string',
                    'line': index + 1
                })

            even_flag = not even_flag
        if not even_flag:
            print(Fore.RED + 'Unexpected end of line. There is unclosed apostrophe!' + Style.RESET_ALL)
            return None

#     formatted_text = formatted_text.replace('\\', '\\\\')

    return formatted_text


# In[23]:


class Analyzer:
    state = 'S'
    string = ''
    collecting_string = ''

    def __init__(self, string):
        self.string = string

    def reset(self):
        self.collecting_string = ''
        self.state = 'S'

    def unexpected(self, symbol):
        self.state = 'error'
        print(Back.RED, Fore.WHITE, 'ERRORE!', Style.RESET_ALL,
              'Unexpected symbol \"' + symbol + '\"')
        return {
            'kind': 'error',
            'token': symbol,
            'residue': ''
        }

    def symbol_return(self, symbol):
        self.string = symbol + self.string
        if symbol != '':
            self.collecting_string = self.collecting_string[:-1]

    def collect_next(self):
        #         print('String: "',  end='')
        #         print(Fore.BLUE + self.string + Style.RESET_ALL, end='')
        #         print('"')

        try:
            symbol = self.string[0]
            self.string = self.string[1:]
        except:
            symbol = ''
        self.collecting_string += symbol

        if self.state == 'S':
            if symbol.isalpha() or symbol == '_':
                self.state = 'letter_at_first'
            elif symbol == '<':
                self.state = '<_at_first'
            elif symbol == '>':
                self.state = '>_at_first'
            elif symbol in operations:
                return {
                    'kind': 'operation',
                    'token': symbol,
                    'residue': self.string
                }
            elif symbol.isdigit():
                self.state = 'digit_at_first'
            elif symbol == '.':
                self.state = '._at_first'
            return self.collect_next()

        if self.state in ['number -> .. -> number']:
            if symbol.isdigit():
                return self.collect_next()
            elif symbol in operations + ['']:
                self.symbol_return(symbol)
                return {
                    'kind': 'integer_interval',
                    'token': self.collecting_string,
                    'residue': self.string
                }
            else:
                return self.unexpected(symbol)

        if self.state in ['number -> ..']:
            if symbol.isdigit():
                self.state = 'number -> .. -> number'
                return self.collect_next()
            else:
                return self.unexpected(symbol)

        if self.state == 'digit_at_first':
            if symbol.isdigit():
                return self.collect_next()
            elif symbol == '.':
                self.state = 'number -> .'
                return self.collect_next()
            elif symbol == 'e':
                self.state = 'number -> e'
                return self.collect_next()
            elif symbol in operations + ['']:
                self.symbol_return(symbol)
                return {
                    'kind': 'integer',
                    'token': self.collecting_string,
                    'residue': self.string
                }
            else:
                return self.unexpected(symbol)

        if self.state == 'number -> .':
            if symbol == '.':
                self.symbol_return(symbol)
                self.symbol_return(symbol)
                return {
                    'kind': 'integer',
                    'token': self.collecting_string,
                    'residue': self.string
                }

        if self.state == '._at_first':
            if symbol == '.':
                return {
                    'kind': 'separator',
                    'token': self.collecting_string,
                    'residue': self.string
                }

        if self.state in ['._at_first', 'number -> .']:
            if symbol.isdigit():
                return self.collect_next()
            elif symbol == 'e':
                self.state = 'number -> e'
                return self.collect_next()
            elif symbol in operations + ['']:
                self.symbol_return(symbol)
                return {
                    'kind': 'real',
                    'token': self.collecting_string,
                    'residue': self.string
                }
            elif symbol == '.':
                self.state = 'number -> ..'
                return self.collect_next()
            else:
                return self.unexpected(symbol)

        if self.state == 'number -> e':
            if symbol in ['+', '-']:
                self.state = 'number -> e -> +/-'
                return self.collect_next()
            elif symbol.isdigit():
                self.state = 'number -> e -> digit'
                return self.collect_next()
            else:
                return self.unexpected(symbol)

        if self.state in ['number -> e -> +/-', 'number -> e -> digit']:
            if symbol.isdigit():
                return self.collect_next()
            elif symbol in operations + ['']:
                self.symbol_return(symbol)
                return {
                    'kind': 'real',
                    'token': self.collecting_string,
                    'residue': self.string
                }
            else:
                return self.unexpected(symbol)

        if self.state == '<_at_first':
            if symbol in ['>', '=']:
                return {
                    'kind': 'operation',
                    'token': self.collecting_string,
                    'residue': self.string
                }
            else:
                self.symbol_return(symbol)
                return {
                    'kind': 'operation',
                    'token': self.collecting_string,
                    'residue': self.string
                }

        if self.state == '>_at_first':
            if symbol == '=':
                return {
                    'kind': 'operation',
                    'token': self.collecting_string,
                    'residue': self.string
                }
            else:
                self.symbol_return(symbol)
                return {
                    'kind': 'operation',
                    'token': self.collecting_string,
                    'residue': self.string
                }

        if self.state == 'letter_at_first':
            if symbol.isalpha() or symbol.isdigit() or symbol == '_':
                return self.collect_next()
            elif symbol in operations + ['']:
                self.symbol_return(symbol)
                return {
                    'kind': 'identifier',
                    'token': self.collecting_string,
                    'residue': self.string
                }
            else:
                return self.unexpected(symbol)

        return {
            'kind': 'exeption',
            'token': str(self.state),
            'residue': self.string
        }


# In[24]:


def find_in_begin_of(line):
    global separators, operations, service_words
    for i in range(len(line), -1, -1):
        if line[:i] in separators + operations + service_words + constants + identifiers:
            return [line[:i], line[i:]]
    return False


# In[25]:


def split_by_token(line):
    found = find_in_begin_of(line)
    if found:
        return found

#     Not found a tabled token in begin of line... OKay! Search the right border of this identifier or constant!
    for right_border in range(len(line)+1):
        if find_in_begin_of(line[right_border:]):
            break
    return [line[:right_border], line[right_border:]]


# In[26]:


def get_next_token():
    global sergements, service_words, operations, separators, constants, identifiers
    
    if not segments:
        return False
    
    while segments and not segments[0]['text'] and segments[0]['type'] == 'code':
        segments.pop(0)
    if not segments:
        return False
        
    line = segments[0]['line']
    
    if segments[0]['type'] == 'code':
        [token, segments[0]['text']] = split_by_token(segments[0]['text'])
        if not segments[0]['text']:
            segments.pop(0)
            
        tables = [service_words, operations, separators, constants, identifiers]
        symbols = ['W', 'O', 'R', 'C', 'I']
        found = False

        for index, table in enumerate(tables):
            if token in table:
                return [symbols[index], table.index(token), line]
                found = True
                break

        if not found:
            automat = Analyzer(token)
            tail = token

            while tail:
                automat.reset()
                analyzed = automat.collect_next()
                kind = analyzed['kind']
                token_name = analyzed['token']
                tail = analyzed['residue']

                if kind == 'identifier':
                    if {'type': 'identifier', 'value': token} not in identifiers:
                        identifiers.append({
                            'type': 'identifier',
                            'value': token
                        })
                    else:
                        return ['I', identifiers.index({'type': 'identifier', 'value': token})]
                    return ['I', len(identifiers) - 1, line]
                if kind in ['string', 'integer', 'real']:
                    constants.append({
                        'type': kind,
                        'value': token
                    })
                    return ['C', len(constants) - 1, line]
    else:
        constants.append({
            'type': 'string',
            'value': segments[0]['text']
        })
        segments.pop(0)
        return ['C', len(constants) - 1, line]


# In[27]:


def get_token_name(token):
    global service_words, operations, separators, constants, identifiers
    codes = ['W', 'O', 'R', 'C', 'I']
    tables = [service_words, operations, separators, constants, identifiers]
    if token[0] in ['C', 'I']:
        return tables[codes.index(token[0])][token[1]]['value']
    return tables[codes.index(token[0])][token[1]]


# In[28]:

segments = ''
identifiers = []
constants = []
chain = []
token = ''


def clr():
    global segments, constants, identifiers, chain, token
    segments = ''
    identifiers = []
    constants = []
    chain = []
    token = ''


result = ''
index = 0
file_dir = ''
root = Tk()
root.title("Лексический анализатор")
root.configure(bg="#bebebe")
fontForButtons = Font(family="Helvetica", size=18)
fontForText = Font(family="Helvetica", size=17)


def clearForNewFile():
    global index, result, chain
    resultLexical.delete(1.0, END)
    sourseField.delete(1.0, END)
    result = ''
    index = 0
    clr()
    view_records()


def openNewFile():
    global segments, identifiers, constants, file_dir, chain, token
    file_dir = filedialog.askopenfilename(filetypes=(
        ('Basic', '*.bas'), ('All files', '*.*')))
    try:
        data = open(file_dir, 'r').read()
        clearForNewFile()
        sourseField.insert(1.0, data)
        segments = filter_program(open(file_dir).read())
        constants = []
        identifiers = []
        chain = []
        token = 'nu sho, poihali'
        goFullButton['state'] = NORMAL
        goStepButton['state'] = NORMAL
    except:
        print('Файл не выбран')


def byStep():
    global segments, constants, identifiers, chain, token, result
    token = get_next_token()
    if token:
        chain.append(token)
        # print(token, get_token_name(token))
        # print(identifiers)
        result += '{}{} '.format(token[0], token[1])
        currentSymb.delete(1.0, END)
        currentSymb.insert(1.0, get_token_name(token))
        resultLexical.delete(1.0, END)
        resultLexical.insert(1.0, result)
        view_records()
    else:
        currentSymb.delete(1.0, END)
        goStepButton['state'] = DISABLED
        goFullButton['state'] = DISABLED
        data = {
            'chain': chain,
            'tables': {
                'service_words': service_words,
                'operations': operations,
                'separators': separators,
                'constants': constants,
                'identifiers': identifiers
            }
        }

        with open('./res/lab1.json', 'w') as outfile:
            json.dump(data, outfile)


def fullProgram():
    global result, index
    global segments, constants, identifiers, chain, token
    segments = filter_program(open(file_dir).read())
    constants = []
    identifiers = []
    chain = []
    token = 'nu sho, poihali'
    while token:
        token = get_next_token()
        if token:
            chain.append(token)
    data = {
        'chain': chain,
        'tables': {
            'service_words': service_words,
            'operations': operations,
            'separators': separators,
            'constants': constants,
            'identifiers': identifiers
        }
    }
    with open('./res/lab1.json', 'w') as outfile:
        json.dump(data, outfile)
    result = data
    index = len(result['chain'])
    outputString = ''
    for i in range(index):
        outputString += '{}{}{}'.format(result['chain'][i][0], result['chain'][i][1], ' ')
    resultLexical.delete(1.0, END)
    resultLexical.insert(1.0, outputString)
    currentSymb.delete(1.0, END)
    goStepButton['state'] = DISABLED
    goFullButton['state'] = DISABLED
    view_records()


def view_records():  # отображение данных из таблиц
    global identifiers, constants
    [tableID.delete(i) for i in tableID.get_children()]
    [tableConst.delete(i) for i in tableConst.get_children()]

    [tableID.insert('', END, values=(i, identifiers[i]['value'])) for i in range(len(identifiers))]
    [tableConst.insert('', END, values=(i, constants[i]['value'])) for i in range(len(constants))]


# toolbar
toolbar = Frame(root, bg="#bebebe")
toolbar.grid(row=0, column=3, rowspan=3)
openFileButton = Button(toolbar, text="Открыть", command=openNewFile, font=fontForButtons, width=10)
openFileButton.pack(side=TOP, padx=20, pady=10, anchor=W)
goStepButton = Button(toolbar, text="Шаг", command=byStep,
                      font=fontForButtons, width=10, state=DISABLED)
goStepButton.pack(side=TOP, padx=20, pady=(0, 10), anchor=W)
goFullButton = Button(toolbar, text="Полностью", command=fullProgram,
                      font=fontForButtons, width=10, state=DISABLED)
goFullButton.pack(side=TOP, padx=20, pady=(0, 10), anchor=W)
Label(toolbar, text="Текущий", font=fontForText,
      bg="#bebebe").pack(side=TOP, padx=20, pady=(20, 10), anchor=W)
currentSymb = Text(toolbar, font=fontForText, width=11, height=1)
currentSymb.pack(side=TOP, padx=20, pady=(0, 10), anchor=W)
# end toolbar
Label(root, text="Исходная программа", font=fontForText,
      bg="#bebebe").grid(row=0, column=0, padx=20, pady=10)
sourseField = Text(root, font=fontForText, width=25)
sourseField.grid(row=1, column=0, padx=20, pady=(0, 20), rowspan=2)
Label(root, text="Результат анализа", font=fontForText,
      bg="#bebebe").grid(row=0, column=1, padx=20, pady=10)
resultLexical = Text(root, font=fontForText, width=25)
resultLexical.grid(row=1, column=1, padx=20, pady=(0, 20), rowspan=2)

tableID = ttk.Treeview(root, columns=('#id', 'name'), height=13, show='headings')
tableID.column('#id', width=90, anchor=CENTER)
tableID.column('name', width=90, anchor=CENTER)
tableID.heading('#id', text='#id')
tableID.heading('name', text='name')
tableID.grid(row=1, column=2)

tableConst = ttk.Treeview(root, columns=('#const', 'value'), height=13, show='headings')
tableConst.column('#const', width=90, anchor=CENTER)
tableConst.column('value', width=90, anchor=CENTER)
tableConst.heading('#const', text='#const')
tableConst.heading('value', text='value')
tableConst.grid(row=2, column=2)
root.mainloop()
