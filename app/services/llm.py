import os
from openai import OpenAI

def get_openai_client() -> OpenAI:
    """Returns an instance of OpenAI client if key is configured, otherwise None."""
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        return None
    return OpenAI(api_key=api_key)

def openai_answer(question: str, context: str) -> str:
    """Generates an answer using gpt-4o-mini with provided context, falling back gracefully if no API key is set."""
    api_key = os.environ.get("OPENAI_API_KEY")
    client = get_openai_client()

    print("This is key===========>", api_key)
    if client is None or not api_key:
        return "I don't have an LLM configured. Here's the most relevant info I found:\n\n"

    try:
        # Re-verify and set the api key (optional, safeguard)
        client.api_key = api_key
        prompt = (
            "You are a helpful assistant. Answer the user's question strictly using the provided context.\n"
            "If the answer isn't in the context, say you don't know.\n\n"
            f"Context:\n{context}\n\nQuestion: {question}\nAnswer:"
        )
        resp = client.chat.completions.create(
            model=os.environ.get("OPENAI_MODEL", "gpt-4o-mini"),
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,
            max_tokens=400,
        )
        print("this resp", resp)
        return resp.choices[0].message.content.strip()
    except Exception as e:
        print(f"OpenAI error: {e}")
        return "LLM error or not configured. Returning retrieved context instead.\n\n" + context
