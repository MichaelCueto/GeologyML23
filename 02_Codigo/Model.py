import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split

class Model():
    def __init__(self,root):
        self.data = ''
        self.root = root

    def Load_Data(self):
        self.data = pd.read_excel(self.root)

    def Norm_Data(self):
        data = pd.read_csv
        

        
    
