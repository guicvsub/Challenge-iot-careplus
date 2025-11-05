import pickle
import os
from typing import Dict, Any, Optional

DB_FILE = "db.pkl"

def _load_db() -> Dict[str, Any]:
    """Carrega o banco de dados (dicionário) do arquivo pickle."""
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "rb") as f:
                return pickle.load(f)
        except EOFError:
            # Arquivo vazio ou corrompido, retorna um dicionário vazio
            return {}
    return {}

def _save_db(db: Dict[str, Any]):
    """Salva o banco de dados (dicionário) no arquivo pickle."""
    with open(DB_FILE, "wb") as f:
        pickle.dump(db, f)

# --- CRUD Operations ---

def create_user(nome: str, vetor: Any, perfil: str) -> bool:
    """
    CREATE: Adiciona um novo usuário ao banco de dados.
    Retorna True se o usuário foi criado, False se já existia.
    """
    db = _load_db()
    if nome in db:
        return False
    
    db[nome] = {"vetor": vetor, "perfil": perfil}
    _save_db(db)
    return True

def read_user(nome: str) -> Optional[Dict[str, Any]]:
    """
    READ (Individual): Retorna os dados de um usuário específico.
    """
    db = _load_db()
    return db.get(nome)

def read_all_users() -> Dict[str, Any]:
    """
    READ (All): Retorna todos os usuários no banco de dados.
    """
    return _load_db()

def update_user_profile(nome: str, novo_perfil: str) -> bool:
    """
    UPDATE: Atualiza apenas o perfil de usuário (Nutricionista/Usuário) de um usuário existente.
    Retorna True se o usuário foi atualizado, False se não foi encontrado.
    """
    db = _load_db()
    if nome not in db:
        return False
    
    # Manter o vetor de reconhecimento facial original
    db[nome]["perfil"] = novo_perfil
    _save_db(db)
    return True

def delete_user(nome: str) -> bool:
    """
    DELETE: Remove um usuário do banco de dados.
    Retorna True se o usuário foi removido, False se não foi encontrado.
    """
    db = _load_db()
    if nome in db:
        del db[nome]
        _save_db(db)
        return True
    return False

# Funções auxiliares para o código principal

def get_db_for_recognition() -> Dict[str, Any]:
    """Retorna o DB para uso no loop de reconhecimento facial."""
    return _load_db()

def get_available_profiles() -> Dict[str, str]:
    """Retorna os tipos de usuário disponíveis (Nutricionista/Usuário)."""
    # Mapeamento simples para a GUI, mas os valores são os tipos de perfil
    return {"1": "Nutricionista", "2": "Usuário"}

def get_profile_messages() -> Dict[str, str]:
    """Retorna as mensagens de boas-vindas por tipo de usuário."""
    return {
        "Nutricionista": "Bem-vindo(a), Nutricionista! Seu acesso ao sistema de gestão está liberado.",
        "Usuário": "Bem-vindo(a), Usuário! Seu perfil foi carregado com sucesso."
    }

if __name__ == '__main__':
    # Exemplo de uso para demonstração
    print("--- Teste CRUD ---")
    
    # 1. CREATE (Simulado)
    print("\n1. CREATE (Adicionar 'Teste1')")
    # Usando um vetor de exemplo (apenas para teste)
    vetor_exemplo = [0.1, 0.2, 0.3] 
    if create_user("Teste1", vetor_exemplo, "Usuário"):
        print("Usuário Teste1 criado com sucesso.")
    
    # 2. READ ALL
    print("\n2. READ ALL (Usuários Atuais)")
    users = read_all_users()
    for name, data in users.items():
        print(f" - {name}: {data['perfil']}")
        
    # 3. UPDATE
    print("\n3. UPDATE (Mudar perfil de 'Teste1' para 'Nutricionista')")
    if update_user_profile("Teste1", "Nutricionista"):
        print("Perfil de Teste1 atualizado.")
        user_data = read_user("Teste1")
        if user_data:
            print("Novo perfil:", user_data["perfil"])
        
    # 4. DELETE
    print("\n4. DELETE (Remover 'Teste1')")
    if delete_user("Teste1"):
        print("Usuário Teste1 removido.")
        
    # 5. READ ALL (Verificação)
    print("\n5. READ ALL (Verificação após DELETE)")
    users = read_all_users()
    if "Teste1" not in users:
        print("Teste1 não está mais no DB.")
    else:
        print("Erro: Teste1 ainda está no DB.")
    
    # Limpar o arquivo de teste para não poluir o ambiente real
    if os.path.exists(DB_FILE):
        os.remove(DB_FILE)
        print(f"\nArquivo {DB_FILE} limpo.")