from openai import OpenAI
import os


def infer_response(prompt, model):
    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        raise ValueError("OPENAI_API_KEY is not set.")

    client = OpenAI(api_key=api_key)

    def get_response(text):
        completion = client.chat.completions.create(
            model=model,
            messages=text,
            temperature=1.0 if model in ["gpt-5", "gpt-5-mini"] else 0.0,
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
