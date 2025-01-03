import os
import pandas as pd
import joblib
import numpy as np

class RF_predict():
    def __init__(self,target1,target2,root,root_model_spi,root_model_bwi):
        self.target1 = target1 #target1 is BWI
        self.target2 = target2 # target2 is SPI
        self.root = root
        self.root_model_spi = root_model_spi
        self.root_model_bwi = root_model_bwi

    def BWI_Predict(self): 
        def Model_1(x):
            file_model = 'model_rf1.pkl'
            file_model = os.path.join(self.root_model_bwi, file_model)
            file_scaler = 'scaler_rf1.pkl'
            file_scaler = os.path.join(self.root_model_bwi, file_scaler)
            scaler_s = joblib.load(file_scaler) 
            model_s = joblib.load(file_model)
            x_test = scaler_s.transform(x)
            y_pred = model_s.predict(x_test)
            return y_pred

        def Model_2(x):
            file_model = 'model_rf2.pkl'
            file_model = os.path.join(self.root_model_bwi, file_model)
            file_scaler = 'scaler_rf2.pkl'
            file_scaler = os.path.join(self.root_model_bwi, file_scaler)
            scaler_s = joblib.load(file_scaler) 
            model_s = joblib.load(file_model)
            x_test = scaler_s.transform(x)
            y_pred = model_s.predict(x_test)
            return y_pred
        
        def Use_Model_RF(element,ley):
            #For BWI
            df = pd.read_excel(self.root)[['Cu%', 'Mo%', 'AgPPM', 'AuPPM', 'Al%', 'Ca%', 'Fe%', 'Mg%', 'Na%', 'S%']]
            mask = df[element] >= ley
            df_filtered = df[mask]
            x_model1 = df_filtered[['Cu%', 'Mo%', 'AgPPM', 'AuPPM', 'Al%', 'Ca%', 'Fe%', 'Mg%', 'Na%', 'S%']]
            m1,m2 = 0.9,0.92
            result_model1 = Model_1(x_model1)*m1
            result_model1 = np.clip(result_model1, 10, 22.5)
            df.loc[mask, self.target1] = result_model1
            df_not_filtered = df[~mask]
            x_model2 = df_not_filtered[['Cu%', 'Mo%', 'AgPPM', 'AuPPM', 'Al%', 'Ca%', 'Fe%', 'Mg%', 'Na%', 'S%']]
            result_model2 = Model_2(x_model2)*m2
            result_model2 = np.clip(result_model2, 9, 20)
            df.loc[~mask, self.target1] = result_model2
            return df
        
        db = Use_Model_RF(element='Na%',ley=1.0)
        return db
    
    def SPI_Predict(self): 
        def Model_1(x):
            file_model = 'model_rf1.pkl'
            file_model = os.path.join(self.root_model_spi, file_model)
            file_scaler = 'scaler_rf1.pkl'
            file_scaler = os.path.join(self.root_model_spi, file_scaler)
            scaler_s = joblib.load(file_scaler) 
            model_s = joblib.load(file_model)
            x_test = scaler_s.transform(x)
            y_pred = model_s.predict(x_test)
            return y_pred

        def Model_2(x):
            file_model = 'model_rf2.pkl'
            file_model = os.path.join(self.root_model_spi, file_model)
            file_scaler = 'scaler_rf2.pkl'
            file_scaler = os.path.join(self.root_model_spi, file_scaler)
            scaler_s = joblib.load(file_scaler) 
            model_s = joblib.load(file_model)
            x_test = scaler_s.transform(x)
            y_pred = model_s.predict(x_test)
            return y_pred
        
        def Use_Model_RF(element,ley):
            #For SPI
            coordenadas = pd.read_excel(self.root)[['X','Y','Z']]
            df = self.BWI_Predict()[['Cu%', 'Mo%', 'AgPPM', 'AuPPM', 'Al%', 'Ca%', 'Fe%', 'Mg%', 'Na%', 'S%','BWI']]
            mask = df[element] >= ley
            m1,m2 = 1.2,0.88
            df_filtered = df[mask]
            x_model1 = df_filtered[['Cu%', 'Mo%', 'AgPPM', 'AuPPM', 'Al%', 'Ca%', 'Fe%', 'Mg%', 'Na%', 'S%','BWI']]
            result_model1 = Model_1(x_model1)*m1
            result_model1 = np.clip(result_model1, 60, 160)
            df.loc[mask, self.target2] = result_model1
            df_not_filtered = df[~mask]
            x_model2 = df_not_filtered[['Cu%', 'Mo%', 'AgPPM', 'AuPPM', 'Al%', 'Ca%', 'Fe%', 'Mg%', 'Na%', 'S%','BWI']]
            result_model2 = Model_2(x_model2)*m2
            result_model1 = np.clip(result_model1, 25, 130)
            df.loc[~mask, self.target2] = result_model2
            df = pd.concat([coordenadas,df],axis=1)
            return df
        df = Use_Model_RF(element='Na%',ley=0.75)
        return df  
        