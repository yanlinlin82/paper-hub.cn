from openai import OpenAI
import os
import sys

if len(sys.argv) < 2:
    print("Usage: python test.py <filename.txt>")

if len(sys.argv) > 1:
    filename = sys.argv[1]
    with open(filename, 'r') as file:
        title = file.readline().strip()
        abstract = file.read()
else:
    print("Please provide a filename as a command line argument.")

import constants
os.environ["OPENAI_API_KEY"] = constants.OPENAI_API_KEY


client = OpenAI()
# defaults to getting the key using os.environ.get("OPENAI_API_KEY")
# if you saved the key under a different environment variable name, you can do something like:
# client = OpenAI(
#   api_key=os.environ.get("CUSTOM_ENV_NAME"),
# )

input = f"Here goes the abstract of the paper '{title}':\n{abstract}\n\nPlease summary the paper in Chinese."
print(input, file=sys.stderr)

completion = client.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=[
        # {"role": "system", "content": "You are a poetic assistant, skilled in explaining complex programming concepts with creative flair."},
        # {"role": "user", "content": "Compose a poem that explains the concept of recursion in programming."}

        # {"role": "user", "content": "What is the meaning of life?"},

        #{"role": "user", "content": "What is the second month in a year?"},
        {"role": "user", "content": input},
    ]
)
print(completion, file=sys.stderr)

result = completion.choices[0].message.content
print(result)
