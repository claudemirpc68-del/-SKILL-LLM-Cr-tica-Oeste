import React, { useState, useEffect } from 'react';
import { Check, X } from 'lucide-react';

export default function App() {
  const [activeTab, setActiveTab] = useState('new');
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [editedComments, setEditedComments] = useState({});
  const [activeCategory, setActiveCategory] = useState('Todas');
  const [wsStatus, setWsStatus] = useState('connecting');
  const [selectedIds, setSelectedIds] = useState(new Set());

  // Configuração da API via env ou fallback local
  const API_URL = import.meta.env.VITE_API_URL || '127.0.0.1:8080';
  const HTTP_PROTOCOL = window.location.protocol === 'https:' ? 'https://' : 'http://';
  const WS_PROTOCOL = window.location.protocol === 'https:' ? 'wss://' : 'ws://';
  
  const BASE_URL = `${HTTP_PROTOCOL}${API_URL}`;
  const WS_URL = `${WS_PROTOCOL}${API_URL}/ws`;

  // Busca dados e conecta no WebSocket ao carregar
  useEffect(() => {
    fetchItems();
    
    const ws = new WebSocket(WS_URL);
    
    ws.onopen = () => setWsStatus('connected');
    ws.onclose = () => setWsStatus('disconnected');
    ws.onerror = () => setWsStatus('disconnected');
    
    ws.onmessage = (event) => {
      const message = JSON.parse(event.data);
      if (message.type === 'new_comment') {
        setItems(prevItems => [message.data, ...prevItems]);
      }
    };
    
    return () => ws.close();
  }, []);

  const fetchItems = async () => {
    try {
      const response = await fetch(`${BASE_URL}/api/comments`);
      const data = await response.json();
      setItems(data);
      setLoading(false);
    } catch (error) {
      console.error("Erro ao buscar dados:", error);
      // Fallback para exibir o visual mesmo se backend falhar (apenas UI mockup data)
      setItems([
        {
          id: 999,
          video_id: '9II9zLSPTio',
          title: "TESTE REAL - JBS e Política",
          date: "06/05/2026",
          summary: "Análise sobre a JBS na pauta diplomática entre Lula e Trump.",
          comment: "Excelente análise, Revista Oeste! O debate sobre a JBS e a diplomacia econômica é fundamental para o futuro do Brasil. Sistema Antigravity testado e aprovado! 🚀",
          status: "pending"
        },
        {
          id: 1,
          video_id: 'v1',
          title: "Jornal da Oeste - 1º Edição",
          date: "06/05/2026",
          summary: "Discussão sobre a reforma tributária e efeitos nas empresas.",
          comment: "A análise sobre a reforma foi superficial, faltando detalhes sobre o impacto em pequenos negócios.",
          status: "pending"
        },
        {
          id: 2,
          video_id: 'v2',
          title: "Oeste com Elas",
          date: "06/05/2026",
          summary: "Entrevista sobre as eleições de 2026.",
          comment: "Perspectiva interessante, mas faltou questionar as propostas reais dos candidatos.",
          status: "pending"
        },
        {
          id: 3,
          video_id: 'v3',
          title: "Esporte sem Firula",
          date: "06/05/2026",
          summary: "Debate sobre Copa do Mundo e economia no futebol",
          comment: "Bom debate, mas faltou analisar o impacto financeiro dos eventos esportivos.",
          status: "pending"
        }
      ]);
      setLoading(false);
    }
  };

  const approveItem = async (id, originalText) => {
    const finalComment = editedComments[id] !== undefined ? editedComments[id] : originalText;
    
    // Tenta backend, senão apenas UI State
    try {
      const res = await fetch(`${BASE_URL}/api/approve/${id}`, { 
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ comment: finalComment })
      });
      if(res.ok) fetchItems();
      else throw new Error("API err");
    } catch(e) {
      setItems(items.map(i => i.id === id ? {...i, status: 'approved', comment: finalComment} : i));
    }
  };

  const rejectItem = async (id) => {
    try {
      const res = await fetch(`${BASE_URL}/api/reject/${id}`, { method: 'POST' });
      if(res.ok) fetchItems();
      else throw new Error("API err");
    } catch(e) {
      setItems(items.map(i => i.id === id ? {...i, status: 'rejected'} : i));
    }
  };

  const toggleSelect = (id) => {
    setSelectedIds(prev => {
      const next = new Set(prev);
      if (next.has(id)) next.delete(id);
      else next.add(id);
      return next;
    });
  };

  const approveBulk = async () => {
    if (selectedIds.size === 0) return;
    
    const itemsToApprove = Array.from(selectedIds).map(id => ({
      id,
      comment: editedComments[id] !== undefined ? editedComments[id] : items.find(i => i.id === id)?.comment
    }));

    try {
      const res = await fetch(`${BASE_URL}/api/bulk_approve`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ items: itemsToApprove })
      });
      
      if(res.ok) {
        fetchItems();
        setSelectedIds(new Set());
        alert(`${selectedIds.size} comentários aprovados com sucesso!`);
      }
    } catch (error) {
      console.error("Erro ao aprovar em lote:", error);
    }
  };

  const pendingItems = items.filter(i => i.status === 'pending');
  const historyItems = items.filter(i => i.status === 'approved' || i.status === 'rejected');
  
  // Filtro inteligente por categoria (usando palavras-chave do resumo/título)
  const filteredPending = pendingItems.filter(item => {
    if (activeCategory === 'Todas') return true;
    const text = (item.title + " " + item.summary).toLowerCase();
    if (activeCategory === 'Política') return text.includes('polític') || text.includes('eleiç') || text.includes('senado') || text.includes('lula') || text.includes('governo');
    if (activeCategory === 'Economia') return text.includes('econom') || text.includes('tributári') || text.includes('mercado') || text.includes('financeir') || text.includes('empresas');
    if (activeCategory === 'Sociedade') return text.includes('sociedade') || text.includes('saúde') || text.includes('esporte') || text.includes('cultura');
    return true;
  });
  
  const approvedItems = historyItems.filter(i => i.status === 'approved');
  const rejectedItems = historyItems.filter(i => i.status === 'rejected');
  const totalProcessed = approvedItems.length + rejectedItems.length;
  const accuracy = totalProcessed === 0 ? 0 : Math.round((approvedItems.length / totalProcessed) * 100);

  return (
    <div className="app-container">
      {/* Header */}
      <header className="header">
        <div className="logo">Revista<span>Oeste</span></div>
        <h1>Painel de Aprovação de Comentários</h1>
        
        {/* Indicador de Antena / Real-Time */}
        <div style={{
          marginLeft: 'auto', 
          display: 'flex', 
          alignItems: 'center', 
          gap: '8px', 
          fontSize: '0.85rem', 
          fontWeight: '600',
          background: 'rgba(0,0,0,0.2)',
          padding: '6px 12px',
          borderRadius: '20px'
        }}>
          <div style={{
            width: '10px', 
            height: '10px', 
            borderRadius: '50%', 
            backgroundColor: wsStatus === 'connected' ? '#2e9f4a' : '#d33833',
            boxShadow: wsStatus === 'connected' ? '0 0 8px #2e9f4a' : '0 0 8px #d33833'
          }}></div>
          {wsStatus === 'connected' ? 'Antena Conectada (Ao Vivo)' : 'Buscando Sinal...'}
        </div>
      </header>

      {/* Tabs */}
      <div className="tabs">
        <button className={`tab ${activeTab === 'new' ? 'active' : ''}`} onClick={() => setActiveTab('new')}>
          Novos Comentários Sugeridos
        </button>
        <button className={`tab ${activeTab === 'history' ? 'active' : ''}`} onClick={() => setActiveTab('history')}>
          Histórico de Comentários
        </button>
        <button className={`tab ${activeTab === 'stats' ? 'active' : ''}`} onClick={() => setActiveTab('stats')}>
          Estatísticas de Treinamento
        </button>
      </div>

      {/* Main Layout */}
      <div className="layout">
        {/* Coluna Esquerda */}
        <div className="left-column">
          <div className="filters">
            <div className="filters-group">
              <label>Data:</label>
              <select>
                <option>{new Date().toLocaleDateString('pt-BR')}</option>
                <option>05/05/2026</option>
                <option>04/05/2026</option>
              </select>
            </div>
            <div className="filters-group" style={{ marginLeft: '10px' }}>
              <label>Categoria:</label>
              <div className="category-tags">
                {['Todas', 'Política', 'Economia', 'Sociedade'].map(cat => (
                  <button 
                    key={cat}
                    className={`category-tag ${activeCategory === cat ? 'active' : ''}`}
                    onClick={() => setActiveCategory(cat)}
                  >
                    {cat}
                  </button>
                ))}
              </div>
            </div>
          </div>

          <div className="comments-list">
            {loading && <p>Carregando...</p>}
            
            {/* Botões de Ação em Lote */}
            {activeTab === 'new' && selectedIds.size > 0 && (
              <div className="bulk-actions" style={{ 
                padding: '15px', 
                background: 'rgba(190, 139, 45, 0.1)', 
                borderRadius: '8px', 
                marginBottom: '15px',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                border: '1px solid var(--primary-gold)'
              }}>
                <span style={{fontWeight: '600'}}>{selectedIds.size} itens selecionados</span>
                <button 
                  className="btn-approve" 
                  onClick={approveBulk}
                  style={{ padding: '8px 20px', borderRadius: '4px' }}
                >
                  Aprovar Selecionados
                </button>
              </div>
            )}
            
            {/* CONTEÚDO DA ABA NOVOS COMENTÁRIOS */}
            {activeTab === 'new' && (
              <>
                {!loading && filteredPending.length === 0 && <p>Nenhum comentário encontrado nesta categoria.</p>}
                {filteredPending.map((item) => (
                  <div className="comment-item" key={item.id}>
                    <div className="comment-header">
                      <input 
                        type="checkbox" 
                        checked={selectedIds.has(item.id)}
                        onChange={() => toggleSelect(item.id)}
                        style={{ width: '18px', height: '18px', cursor: 'pointer' }} 
                      />
                      <h3>{item.title}</h3>
                      <span className="date">{item.date}</span>
                    </div>
                    
                    <p className="comment-summary">
                      <strong>Resumo:</strong> {item.summary}
                    </p>

                    <div className="comment-suggestion-box">
                      <p style={{marginBottom: '5px', fontWeight: 600, fontSize: '0.9rem', color: 'var(--text-dim)'}}>
                        Sua Opinião / Comentário (Editável):
                      </p>
                      <textarea 
                        className="comment-textarea"
                        value={editedComments[item.id] !== undefined ? editedComments[item.id] : item.comment}
                        onChange={(e) => setEditedComments({...editedComments, [item.id]: e.target.value})}
                        style={{
                          width: '100%',
                          minHeight: '80px',
                          padding: '10px',
                          borderRadius: '4px',
                          border: '1px solid var(--border-color)',
                          marginBottom: '15px',
                          fontFamily: 'inherit',
                          fontSize: '0.95rem',
                          lineHeight: '1.5',
                          resize: 'vertical',
                          backgroundColor: '#fff'
                        }}
                      />
                      
                      <div className="comment-actions">
                        <button className="btn btn-approve" onClick={() => approveItem(item.id, item.comment)}>
                          <Check size={18} /> Aprovar e Postar
                        </button>
                        <button className="btn btn-reject" onClick={() => rejectItem(item.id)}>
                          <X size={18} /> Rejeitar
                        </button>
                      </div>
                    </div>
                  </div>
                ))}
              </>
            )}

            {/* CONTEÚDO DA ABA HISTÓRICO */}
            {activeTab === 'history' && (
              <>
                {!loading && historyItems.length === 0 && <p>Nenhum histórico disponível.</p>}
                {historyItems.map((item) => (
                  <div className="comment-item" key={item.id} style={{ opacity: 0.8 }}>
                    <div className="comment-header">
                      <h3 style={{color: item.status === 'approved' ? 'var(--btn-approve)' : 'var(--btn-reject)'}}>
                        {item.status === 'approved' ? '[APROVADO]' : '[REJEITADO]'} {item.title}
                      </h3>
                      <span className="date">{item.date}</span>
                    </div>
                    <p className="comment-summary"><strong>Resumo:</strong> {item.summary}</p>
                    <p style={{ marginTop: '10px', padding: '10px', background: 'var(--bg-color)', borderRadius: '4px' }}>
                      <strong>Comentário Final:</strong> {item.comment}
                    </p>
                  </div>
                ))}
              </>
            )}

            {/* CONTEÚDO DA ABA ESTATÍSTICAS */}
            {activeTab === 'stats' && (
              <div className="comment-item" style={{textAlign: 'center', padding: '40px 20px'}}>
                <h2 style={{color: 'var(--primary-brand)', marginBottom: '10px'}}>Dashboard de RLHF Ativado</h2>
                <p>À medida que você aprova e edita comentários, a precisão do agente LLaMA-3 crescerá.</p>
                <div style={{marginTop: '30px', display: 'flex', justifyContent: 'space-around'}}>
                  <div>
                    <h1 style={{fontSize: '3rem', color: 'var(--text-main)'}}>{historyItems.filter(i => i.status === 'approved').length}</h1>
                    <p>Aprovados</p>
                  </div>
                  <div>
                    <h1 style={{fontSize: '3rem', color: 'var(--text-main)'}}>{historyItems.filter(i => i.status === 'rejected').length}</h1>
                    <p>Rejeitados</p>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Coluna Direita (Sidebar) */}
        <div className="right-column">
          <div className="sidebar-box">
            <h3>Visão Geral</h3>
            <div className="stats-row">
              <span>Aprovados:</span> <strong>{approvedItems.length}</strong>
            </div>
            <div className="stats-row" style={{ marginBottom: '20px' }}>
              <span>Rejeitados:</span> <strong>{rejectedItems.length}</strong>
            </div>
            
            {approvedItems.length > 0 && (
              <>
                <h4 style={{ fontSize: '0.85rem', marginBottom: '10px', color: 'var(--text-dim)' }}>Últimas Aprovações:</h4>
                <ul className="history-list">
                  {approvedItems.slice(-3).map(item => (
                    <li key={`app-${item.id}`}>{item.title}</li>
                  ))}
                </ul>
              </>
            )}
            {approvedItems.length === 0 && <p style={{fontSize: '0.85rem', color: 'var(--text-dim)'}}>Nenhuma aprovação ainda.</p>}
          </div>

          <div className="sidebar-box">
            <h3>Métrica RLHF</h3>
            <div className="stats-row" style={{ marginBottom: '5px' }}>
              <span>Taxa de Aprovação: </span> <strong>{accuracy}%</strong>
            </div>
            <div className="progress-bar-container">
              <div className="progress-bar-fill" style={{ width: `${accuracy}%` }}></div>
            </div>
          </div>

          <div className="sidebar-box">
            <h3>Feedbacks de Rejeição:</h3>
            {rejectedItems.length > 0 ? (
              <ul className="history-list reject-dots">
                {rejectedItems.slice(-3).map(item => (
                  <li key={`rej-${item.id}`}>{item.title}</li>
                ))}
              </ul>
            ) : (
              <p style={{fontSize: '0.85rem', color: 'var(--text-dim)'}}>Nenhuma rejeição no momento.</p>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
