import cv2
import dlib
import numpy as np
import os
import db_operations # Importa o módulo com as funções CRUD

# --- Constantes do Sistema ---
PREDICTOR = "shape_predictor_5_face_landmarks.dat"
RECOG = "dlib_face_recognition_resnet_model_v1.dat"
THRESH = 0.6

# --- Inicialização do Dlib ---
try:
    detector = dlib.get_frontal_face_detector()
    sp = dlib.shape_predictor(PREDICTOR)
    rec = dlib.face_recognition_model_v1(RECOG)
except RuntimeError as e:
    print(f"Erro ao carregar modelos do Dlib: {e}")
    print("Certifique-se de que os arquivos 'shape_predictor_5_face_landmarks.dat' e 'dlib_face_recognition_resnet_model_v1.dat' estão presentes.")
    exit()

# --- Variáveis de Estado ---
cap = cv2.VideoCapture(0)
validando = False
ultimo = 0
cooldown = 3
# Variáveis de comunicação serial (mantidas como comentário)
'''
import serial
import time
PORT = "COM7"
BAUD = 9600
ser = serial.Serial(PORT, BAUD, timeout=0.5)
time.sleep(2)
'''

# --- Funções Auxiliares para o CRUD no Console ---

def handle_create(vec):
    """Lida com a operação de Cadastro (CREATE)."""
    nome = input("Nome: ").strip()
    if not nome:
        print("Nome inválido.")
        return

    # A função db_operations.read_user() é usada para verificar se o usuário já existe.
    try:
        if db_operations.read_user(nome):
            print(f"Erro: O usuário '{nome}' já existe no banco de dados.")
            return
    except AttributeError:
        print("Erro de importação: A função 'db_operations.read_user' não foi encontrada. Verifique se 'db_operations.py' está no mesmo diretório.")
        return

    print("\nEscolha o perfil de investidor:")
    profiles = db_operations.get_available_profiles()
    for num, profile_name in profiles.items():
        print(f"{num} - {profile_name}")
    
    opcao = input("Digite o número: ").strip()
    perfil = profiles.get(opcao, "Conservador") # Padrão para Conservador

    if db_operations.create_user(nome, vec, perfil):
        print(f"Sucesso: Usuário '{nome}' cadastrado com perfil '{perfil}'.")
    else:
        print(f"Erro ao cadastrar '{nome}'.")

def handle_read_all():
    """Lida com a operação de Listar Todos (READ All)."""
    try:
        users = db_operations.read_all_users()
    except AttributeError:
        print("Erro de importação: A função 'db_operations.read_all_users' não foi encontrada. Verifique se 'db_operations.py' está no mesmo diretório.")
        return
        
    if not users:
        print("\n--- Banco de Dados Vazio ---")
        return

    print("\n--- Lista de Usuários Cadastrados ---")
    for i, (nome, dados) in enumerate(users.items(), 1):
        # Mostra o nome e o perfil, mas omite o vetor para simplicidade
        print(f"{i}. Nome: {nome} | Perfil: {dados['perfil']}")
    print("--------------------------------------")

def handle_update():
    """Lida com a operação de Atualizar Perfil (UPDATE)."""
    nome = input("Nome do usuário para atualizar: ").strip()
    if not nome: return

    try:
        user = db_operations.read_user(nome)
    except AttributeError:
        print("Erro de importação: A função 'db_operations.read_user' não foi encontrada. Verifique se 'db_operations.py' está no mesmo diretório.")
        return
        
    if not user:
        print(f"Erro: Usuário '{nome}' não encontrado.")
        return

    print(f"\nUsuário encontrado. Perfil atual: {user['perfil']}")
    print("Escolha o novo perfil de investidor:")
    profiles = db_operations.get_available_profiles()
    for num, profile_name in profiles.items():
        print(f"{num} - {profile_name}")
    
    opcao = input("Digite o número: ").strip()
    novo_perfil = profiles.get(opcao, user['perfil']) # Mantém o atual se a opção for inválida

    if db_operations.update_user_profile(nome, novo_perfil):
        print(f"Sucesso: Perfil de '{nome}' atualizado para '{novo_perfil}'.")
    else:
        print(f"Erro ao atualizar o perfil de '{nome}'.")

def handle_delete():
    """Lida com a operação de Excluir Usuário (DELETE)."""
    nome = input("Nome do usuário para EXCLUIR: ").strip()
    if not nome: return

    if db_operations.delete_user(nome):
        print(f"Sucesso: Usuário '{nome}' removido do banco de dados.")
    else:
        print(f"Erro: Usuário '{nome}' não encontrado.")

# --- Loop Principal ---

print("[E]=Cadastrar | [V]=Validar ON/OFF | [L]=Listar | [U]=Atualizar Perfil | [D]=Deletar | [Q]=Sair")

while True:
    ok, frame = cap.read()
    if not ok: break

    # Processamento de reconhecimento facial
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    rects = detector(rgb, 1)
    
    current_vec = None # Vetor da face detectada (se houver)

    for r in rects:
        shape = sp(rgb, r)
        chip = dlib.get_face_chip(rgb, shape)
        current_vec = np.array(rec.compute_face_descriptor(chip), dtype=np.float32)

        # Lógica de Validação (READ durante a execução)
        if validando:
            try:
                db = db_operations.get_db_for_recognition()
            except AttributeError:
                print("Erro de importação: A função 'db_operations.get_db_for_recognition' não foi encontrada. Verifique se 'db_operations.py' está no mesmo diretório.")
                db = {} # Continua com um DB vazio para evitar quebrar o loop

            nome, dist, perfil = "Desconhecido", 999, None
            
            if db:
                for n, dados in db.items():
                    d = np.linalg.norm(current_vec - dados["vetor"])
                    if d < dist:
                        nome, dist, perfil = n, d, dados["perfil"]

            if dist > THRESH:
                nome, perfil = "Desconhecido", None

            messages = db_operations.get_profile_messages()
            color = (0, 255, 0) if nome != "Desconhecido" else (0, 0, 255)
            cv2.rectangle(frame, (r.left(), r.top()), (r.right(), r.bottom()), color, 2)

            if nome != "Desconhecido":
                texto = f"{nome} - {perfil}"
                cv2.putText(frame, texto, (r.left(), r.top() - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
                print(messages.get(perfil, "Bem-vindo!")) # Usa .get para segurança
            else:
                cv2.putText(frame, "Desconhecido", (r.left(), r.top() - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
            
            # Lógica de comunicação serial (mantida como comentário)
            '''
            if nome != "Desconhecido" and time.time()-ultimo > cooldown:
                ser.write(b'O')
                ultimo = time.time()
            '''

    cv2.imshow("Faces", frame)
    k = cv2.waitKey(1) & 0xFF

    # --- Comandos do Console (CRUD) ---
    if k == ord('q'): break
    if k == ord('v'): validando = not validando
    
    # CREATE - Cadastro de novo usuário
    if k == ord('e') and current_vec is not None:
        handle_create(current_vec)
    elif k == ord('e') and current_vec is None:
        print("Erro: Nenhuma face detectada para cadastrar.")

    # READ - Listar todos os usuários
    if k == ord('l'):
        handle_read_all()
        
    # UPDATE - Atualizar perfil de usuário
    if k == ord('u'):
        handle_update()
        
    # DELETE - Excluir usuário
    if k == ord('d'):
        handle_delete()

cap.release()
cv2.destroyAllWindows()
'''ser.close()'''
