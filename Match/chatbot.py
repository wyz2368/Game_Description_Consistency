from google import genai
from openai import OpenAI
import os

def infer_from_gemini(prompt):
    """
    Use the Gemini API to infer a response from a given prompt.
    """
    client = genai.Client(api_key="")  # Add your API key here
    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=[prompt]
    )
    return response.text.strip()


def infer_from_gpt(prompt):
    os.environ["OPENAI_API_KEY"] = "" # Add your API key here
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    
    def get_response(text):
        completion = client.chat.completions.create(
            # model="gpt-4-0125-preview",
            # model = "gpt-4-1106-preview",
            # model="gpt-3.5-turbo",
            # model = "gpt-3.5-turbo-16k",
            model = "gpt-4o",
            messages=text,
            temperature=0.0,
            top_p=1.0
        )
        return completion.choices[0].message.content
    
    message_pool = []
    init_message = "You are a helpful assistant."
    system_message = {"role": "system", "content": init_message}
    message_pool.append(system_message)
    
    user_message = {"role": "user", "content": prompt}
    message_pool.append(user_message)
    
    response = get_response(message_pool)
    
    return response


def infer_from_deepseek(prompt):
    client = OpenAI(api_key="", base_url="https://api.deepseek.com")
    
    def get_response(text):
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=text,
            stream=False
        )
        return response.choices[0].message.content
    
    message_pool = []
    init_message = "You are a helpful assistant."
    system_message = {"role": "system", "content": init_message}
    message_pool.append(system_message)
    
    user_message = {"role": "user", "content": prompt}
    message_pool.append(user_message)
    
    response = get_response(message_pool)
    
    return response


def infer_response(prompt, model):
    if model == "gemini":
        response = infer_from_gemini(prompt)
    elif model == "gpt":
        response = infer_from_gpt(prompt)
    elif model == "deepseek":
        response = infer_from_deepseek(prompt)
    else:
        raise ValueError("Invalid model specified.")
    
    return response
    
    