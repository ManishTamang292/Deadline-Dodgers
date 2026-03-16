from openai import OpenAI

class CampusAI:

    def __init__(self, api_key):
        self.client = OpenAI(api_key=api_key)

    def ask(self, question):

        prompt = f"""
You are a campus assistant helping students.

You can answer about:
- facilities
- clubs
- transport
- rewards
- study areas
- campus events

Question: {question}
"""

        response = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role":"user","content":prompt}]
        )

        return response.choices[0].message.content