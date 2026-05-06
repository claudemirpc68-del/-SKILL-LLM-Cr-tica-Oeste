from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import uvicorn
import asyncio
import json
import os
from poster import YouTubePoster
from collector import YouTubeFetcher
from generator import CritiqueGenerator

app = FastAPI(title="LLM Crítica Oeste API")

# Inicializa componentes com proteção
try:
    poster = YouTubePoster()
except Exception as e:
    print(f"AVISO: Falha ao iniciar YouTubePoster: {e}. O sistema funcionará em modo simulação.")
    poster = YouTubePoster(credentials_file=None) # Força modo mock

fetcher = YouTubeFetcher()
generator = CritiqueGenerator()

# Configuração de CORS para permitir que o React (Vite) acesse o backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Em produção, especifique o domínio
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- GERENCIADOR DE WEBSOCKETS (REAL-TIME) ---
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except:
                pass

manager = ConnectionManager()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text() # Apenas mantem a conexão aberta
    except WebSocketDisconnect:
        manager.disconnect(websocket)

# Modelos de Dados
class CommentItem(BaseModel):
    id: int
    video_id: str
    title: str
    channel: str
    date: str
    summary: str
    comment: str
    status: str
    thumbnail: str

class ApproveRequest(BaseModel):
    comment: str

class BulkApproveRequest(BaseModel):
    items: List[dict] # Lista de {id, comment}


# Banco de dados temporário (Mock)
db_comments = [
    {
        "id": 999,
        "video_id": "9II9zLSPTio",
        "title": "TESTE REAL - JBS e Política",
        "channel": "Revista Oeste",
        "date": "06/05/2026",
        "summary": "Análise sobre a JBS na pauta diplomática entre Lula e Trump.",
        "comment": "Excelente análise, Revista Oeste! O debate sobre a JBS e a diplomacia econômica é fundamental para o futuro do Brasil. Sistema Antigravity testado e aprovado! 🚀",
        "status": "pending",
        "thumbnail": "https://img.youtube.com/vi/9II9zLSPTio/mqdefault.jpg"
    },
    {
        "id": 1,
        "video_id": "dQw4w9WgXcQ", # Exemplo
        "title": "Debate sobre CLT e impacto nas empresas",
        "channel": "Revista Oeste",
        "date": "05/05/2026",
        "summary": "Uma análise detalhada sobre as recentes mudanças propostas na legislação trabalhista.",
        "comment": "O debate ignorou os efeitos sobre pequenas empresas; faltou profundidade na análise técnica.",
        "status": "pending",
        "thumbnail": "https://images.unsplash.com/photo-1590283603385-17ffb3a7f29f?auto=format&fit=crop&q=80&w=400"
    },
    {
        "id": 2,
        "video_id": "jNQXAC9IVRw", # Exemplo
        "title": "Entrevista sobre eleições de 2026",
        "channel": "Revista Oeste",
        "date": "04/05/2026",
        "summary": "Discussão sobre o cenário eleitoral antecipado.",
        "comment": "A conversa foi interessante, mas evitou discutir propostas concretas dos candidatos.",
        "status": "pending",
        "thumbnail": "https://images.unsplash.com/photo-1529107386315-e1a2ed48a620?auto=format&fit=crop&q=80&w=400"
    }
]

