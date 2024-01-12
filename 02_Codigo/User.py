from Model import GeologyML 
from Predict import RF_predict
import pandas as pd

class user_class():
    def __init__(self):
        pass

    def Generate_Model(self,root):
        root_model_bwi = '../04_Model/Hardness/BWI/BWI_1ley/'
        root_model_spi = '../04_Model/Hardness/SPI/SPI_1ley/'
        GeologyML(target='SPI',element='Na%',ley=1).RF_Model(root,root_model_spi)
        GeologyML(target='BWI',element='Na%',ley=1).RF_Model(root,root_model_bwi)

    def Generate_Data(self,root,root_bbdd):
        target1 = 'BWI'
        target2 = 'SPI'
        root_model_bwi = '../04_Model/Hardness/BWI/BWI_1ley/'
        root_model_spi = '../04_Model/Hardness/SPI/SPI_1ley/'
        df = RF_predict(target1,target2,root,root_model_spi,root_model_bwi).SPI_Predict()
        df.to_csv(root_bbdd, index=False)

#Generate_Model
# user_class().Generate_Model(root='../03_BBDD/data_dureza_train.xlsx')
# user_class().Generate_Model(root='../03_BBDD/data_dureza_train.xlsx',root_bbdd='../03_BBDD/Resultados_Dureza.xlsx')