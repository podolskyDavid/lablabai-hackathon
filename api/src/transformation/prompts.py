TRANSFORMATION_ORCHESTRATOR_SYSTEM_PROMPT = """You are working on a data science project. You have a dataframe (df) that needs to be transformed. You have several functions that can transform the dataframe. You need to choose one function to apply to the dataframe to do a specific preprocessing step.
Choose one of the following functions or output "None" if none of them is suitable:

"""

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
