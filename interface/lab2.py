#!/usr/bin/env python
# coding: utf-8

# In[6]:


import re
import sys
import json
# from IPython.display import display
# from colorama import Fore, Back, Style
import subprocess


# In[ ]:





# In[48]:


def get_priority(operation):
    priorities = [
        ['(', '[', 'АЭМ', 'Ф', 'IF', 'WHILE'],
        [')', ']', ',', ';', 'THEN', 'ELSE'],
        ['=', 'goto'],
        ['||'],
        ['&&'],
        ['!'],
        ['<', '>', '<=', '>=', '==', '!='],
        ['+', '-'],
        ['*', '/'],
        ['^'],
        ['RETURN'],
        [':'],
        ['НФ', 'КФ', 'НП', 'КП']
    ]
    for index, row in enumerate(priorities):
        if operation in row:
            return index
    return False


# In[3]:


def get_token_name(token):
    global service_words, operations, separators, constants, identifiers
    codes = ['W', 'O', 'R', 'C', 'I']
    tables = [service_words, operations, separators, constants, identifiers]
    if token[0] in ['C', 'I']:
        return tables[codes.index(token[0])][token[1]]['value']
    return tables[codes.index(token[0])][token[1]]


# In[4]:


def get_token_type(token):
    global service_words, operations, separators, constants, identifiers
    token_name = get_token_name(token)
    if token_name in service_words:
        return 'service_word'
    if token_name in operations:
        return 'operation'
    if token_name in separators:
        return 'separator'
    if token[0] == 'C':
        return constants[token[1]]['type']
    if token[0] == 'I':
        return identifiers[token[1]]['type']
    return False


# In[99]:


subprocess.run(["python", "lab1.py"])
with open('./lab1.json') as lab1_file:
    data = json.load(lab1_file)
chain = data['chain']
tables = data['tables']
service_words = data['tables']['service_words']
operations = data['tables']['operations']
separators = data['tables']['separators']
constants = data['tables']['constants']
identifiers = data['tables']['identifiers']

stack = []
result = []
AEM_counter = None
F_counter = None
M_counter = 0

identifier_context = False
if_context = None
while_context = None
while_m = 0
type_context = None
var_pool = []
var_type = None
func_context = False
arg_counter = 0
dim_counter = 0

token_number = 0
for token in chain:
    token_number += 1
    token_name = get_token_name(token)
    token_type = get_token_type(token)
    previous_stack = list(stack)
    
    if token_type != 'separator' or token_name in ['(', ')', '[', ']', ',', ':', ';']:
        if token_type == 'identifier':
            identifier_context = True
            
        if token_name == 'return':
            stack.append('RETURN')
            continue
            
#         Var and func declaring
        if token_name in ['void', 'int', 'float', 'char']:
            type_context = 'type'
            var_type = token_name
            var_pool = []
            if func_context:
                arg_counter = 1 if arg_counter == 0 else arg_counter
            
        if type_context in ['type', 'type ids'] and token_type == 'identifier':
            type_context = 'type ids'
            var_pool.append(token_name)
#         also look at the ';' processing below
            
        if token_name == '}' and not if_context and not while_context:
            result.append('КФ')
            func_context = False
            arg_counter = 0
            
#         WHILE processing
        if token_name == 'while':
            stack.append('WHILE')
            while_context = 'while'
            M_counter += 1
            while_m = M_counter
            result.append('НЦ M' + str(while_m) + ':')
            
        if token_name == 'do' and while_context == 'while':
            while stack and stack[-1] != 'WHILE':
                result.append(stack.pop())
            while_context = 'while do'
            M_counter += 1
            result.append('M' + str(M_counter) + ' УПЛ')
        
        if token_name == 'end while' and while_context == 'while do':
            while stack and stack[-1] != 'WHILE':
                result.append(stack.pop())
            if stack and stack[-1] == 'WHILE':
                stack.pop()
            result.append('КЦ M' + str(while_m) + ' БП M' + str(M_counter) + ':')
            while_context = None
            
#         IF processing        
        if token_name == 'if':
            stack.append('IF')
            if_context = 'if'
            
        if token_name == 'then' and if_context == 'if':
            if_context = 'if then'
            while stack and stack[-1] != 'IF':
                result.append(stack.pop())
            M_counter += 1
            result.append('M' + str(M_counter) + ' УПЛ')
            
        if token_name == 'else' and if_context == 'if then':
            if_context = 'if then else'
            while stack and stack[-1] != 'IF':
                result.append(stack.pop())
            M_counter += 1
            result.append('M' + str(M_counter) + ' БП M' + str(M_counter-1) + ':')
                
        if token_name == 'end if':
            if if_context == 'if then':
                while stack and stack[-1] != 'IF':
                    result.append(stack.pop())
                if stack and stack[-1] == 'IF':
                    stack.pop()
                result.append('M' + str(M_counter) + ':')
                if_context = None
            if if_context == 'if then else':
                while stack and stack[-1] != 'IF':
                    result.append(stack.pop())
                if stack and stack[-1] == 'IF':
                    stack.pop()
                result.append('M' + str(M_counter) + ':')
                if_context = None
                
