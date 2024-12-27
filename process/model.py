import os
import joblib
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from clean_data import Clean
from params import rg
from sklearn.model_selection import train_test_split, RandomizedSearchCV, cross_validate
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.preprocessing import MinMaxScaler
import warnings
warnings.filterwarnings("ignore")


class DurezaModel:
    def __init__(self, data_path, features, target, models_dir="models"):
        self.data_path = data_path
        self.target = target
        self.features = features
        self.models_dir = models_dir
        os.makedirs(self.models_dir, exist_ok=True)  # Crear carpeta de modelos

    def split_data(self, split=True):
        """Divide los datos en entrenamiento y prueba, o usa todo el conjunto de datos."""
        df = Clean(self.data_path).Null_Analysis()
        X = df[self.features]
        y = df[self.target]
        
        if split:
            return train_test_split(X, y, test_size=0.2, random_state=42)
        else:
            return X, X, y, y  # Usa todo el conjunto para entrenamiento

    def scaler_data(self, split=True, save_scaler=True):
        """Escala los datos utilizando MinMaxScaler."""
        X_train, X_test, y_train, y_test = self.split_data(split=split)
        scaler = MinMaxScaler(feature_range=(0, 1))
        X_train = scaler.fit_transform(X_train)
        X_test = scaler.transform(X_test)

        if save_scaler:
            scaler_path = os.path.join(self.models_dir, "scaler_rf.pkl")
            joblib.dump(scaler, scaler_path)
        return X_train, X_test, y_train, y_test

    def rfr_best_params(self, split=True):
        """Encuentra los mejores parámetros para RandomForestRegressor."""
        gsc = RandomizedSearchCV(
            estimator=RandomForestRegressor(),
            param_distributions=rg,
            n_iter=50,
            cv=5,
            verbose=0,
            random_state=42,
            n_jobs=-1
        )
        X_train, _, y_train, _ = self.scaler_data(split=split, save_scaler=True)
        grid_result = gsc.fit(X_train, y_train)
        return grid_result.best_params_

    def rfr_model(self, split=True, save_model=True):
        """Entrena el modelo RandomForestRegressor y predice valores."""
        best_params = self.rfr_best_params(split=split)
        rfr = RandomForestRegressor(
            **best_params, random_state=42, n_jobs=-1
        )
        X_train, X_test, y_train, y_test = self.scaler_data(split=split, save_scaler=False)
        rfr.fit(X_train, y_train)

        if save_model:
            model_path = os.path.join(self.models_dir, "model_rf.pkl")
            joblib.dump(rfr, model_path)

        y_pred = rfr.predict(X_test)
        self.ml_graphics(y_test, y_pred)
        self.scoring_analysis(rfr,X_train,y_train)

    def ml_graphics(self, y_real, y_pred):
        """Mostrar Graficas de Real vs Predicho"""

        # Convertir a NumPy arrays si aún no lo son
        y_real = np.array(y_real).flatten()
        y_pred = np.array(y_pred).flatten()

        # Calcular los límites mínimos y máximos
        min_val = min(y_real.min(), y_pred.min())
        max_val = max(y_real.max(), y_pred.max())

        # Crear la figura
        fig, axes = plt.subplots(1, 2, figsize=(14, 6))

        # ------------------------ Scatter Plot ------------------------
        axes[0].scatter(y_real, y_pred, color='royalblue', alpha=0.7, label='Valores')
        axes[0].plot([min_val, max_val], [min_val, max_val],
                    color='red', linestyle='--', label='Función identidad')  # Línea identidad
        axes[0].set_title("Valores Reales vs Predichos")
        axes[0].set_xlabel("Valores Reales")
        axes[0].set_ylabel("Valores Predichos")
        axes[0].legend()
        axes[0].grid(True)

        # ------------------------ Distribución con Seaborn ------------------------
        sns.histplot(y_real, color='skyblue', alpha=0.7, label='Reales', kde=True, ax=axes[1])
        sns.histplot(y_pred, color='orange', alpha=0.7, label='Predichos', kde=True, ax=axes[1])

        axes[1].set_title("Distribución de Valores Reales vs Predichos")
        axes[1].set_xlabel("Valor")
        axes[1].set_ylabel("Densidad")
        axes[1].legend()
        axes[1].grid(True)

        # Guardar el gráfico
        plt.tight_layout()
        output_path = os.path.join(self.models_dir, "real_vs_predicho.png")
        plt.savefig(output_path, dpi=300, bbox_inches="tight")
        plt.close(fig)
        print(f"Gráfico guardado en: {output_path}")
    
    def scoring_analysis(self,model,X,y):
        print("Scoring Analysis and Graphics")
        scoring = {'abs_error': 'neg_mean_absolute_error', 'squared_error': 'neg_mean_squared_error', 'r2': 'r2','explained_variance': 'explained_variance'}
        scores = cross_validate(model, X, y, cv=5, scoring=scoring, return_train_score=True)
        print("MAE :", abs(scores['test_abs_error'].mean()) ,
                "| R2 :", scores['test_r2'].mean(), 
                "| EV :", scores['test_explained_variance'].mean())
