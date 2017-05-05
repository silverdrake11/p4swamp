'''
MIT License

Copyright (c) 2017 Kevin Nasto

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
'''


import marshal
import os
import subprocess
import sys


USER_KWARGS = ('spec', 'binary')


class P4Error(Exception):
    pass

    
def _convert_to_binary(spec_dict):
    bin_dict = {}
    for k, v in spec_dict.items():
        try:
            k = str.encode(k)
        except TypeError:
            pass
        try:
            bin_dict[k] = str.encode(v, errors='ignore')
        except TypeError:
            bin_dict[k] = v
    return bin_dict
    

def _parse_spec(kwargs):
    '''
    Makes sure that the spec argument is a dictionary. If running Python 3 
    the dictionary must be converted to binary format because the p4 -G option 
    requires it.
    '''
    spec = None
    if 'spec' in kwargs:
        spec = kwargs['spec']
        if not isinstance(spec, dict):
            raise TypeError("'spec' must be a dictionary!")
        if sys.version_info[0] >= 3:
            spec = _convert_to_binary(spec)
    return spec

    
def _parse_bin_arg(kwargs):
    '''
    Returns the value if 'binary' argument is found, otherwise returns 
    false. Throws an error if the argument is not a boolean.
    '''
    if 'binary' in kwargs:
        binary_arg = kwargs['binary']
        if not isinstance(binary_arg, bool):
            raise TypeError("'binary' input argument must be of type bool!")
        return binary_arg
    else:
        return False
        
        
def _check_kwargs(kwargs):
    '''
    Checks the kwargs dictionary for the correct arguments. This is required for 
    Python 2 compatibility as Python 2 will not allow a single keyword argument 
    if *args is passed in.
    '''
    for key in kwargs:
        if key not in USER_KWARGS:
            raise ValueError("The argument specified '" + key + "' is not valid!")

    
def _convert_to_utf8(data_dict, binary=False):
    item = {}
    for k, v in data_dict.items():
        k = str(k, 'utf8')
        if not binary:
            try:
                v = str(v, 'utf8', errors='ignore')
            except TypeError: # e.g. if v is an integer
                v = str(v)
        item[k] = v
    return item
    
    
def p4swamp(*commands, **kwarg_input):
    '''
    It's a little bit tricky working with the p4 -G option. More information is
    available in the links below.
    http://stackoverflow.com/a/1713986
    http://stackoverflow.com/a/33482438/1890801
    http://stackoverflow.com/a/28770814/1890801
    '''
            
    _check_kwargs(kwarg_input)        
    binary = _parse_bin_arg(kwarg_input) # User argument specifying whether p4 output should be left in binary or converted to str
    spec = _parse_spec(kwarg_input) # Note in Python 3 spec must be converted binary format!
    
    proc_kwargs = {}
    proc_kwargs['stdout'] = subprocess.PIPE
        
    if spec is not None:
        read, write = os.pipe()
        os.write(write, marshal.dumps(spec, 0)) # We need to specify the marshal version for encoding
        os.close(write)
        proc_kwargs['stdin'] = read
            
    commands = ['p4', '-G'] + list(commands) # The -G option tells perforce to give us the marshalled object instead of a string

    proc = subprocess.Popen(commands, **proc_kwargs)
            
    pipe = proc.stdout
    data = []
    
    try:
        while True:
        
            record = marshal.load(pipe)
            
            if sys.version_info[0] >= 3: # The output perforce gives is bytes which is not the default used in Python 3
                record = _convert_to_utf8(record, binary=binary)
                
            data.append(record)
            
    except EOFError:
        pass
        
    pipe.close()
    proc.wait()
            
    return data
    
    
def p4(*commands, **kwargs):
    '''
    Runs the p4 command/s and if there is an error throws an exception. If there
    is a warning, prints it.
    '''
        
    data = p4swamp(*commands, **kwargs)
            
    if len(data) > 0: 
        status = data[0]
        if 'code' in status:
            if status['code'] == 'error': # Throw an exception if a perforce error occurs
                print('')
                for command in commands:
                    sys.stdout.write(command + ' ')
                print('\n')
                raise P4Error(status['data'])
            if status['code'] == 'warn': # Print warning if it occurs
                print(status['data'])
            
    return data