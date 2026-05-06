# ⚙️ LLM Crítica Oeste

> Sistema autônomo de geração, curadoria e publicação de comentários críticos nos vídeos do canal **Revista Oeste** no YouTube, com painel de aprovação humana e motor de aprendizado contínuo (RLHF).

---

## 🧠 Visão Geral

O **LLM Crítica Oeste** monitora o canal da Revista Oeste em tempo real. Quando um novo vídeo é detectado, extrai a transcrição, gera um resumo e cria um comentário crítico via LLM. O comentário vai para um **painel de aprovação humana** antes de ser publicado.

Cada aprovação/rejeição alimenta automaticamente um dataset de **RLHF**, melhorando o modelo continuamente.

```
YouTube Canal → Coletor → IA (Resumo + Crítica) → Painel de Aprovação → YouTube Comentário
                                                           ↓
                                                    Dataset RLHF (LoRA)
```

---

## ✨ Funcionalidades

| Módulo | Descrição |
|--------|-----------|
| 🎥 **Coletor** | Monitora o canal em loop (a cada 2 min) |
| 📝 **Sumarizador** | Extrai transcrições e condensa o conteúdo |
| 🤖 **Gerador de Crítica** | LLM gera comentário analítico e conciso |
| 🖥️ **Painel de Aprovação** | Interface React com aprovação individual ou em lote |
| 📡 **Real-Time (WebSocket)** | Novos vídeos aparecem instantaneamente no painel |
| 📊 **Métricas RLHF** | Taxa de aprovação e dataset para fine-tuning |
| ✅ **Publicação** | Posta o comentário aprovado no YouTube via OAuth2 |

---

## 🚀 Como Rodar Localmente

**Backend:**
```bash
cd backend
pip install -r requirements.txt
python main.py
```

**Frontend:**
```bash
cd antigravity-ui
npm install
npm run dev
```

Acesse em: `http://localhost:5173`

---

## 🐳 Deploy (Coolify)

### Variáveis de Ambiente

| Variável | Serviço | Descrição |
|----------|---------|-----------|
| `PORT` | Backend | Porta da API (padrão: `8080`) |
| `VITE_API_URL` | Frontend | Domínio da API |

```bash
docker-compose up --build
```

---

## 🛠️ Tecnologias

**Backend:** Python · FastAPI · yt-dlp · YouTube API v3 · WebSockets

**Frontend:** React · Vite · Lucide Icons

**Infra:** Docker · Nginx · Coolify

---

<p align="center">Desenvolvido com ⚙️ pelo sistema <strong>Antigravity</strong></p>
