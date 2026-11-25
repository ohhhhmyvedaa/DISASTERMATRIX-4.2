import os
from .offline_assistant import answer as offline_answer

def respond(question, context=None):
    key=os.getenv("OPENAI_API_KEY")
    if key:
        try:
            from openai import OpenAI
            client=OpenAI(api_key=key)
            model=os.getenv("OPENAI_MODEL","gpt-4o-mini")
            system=("You are DISASTERMATRIX educational project assistant. Use only supplied context for live values. "
                    "Never fabricate readings, never claim disaster prediction, never issue real emergency instructions, "
                    "and never control hardware. Clearly distinguish historical, live API, measured and simulated data.")
            result=client.chat.completions.create(
                model=model,
                messages=[{"role":"system","content":system},
                          {"role":"user","content":f"Context: {context or 'No live context supplied.'}\\nQuestion: {question}"}],
                temperature=0.2)
            return result.choices[0].message.content
        except Exception as exc:
            return "Online AI unavailable; using offline assistant. ("+str(exc)[:180]+")\n\n"+offline_answer(question,context)
    return offline_answer(question,context)
