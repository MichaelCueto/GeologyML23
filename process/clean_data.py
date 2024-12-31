import pandas as pd
from sklearn.impute import KNNImputer
from params import features
import warnings
warnings.filterwarnings("ignore")

class Clean:
    def __init__(self, root):
        self.root = root

    def Get_Data(self):
        """Lee los datos desde un archivo CSV."""
        return pd.read_csv(self.root)

    def Null_Analysis(self):
        """Completa valores faltantes usando KNNImputer solo en columnas seleccionadas."""
        df = self.Get_Data()
        df_features = df[features]
        coordenadas = df[['X','Y','Z']]
        imputer = KNNImputer(n_neighbors=4)
        df_features_imputed = imputer.fit_transform(df_features)
        df_features_imputed = pd.DataFrame(df_features_imputed, columns=features)
        other_columns = df.drop(columns=features + ['X', 'Y', 'Z'])
        df_final = pd.concat([coordenadas, df_features_imputed, other_columns.reset_index(drop=True)], axis=1)
        return df_final

        

