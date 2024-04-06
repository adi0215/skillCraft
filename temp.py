from pathlib import Path
import json

# Define the source and destination root directories
src_root = Path('C:\\Users\\Adarsh\\Downloads\\MATH\\test')
dst_file = Path('apt_test_set.jsonl')

# Make sure the destination directory exists (if it's in a subdirectory)
dst_file.parent.mkdir(parents=True, exist_ok=True)
def transform_problem(problem):
    return {"messages": [{"role": "user", "content": f"{problem['problem']}"}, {"role": "assistant", "content": problem['solution']}]}

# Open the destination JSONL file for writing
with dst_file.open('w') as dst_f:
    # Recursively process each JSON file in the source directory
    for src_file_path in src_root.rglob('*.json'):
        # Read the original problem
        with src_file_path.open('r') as f:
            problem = json.load(f)
        
        # Transform the problem into the new schema
        transformed_content = transform_problem(problem)
        
        # Write the transformed content to the destination JSONL file
        json.dump(transformed_content, dst_f)
        dst_f.write('\n')

print("Transformation complete.")

"""
import json

# Path to your JSONL file
input_file_path = 'apt_train_set.jsonl'
# Path where you want to save the text file
output_file_path = 'extracted_contents.txt'

with open(input_file_path, 'r') as input_file, open(output_file_path, 'w') as output_file:
    for line in input_file:
        entry = json.loads(line)
        content = ""
        for message in entry['messages']:
            content = content + message['content']
        # Write the content to the output file, followed by a newline
        output_file.write(content)

print("Extraction complete. Contents saved to:", output_file_path)
"""
"""
import tiktoken
encoding = tiktoken.get_encoding("cl100k_base")

encoding = tiktoken.encoding_for_model("gpt-3.5-turbo")
with open("extracted_contents.txt", "r", encoding='utf-8') as f:
    content = [i for i in f.read()]
    for i, ch in enumerate(content):
        if ord(ch) < 32 or ord(ch) > 126:
            content[i] = " "
content = "".join(content)
print(len(encoding.encode(content)))
"""


