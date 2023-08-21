
import pandas as pd
import hashlib
import random
import string
import re
import numpy as np
from sklearn.preprocessing import StandardScaler, MinMaxScaler, LabelEncoder, PolynomialFeatures
from fuzzywuzzy import process
from sklearn.linear_model import LinearRegression
from nltk.tokenize import word_tokenize
from nltk.stem import PorterStemmer, WordNetLemmatizer
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from gensim.models import Word2Vec
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis as LDA
from statsmodels.tsa.seasonal import seasonal_decompose
from nltk.corpus import stopwords
import nltk

def fill_missing_values(df, col, value="Unknown"):
    """
    Fill missing values in the dataframe with given value.
    
    Parameters:
        df (DataFrame): Input DataFrame.
        col (str): Name of the column.
        value (str): Value to fill missing values with.
        
    Returns:
        DataFrame: DataFrame with handled missing values.
    """

    # Fill missing values
    df = df.fillna({col: "Unknown"})

    return df

def delete_missing(df, column):
    """
    Remove rows with missing values for a specific column.

    Parameters:
    - df: DataFrame
    - column: Column name as a string

    Returns:
    - DataFrame without rows containing missing values for the specified column
    """
    return df.dropna(subset=[column])

def impute_missing(df, column, strategy='mean'):
    """
    Fill missing values using various techniques.

    Parameters:
    - df: DataFrame
    - column: Column name as a string
    - strategy: Imputation strategy ('mean', 'median', 'mode', or 'constant')
    
    Returns:
    - DataFrame with imputed values for the specified column
    """
    if strategy == 'mean':
        df[column].fillna(df[column].mean(), inplace=True)
    elif strategy == 'median':
        df[column].fillna(df[column].median(), inplace=True)
    elif strategy == 'mode':
        df[column].fillna(df[column].mode()[0], inplace=True)
    elif strategy == 'constant':
        df[column].fillna(0, inplace=True)  # This fills with zero, but you can replace it with any constant value
    return df

def predict_missing(df, column, features):
    """
    Use a machine learning model (Linear Regression) to predict and fill missing values.

    Parameters:
    - df: DataFrame
    - column: The target column with missing values
    - features: List of feature column names

    Returns:
    - DataFrame with predicted values for the missing values in the specified column
    """
    train = df.dropna()
    test = df[df[column].isna()]

    model = LinearRegression()
    model.fit(train[features], train[column])
    predictions = model.predict(test[features])

    df.loc[df[column].isna(), column] = predictions
    return df

def standardize(df, column):
    """
    Standardize a column to have mean=0 and variance=1.

    Parameters:
    - df: DataFrame
    - column: Column name as a string

    Returns:
    - DataFrame with standardized values for the specified column
    """
    scaler = StandardScaler()
    df[column] = scaler.fit_transform(df[[column]])
    return df

def minmax_scale(df, column):
    """
        Apply Min-Max scaling to a column.

        Parameters:
        - df: DataFrame
        - column: Column name as a string

        Returns:
        - DataFrame with Min-Max scaled values for the specified column
    """
    scaler = MinMaxScaler()
    df[column] = scaler.fit_transform(df[[column]])
    return df

import numpy as np

def log_transform(df, column):
    """
    Apply log transformation to a column.

    Parameters:
    - df: DataFrame
    - column: Column name as a string

    Returns:
    - DataFrame with log-transformed values for the specified column
    """
    df[column] = np.log(df[column])
    return df

def one_hot_encode(df, column):
    """
    One-hot encode a categorical column.

    Parameters:
    - df: DataFrame
    - column: Column name as a string

    Returns:
    - DataFrame with one-hot encoded columns for the specified column
    """
    return pd.get_dummies(df, columns=[column], drop_first=True)

def label_encode(df, column):
    """
    Label encode a categorical column.

    Parameters:
    - df: DataFrame
    - column: Column name as a string

    Returns:
    - DataFrame with label encoded values for the specified column
    """
    le = LabelEncoder()
    df[column] = le.fit_transform(df[column])
    return df

def frequency_encode(df, column):
    """
    Frequency encode a categorical column.

    Parameters:
    - df: DataFrame
    - column: Column name as a string

    Returns:
    - DataFrame with frequency encoded values for the specified column
    """
    freq = df[column].value_counts()
    df[column + "_freq_encode"] = df[column].map(freq)
    return df

