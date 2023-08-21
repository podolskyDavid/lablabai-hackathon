from datetime import datetime, timedelta

import pandas as pd
import numpy as np
import json
from collections import Counter


def insert_info_row(df):
    """
    Insert a row of JSON strings as the first row of df.
    Each entry in this row contains information about the corresponding column in df.

    Sample df:

                strings  ints categorical                                        object                      dates  one_hot_a  one_hot_b  one_hot_c  one_hot_d
    0   first_value  -1.0           a                                            [] 2023-08-20 15:08:10.300975       True      False      False      False
    1  second_value   0.0           a                                     [1, 2, 3] 2023-08-21 16:08:10.300975       True      False      False      False
    2          None   NaN           a                                          None 2023-08-22 17:08:10.300975       True      False      False      False
    3  fourth_value   0.0           b                                          None 2023-08-23 18:08:10.300975      False       True      False      False
    4   fifth_value   1.0           b                                        {1: 2} 2023-08-24 19:08:10.300975      False       True      False      False
    5          None   NaN           c  [[2.058335917824e-312, 2.334195370625e-312]] 2023-08-25 20:08:10.300975      False      False       True      False
    6          None   0.0           c                                           NaN 2023-08-26 21:08:10.300975      False      False       True      False
    7  eighth_value   0.0           d                                           NaN 2023-08-27 22:08:10.300975      False      False      False       True

    The first row of the returned dataframe, i.e. frontend_df, will contain the following info JSON strings:

    {'dtype': 'string', 'top3': {'first_value': 0.125, 'second_value': 0.125, 'fourth_value': 0.125}, 'invalid': 0.375}
    {'dtype': 'numeric', 'min': -1.0, 'max': 1.0, 'avg': 0.0, 'stddev': 0.6324555320336759, 'invalid': 0.25}
    {'dtype': 'string', 'top3': {'a': 0.375, 'b': 0.25, 'c': 0.25}, 'invalid': 0.0}
    {'dtype': 'object', 'invalid': 0.5}
    {'dtype': 'datetime', 'first_date': '2023-08-20 15:08:10.300975', 'last_date': '2023-08-27 22:08:10.300975',
     # CAUTION: the 'period' field won't exist if there's no period in the column of dtype datetime!
     'period': '1 days 01:00:00', 'invalid': 0.0}
    {'dtype': 'boolean', 'true': 0.375, 'invalid': 0.0}
    {'dtype': 'boolean', 'true': 0.25, 'invalid': 0.0}
    {'dtype': 'boolean', 'true': 0.25, 'invalid': 0.0}
    {'dtype': 'boolean', 'true': 0.125, 'invalid': 0.0}

    """
    if df.shape[0] == 0 or df.shape[1] == 0:
        return df

    result = {}
    one_hot_dataframes = []
    for col in df.columns:
        col_data = df[col]
        # Checking invalid values
        invalid = (col_data.isna().sum() + col_data.dropna().apply(
            lambda x: x == 'None' or x == 'none' or x == 'NaN' or x == 'nan'
        ).sum()) / len(df)

        if np.issubdtype(df[col].dtype, np.number):
            # Numerical Column
            result[col] = json.dumps({
                "dtype": "numeric",
                "min": col_data.min().item(),
                "max": col_data.max().item(),
                "avg": col_data.mean().item(),
                "stddev": col_data.std().item(),
                "invalid": invalid
            })
        elif isinstance(col_data[0], pd.Timestamp):
            # DateTime Column
            sorted_col_data = sorted(col_data)
            periods = [x - y for x, y in zip(sorted_col_data[1:], sorted_col_data[:-1])]
            common_period = periods[0] if len(set(periods)) == 1 else None
            result[col] = json.dumps({
                "dtype": "datetime",
                "first_date": str(col_data.min()),
                "last_date": str(col_data.max()),
                "period": str(common_period),
                "invalid": invalid
            })
        elif np.issubdtype(df[col].dtype, np.bool_):
            # Boolean Column
            result[col] = json.dumps({
                "dtype": "boolean",
                "true": (col_data.sum() / len(df)),
                "invalid": invalid,
            })
        else:
            try:
                if col_data.nunique() == 2 and len(set(col_data.dropna())) == 2:
                    # One-hot Column
                    one_hot_dataframes.append(col_data)
                else:
                    # String Column or Non encodable Object
                    cleaned_col_data = col_data.dropna()
                    value_counts = cleaned_col_data.value_counts().apply(lambda x: x / len(df))
                    top3 = {k: v for k, v in zip(value_counts.index[:3], value_counts.values[:3])}
                    result[col] = json.dumps({
                        "dtype": "string",
                        "top3": top3,
                        "invalid": invalid,
                    })
            except TypeError:
                # Non encodable Object
                result[col] = json.dumps({
                    "dtype": "object",
                    "invalid": invalid
                })

    # handling One-Hot Columns
    # TODO probably doesn't work properly for multiple one-hot columns
    if one_hot_dataframes:
        one_hot_df = pd.concat(one_hot_dataframes, axis=1)
        for col in one_hot_df.columns:
            # Selecting all columns following One-Hot pattern
            aligned_cols = [col_ for col_ in one_hot_df.columns if
                            set(one_hot_df[col_].unique()) == set(one_hot_df[col].unique()) and col_ != col]
            result[col] = json.dumps({
                "dtype": "one-hot",
                "aligned": aligned_cols,
                "true": (one_hot_df[col].sum() / len(df)),
                "invalid": invalid,
            })
    df = pd.concat([pd.DataFrame(result, index=[0]), df], ignore_index=True)
    return df


if __name__ == '__main__':
    pd.set_option('display.max_rows', 500)
    pd.set_option('display.max_columns', 500)
    pd.set_option('display.width', 1000)
    pd.set_option('display.expand_frame_repr', False)

    data = {'strings': ['first_value', 'second_value', None, 'fourth_value', 'fifth_value', None, None, 'eighth_value'],
            'ints': [-1, 0, np.nan, 0, 1, np.nan, 0, 0],
            'categorical': ['a', 'a', 'a', 'b', 'b', 'c', 'c', 'd'],
            'object': [[], [1, 2, 3], None, None, {1: 2}, np.ndarray([1, 2]), np.nan, np.nan],
            }
    df = pd.DataFrame(data)
    # Add 'dates' column
    start_date = datetime.now()
    df['dates'] = [start_date + timedelta(days=i, hours=i) for i in range(len(df))]
    # Create One-Hot representation of the 'categorical' column while keeping it
    one_hot = pd.get_dummies(df['categorical'])
    one_hot.columns = ['one_hot_' + str(col) for col in one_hot.columns]
    df = pd.concat([df, one_hot], axis=1)

    print(df.head(100))

    df_frontend = insert_info_row(df)
    for col in df_frontend.iloc[0]:
        print(json.loads(col))
