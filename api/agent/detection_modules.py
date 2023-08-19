import pandas as pd
from sklearn.feature_selection import VarianceThreshold
import io
from detect_transformations import detect_transformations

def general_summary(df, n=10):
    """
    Provides the first few rows of the DataFrame.
    
    Parameters:
    - df: DataFrame
    - n: Number of rows to return
    
    Returns:
    - Instructions what transformations to do in general based on a view of the data. 
    """
    # TODO: use only this function as input to tool_making(), possibly experiment with adding some more stats to the prompt
    head = df.head(n)
    buf = io.StringIO()
    df.info(buf=buf)
    s = buf.getvalue()
    numerical = df.describe()
    
    infos = {
        "Description of the Numerical Columns": numerical.to_string(),
        "Head of the DataFrame": head.to_string(),
        "Column Infos": s
    }
    
    steps = detect_transformations(df, infos)
    
    return steps

def datatype_summary(df):
    """
    Provides the data types for each column. 

    Parameters:
    - df: DataFrame

    Returns:
    - Instructions what transformations to do base don the data types. 
    """
    overview = pd.DataFrame({
        'Data Type': df.dtypes,
        'Columns': df.columns,
    })
    
    steps = detect_transformations(df, overview)
    
    return steps
    
def unique_values_summary(df):
    """
    Provides the number of unique values in each column of the dataset.

    Parameters:
    - df: DataFrame

    Returns:
    - Instructions what transformations to do to handle the unique values or lack of them. 
    """
    overview = pd.DataFrame({
        'Column': df.columns,
        'Unique Values': df.nunique(),
        'Percentage': df.nunique() / len(df) * 100
    })
    
    infos = {
        "Unique Values": overview.to_string()
    }
    
    steps = detect_transformations(df, infos)
    return steps

def detect_high_correlation(df, threshold=0.85):
    """
    Detects highly correlated columns in a DataFrame.

    Args:
        df (DataFrame): DataFrame
        threshold (float, optional): Minimum correlation for highly-correlated features. Defaults to 0.85.

    Returns:
        _type_: _description_
    """
    corr_matrix = df.corr()
    correlated_features = set()
    
    for i in range(len(corr_matrix.columns)):
        for j in range(i):
            if abs(corr_matrix.iloc[i, j]) > threshold:
                colname = corr_matrix.columns[i]
                correlated_features.add(colname)
                
    infos = {
        "Highly Correlated Features": correlated_features,
        "Head": df.head().to_string(),
        "Correlation Matrix": corr_matrix.to_string()
    }
    
    steps = detect_transformations(df, infos)
                
    return steps