#!/usr/bin/env python3

import errors

def to_vector(buf, member, mem_handle, num_bits, byteorder):
    begin_offset = buf[int(member['offset'], 16):int(member['offset'], 16)+int(num_bits/8)]
    begin_offset = int.from_bytes(begin_offset, byteorder=byteorder)
    end_offset = buf[int(member['offset'], 16) + 8:int(member['offset'], 16) + 8 + int(num_bits/8)]
    end_offset = int.from_bytes(end_offset, byteorder=byteorder)
    end_cap_offset = buf[int(member['offset'], 16) + 16:int(member['offset'], 16) + 16 + int(num_bits/8)]
    end_cap_offset = int.from_bytes(end_cap_offset, byteorder=byteorder)
 
    if (end_offset - begin_offset) % int(num_bits / 8) != 0: return False
    else: num_entry = int((end_offset - begin_offset) / int(num_bits / 8))

    entry_list = []
    try:
        for i in range(0, num_entry):
            temp = int.from_bytes(mem_handle.get_reader().read(begin_offset + i * 8, 8), byteorder=byteorder)
            if temp == 0:
                raise errors.VectorValueError
            
            entry_list.append(temp)
    except Exception as exception:
        raise errors.VectorValueError
    return entry_list

def to_boolean(buf, member):
    buf = buf[int(member['offset'], 16):int(member['offset'], 16)+1]
    value = int.from_bytes(buf, byteorder='little')
    return value

def to_enum(buf, member, num_bits, is_signed=False, byteorder='little'):
    buf = buf[int(member['offset'], 16):int(member['offset'], 16)+int(num_bits/8)]
    num = int.from_bytes(buf, byteorder=byteorder, signed=is_signed)
    
    return num


def to_interger(buf, member, num_bits=64, is_signed=False, byteorder='little'):

    buf = buf[int(member['offset'], 16):int(member['offset'], 16)+int(num_bits/8)]
    num = int.from_bytes(buf, byteorder=byteorder, signed=is_signed)
    
    return num

def to_string(buf, member, base_addr=None, mem_handle=None, is_nullable=True, byteorder='little', encoding='utf-8'):
   
    buf = buf[int(member['offset'], 16):int(member['offset'], 16)+int(member['size'], 16)]
    str_len = buf[23]
    
    begin_offset = (int(member['offset'], 16) + base_addr if str_len < 23 else int.from_bytes(buf[:8], byteorder=byteorder))
    str_len = (str_len if str_len < 23 else int.from_bytes(buf[8:12], byteorder=byteorder))
    
    if encoding == 'utf-16': str_len = str_len * 2

    if str_len == 0: return ''
    return mem_handle.get_reader().read(begin_offset, str_len).decode(encoding)

def to_pointer(buf, member, num_bits=64, byteorder='little'):
    
    ptr = buf[int(member['offset'], 16):int(member['offset'], 16)+int(num_bits/8)]
    ptr = int.from_bytes(ptr, byteorder=byteorder)

    return ptr