.. image:: https://travis-ci.org/jgirardet/dtc.svg?branch=master
    :target: https://travis-ci.org/jgirardet/dtc

.. image:: https://ci.appveyor.com/api/projects/status/ffd44ndqx713yuhd/branch/master?svg=true
    :target: https://ci.appveyor.com/project/jgirardet/dtc

=======================================================
DTC :"Generate Dataclasses without writting them !"
=======================================================


.. warning::
		
	This is an alpha version


Basic Usage
------------

Dataclass instance lazy building from json
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python
		
	    >>> import dtc
	    >>> JSON = b"""{"flooat": 12.564, "boolean": true, "integer": 12}"""
	    >>> my_class = dtc.from_json(JSON)
	    >>> my_class
	    Base(flooat=12.564, boolean=True, integer=12)
	    >>> from dataclasses import *
	    >>> is_dataclass(my_class)
	    True
	    >>> JSON = b"""[{"flooat": 12.4, "boolean": true, "integer": 1}, {"flooat": 12.564, "boolean": true, "integer": 12},{"flooat": 1.4, "boolean": false, "integer": 0}]"""
	    # parse from json object or list
	    >>> dtc.from_json(JSON
		[Base(flooat=12.4, boolean=True, integer=1), Base(flooat=12.564, boolean=True, integer=12), Base(flooat=1.4, boolean=False, integer=0)]

	

Get dataclass implementation code
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python
		
		>>> my_class = dtc.from_json(JSON)

		>>> code = dtc.format_class(my_class)
		>>> print(code)
		@dataclass
		class Base:
		    flooat: float
		    boolean: bool
		    integer: int
			
		# Et Voilà !



* License : GNU General Public License v3 or later (GPLv3+) 
* Source: https://github.com/jgirardet/dtc


