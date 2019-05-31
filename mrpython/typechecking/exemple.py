#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed May 15 11:36:47 2019

@author: 3535008
"""

def get_max(L):
    """list[int]->int"""
    
    #val_max:int
    val_max = 0
    #x:int
    for x in L:
        if x > val_max:
            val_max = x
    
    return val_max