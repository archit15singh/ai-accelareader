import requests
import json
import os
from dotenv import load_dotenv
import litellm

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")

def fetch_litellm_response(prompt, response_format=None):
    response = litellm.completion(
        model="gpt-4o-2024-08-06",
        messages=[{"role": "user", "content": prompt}],
        response_format=response_format,
        api_key=api_key,
    )
    cost = response._hidden_params.get("response_cost", 0.0)
    print(f"LLM Call Cost: ${cost:.6f}")
    return response["choices"][0]["message"]["content"]

def generate(text_from_book):
    if not text_from_book.strip():
        return None, None

    prompt_template = """
Given the following excerpt from a technical book:

# Excerpt from the book
{}

# Instructions
Your goal is to generate **structured, high-quality Anki flashcards** (front-back format) that thoroughly cover the given concept. 
Each flashcard should focus on a specific aspect to ensure deep understanding and long-term retention.

### **Output Format**
The response should be in **JSON format** to facilitate easy import into Anki:

```json
{{
    "flashcards": [
        {{
            "front": "markdown content",
            "back": "markdown content"
        }},
        {{
            "front": "markdown content",
            "back": "markdown content"
        }}
    ]
}}
"""

    tags_prompt_template = """
Given the following excerpt from a technical book, generate a concise list of broad Anki tags.
The tags should be simple, high-level, and avoid excessive granularity to prevent clutter.
Focus on general topics rather than overly specific details.

### **Output Format**
The response should be in **JSON format** to facilitate easy import into Anki:

```json
{{
    "tags": ["tag_1", "tag_2", ...]
}}
"""

    prompt = prompt_template.format(text_from_book)

    flashcards = fetch_litellm_response(
        prompt, response_format={"type": "json_object"}
    )
    flashcards = json.loads(flashcards)["flashcards"]

    for flashcard in flashcards:
        print("*" * 100)
        print(flashcard["front"])
        print("*" * 100)
        print("*" * 100)
        print(flashcard["back"])
        print("*" * 100)

    tags_prompt = tags_prompt_template.format(text_from_book)
    tags = fetch_litellm_response(
        tags_prompt, response_format={"type": "json_object"}
    )
    tags = json.loads(tags)["tags"]

    for tag in tags:
        print("*" * 100)
        print(tag)
        print("*" * 100)

    return flashcards, tags

def create_flashcard(deck_name, front, back, tags, api_url="http://localhost:8765"):
    payload = {
        "action": "addNote",
        "version": 6,
        "params": {
            "note": {
                "deckName": deck_name,
                "modelName": "KaTeX and Markdown Basic",
                "fields": {
                    "Front": front,
                    "Back": back,
                },
                "tags": tags,
                "options": {"allowDuplicate": False},
            }
        },
    }

    try:
        response = requests.post(api_url, json=payload)
        response.raise_for_status()
        result = response.json()

        if result.get("error") is None:
            print(f"Card added successfully: {result}")
        else:
            print(f"Error: {result['error']}")
    except requests.RequestException as e:
        print(f"Failed to connect to Anki: {e}")

def main():
    deck_name = "core python books"

    with open("text_from_book.txt", "r", encoding="utf-8") as file:
        book_text = file.read()

    sections = [
        section.strip()
        for section in book_text.split("**********************************************************************")
        if section.strip()
    ]

    for index, section in enumerate(sections):
        print("*" * 100)
        print(f"running index: {index}")
        print("*" * 100)

        flashcards, tags = generate(section)
        for flashcard in flashcards:
            create_flashcard(
                deck_name,
                front=flashcard["front"],
                back=flashcard["back"],
                tags=tags,
            )

if __name__ == "__main__":
    main()
