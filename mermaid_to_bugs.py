from tokenize import tokenize
from io import BytesIO

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
    def __str__(self):
        rtn = f"Name: {self.name}\nValue: {self.value}\nType: {self.type}\nDensity: {self.density}\n"
        rtn = rtn + 'Parents: '
        for p in self.parents:
            rtn = rtn + p.name + ', '

        rtn = rtn + '\nChildren: '
        for c in self.children:
            rtn = rtn + c.name + ', '
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
    # Array of order to create everything, add stuff to this after each line of the file is processed
    nodes_to_process = []

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


        # TODO continue from here with the above code. Basically starting the processing from scrath. 
        # The below code is only being kept for reference, and will be deleted once the above code is complete.










    # for index, line in enumerate(lines):
    #     # Skip blank lines
    #     if line == '\n' or line == '':
    #         continue
    #     to_process = [line]
    #     if '->' in line:
    #         # Split into 2 halves to process
    #         to_process = [str.strip(piece) for piece in line.split('-->')] 
    #     # TODO send to function to return final array with all connections specified
    #     next_batch = identify_connections(to_process)
    #     for x in next_batch:
    #         nodes_to_process.append(x)
    # # print(nodes_to_process)

    # #TODO now need to iterate over nodes_to_process and create the actual node objects with connections
    # # print("nodes_to_process",nodes_to_process)
    # for element in nodes_to_process:
    #     node_objects = create_nodes(element)
    #     for node_update in node_objects:
    #         update_graph(node_update)
    
    # # for key, value in node_dict.items():
    #     # print(key, value)
            

    # BUGS_code = 'model {\n'
    # for node_name, node_object in node_dict.items():
    #     if isinstance(node_object, node):
    #         n = node_object
    #     else:
    #         raise ValueError("Internal Server Error: Node is only accepted type")
        
    #     if n.type == 'constant':
    #         BUGS_code = BUGS_code + f'{n.name} <- {n.value}\n'
    #     elif n.type == 'logical':
    #         if len(n.parents) == 0:
    #             BUGS_code = BUGS_code + f'{n.name} <- ({n.value})\n'
    #         else:
    #             # if n.function == 'step':
    #             # Identify possible variables to replace
    #             g = tokenize(BytesIO(n.value.encode("utf-8")).readline)
    #             possible_variables = []
    #             for toktype, tokval, st, end, _ in g:
    #                 if tokval.isidentifier():
    #                     possible_variables.append(tokval)
    #             # print("possible_variables", possible_variables)

    #             for token in possible_variables:
    #                 if token in LOGICAL_FUNCTIONS:
    #                     possible_variables.remove(token)
    #             # print("possible_variables", possible_variables)

    #             if len(n.parents) != len(possible_variables):
    #                 raise ValueError(f"Number of parents does not equal number of variables in child: {n.parents} != {possible_variables}")
    #             updated_value = n.value
    #             # print("updated value", updated_value)
    #             for index, val in enumerate(possible_variables):
    #                 # print("val", val)
    #                 # print("parent", n.parents[index].name)
    #                 updated_value = updated_value.replace(val, n.parents[index].name)
    #             # print("updated value", updated_value)

    #             BUGS_code = BUGS_code + f'{n.name} <- {updated_value}\n'

    #             # else:
    #             #     raise ValueError(f"Invalid logical function: {n.function}")
    #     elif n.type == 'stochastic':
    #         if len(n.parents) == 0:
    #             # TODO ??
    #             BUGS_code = BUGS_code + f'{n.name} <- ({n.value})\n'
    #         else:
    #             if n.density == 'dbin':
    #                 # Takes 2 arguments
    #                 if len(n.parents) == 2:
    #                     BUGS_code = BUGS_code + f'{n.name} <- dbin({n.parents[0].value},{n.parents[1].value})\n'
    #                 else:
    #                     raise ValueError(f"dbin requires 2 parents, recieved {len(n.parents)}")
    #             elif n.density == 'dbern':
    #                 # Takes 1 argument
    #                 if len(n.parents) == 1:
    #                     BUGS_code = BUGS_code + f'{n.name} <- dbern({n.parents[0].name})\n'
    #                 else:
    #                     raise ValueError(f"dbern requires 1 parent, recieved {len(n.parents)}")
    #             else:
    #                 raise ValueError(f"Invalid stochastic function: {n.density}")


    BUGS_code = BUGS_code + '}'
    return BUGS_code

def clear_all_data():
    node_dict.clear()
    return