
print("PROMPT_BUILDER_V2_LOADED")
def build_prompt(
    question: str,
    context: str) -> str:
    return f"""
            Você é um especialista em engenharia de dados.
            Responda APENAS usando os resultados encontrados.
            Liste:
            - arquivo
            - trecho encontrado
            - explicação do uso
            
            RESULTADOS:
            CONTEXTO:
            {context}
            PERGUNTA:
            {question}
            RESPOSTA:
            """