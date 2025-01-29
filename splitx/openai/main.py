import openai
import base64
import os

openai.api_key = os.getenv("OPENAI_API_KEY")

def extract_total_bill_amount(base64_image):

    image_data = base64.b64decode(base64_image)


    response = openai.ChatCompletion.create(
        model="gpt-4-vision-preview",
        messages=[
            {
                "role": "system",
                "content": "You are an AI assistant that extracts the total bill amount from invoices."
            },
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "Extract the total bill amount from this invoice."},
                    {"type": "image", "image": image_data}
                ]
            }
        ],
        max_tokens=100
    )


    extracted_text = response["choices"][0]["message"]["content"]

    return extracted_text

