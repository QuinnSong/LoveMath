#!/usr/bin/env python

# Author: Quinn Song
# kidsmode.py: use regex patterns to check if expression is valid;
# add return True or False

import random
import re

# Regex patterns to validate exp
MD_PATTERN = '(\d+(\*|/)\d+)'  ## * AND /
AM_PATTERN = '(\d+(\+|-)\d+)'  ## + AND -
BRA_PATTERN = '.*?(\([^)(]+\))' ## ( AND )

def replace_mul_div (exp, pattern, num_limit):
    """
    1) for * and /, make sure all ops result is in range limit
    2) for /, make sure there is no reminder
    3) finally replace * and / with actual result values
    """
    while re.findall(pattern, exp):
        md = re.findall(pattern, exp)
        if eval(md[0][0]) not in range(0, num_limit + 1):
            exp = None
            break
        if md[0][1] == '/':
            i,j = md[0][0].split('/')
            if int(i)%int(j) != 0:
                exp = None
                break
        exp = exp.replace(md[0][0], str(eval(md[0][0]))) 
    return exp

def replace_bras (exp, num_limit):
    """
    1) for (), make sure all ops result is in range limit
    2) finally replace () with actual result values
    """
    
    while re.findall(BRA_PATTERN, exp):
        bras = re.findall(BRA_PATTERN, exp)
        if any(eval(a) not in range(0, num_limit + 1) for a in bras):
            exp = None
            break
        for b in bras:
            tmp = check_in_bras (b.strip(')('), num_limit)
            if not tmp:
                exp = None
                break
            else:
                exp = exp.replace(b, str(eval(b)))
        if not exp: break
    return exp

def check_in_bras (exp, num_limit):
    """
    Check if the exp inside () is valid
    """
    exp = replace_mul_div(exp, MD_PATTERN, num_limit)
    if not exp:
        return False
    exp = replace_mul_div(exp, AM_PATTERN, num_limit)
    return True if exp else False

def isExpValid(exp, num_limit):
    """
    Main function to validate a expression
    """
    if eval(exp) not in range(0, num_limit + 1):
        return False

    exp = replace_bras (exp, num_limit)
    if exp and check_in_bras (exp, num_limit):
        return True
    else: return False

if __name__ == '__main__':
    #print isExpValid('((5+2)*1+3-10)+2*3', 5)
    #print isExpValid('6+(3-2)+5', 6)
    print isExpValid('(6-3)*6', 10)

    
        
    
    