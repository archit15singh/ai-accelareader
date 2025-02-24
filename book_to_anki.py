
import requests
import json
import os
from dotenv import load_dotenv
import openai

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")

client = openai.OpenAI(api_key=api_key)


def fetch_openai_response(prompt, response_format=None):
    response = client.chat.completions.create(
        model="gpt-4o-2024-08-06",
        messages=[{"role": "user", "content": prompt}],
        response_format=response_format,
    )
    return response.choices[0].message.content


def generate():
    with open("text_from_book.txt", "r", encoding="utf-8") as f:
        text_from_book = f.read()
    
    if not text_from_book.strip():
        return None, None

    prompt_template = """
Given the following excerpt from a technical book:

# Excerpt from the book
{}

# Instructions
Your goal is to generate **structured, high-quality Anki flashcards** (front-back format) that thoroughly cover the given concept. 
Each flashcard should focus on a specific aspect to ensure deep understanding and long-term retention.


⚠️ **STRICT REQUIREMENTS:**  
- **Do NOT omit any details** from the excerpt. Every important technical insight should be included, especially those relevant to a **software engineer**.
- **Think step by step.** Break down the concept logically before generating flashcards.
- **Think deeply.** Extract all nuances, edge cases, and performance considerations.
- **Think creatively.** Provide alternative perspectives, real-world applications, and engaging recall challenges.

### **Aspects to Cover**
Each flashcard should focus on one of the following aspects:

1. **Core Concept Understanding**  
   - Summarize the concept in simple terms.  
   - Explain why it exists and what problem it solves.  
   - Provide a clear and minimal Python example.  

2. **Common Mistakes & Debugging**  
   - Show incorrect usage patterns.  
   - Explain why they are incorrect and how to fix them.  
   - Include a corrected version with an explanation.  

3. **Comparison with Alternative Methods**  
   - Compare this concept to other approaches.  
   - Provide a pros/cons analysis in a structured table.  
   - Include example implementations for comparison.  

4. **Best Practices & Edge Cases**  
   - Outline the best way to use this concept.  
   - Highlight common pitfalls and edge cases.  
   - Provide real-world best practice recommendations.  

5. **Real-World Applications**  
   - Explain practical scenarios where this concept is useful.  
   - Include a real-world example in Python.  

6. **Active Recall Challenges**  
   - Generate questions that require deep thinking and force retrieval.  
   - Cover why, how, and when to use the concept.  
   - Include conceptual and code-based challenges.  

ALWAYS USE CODE SNIPPETS AS EXAMPLES AND DETAIL IT AS MUCH AS YOU CAN.
REMEMBER, YOU CAN CREATE AS MANY FLASHCARDS FOR EACH OF THE POINT ABOVE!
---

### **Output Format**
The response should be in **JSON format** to facilitate easy import into Anki:

```json
{{
    "flashcards": [
        {{
            "front": "markdown content",
            "back": "markdown content",
        }},
        {{
            "front": "markdown content",
            "back": "markdown content",
        }},
    ]
}}
"""

    tags_prompt_template = """
Given the following excerpt from a technical book, generate a concise list of broad Anki tags.
The tags should be simple, high-level, and avoid excessive granularity to prevent clutter.
Focus on general topics rather than overly specific details.

# Excerpt from the book
{}

---

### **Output Format**
The response should be in **JSON format** to facilitate easy import into Anki:

```json
{{
    "tags": ["tag_1", "tag_2", ...]
}}
"""


    prompt = prompt_template.format(text_from_book)

    flashcards = fetch_openai_response(
        prompt, response_format={"type": "json_object"}
    )
    flashcards = json.loads(flashcards)["flashcards"]

    for flashcard in flashcards:
        print("*"*100)
        print(flashcard['front'])
        print("*"*100)
        print("*"*100)
        print(flashcard['back'])
        print("*"*100)


    tags_prompt = tags_prompt_template.format(text_from_book)
    tags = fetch_openai_response(
        tags_prompt, response_format={"type": "json_object"}
    )
    tags = json.loads(tags)["tags"]
    
    for tag in tags:
        print("*"*100)
        print(tag)
        print("*"*100)
    
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


if __name__ == "__main__":
    deck_name = "core python books"
    flashcards, tags = generate()

    for flashcard in flashcards:
        create_flashcard(deck_name, front=flashcard['front'], back=flashcard['back'], tags=tags)
