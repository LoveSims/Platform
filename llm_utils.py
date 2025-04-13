# llm_utils.py
# This file contains utility functions for generating and parsing responses from OpenAI models.

import os
from dotenv import load_dotenv
import numpy as np
import pickle
import pandas as pd
import json
import re
from typing import Dict, List, Tuple

from openai import OpenAI 
# load_dotenv()
# oai = OpenAI(api_key = os.getenv('OPENAI_API_KEY'))
from settings import *
oai = OpenAI(api_key = OPENAI_API_KEY)

def gen_oai(messages, model='gpt-4o', temperature=1):
    if model is None:
        model = 'gpt-4o'
    try:
        response = oai.chat.completions.create(
            model=model,
            temperature=temperature,
            messages=messages,
            max_tokens=1000
        )
        content = response.choices[0].message.content
        return content
    except Exception as e:
        print(f"Error generating completion: {e}")
        raise e

def simple_gen_oai(prompt, model='gpt-4o', temperature=1):
    messages = [{"role": "user", "content": prompt}]
    return gen_oai(messages, model, temperature)

# Prompt utils

# Prompt inputs
def fill_prompt(prompt, placeholders):
    for placeholder, value in placeholders.items():
        placeholder_tag = f"!<{placeholder.upper()}>!"
        if placeholder_tag in prompt:
            prompt = prompt.replace(placeholder_tag, str(value))
    return prompt

def make_output_format(modules):
    output_format = "Output Format:\n{\n"
    for module in modules:
        if 'name' in module and module['name']:
            output_format += f'    "{module["name"].lower()}": "<your response>",\n'
    output_format = output_format.rstrip(',\n') + "\n}"
    return output_format

def modular_instructions(modules):
    """
    Given some modules in the form:

    name (optional, makes it a step)
    instruction (required)

    make the whole prompt.
    """
    prompt = ""
    step_count = 0
    for module in modules:
        if 'name' in module:
            step_count += 1
            prompt += f"Step {step_count} ({module['name']}): {module['instruction']}\n"
        else:
            prompt += f"{module['instruction']}\n"
    prompt += "\n"
    prompt += make_output_format(modules)
    return prompt

# Prompt outputs
def parse_json(response, target_keys=None):
    json_start = response.find('{')
    json_end = response.rfind('}') + 1
    cleaned_response = response[json_start:json_end].replace('\\"', '"')
    
    try:
        parsed = json.loads(cleaned_response)
        if target_keys:
            parsed = {key: parsed.get(key, "") for key in target_keys}
        return parsed
    except json.JSONDecodeError:
        print("Tried to parse json, but it failed. Switching to regex fallback.")
        print(f"Response: {cleaned_response}")
        parsed = {}
        for key_match in re.finditer(r'"(\w+)":\s*', cleaned_response):
            key = key_match.group(1)
            if target_keys and key not in target_keys:
                continue
            value_start = key_match.end()
            if cleaned_response[value_start] == '"':
                value_match = re.search(r'"(.*?)"(?:,|\s*})', 
                                        cleaned_response[value_start:])
                if value_match:
                    parsed[key] = value_match.group(1)
            elif cleaned_response[value_start] == '{':
                nested_json = re.search(r'(\{.*?\})(?:,|\s*})', 
                                        cleaned_response[value_start:], re.DOTALL)
                if nested_json:
                    try:
                        parsed[key] = json.loads(nested_json.group(1))
                    except json.JSONDecodeError:
                        parsed[key] = {}
            else:
                value_match = re.search(r'([^,}]+)(?:,|\s*})', 
                                        cleaned_response[value_start:])
                if value_match:
                    parsed[key] = value_match.group(1).strip()
        
        if target_keys:
            parsed = {key: parsed.get(key, "") for key in target_keys}
        return parsed

# End-to-end generation and parsing
def mod_gen(modules: List[Dict], placeholders: Dict, target_keys=None) -> Dict:
    prompt = modular_instructions(modules)
    filled = fill_prompt(prompt, placeholders)
    response = simple_gen_oai(filled)
    if len(response) == 0:
        print("Error: response was empty")
        return {}
    if target_keys is None:
        target_keys = [module["name"].lower() for module in modules if "name" in module]
    parsed = parse_json(response, target_keys)
    return parsed

def json_gen_oai(prompt, response_format, model='gpt-4o', temperature=1):
    """
    Generate a response in JSON format using OpenAI.
    
    Args:
        prompt (str): The prompt to send to the model.
        response_format (dict): The expected JSON structure with example values.
        model (str): The model to use.
        temperature (float): Sampling temperature.
        
    Returns:
        dict: The parsed JSON response.
    """
    messages = [
        {"role": "system", "content": "You are a helpful assistant that always responds in the exact JSON format specified."},
        {"role": "user", "content": f"""
Please provide a response in the following JSON format:
{response_format}

Here is the task:
{prompt}

Remember to:
1. Follow the exact JSON structure shown above.
2. Include all required fields.
3. Use appropriate data types (numbers for scores, strings for text).
4. Ensure the response is valid JSON.
"""}
    ]
    
    try:
        response = oai.chat.completions.create(
            model=model,
            temperature=temperature,
            messages=messages,
            response_format={"type": "json_object"},
            max_tokens=1000
        )
        content = response.choices[0].message.content
        return json.loads(content)
    except Exception as e:
        print(f"Error generating JSON completion: {e}")
        raise e
