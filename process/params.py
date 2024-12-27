features = ['Cu%','Mo%','AgPPM','AuPPM','Al%','Ca%','Fe%','Mg%','Na%','S%']
target = ['SPI']
# target_bwi = ['BWI']

rg = {'bootstrap': [True, False], 
          'max_depth': [5,10,15,None],
          'max_features': ['auto', 0.2, 0.5, 0.9], 
          'min_samples_leaf': [1,2,4,16],
          'min_samples_split': [2,5,10], 
          'n_estimators': [200, 400, 600]}