# -*- coding: cp936 -*-
#!/usr/bin/env python

# Author: Quinn Song
# add_brackets.py: insert one or two pairs of brackets randomly;
# add return a valid expression

import random
import re

def apply_pattern1 (source):
    """
    Add brakets using pattern 1
    """
    source = re.sub('([+*/-])(?!\(|\d+\))', '\g<1>(',source, count = 1)
    return re.sub('(\(\d+[+*/-]\d+)([+*/-]*)', '\g<1>)\g<2>',source, count = 1)
    
def apply_pattern2(source):
    """
    Add brackets using the lambda functions of four patterns
    """
    f0 = lambda s: re.sub(r'^(.*[+*/-].*)((?:[+*/-]\d+)+)', '(\g<1>)\g<2>', s)
    f1 = lambda s: re.sub('(\d+[+*/-])(.*[+*/-].*)$', '\g<1>(\g<2>)',s)
    f2 = lambda s: re.sub('(\d+[+*/-])(.*[+*/-].*)([+*/-]\d+)$', '\g<1>(\g<2>)\g<3>',s)
    f3 = lambda s: re.sub('(\d+[+*/-])((?:\d+[+*/-]){1,3}\d+)([+*/-]\d+)$', '\g<1>(\g<2>)\g<3>',s)
    f = [ f0, f1, f2, f3 ]
    choice = random.randint(0, 3)
    return f[choice](source)
    
def add_br (source):
    """
    Apply patterns randomly based on defined list
    """
    none = lambda x: x
    g = [ apply_pattern1, apply_pattern2, none]
    choice = random.choice([0, 0, 1, 1, 1, 1, 2, 2])
    return g[choice](source)
    
def main (source):
    """
    Main function
    """
    tmp = add_br(source)
    return add_br(tmp) if random.choice([True, False]) else tmp
    
if __name__ == '__main__':
    #op = '1+2-3*5/8-9+20*3-6'
    op = '27+4*41-5+7-11'
    print main(op)

    
    