# Função de monitoramento em segundo plano
async def monitor_channel():
    print("Iniciando Agente de Monitoramento Autônomo...")
    while True:
        try:
            print("Verificando novos vídeos no canal Revista Oeste...")
            new_videos = fetcher.fetch_new_videos(limit=3)
            
            for video in new_videos:
                # Verifica se o vídeo já está no nosso "banco de dados"
                exists = any(item["video_id"] == video["id"] for item in db_comments)
                
                if not exists:
                    print(f"Novo vídeo detectado: {video['title']}. Processando IA...")
                    
                    # Extrai detalhes (descrição/transcrição parcial via API Rápida)
                    details = fetcher.get_video_details(video["id"])
                    
                    if not details:
                        print(f"Ignorado: '{video['title']}' (A live ainda está agendada/futura).")
                        continue
                        
                    content = details.get("content_combined") or video["title"]
                    
                    # IA gera resumo e crítica
                    summary = generator.summarize(content)
                    critique = generator.generate_critique(summary)
                    
                    # Adiciona à fila
                    new_item = {
                        "id": len(db_comments) + 1,
                        "video_id": video["id"],
                        "title": video["title"],
                        "channel": "Revista Oeste",
                        "date": datetime.now().strftime("%d/%m/%Y"),
                        "summary": summary,
                        "comment": critique,
                        "status": "pending",
                        "thumbnail": f"https://img.youtube.com/vi/{video['id']}/mqdefault.jpg"
                    }
                    db_comments.insert(0, new_item) # Adiciona no topo
                    print(f"Vídeo '{video['title']}' adicionado à fila de aprovação.")
                    
                    # Notifica o Frontend via WebSocket em tempo real
                    await manager.broadcast({"type": "new_comment", "data": new_item})

        except Exception as e:
            print(f"Erro no monitoramento: {e}")
        
        # Espera 2 minutos antes da próxima verificação (Real-Time loop)
        await asyncio.sleep(120)

@app.on_event("startup")
async def startup_event():
    # Inicia o monitoramento em segundo plano
    asyncio.create_task(monitor_channel())

@app.get("/api/comments", response_model=List[CommentItem])
async def get_comments():
    return db_comments

@app.post("/api/approve/{comment_id}")
async def approve_comment(comment_id: int, req: ApproveRequest):
    for item in db_comments:
        if item["id"] == comment_id:
            # Atualiza o comentário com a versão editada pelo usuário
            final_comment = req.comment
            item["comment"] = final_comment
            
            # Tenta postar no YouTube
            success = poster.post_comment(item["video_id"], final_comment)
            if success:
                item["status"] = "approved"
                
                # Auto-Append no Dataset para RLHF (Treinamento LoRA)
                dataset_dir = "datasets"
                os.makedirs(dataset_dir, exist_ok=True)
                log_file = os.path.join(dataset_dir, "critica_oeste_log.json")
                
                log_entry = {
                    "input": f"Resumo: {item['summary']}",
                    "output": final_comment
                }
                
                dataset = []
                if os.path.exists(log_file):
                    try:
                        with open(log_file, "r", encoding="utf-8") as f:
                            dataset = json.load(f)
                    except json.JSONDecodeError:
                        pass
                
                dataset.append(log_entry)
                
                with open(log_file, "w", encoding="utf-8") as f:
                    json.dump(dataset, f, indent=2, ensure_ascii=False)
                
                return {"message": "Comentário postado, aprovado e adicionado ao dataset RLHF com sucesso"}
            else:
                raise HTTPException(status_code=500, detail="Erro ao postar no YouTube. Verifique as credenciais.")
    raise HTTPException(status_code=404, detail="Comentário não encontrado")

@app.post("/api/reject/{comment_id}")
async def reject_comment(comment_id: int):
    for item in db_comments:
        if item["id"] == comment_id:
            item["status"] = "rejected"
            return {"message": "Comentário rejeitado"}
    raise HTTPException(status_code=44, detail="Comentário não encontrado")

@app.get("/api/stats")
async def get_stats():
    return {
        "efficiency": "88.4%",
        "volume": 432,
        "response_time": "12m",
        "accuracy_trend": "+5.2%"
    }

@app.post("/api/bulk_approve")
async def bulk_approve(req: BulkApproveRequest):
    approved_count = 0
    for entry in req.items:
        item_id = entry.get("id")
        user_comment = entry.get("comment")
        
        for item in db_comments:
            if item["id"] == item_id and item["status"] == "pending":
                # Simula aprovação
                item["status"] = "approved"
                item["comment"] = user_comment
                
                # RLHF Log
                log_entry = {
                    "video_id": item["video_id"],
                    "title": item["title"],
                    "original_summary": item["summary"],
                    "final_comment": user_comment,
                    "timestamp": datetime.now().isoformat()
                }
                save_to_rlhf_dataset(log_entry)
                
                # Mock Poster
                poster.post_comment(item["video_id"], user_comment)
                approved_count += 1
                break
    return {"message": f"{approved_count} comentários aprovados!"}

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8080))
    host = os.getenv("HOST", "0.0.0.0")
    uvicorn.run(app, host=host, port=port)
