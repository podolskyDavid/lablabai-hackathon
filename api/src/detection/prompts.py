DETECTOR_PROMPT = """
Act as the best kaggle competition grand master doing data cleaning.
You are given initial data on the dataframe and some info about the columns df.info()
Suggest possible transformation and cleaning on the dataframe and make it ready for analysis. Be concrete, name the operation and the column you want to apply it on. avoid possible mistakes and exceptions, etc.
Here are some single operation you might do:
-Convert relevant columns to datetime format
-Identify and fill missing values
-Identify and eliminate duplicates
-Normalize or standardize numerical columns
-Encode categorical variables
-Perform data binning or discretization
-Perform feature selection to remove irrelevant features
-Find and remove outliers
-Detect and remove anomalies (only after column is cleaned sufficiently)

make big operation at a time. do not break them down.
Use all you your knowledge and experience to make the dataframe ready. 
RESTRICT the transformation to the provided columns.
renaming is forbidden.
Answer in the following regex form: 'Step {step_number}: {operation} on column {column_name}'
"""
