#!/usr/bin/env python3

import openai
# import configparser
from configparser import ConfigParser
import os
import pandas as pd
from fastapi import FastAPI
import uuid

app = FastAPI()

@app.get("/")
def read_root():
    return {"hello": "world"}

api_keys_location = os.path.join(".openai_keys")

def create_template_ini_file():
    """
    create a template .ini file if it doesn't exist.
    this is just a placeholder. you might want to fill in the logic.
    """
    if not os.path.exists(api_keys_location):
        with open(api_keys_location, 'w') as f:
            f.write("[openai]\n")
            f.write("organization_id = your_organization_id\n")
            f.write("secret_key = your_secret_key\n")


def initialize_openai_api():
    """
    initialize the openai api
    """
    # check if file at api_keys_location exists
    create_template_ini_file()
    
    # config = configparser.configparser()
    config = ConfigParser()
    config.read(api_keys_location)

    openai.organization_id = config['openai']['organization_id'].strip('"').strip("'")
    openai.api_key = config['openai']['secret_key'].strip('"').strip("'")


initialize_openai_api()

def generate(prompt):
    message = {"role": "user", "content": prompt}
    messages = [message]

    response = openai.ChatCompletion.create(
            model='gpt-3.5-turbo',
            messages=messages,
            max_tokens=1000,
            stream=True,
            )

    text_all = ''
    for i, chunk in enumerate(response):
        if chunk['choices'][0]['finish_reason']:
            break

        return_token = chunk['choices'][0]['delta']['content']
        print(return_token, end='')
        text_all += return_token

    return text_all





@app.get("/generate")
def generate_feature(csv_text, generation_instruction):
    # df = pd.read_csv(csv_text)
    # csv_text is already the text of the csv file, just parse it
    os.makedirs('tmp', exist_ok=True)
    tmp_file = os.path.join('tmp', f'{uuid.uuid4()}.csv')

    # split on  \n
    csv_text_lines = csv_text.split('\\n')

    with open(tmp_file, 'w') as f:
        # f.write(csv_text)
        for line in csv_text_lines:
            f.write(line)
            f.write('\n')

    df = pd.read_csv(tmp_file)
    print("df:", df)






    # df = df.dropna()
    # df = df.reset_index(drop=true)

    # copy it to a new dataframe
    df_new = df.copy()

    # add column to new dataframe 'new_column'
    df_new['new_column'] = None

    i = 0
    # for i, row in enumerate(df.iterrows()):
    for row in df.iterrows():
        print("row:", row)
        print(f'i: {i}')
        prompt = f'those are the existing values in the row:\n'
        prompt += f'{row}\n'
        prompt += f'please generate a new value using the following instruction: "{generation_instruction}"\n'
        prompt += 'respond just with the generated value and nothing else, no explanation needed'
        generated_value = generate(prompt)
        print("generated_value:", generated_value)
        df_new.at[i, 'new_column'] = generated_value
        i += 1

    print("df_new:", df_new)
    # return df_new.to_csv(index=false)
    return df_new.to_csv()



if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)







