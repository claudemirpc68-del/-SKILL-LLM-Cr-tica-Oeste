import os
import pickle
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

# Escopo necessário para postar comentários
SCOPES = ['https://www.googleapis.com/auth/youtube.force-ssl']

class YouTubePoster:
    def __init__(self, credentials_file='client_secrets.json', token_file='token.pickle'):
        self.credentials_file = credentials_file
        self.token_file = token_file
        self.youtube = self._authenticate()

    def _authenticate(self):
        creds = None
        # O arquivo token.pickle armazena os tokens de acesso e atualização do usuário
        if os.path.exists(self.token_file):
            with open(self.token_file, 'rb') as token:
                creds = pickle.load(token)
        
        # Se não houver credenciais válidas, deixa o usuário logar
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                if not os.path.exists(self.credentials_file):
                    print(f"AVISO: Arquivo {self.credentials_file} não encontrado!")
                    return None
                
                flow = InstalledAppFlow.from_client_secrets_file(self.credentials_file, SCOPES)
                creds = flow.run_local_server(port=0)
            
            # Salva as credenciais para a próxima vez
            with open(self.token_file, 'wb') as token:
                pickle.dump(creds, token)

        return build('youtube', 'v3', credentials=creds)

    def post_comment(self, video_id, text):
        """Posta um comentário em um vídeo específico."""
        if not self.youtube:
            print("AVISO: Autenticação não configurada. Simulando postagem (Mock) para testes e geração de dataset...")
            return True

        try:
            print(f"Tentando postar comentário no vídeo {video_id}...")
            request = self.youtube.commentThreads().insert(
                part="snippet",
                body={
                    "snippet": {
                        "videoId": video_id,
                        "topLevelComment": {
                            "snippet": {
                                "textOriginal": text
                            }
                        }
                    }
                }
            )
            response = request.execute()
            print(f"✅ SUCESSO: Comentário postado no YouTube! ID: {response['id']}")
            return True
        except Exception as e:
            print(f"❌ ERRO CRÍTICO AO POSTAR: {str(e)}")
            return False

if __name__ == "__main__":
    # Teste manual
    # poster = YouTubePoster()
    # poster.post_comment("ID_DO_VIDEO", "Teste de comentário automático via Antigravity.")
    pass