#         DIM processing
        if token_name == 'dim':
#             result.append('НА')
            dim_counter = 1
            
            
#         SUB processing
        if token_name == 'sub':
            result.append('НП')
            func_context = 'sub'
            
        if token_name == 'end sub':
            while stack and stack[-1] != 'КП':
                result.append(stack.pop())
            result.append('КП')
                
#         Ordinary expression processing
        if token_type in ['identifier', 'integer', 'string', 'real']:
            result.append(token_name)
            
        if token_type in ['operation'] or token_name in ['=', 'goto', ':']:
            token_name = 'БП' if token_name == 'goto' else token_name
            if not stack:
                stack.append(token_name)
            else:        
                while stack and get_priority(stack[-1]) > get_priority(token_name):
                    result.append(stack.pop())
                else:
                    stack.append(token_name)
                    
#         Brackets processing
        if token_name == '(' and not identifier_context:
            stack.append('(')
            
        if token_name == ')' and not (F_counter):
            while stack[-1] != '(':
                # print(stack)
                result.append(stack.pop())
            stack.pop()
            if stack and stack[-1] == 'WHILE':
                while_context = 'while ()'
                M_counter += 1
                result.append('M' + str(M_counter) + ' УПЛ')
            if type_context == 'type ids':
                result.append(str(len(var_pool)) + ' ' + var_type)
            
#         Arrays processing
        if token_name == '[':
            stack.append('АЭМ')
            AEM_counter = 2
            
        if token_name == ',' and AEM_counter:
            while stack[-1] != 'АЭМ':
                result.append(stack.pop())
            AEM_counter += 1
            
        if token_name == ']':
            while stack[-1] != 'АЭМ':
                result.append(stack.pop())
            result.append(str(AEM_counter) + ' ' + stack.pop())
            AEM_counter = None
            
#         Functions processing
        if token_name == '(' and (identifier_context or func_context):
            stack.append('Ф')
            F_counter = 1
            
            if type_context:
                func_context = True
                arg_counter = 0
                result.append('1 ' + str(var_type))
                type_context = None
            
        if token_name == ',' and F_counter:
            while stack[-1] != 'Ф':
                result.append(stack.pop())
            F_counter += 1
                
        if token_name == ',' and dim_counter:
            dim_counter += 1
        
        if token_name == ')' and F_counter:
            F_counter += 1
            
            if type_context == 'type ids':
                result.append(str(len(var_pool)) + ' ' + var_type)
                type_context = None
            
            while stack[-1] != 'Ф':
                result.append(stack.pop())

            result.append(str(F_counter) + ' ' + stack.pop())
            F_counter = None
            func_context = 'sub args'
            
#         ";" processing
        if token_name == ';' or token_number == len(chain):
            if dim_counter:
                result.append(str(dim_counter) + ' НА')
                dim_counter = 0
            if func_context == 'sub':
                result.append('1 Ф')
            func_context = None
            while stack and stack[-1] not in ['IF', 'WHILE', 'КП'] and stack[-1] != 'Ф':
                result.append(stack.pop())
            if type_context == 'type ids':
                result.append(str(len(var_pool)) + ' '+ var_type)
                type_context = None

        # print(str(token_name), Fore.WHITE + str(token_type) + Style.RESET_ALL)
        # print('Stack:', previous_stack, '->', stack)
        # print('Result:', result)
        # print()
        
        if token_type != 'identifier':
            identifier_context = False
            
    
previous_stack = list(stack)
while stack:
    result.append(stack.pop())
    
string = ''
for i in result:
    string += ' ' + i

# # print(Fore.RED + 'END' + Style.RESET_ALL)
# # print('Stack:', previous_stack, '->', stack)
# # print('Result:', string, Fore.BLUE)

data = {
    'rpn': result,
    'tables': tables
}

with open('./lab2.json', 'w') as outfile:
    json.dump(data, outfile)

res = ''
for item in result:
    res += str(item) + ' '

with open('./lab2.txt', 'w') as outfile:
    outfile.write(res)


# In[ ]:





# In[ ]:





# In[ ]:




