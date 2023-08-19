import pandas as pd
import numpy as np
import unittest
from transform_modules import fill_missing_values, delete_missing, impute_missing, predict_missing, standardize

class TestTransformModules(unittest.TestCase):
    
    def setUp(self):
        self.df = pd.DataFrame({'A': [1, 2, np.nan, 4], 'B': [5, np.nan, 7, 8], 'C': ['a', 'b', np.nan, 'd']})
    
    def test_fill_missing_values(self):
        filled_df = fill_missing_values(self.df, 'C', 'Unknown')
        self.assertEqual(filled_df.isnull().sum().sum(), 0)
        self.assertEqual(filled_df.loc[2, 'C'], 'Unknown')
        
    def test_delete_missing(self):
        deleted_df = delete_missing(self.df, 'B')
        self.assertEqual(deleted_df.isnull().sum().sum(), 0)
        self.assertEqual(deleted_df.shape[0], 3)
        
    def test_impute_missing(self):
        mean_imputed_df = impute_missing(self.df, 'A', 'mean')
        self.assertEqual(mean_imputed_df.isnull().sum().sum(), 0)
        self.assertEqual(mean_imputed_df.loc[2, 'A'], 2.3333333333333335)
        
        median_imputed_df = impute_missing(self.df, 'A', 'median')
        self.assertEqual(median_imputed_df.isnull().sum().sum(), 0)
        self.assertEqual(median_imputed_df.loc[2, 'A'], 2.0)
        
        mode_imputed_df = impute_missing(self.df, 'C', 'mode')
        self.assertEqual(mode_imputed_df.isnull().sum().sum(), 0)
        self.assertEqual(mode_imputed_df.loc[2, 'C'], 'a')
        
        constant_imputed_df = impute_missing(self.df, 'B', 'constant')
        self.assertEqual(constant_imputed_df.isnull().sum().sum(), 0)
        self.assertEqual(constant_imputed_df.loc[1, 'B'], 0)
        
    def test_predict_missing(self):
        self.df['D'] = [10, 20, 30, np.nan]
        predicted_df = predict_missing(self.df, 'D', ['A', 'B'])
        self.assertEqual(predicted_df.isnull().sum().sum(), 0)
        self.assertEqual(predicted_df.loc[3, 'D'], 40.0)
        
    def test_standardize(self):
        standardized_df = standardize(self.df, 'A')
        self.assertAlmostEqual(standardized_df['A'].mean(), 0)
        self.assertAlmostEqual(standardized_df['A'].std(), 1)