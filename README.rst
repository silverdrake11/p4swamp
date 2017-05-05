************
p4swamp
************

p4swamp is a wrapper for the Perforce command-line utility (p4). It does does not require external dependencies (pure Python). The module takes as input p4 commands (see `P4 Documentation`_ for complete list and usage) and outputs a list of Python dictionary objects. In addition specifying a workspace is supported.
   
   
.. image:: https://img.shields.io/badge/source-GitHub-green.svg?maxAge=3600&style=flat-square
    :target: https://github.com/silverdrake11/p4swamp

    
Requirements
-------------

- Perforce command-line utility (p4) must be installed
- Python 2.6 and above (including Python 3)


Installation
------------
::

    pip install p4swamp


****************
Usage
****************

These are some examples of use cases. For additional details of the commands available see the `P4 Documentation`_


Import Statement
----------------
.. code:: python

    from p4swamp import p4

Read Client Specification
-------------------------
::

    >> p4('client', '-o', 'myclient')

    [{'Access': '2017/03/24 10:29:53',
      'Client': 'myclient',
      'Description': 'Testing example\n',
      'LineEnd': 'local',
      'Options': 'noallwrite noclobber nocompress unlocked nomodtime normdir',
      'Root': 'C:\\myclient',
      'SubmitOptions': 'submitunchanged',
      'Update': '2017/05/03 19:01:53',
      'View0': '//depot/myproject/... //myclient/myproject/...',
      'View1': '+//depot/myfiles/data.txt //myclient/data.txt',
      'code': 'stat'}]

Note that the output is actually a list of dictionaries. Also note that the client view starts at `View0` and continues like so `View0`, `View1`, `View2`, ...

Write Client Specification
--------------------------
Creating the client and getting the data:

.. code:: python
        
    newclient1 = p4('client', '-o', 'newclient1')[0]  # Don't forget the [0] to get the dictionary! 
    newclient1['Root'] = 'C:\\myfolder\here'
    newclient1['View0'] = '//depot/icecream/... //newclient1/icecream/...'
   
Then writing the modified specification:

::

    >> p4('client', '-i', spec=newclient1)
    
    [{
        'data': 'Client newclient1 saved.', 
        'code': 'info', 
        'level': '0'}]


Using The Binary Option
-----------------------

If for any reason the output you expect from P4 is not a string, you must use the `binary` option and set it to `True`. This is because by default the P4 output is converted to unicode in Python 3. This is of course unless you are using Python 2 (however it's still recommended to use the `binary` flag because if the code is converted to Python 3, things will break!)

Here is an example of a use case:

.. code:: python
    
    from p4swamp import p4
    
    p4_output = p4('print', '//depot/icecream/db.sqlite3', binary=True)
    sql_bytes = b''.join([item['data'] for item in p4_output[1:]])


Other Options
--------------

By default the `p4` function throws a `P4Error` if Perforce detects an error. If Perforce detects a warning, then the warning is printed. If you would like neither of that functionality (silent mode), then use the `p4swamp` function instead of the `p4` function.

.. code:: python

    from p4swamp import p4swamp

.. _P4 Documentation: https://www.perforce.com/perforce/doc.current/manuals/cmdref/