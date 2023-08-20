SELECT_TRANSFORMATION_PROMPT = """You are working on a data science project. You have a dataframe (df) that needs to be transformed. You have a list of functions that can transform the dataframe. You have to decide if there's a function to apply to the dataframe to do a specific preprocessing step in this list.
Choose one of the following functions to apply to the dataframe (df) or output "None" if none of them are suitable:

"""
GENERATE_FUNCTION_CALL_PROMPT = """{function_definition}
Write code to execute this function, passing a DataFrame (df) as a parameter to achieve the following preprocessing step:
{step}
Information about the DataFrame (df):
{summary_string}
The code you write should be wrapped by
```python
```"""

GENERATE_IMPORTS_PROMPT = """
Consider the following imports:
{imports}
Generate only import statements that are required for this code snippet to run:
{snippet}
Select ONLY the import statements that are actually used in the code snippet. Don't generate any other code or comments. You can create import statements not from this list.
The code you write should be wrapped by
```python
```"""


TOOL_MAKER_PROMPT = """Please write a generic Python function to solve this type of problems using only standard python libraries. The only input should be the dataframe (df). You are always working on pandas dataframe. The output of each transformation should be a new pandas dataframe. All the function should be wrapped by
```python
```"""

TOOL_WRAPPER_PROMPT = """Success! The function is correct. We will need to summarize the function and use cases up for further use. Please extract the information from the history in the following format:

Here is a function to apply a transformation to a dataframe:
```python
{the function, including necessary imports}
```

Example Dataframe Before:
{DataFrame}

Example Dataframe After:
"""