def create_polynomial_features(df, columns, degree=2):
    """
    Create polynomial features for specified columns.

    Parameters:
    - df: DataFrame
    - columns: List of column names
    - degree: Degree of polynomial features

    Returns:
    - DataFrame with polynomial features for the specified columns
    """
    poly = PolynomialFeatures(degree=degree, include_bias=False)
    new_features = poly.fit_transform(df[columns])
    new_cols = poly.get_feature_names_out(columns)
    df = pd.concat([df, pd.DataFrame(new_features, columns=new_cols, index=df.index)], axis=1)
    return df

def create_interaction_term(df, col1, col2):
    """
    Create an interaction term between two columns.

    Parameters:
    - df: DataFrame
    - col1, col2: Names of the two columns

    Returns:
    - DataFrame with a new interaction term column
    """
    df[f"{col1}_x_{col2}"] = df[col1] * df[col2]
    return df

def tokenize_text(df, column):
    """
    Tokenize the text in the specified column.

    Parameters:
    - df: DataFrame
    - column: Name of the text column to tokenize

    Returns:
    - DataFrame with a new column containing tokenized text
    """
    df[column + "_tokens"] = df[column].apply(word_tokenize)
    return df

def stem_text(df, column):
    """
    Apply stemming to the specified text column.

    Parameters:
    - df: DataFrame
    - column: Name of the text column to stem

    Returns:
    - DataFrame with a new column containing stemmed text
    """
    stemmer = PorterStemmer()
    df[column + "_stemmed"] = df[column].apply(lambda x: ' '.join([stemmer.stem(word) for word in word_tokenize(x)]))
    return df

def lemmatize_text(df, column):
    """
    Lemmatize the text in the specified column.

    Parameters:
    - df: DataFrame
    - column: Name of the text column to lemmatize

    Returns:
    - DataFrame with a new column containing lemmatized text
    """
    lemmatizer = WordNetLemmatizer()
    df[column + "_lemmatized"] = df[column].apply(lambda x: ' '.join([lemmatizer.lemmatize(word) for word in word_tokenize(x)]))
    return df

def tfidf_vectorize(df, column):
    """
    Convert text column to TF-IDF vectors.

    Parameters:
    - df: DataFrame
    - column: Name of the text column to vectorize

    Returns:
    - DataFrame with TF-IDF vectorized columns
    """
    vectorizer = TfidfVectorizer()
    vectors = vectorizer.fit_transform(df[column])
    return pd.DataFrame(vectors.toarray(), columns=vectorizer.get_feature_names_out())

def count_vectorize(df, column):
    """
    Convert text column to Count Vectors.

    Parameters:
    - df: DataFrame
    - column: Name of the text column to vectorize

    Returns:
    - DataFrame with Count Vectorized columns
    """
    vectorizer = CountVectorizer()
    vectors = vectorizer.fit_transform(df[column])
    return pd.DataFrame(vectors.toarray(), columns=vectorizer.get_feature_names_out())

def get_word2vec_embeddings(sentences, size=100, window=5, min_count=1, workers=4):
    """
    Get Word2Vec embeddings for provided sentences.

    Parameters:
    - sentences: List of tokenized sentences
    - size: Dimension of the embedding vectors
    - window: Maximum distance between the current and predicted word within a sentence
    - min_count: Ignores all words with total frequency lower than this
    - workers: Number of CPU cores to use

    Returns:
    - Trained Word2Vec model
    """
    model = Word2Vec(sentences, vector_size=size, window=window, min_count=min_count, workers=workers)
    model.train(sentences, total_examples=len(sentences), epochs=10)
    return model

def drop_duplicates(df, subset=None, keep='first'):
    """
    Drop duplicate rows from the dataframe based on subset of columns.
    
    Parameters:
        df (DataFrame): Input DataFrame.
        subset (list or str): List of columns to consider for identifying duplicates.
        keep (str): {'first', 'last', False}, default 'first'. Determines which duplicates to keep.
        
    Returns:
        DataFrame: DataFrame with duplicates dropped.
    """
    return df.drop_duplicates(subset=subset, keep=keep)

