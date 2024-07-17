#!/usr/bin/env python3

import string
import errors
    
def validate_vector(buf, member, mem_handle, num_bits, is_nullable, byteorder):
    begin_offset = buf[int(member['offset'], 16):int(member['offset'], 16) + int(num_bits/8)]
    begin_offset = int.from_bytes(begin_offset, byteorder=byteorder)
    end_offset = buf[int(member['offset'], 16) + 8:int(member['offset'], 16) + 8 + int(num_bits/8)]
    end_offset = int.from_bytes(end_offset, byteorder=byteorder)
    end_cap_offset = buf[int(member['offset'], 16) + 16:int(member['offset'], 16) + 16 + int(num_bits/8)]
    end_cap_offset = int.from_bytes(end_cap_offset, byteorder=byteorder)

    validate_pointer(begin_offset, None, num_bits, mem_handle, byteorder, is_nullable, is_ptr_val=True)
    validate_pointer(end_offset, None, num_bits, mem_handle, byteorder, is_nullable, is_ptr_val=True)
    validate_pointer(end_cap_offset, None, num_bits, mem_handle, byteorder, is_nullable, is_ptr_val=True)
    
    if (end_offset - begin_offset) % int(num_bits / 8) != 0: return False
    else: num_entry = int((end_offset - begin_offset) / int(num_bits / 8))
    
    assert num_entry > 0 and num_entry < 10000
    
    try:
        for i in range(0, num_entry):
            temp = int.from_bytes(mem_handle.get_reader().read(begin_offset + i * 8, 8), byteorder=byteorder)
            validate_pointer(temp, member, num_bits, mem_handle, byteorder, is_nullable, is_ptr_val=True)
    except Exception as exception:
        raise errors.VectorValueError
    
    return True
    
def validate_pointer(buf, member, num_bits, mem_handle, byteorder='little', is_nullable=False, is_ptr_val = False):
    if is_ptr_val == False:
        off = int(member['offset'], 16)
        ptr = buf[off : off+(num_bits//8)]
        ptr = int.from_bytes(ptr, byteorder=byteorder)
    else: ptr = buf

    if ptr == 0 and is_nullable: return True
    if ptr == 0 and not is_nullable: return False
    if not ptr < 0x800000000000: return False

    return True
    # try:
    #     mem_handle.get_reader().read(ptr, 1)
    # except:
    #     return False

def validate_boolean(buf, member):
    buf = buf[int(member['offset'], 16):int(member['offset'], 16)+1]
    return buf in (b'\x00', b'\x01')

def validate_enum(buf, member, num_bits, is_signed=False, byteorder='little'):
    buf = buf[int(member['offset'], 16):int(member['offset'], 16)+int(num_bits/8)]
    num = int.from_bytes(buf, byteorder=byteorder, signed=is_signed)

    ret = num in (member['available_values'])
    return ret

def validate_interger(buf, member, num_bits=64, is_signed=False, byteorder='little', num=None):
    
    if not num:
        buf = buf[int(member['offset'], 16):int(member['offset'], 16)+int(num_bits/8)]
        num = int.from_bytes(buf, byteorder=byteorder, signed=is_signed)
    # unsigned
    if num_bits == 16 and is_signed == False:
        if num <= 65535 and num >= 0: return True
        else: return False
    elif num_bits == 32 and is_signed == False:
        if num <= 4294967295 and num >= 0: # maximum value for unsigned int32
            return True
        else: return False
    elif num_bits == 64 and is_signed == False:
        if num <= 18446744073709551615 and num >= 0: # maximum value for unsigned int64
            return True
        else: return False
    
    # signed 
    if num_bits == 16 and is_signed == True:
        if num <= 32767 and num >= -32768: # range of signed int16 
            return True 
        else: return False
    elif num_bits == 32 and is_signed == True: 
        if num <= 2147483647 and num >= -2147483648: # range of signed int32  
            return True  
        else: return False   
    elif num_bits == 64 and is_signed == True :  
       if (num <= 9223372036854775807) and (num >= -9223372036854775808): # range of signed int64   
           return True   
       else: return False
    else: return False
    

def validate_string(buf, member, base_addr=None, mem_handle=None, is_nullable=True, byteorder='little', encoding='utf-8'):
    
    buf = buf[int(member['offset'], 16):int(member['offset'], 16)+int(member['size'], 16)]
    str_len = buf[23]
    
    begin_offset = (int(member['offset'], 16)+base_addr if str_len < 23 else int.from_bytes(buf[:8], byteorder=byteorder))
    str_len = (str_len if str_len < 23 else int.from_bytes(buf[8:12], byteorder=byteorder))

    if encoding == 'utf-16': str_len = str_len * 2

    try:
        if str_len == 0:
            return True if is_nullable == True else False
        
        str = mem_handle.get_reader().read(begin_offset, str_len).decode(encoding)
        if not all(c in string.printable for c in str):
            raise errors.NullException

    except Exception as exception:
        return False
    
    return True
