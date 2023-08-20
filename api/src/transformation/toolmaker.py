import re
import json

import openai

from api.src.transformation.prompts import TOOL_MAKER_PROMPT, TOOL_WRAPPER_PROMPT


def generate(prompt, max_tokens=256, temperature=0.0, model="gpt-3.5-turbo"):
    """UNUSED"""
    if model in ["gpt-3.5-turbo", "gpt-4"]:
        params = {
            "model": model,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "messages": [{"role": "user", "content": prompt}]
        }
        for retry in range(3):
            try:
                return openai.ChatCompletion.create(**params)["choices"][0]["message"]["content"]
            except:
                pass
        raise Exception("Failed to generate")

    # For older models, use the completion API with max_tokens=1024
    params = {
        "model": model,
        "max_tokens": min(max_tokens, 1024),
        "temperature": temperature,
        "prompt": prompt
    }
    for retry in range(3):
        try:
            return openai.Completion.create(**params)["choices"][0]["text"]
        except:
            pass


def make_tool(step: str, summary: str, model="gpt-4", temperature=0.3):
    """ A tool is a function created from scratch by an OpenAI model. """
    # TODO Experiment with the prompting in this function
    prompt1 = "\n\n".join([
                              f"Information about the DataFrame (df):\n {summary}",
                              f"For the given dataframe, write a function to apply the following transformation:\n {step}",
                              TOOL_MAKER_PROMPT])
    message = [{"role": "user", "content": prompt1}]

    params = {
        "model": model,
        "max_tokens": 2048,
        "temperature": temperature,
        "messages": message
    }

    for retry in range(3):
        try:
            response = openai.ChatCompletion.create(**params)["choices"][0]["message"]["content"]
            message.append({"role": "assistant", "content": response})
            tool = "\n\n".join(re.findall(r"```python\n(.*?)```", response, re.DOTALL))
            exec(tool, globals(), locals())
            break
        except Exception as e:
            print("ERROR: failed to generate tool", e)
            message.append({"role": "user",
                            "content": f"Failed to execute the function due to the error: {type(e).__name__} {e}. Please fix it and try again."})

    print("Generated a function from scratch:\n\n", message[-1]["content"])

    message.append({"role": "assistant", "content": response})

    prompt2 = f"Information about the DataFrame (df):\n {summary}.\n\n" \
              f"Desired transformation:\n {step}\n\n" \
              f"For the above code and the given dataframe, write unit tests to verify the correctness of the function."
    message.append({"role": "user", "content": prompt2})

    params = {
        "model": model,
        "max_tokens": 2048,
        "temperature": temperature,
        "messages": message
    }
    success = False

    for retry in range(3):
        try:
            response = openai.ChatCompletion.create(**params)["choices"][0]["message"]["content"]
            message.append({"role": "assistant", "content": response})
            verification = "\n\n".join(re.findall(r"```python\n(.*?)```", response, re.DOTALL))
            exec(tool + "\n" + verification, globals(), locals())
            success = True
            break
        except Exception as e:
            print("ERROR: failed to verify", e)
            message.append({"role": "user",
                            "content": f"Failed to verify the function due to the error: {type(e).__name__} {e}. Please fix it and try again."})
    print("Verification:", message[-1]["content"])

    return tool, success

    # if success:
    #     message.append({"role": "user", "content": TOOL_WRAPPER_PROMPT})
    #     params = {
    #         "model": model,
    #         "max_tokens": 2048,
    #         "temperature": temperature,
    #         "messages": message
    #     }
    #     try:
    #         response = openai.ChatCompletion.create(**params)["choices"][0]["message"]["content"]
    #         message.append({"role": "assistant", "content": response})
    #         print("Wrapper:", response)
    #     except Exception as e:
    #         print("ERROR: failed to generate wrapper", e)
    #
    # return tool, verification, success, message