def set_dtype(df, col, dtype):
    """
    Set the datatype for a column.

    Parameters:
        df (DataFrame): Input DataFrame.
        col (str): Name of the column.
        dtype (str): Desired datatype.
        
    Returns:
        DataFrame: DataFrame with the column set to the desired datatype.
    """
    df[col] = df[col].astype(dtype)

    return df

def handle_text_data(df, col, pattern, replacement):
    """
    Replace occurrences of a pattern in a text column.
    
    Parameters:
        df (DataFrame): Input DataFrame.
        col (str): Name of the column.
        pattern (str): Pattern to search for.
        replacement (str): Replacement string.
        
    Returns:
        DataFrame: DataFrame with replaced text.
    """
    df[col] = df[col].str.replace(pattern, replacement)

    return df

def handle_datetime(df, col, format=None, errors='raise', infer_datetime_format=False):
    """
    Convert a column to datetime format.
    
    Parameters:
        df (DataFrame): Input DataFrame.
        col (str): Name of the column.
        format (str, optional): Datetime format string.
        errors (str, default 'raise'): Errors handling.
        infer_datetime_format (bool, default False): Infer datetime format.
        
    Returns:
        DataFrame: DataFrame with datetime formatted column.
    """
    df[col] = pd.to_datetime(df[col], format=format, errors=errors, infer_datetime_format=infer_datetime_format)

    return df

def collapse_categories(df, col, mapping):
    """
    Collapse data into categories.
    
    Parameters:
        df (DataFrame): Input DataFrame.
        col (str): Name of the column.
        mapping (dict): Dictionary with current categories as keys and desired categories as values.
        
    Returns:
        DataFrame: DataFrame with collapsed categories.
    """
    df[col] = df[col].replace(mapping)

    return df

def find_similar_strings(df, col, string, threshold=80):
    """
    Find and replace similar strings in a column based on a reference string.
    
    Parameters:
        df (DataFrame): Input DataFrame.
        col (str): Name of the column.
        string (str): Reference string.
        threshold (int, default 80): Similarity threshold.
        
    Returns:
        DataFrame: DataFrame with replaced similar strings.
    """
    matches = process.extract(string, df[col], limit=len(df[col]))
    for match in matches:
        if match[1] >= threshold:
            df.loc[df[col] == match[0], col] = string

    return df

def truncate_outliers(df, column, lower_percentile=1, upper_percentile=99):
    """
    Cap outliers in the column based on percentiles.

    Parameters:
    - df: DataFrame
    - column: Name of the column to truncate
    - lower_percentile: Lower percentile value
    - upper_percentile: Upper percentile value

    Returns:
    - DataFrame with truncated column
    """
    lower, upper = df[column].quantile([lower_percentile/100, upper_percentile/100])
    df[column] = df[column].clip(lower, upper)
    return df

def sqrt_transform(df, column):
    """
    Apply square root transformation to the column.

    Parameters:
    - df: DataFrame
    - column: Name of the column to transform

    Returns:
    - DataFrame with transformed column
    """
    df[column] = df[column].apply(lambda x: x**0.5 if x > 0 else x)
    return df

def impute_outliers_with_median(df, column, lower_percentile=1, upper_percentile=99):
    """
    Impute outliers in the column using the median.

    Parameters:
    - df: DataFrame
    - column: Name of the column to impute
    - lower_percentile: Lower percentile value
    - upper_percentile: Upper percentile value

    Returns:
    - DataFrame with imputed column
    """
    lower, upper = df[column].quantile([lower_percentile/100, upper_percentile/100])
    median = df[column].median()
    df[column] = df[column].apply(lambda x: median if x < lower or x > upper else x)
    return df

def apply_pca(df, n_components=2):
    """
    Apply Principal Component Analysis.

    Parameters:
    - df: DataFrame
    - n_components: Number of principal components

    Returns:
    - DataFrame with principal components
    """
    pca = PCA(n_components=n_components)
    principal_components = pca.fit_transform(df)
    return pd.DataFrame(data=principal_components, columns=[f"Principal_Component_{i}" for i in range(1, n_components + 1)])

def apply_tsne(df, n_components=2, perplexity=30):
    """
    Apply t-SNE.

    Parameters:
    - df: DataFrame
    - n_components: Number of components
    - perplexity: Perplexity parameter for t-SNE

    Returns:
    - DataFrame with t-SNE components
    """
    tsne = TSNE(n_components=n_components, perplexity=perplexity)
    tsne_results = tsne.fit_transform(df)
    return pd.DataFrame(data=tsne_results, columns=[f"tSNE_{i}" for i in range(1, n_components + 1)])

