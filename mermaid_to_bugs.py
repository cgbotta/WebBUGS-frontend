from tokenize import tokenize
from io import BytesIO
import numpy as np
import os
import bs4

node_dict = {}

LOGICAL_FUNCTIONS = {
    "step": "step",
    "abs": "abs",
    "max": "max",
    "+": "+",
    "-": "-",
    "*": "*",
    "/": "/",
}
STOCHASTIC_FUNCTIONS = {
    "binomial": "dbin",
    "bernoulli": "dbern",
}

class node:
    def __init__(self, name, value):
        self.name = name
        self.value = value
        self.attributes = []
        self.type = None #TODO could make this a predefined enum or something
        self.density = None #TODO this one too 
        self.function = None #TODO and this one
        self.name_only = False
        self.shape = None
    def __str__(self):
        rtn = f"Name: {self.name}\nValue: {self.value}\nType: {self.type}\n"
        return rtn + '\n\n'

def getSubstringBetweenTwoChars(ch1,ch2,str):
    if '[' not in str or ']' not in str:
        return None
    return str[str.find(ch1)+1:str.find(ch2)]

# TODO what I am trying to do is a put against a database, essentially. Should probably check each thing that I am updating
def parse_node(node_str : str):
    n = node('','')

    no_name = False
    no_attributes = False

    if node_str.find(':') == -1:
        no_attributes = True
        n.name = node_str
    else:
        n.name = node_str[0:node_str.find(':')]

    # try to load existing node
    if n.name in node_dict:
        n = node_dict[n.name]

    value = getSubstringBetweenTwoChars('[',']',node_str)
    if value is None:
        no_name = True
    elif value.isnumeric():
        n.value = float(value)
    else:
        n.value = value

    # Process the name
    if node_str.find(':') == -1:
        no_attributes = True
    else:
        #Process the list of attributes
        n.attributes = node_str[node_str.find(':')+1 : node_str.find('[')].split()

        # TODO should move this to beginning, then see if the syntax and function options are correct for the given type
        for attribute in n.attributes:        
            if attribute == 'constant':
                n.type = 'constant'
            elif attribute == 'logical':
                n.type = 'logical'
                n.function = n.value
            elif attribute == 'stochastic':
                n.type = 'stochastic'
                n.density = n.value
            else:
                raise ValueError("Invalid attribute: ", attribute)
    
    if no_name and no_attributes:
        n.name_only = True

    return n
    
def translate_v2(mermaid_code):
    lines = [line.replace(" ","") for line in mermaid_code.splitlines()]

    BUGS_code = 'model {\n'

    loop_stack = []
    for index, line in enumerate(lines):
        # Skip blank lines
        if line == '\n' or line == '':
            continue
        # Identify the type of node we are creating.
        # If line contains a key in STOCHASTIC_FUNCTIONS, then it is a stochastic node.
        # If it contains a key in LOGICAL_FUNCTIONS, then it is a logical node.
        # Otherwise, it is a constant node.
        if any(x in line for x in STOCHASTIC_FUNCTIONS.keys()):
            # Stochastic node
            halves = line.split('=')
            name = halves[0]
            value = halves[1]

            if len(halves) != 2:
                raise ValueError("Invalid stochastic node: ", line)
            
            # Identify possible variables to replace
            g = tokenize(BytesIO(value.encode("utf-8")).readline)
            possible_variables = []
            for toktype, tokval, st, end, _ in g:
                if tokval.isidentifier():
                    possible_variables.append(tokval)
            updated_value = value
            for val in possible_variables:
                if val in STOCHASTIC_FUNCTIONS:
                    updated_value = updated_value.replace(val, STOCHASTIC_FUNCTIONS[val])
                else:
                    if val not in node_dict:
                        raise ValueError(f"Node {val} does not exist")
                    
            node_dict[name] = node(name, value)
            BUGS_code = BUGS_code + f'{name} ~ {updated_value}\n'

        elif any(x in line for x in LOGICAL_FUNCTIONS.keys()):
            # Logical node
            halves = line.split('=')
            name = halves[0]
            value = halves[1]

            if len(halves) != 2:
                raise ValueError("Invalid logical node: ", line)
            
            # Identify possible variables to replace
            g = tokenize(BytesIO(value.encode("utf-8")).readline)
            possible_variables = []
            for toktype, tokval, st, end, _ in g:
                if tokval.isidentifier():
                    possible_variables.append(tokval)

            updated_value = value
            for index, val in enumerate(possible_variables):
                if val in LOGICAL_FUNCTIONS:
                    updated_value = updated_value.replace(val, LOGICAL_FUNCTIONS[val])
                else:
                    if val not in node_dict:
                        raise ValueError(f"Node {val} does not exist")
                    
            node_dict[name] = node(name, value)
            BUGS_code = BUGS_code + f'{name} <- {updated_value}\n'
        elif "for" in line:
            loop_stack.append(1)
            BUGS_code = BUGS_code + f'{line}\n'
        elif line == "}":
            loop_stack.pop()
            BUGS_code = BUGS_code + '}\n'
        else:
            # Constant node
            print(line)
            halves = line.split('=')
            name = halves[0]
            value = halves[1]

            if len(halves) != 2:
                raise ValueError("Invalid constant node: ", line)
            node_dict[name] = node(name, value)
            BUGS_code = BUGS_code + f'{name} <- {value}\n'
            
    BUGS_code = BUGS_code + '}'
    return BUGS_code

    #TODO before I return, make a note of any variables that are unaccounted for and maybe save this is a dict somewhere so that it can be accessed in the data conversion code. 


def translate_data(user_data):
    lines = [line.replace(" ","") for line in user_data.splitlines()]

    BUGS_data = 'list(\n'

    loop_stack = []
    for index, line in enumerate(lines):
        # Skip blank lines
        if line == '\n' or line == '':
            continue
        # Identify each case then handle it
        halves = line.split('=')
        name = halves[0]
        value = halves[1]
        # Check if value is an array
        if '[' in value:
            if ']' not in value:
                raise ValueError("Invalid array: ", value)
            # Get all the values in the array
            array_values = value[value.find('[')+1 : value.find(']')].split(',')
            # Convert all the values to floats
            array_values = [float(x) for x in array_values]
            # Add the array to the dict
            node_dict[name] = node(name, array_values)
            node_dict[name].type = 'array'

            if '.shape' in name:
                pass
                #TODO handle this case 
            else:
                BUGS_data = BUGS_data + f'{name} = c('
                for index, val in enumerate(array_values):
                    if index == len(array_values) - 1:
                        BUGS_data = BUGS_data + f'{val}),\n'
                    else:
                        BUGS_data = BUGS_data + f'{val}, '



        else:
            # These should all be constants, not effecting other vars
            if name in node_dict:
                raise ValueError(f"Node {name} not referenced in code or data")
            node_dict[name] = node(name, value)
            BUGS_data = BUGS_data + f'{name} = {value},\n'
            
        
        
        
        # TODO continue here
        # Maybe what I do here is read in data AFTER I read in the code, and then check that any undefined vars in the code are accounted for in the data. If not, error out. If accounted for, proceed.

    BUGS_data = BUGS_data + ')'
    return BUGS_data



def clear_all_data():
    node_dict.clear()
    dir = "static/images"
    if os.path.exists(dir):
        for f in os.listdir(dir):
            os.remove(os.path.join(dir, f))
    # clear the data in the info file
    # clear the data in the info file
    with open("templates/graphs_page.html",'w') as file:
        pass
    return