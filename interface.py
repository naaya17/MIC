#!/usr/bin/env python3
from abc import ABC, abstractmethod

    
class Object(ABC):
    """Represents a object of a data structure with its default class member."""
    def __init__(self, mem_handle, base_addr):
        self._mem_handle = mem_handle
        self._base_addr = base_addr
        self._buf = None

    @abstractmethod
    def validate():
        pass

    @property
    def base_addr(self):
        return self._base_addr
    
    def __str__(self):
       """Return a string representation of the object."""

       members = []
       for key, value in vars(self).items():
        if key == '_mem_handle' or key == '_buf':
           continue
        if key == 'struct_size':
           value = "\""+value+"\""
        if isinstance(value, dict):
            if 'value' in value:
               members.append(f'"{key}":\"{value["value"]}\"')
               continue
            else:
               members.append(f'"{key}":\"{"No value"}\"')
               continue
        members.append(f'"{key}":{value}')
       nl = ', \n'
       return f"{{{nl.join(members)}}}"
