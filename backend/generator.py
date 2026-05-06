import openai
import os
from dotenv import load_dotenv

load_dotenv()

class CritiqueGenerator:
    def __init__(self, api_key=None, model="llama3-70b-8192"):
        # Pode ser configurado para Groq, Ollama ou OpenAI
        self.client = openai.OpenAI(
            api_key=api_key or os.getenv("LLM_API_KEY", "mock_key"),
            base_url=os.getenv("LLM_BASE_URL", "https://api.groq.com/openai/v1")
        )
        self.model = model

    def summarize(self, text: str) -> str:
        """Gera um resumo abstrativo curto (3 sentenças)."""
        prompt = f"Resuma o seguinte conteúdo da Revista Oeste em exatamente 3 sentenças curtas e objetivas:\n\n{text}"
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=150
            )
            return response.choices[0].message.content
        except Exception:
            return "Resumo indisponível no momento (Modo Mock ativo)."

    def generate_critique(self, summary: str) -> str:
        """Gera uma crítica concisa e analítica (estilo 'critical_concise')."""
        system_prompt = (
            "Você é um analista político crítico e conciso. "
            "Sua tarefa é ler um resumo de um vídeo da Revista Oeste e gerar uma crítica analítica. "
            "Regras: Máximo de 3 sentenças. Tom analítico. Estilo crítico e direto."
        )
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Resumo: {summary}"}
                ],
                max_tokens=100
            )
            return response.choices[0].message.content
        except Exception:
            # Fallback para o exemplo do arquivo de skill se falhar a API
            return "A análise foi genérica; faltou abordar o impacto real sobre o cenário político atual."

if __name__ == "__main__":
    gen = CritiqueGenerator()
    test_summary = "Debate sobre a nova política fiscal e cortes de gastos."
    print(gen.generate_critique(test_summary))
