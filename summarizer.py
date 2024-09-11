from groq import Groq
import os
import datetime

client = Groq(
    api_key=os.environ.get("GROQ_API_KEY")
)

with open('input.txt', 'r') as og_file:
    og = og_file.read()

output = 'PDF' 

completion = client.chat.completions.create(
    model="llama3-70b-8192",
    messages=[
        {
            "role": "user",
            "content": "Please summarize the following text for students with ADHD. The summary should: \n\n1. Be shorter and simpler, using clear and straightforward language. \n\n 2. Maintain the original meaning and important details. \n\n 3. Keep the same point of view and tone as the original text. \n\n 4. Maintain the order of the information. \n\n Do not use bullet points nor headings. \n\n Here is the text:\n\n" + og
        },
        {
            "role": "assistant",
            "content": "Let me help you with that!\n\nTo summarize a text for students with ADHD, I'll break it down into smaller, bite-sized chunks, and use simple language to make it easy to follow. Please provide the text you wish to summarize.\n\n"
        }
    ],
    temperature=1,
    max_tokens=1024,
    top_p=1,
    stream=False,
    stop=None,
)

timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
result = f"summary_{timestamp}.md"
with open(result, 'w') as output_file:
    output_file.write(completion.choices[0].message.content)

# for chunk in completion:
#     print(chunk.choices[0].delta.content or "", end="")
