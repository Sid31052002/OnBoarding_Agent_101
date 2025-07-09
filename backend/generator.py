from openai import OpenAI
from dotenv import load_dotenv
from logger import logger
import os
from vectorstore.rag_retriever import get_top_k_chunks

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def generate_agent_response(history, user_query):
    logger.info("generate_agent_response() was called")

    try:
        faq_chunks = get_top_k_chunks(user_query)
        faq_context = "\n\n".join(faq_chunks)
        logger.info(f"Top chunks: {faq_chunks}")



        system_prompt = (
            "You are a professional onboarding assistant helping customers open a savings account. "
            "Use the FAQ context below to assist. If information is missing, ask follow-up questions.\n\n"
        )

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"FAQ Context:\n{faq_context}\n\nConversation:\n{history}\n\nQuery:\n{user_query}"}
        ]

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages,
            temperature=0.5
        )

        return response.choices[0].message.content.strip()

    except Exception as e:
        print("LLM error:", e)
        return "I'm sorry, I couldn't process your request right now."
