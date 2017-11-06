

import pandas as pd
import  numpy as np

if __name__=='__main__':
    filename = open('Result/listenSession.txt')
    print(len(filename.readline().split(']')))
