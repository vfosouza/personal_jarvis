
print("PROMPT_BUILDER_V2_LOADED")
def build_prompt(
    question: str,
    context: str) -> str:
    return f"""
            Você é um assistente especialista em engenharia de dados.
            Utilize APENAS o contexto abaixo para responder.
            CONTEXTO:
            {context}
            PERGUNTA:
            {question}
            RESPOSTA:
            """