def apply_lda(df, target, n_components=1):
    """
    Apply Linear Discriminant Analysis.

    Parameters:
    - df: DataFrame without target column
    - target: Target column values
    - n_components: Number of components

    Returns:
    - DataFrame with LDA components
    """
    lda = LDA(n_components=n_components)
    lda_results = lda.fit_transform(df, target)
    return pd.DataFrame(data=lda_results, columns=[f"LDA_{i}" for i in range(1, n_components + 1)])

def remove_special_characters_and_numbers(df, column):
    """
    Remove special characters and numbers from the text column.

    Parameters:
    - df: DataFrame
    - column: Name of the text column

    Returns:
    - DataFrame with cleaned text column
    """
    df[column] = df[column].apply(lambda x: re.sub(r'[^a-zA-Z\s]', '', str(x)))
    return df

def to_lowercase(df, column):
    """
    Convert text in the column to lowercase.

    Parameters:
    - df: DataFrame
    - column: Name of the text column

    Returns:
    - DataFrame with text converted to lowercase
    """
    df[column] = df[column].str.lower()
    return df

def remove_stopwords(df, column):
    """
    Remove stop words from the text column.

    Parameters:
    - df: DataFrame
    - column: Name of the text column

    Returns:
    - DataFrame with text with stopwords removed
    """
    nltk.download('stopwords')
    stop = stopwords.words('english')
    df[column] = df[column].apply(lambda x: ' '.join([word for word in str(x).split() if word not in stop]))
    return df

def bin_data(df, column, bins, labels=None):
    """
    Convert continuous data into discrete bins.

    Parameters:
    - df: DataFrame
    - column: Name of the column to bin
    - bins: List of bin edges
    - labels: List of bin labels

    Returns:
    - DataFrame with binned data in a new column
    """
    bin_col_name = column + '_bin'
    df[bin_col_name] = pd.cut(df[column], bins=bins, labels=labels, include_lowest=True)
    return df

def extract_datetime_components(df, column, components=["year", "month", "day", "dayofweek"]):
    """
    Extract specified components from a datetime column.

    Parameters:
    - df: DataFrame
    - column: Name of the datetime column
    - components: List of components to extract (e.g., ["year", "month"])

    Returns:
    - DataFrame with extracted datetime components
    """
    for component in components:
        df[f"{column}_{component}"] = getattr(df[column].dt, component)
    return df

import pandas as pd

def time_since(df, column, event_date, time_unit="days"):
    """
    Compute time since a certain event for each entry in a datetime column.

    Parameters:
    - df: DataFrame
    - column: Name of the datetime column
    - event_date: Date of the event to compute time since
    - time_unit: Unit of time for computation ("days", "seconds", etc.)

    Returns:
    - DataFrame with a new column showing time since the event
    """
    event_datetime = pd.to_datetime(event_date)
    delta = (df[column] - event_datetime)

    if time_unit == "days":
        df[f"time_since_{event_date}"] = delta.dt.days
    elif time_unit == "seconds":
        df[f"time_since_{event_date}"] = delta.dt.seconds
    # Add more units as needed

    return df

def decompose_seasonality(df, column, model='additive', freq=None, plot=True):
    """
    Decompose time series data into trend, seasonal, and residual components.

    Parameters:
    - df: DataFrame with datetime index
    - column: Name of the column containing time series data
    - model: Type of decomposition model ('additive' or 'multiplicative')
    - freq: Frequency of data (e.g., 12 for monthly). If None, pandas will infer.
    - plot: If True, plot the components.

    Returns:
    - Decomposition result object
    """
    result = seasonal_decompose(df[column], model=model, freq=freq)

    return result

def anonymize_email(email):
    """Anonymize an email address using hashlib."""
    hashed_email = hashlib.sha256(email.encode()).hexdigest()
    # Keep the domain for structural purposes but replace the user part
    return hashed_email[:10] + "@" + email.split('@')[-1]

def anonymize_phone(phone):
    """Anonymize phone number by keeping only the last 4 digits."""
    return "XXXX-XXXX-" + phone[-4:]

def anonymize_string(s, length=None):
    """Anonymize a general string."""
    length = length or len(s)
    return ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(length))