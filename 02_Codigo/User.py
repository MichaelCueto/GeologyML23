from Model import GeologyML 
from Predict import RF_predict
import pandas as pd

class user_class():
    def __init__(self):
        pass

    def Generate_Model(self,root):
        root_model_bwi = '../04_Model/Hardness/BWI/'
        root_model_spi = '../04_Model/Hardness/SPI/'
        GeologyML(target='BWI',element='Na%',ley=1).RF_Model(root,root_model_bwi)
        GeologyML(target='SPI',element='Na%',ley=1).RF_Model(root,root_model_spi)
       

    def Generate_Data(self,root,root_bbdd):
        target1 = 'BWI'
        target2 = 'SPI'
        root_model_bwi = '../04_Model/Hardness/BWI/'
        root_model_spi = '../04_Model/Hardness/SPI/'
        df = RF_predict(target1,target2,root,root_model_spi,root_model_bwi).SPI_Predict()
        df.to_excel(root_bbdd, index=False)