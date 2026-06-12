
def build_prompt(question: str, context: str) -> str:
    return f"""
Você é um especialista em engenharia de dados.
Utilize APENAS o contexto fornecido.
CONTEXTO:
{context}
PERGUNTA:
{question}
RESPOSTA:
"""

def build_reference_prompt(question: str, context: str):
    return f"""
Você é especialista em análise de código.
Responda SOMENTE usando os trechos encontrados.
Para cada ocorrência informe:
- arquivo
- trecho encontrado
- explicação do uso
Não invente arquivos ou código.
CONTEXTO:
{context}
PERGUNTA:
{question}
RESPOSTA:
"""