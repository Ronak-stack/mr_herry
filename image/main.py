from dotenv import load_dotenv
from openai import OpenAI

def image_checker():

    client = OpenAI()

    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {
                "role":"user",
                "content":[
                    {
                        "type":"text", "text":"What's in this image?"
                    },
                    {
                        "type":"image_url",
                        "image_url":{
                            "url":"https://upload.wikimedia.org/wikipedia/commons/9/94/The_Golden_Temple_of_Amrithsar_7.jpg"
                        }
                    }
                ]
            }
        ]
    )

    print(response.choices[0].message.content)