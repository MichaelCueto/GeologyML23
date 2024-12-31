import os
import pandas as pd
import joblib
import numpy as np
import traceback
from params import features
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestRegressor

class use_predict():
    def __init__(self,root_data, root_model):
        self.root_data = root_data
        self.root_model = root_model

    def model_predict(self,x):
        try:
            file_scaler = 'scaler_rf.pkl'
            file_model_spi = 'model_rf_spi.pkl'
            file_model_bwi = 'model_rf_bwi.pkl'
            file_scaler = os.path.join(self.root_model, file_scaler)
            file_model_spi = os.path.join(self.root_model, file_model_spi)
            file_model_bwi = os.path.join(self.root_model, file_model_bwi)
            
            scaler_s = joblib.load(file_scaler)
            print(f"Cargando scaler desde: {file_scaler}")

            model_spi = joblib.load(file_model_spi)
            print(f"Cargando modelo SPI desde: {file_model_spi}")

            model_bwi = joblib.load(file_model_bwi)
            print(f"Cargando modelo BWI desde: {file_model_bwi}")
            
            print(f"Datos originales para predicción: {x.head()}")
            x_test = scaler_s.transform(x)
            x_test = pd.DataFrame(x_test, columns=x.columns)
            print(f"Datos transformados (x_test): {x_test.head()}")
            
            spi_pred = model_spi.predict(x_test)
            print("Realizado predicciones con modelo SPI.")
            
            bwi_pred = model_bwi.predict(x_test)
            print("Realizado predicciones con modelo BWI.")
            return spi_pred, bwi_pred
        
        except Exception as e:
            traceback.print_exc()  # Imprime el stack trace para depuración
            raise RuntimeError(f"Error en model_predict: {e}")

    def Use_Model_RF(self):
        try:
            # Leer archivo CSV
            print(f"Intentando leer el archivo: {self.root_data}")
            df = pd.read_csv(self.root_data)
            
            # Verificar columnas requeridas
            print(f"Columnas del archivo: {df.columns.tolist()}")
            missing_features = [col for col in features if col not in df.columns]
            if missing_features:
                raise ValueError(f"Faltan las siguientes columnas requeridas: {missing_features}")

            # Seleccionar características
            coordenedas = df[['X','Y','Z']]
            db = df[features]
    
            # Realizar predicciones
            spi_pred, bwi_pred = self.model_predict(db)
            # Agregar predicciones al DataFrame
            db['SPI'] = spi_pred
            db['BWI'] = bwi_pred
            db_final = pd.concat([coordenedas, db], axis=1)
            return db_final
            print("Predicciones realizadas exitosamente.")

        except FileNotFoundError as e:
            raise RuntimeError(f"No se encontró el archivo: {e}")
        except pd.errors.EmptyDataError:
            raise RuntimeError(f"El archivo {self.root_data} está vacío o es inválido.")
        except Exception as e:
            traceback.print_exc()
            raise RuntimeError(f"Error durante el procesamiento en Use_Model_RF: {e}")