#!/usr/bin/env python
# coding: utf-8

# In[1]:


import re
import pprint
import json
from IPython.display import display
from colorama import Fore, Back, Style


# In[2]:


service_words = ['stop', 'end', 'dim', 'goto', 'gosub', 'if', 'then', 'else', 'end if', 'while', 'end while', 'do', 'sub', 'end sub', 'function', 'end function', 'return']
operations = ['+', '-', '*', '/', '^', '<', '>', '=', '<>', '<=', '>=']
separators = [' ', ',', ':', ';', '(', ')', '[', ']', '\'', '"', "\n"]


# In[3]:


def filter_program(text):
    stack = []
    new_text = ''
    for symb in text:
        if stack and stack[-1] == '$' and symb == '(':
            new_text += '['
            stack.append('(')
        elif stack and stack[-1] == '(' and symb == ')':
            new_text += ']'
            stack.pop()
            stack.pop()
        elif stack and stack[-1] == '$':
            stack.pop()
            new_text += symb
        else:
            new_text += symb
            if symb in '$%&!#':
                stack.append('$')
    text = str(new_text)
            
    formatted_text = []
    text = re.sub(r'[$%&!#]', '', text)
    text = re.sub(r'[\n]+', ";\n", text)
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


# In[4]:


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
        print(Back.RED, Fore.WHITE,'ERRORE!', Style.RESET_ALL, 'Unexpected symbol \"' + symbol + '\"')
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


# In[5]:


def find_in_begin_of(line):
    global separators, operations, service_words
    for i in range(len(line), -1, -1):
        if line[:i] in separators + operations + service_words + constants + identifiers:
            return [line[:i], line[i:]]
    return False


# In[6]:


def split_by_token(line):
    found = find_in_begin_of(line)
    if found:
        return found
    
#     Not found a tabled token in begin of line... OKay! Search the right border of this identifier or constant!        
    for right_border in range(len(line)+1):
        if find_in_begin_of(line[right_border:]):
            break
    return [line[:right_border], line[right_border:]]


# In[7]:


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


# In[8]:


def get_token_name(token):
    global service_words, operations, separators, constants, identifiers
    codes = ['W', 'O', 'R', 'C', 'I']
    tables = [service_words, operations, separators, constants, identifiers]
    if token[0] in ['C', 'I']:
        return tables[codes.index(token[0])][token[1]]['value']
    return tables[codes.index(token[0])][token[1]]


# In[10]:


segments = filter_program(open('./src/lab1.bas').read())
constants = []
identifiers = []
chain = []

token = 'nu sho, poihali'
while token:
    token = get_next_token()
    if token:
        chain.append(token)
        print(token, get_token_name(token))
    
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
print(identifiers)


# In[ ]:





# In[ ]:




