import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.preprocessing import StandardScaler,MinMaxScaler
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.svm import SVR
from sklearn.model_selection import GridSearchCV, cross_validate, cross_val_score, RandomizedSearchCV
import warnings
import joblib
import os
import math
warnings.filterwarnings("ignore")

class GeologyML():
    def __init__(self,target,element,ley):
        self.target = target
        self.element = element
        self.ley = ley

    def Grafics_ML(self,y_train,yp):
        # Primera gráfica de líneas
        fig, ax1 = plt.subplots(figsize=(12, 6))
        t = np.arange(0, len(yp), 1)
        ax1.plot(t, yp, label='Predicciones', color='blue')
        ax1.plot(t, y_train, label='Datos reales', color='orange')
        ax1.set_ylabel(self.target)
        ax1.grid(True)
        ax1.legend()

        # Segunda gráfica de scatter plot
        fig2, ax2 = plt.subplots(figsize=(8, 8))
        ax2.scatter(y_train, yp, label='y_train vs yp', color='green', alpha=0.5)
        ax2.set_xlabel('y_train')
        ax2.set_ylabel('Predicciones')
        ax2.grid(True)
        ax2.legend()
        plt.show()

    def Assay_Limit(self,data):
        df1 = data.loc[data[self.element] >= self.ley]
        df2 = data.loc[data[self.element] < self.ley]
        return df1,df2

    def RF_Best_Params(self,X,y,search_all):
        #print('Best Parameters of Random Forest Ramdomorized')
        rg = {'bootstrap': [True, False], 
                'max_depth': [500,750,1000,None],
                'max_features': ['auto','sqrt','log2',0.2,0.3,0.6,0.9], 
                'min_samples_leaf': [1,2,4,16,32,64,128],
                'min_samples_split': [2,5,10,20,40,80], 
                'n_estimators': [1000, 1200, 1400, 1600, 1800, 2000]}
        if search_all:
                gsc = GridSearchCV(estimator=RandomForestRegressor(), param_grid=rg,
                                cv=5, verbose=0, n_jobs=-1)
        else:
                gsc = RandomizedSearchCV(estimator=RandomForestRegressor(), param_distributions=rg, n_iter=100,
                                cv=5, verbose=0, random_state=42,n_jobs=-1)
        grid_result = gsc.fit(X, y)
        best_params = grid_result.best_params_
        return best_params

    def RF_Scoring(self,X,y,params,root_model,name):
        rfr = RandomForestRegressor(max_depth=params["max_depth"], n_estimators=params["n_estimators"],
                                min_samples_leaf=params["min_samples_leaf"],max_features= params["max_features"],
                                        min_samples_split=params["min_samples_split"],bootstrap=params["bootstrap"],
                                        verbose=0, warm_start=True,random_state=42,n_jobs=-1)
        #print("Best Params: ",params)
        rfr.fit(X, y)
        file_model= name +'.pkl'
        file_model = os.path.join(root_model, file_model)
        joblib.dump(rfr,file_model)

        # print("Scoring Analysis and Graphics")
        # scoring = {'abs_error': 'neg_mean_absolute_error', 'squared_error': 'neg_mean_squared_error', 'r2': 'r2','explained_variance': 'explained_variance'}
        # scores = cross_validate(rfr, X, y, cv=10, scoring=scoring, return_train_score=True)
        # print("Random Forest Regression Analysis")
        # print("MAE :", abs(scores['train_abs_error'].mean()), "| RMSE :",
        #         math.sqrt(abs(scores['train_squared_error'].mean())),
        #         "| R2 :", scores['train_r2'].mean(), "| EV :", scores['train_explained_variance'].mean())
        yp = rfr.predict(X)
        #self.Grafics_ML(y, yp)


    def RF_Model(self,root,root_model):
        if self.target == 'BWI':
            df = pd.read_excel(root)
            df = df.sample(frac=1)
            df1, df2  = self.Assay_Limit(df)
            X1 = df1[['Cu%', 'Mo%','AgPPM', 'AuPPM', 'Al%', 'Ca%', 'Fe%', 'Mg%', 'Na%', 'S%']]
            y1 = df1[self.target]
            X2 = df2[['Cu%', 'Mo%','AgPPM', 'AuPPM', 'Al%', 'Ca%', 'Fe%', 'Mg%', 'Na%', 'S%']]
            y2 = df2[self.target]
            # X1_train, X1_test, y1_train, y1_test = train_test_split(X1, y1, test_size=0.2, random_state=42)
            # X2_train, X2_test, y2_train, y2_test = train_test_split(X2, y2, test_size=0.2, random_state=42)
        if self.target == 'SPI':
            df = pd.read_excel(root)
            df = df.sample(frac=1)
            df1, df2  = self.Assay_Limit(df)
            X1 = df1[['Cu%', 'Mo%','AgPPM', 'AuPPM', 'Al%', 'Ca%', 'Fe%', 'Mg%', 'Na%', 'S%','BWI']]
            y1 = df1[self.target]
            X2 = df2[['Cu%', 'Mo%','AgPPM', 'AuPPM', 'Al%', 'Ca%', 'Fe%', 'Mg%', 'Na%', 'S%','BWI']]
            y2 = df2[self.target]
            
        # Normalizar los datos
        scaler1 = MinMaxScaler(feature_range=(0,1))
        scaler1.fit(X1)
        X1 = scaler1.transform(X1)
        file_scaler1= 'scaler_rf1.pkl'
        file_scaler1 = os.path.join(root_model, file_scaler1)
        joblib.dump(scaler1,file_scaler1)

        scaler2 = MinMaxScaler(feature_range=(0,1))
        scaler2.fit(X2)
        X2 = scaler2.transform(X2)
        file_scaler2= 'scaler_rf2.pkl'
        file_scaler2 = os.path.join(root_model, file_scaler2)
        joblib.dump(scaler2,file_scaler2)
        
        best_params_1 = self.RF_Best_Params(X1,y1,search_all=False)
        best_params_2 = self.RF_Best_Params(X2,y2,search_all=False)
        
        self.RF_Scoring(X1,y1,best_params_1,root_model,name='model_rf1')
        self.RF_Scoring(X2,y2,best_params_2,root_model,name='model_rf2')
                


        
    
