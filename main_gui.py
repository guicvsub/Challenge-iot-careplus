import tkinter as tk
from tkinter import messagebox
import cv2
import dlib
import numpy as np
from PIL import Image, ImageTk
import db_operations # Módulo CRUD

# --- Constantes do Sistema ---
PREDICTOR = "shape_predictor_5_face_landmarks.dat"
RECOG = "dlib_face_recognition_resnet_model_v1.dat"
THRESH = 0.6

# --- Inicialização do Dlib (Tratamento de Erro Robusto) ---
detector = None
sp = None
rec = None
dlib_loaded = False

try:
    detector = dlib.get_frontal_face_detector()
    sp = dlib.shape_predictor(PREDICTOR)
    rec = dlib.face_recognition_model_v1(RECOG)
    dlib_loaded = True
except RuntimeError as e:
    print(f"Erro ao carregar modelos do Dlib: {e}")
    print("Certifique-se de que os arquivos .dat estão presentes no diretório de execução.")
    # Se falhar, as variáveis continuam None e dlib_loaded é False

# --- Variáveis Globais ---
cap = cv2.VideoCapture(0)
current_vec = None # Vetor da face detectada
validando = False

# --- Classe Principal da Aplicação ---
class FaceCRUDApp:
    def __init__(self, window, window_title):
        self.window = window
        self.window.title(window_title)
        
        # Frame principal para a GUI (lado a lado: Vídeo e Controles)
        main_frame = tk.Frame(window)
        main_frame.pack(padx=10, pady=10)

        # 1. Frame do Vídeo (Esquerda)
        video_frame = tk.Frame(main_frame)
        video_frame.pack(side=tk.LEFT, padx=10)
        
        self.video_label = tk.Label(video_frame, text="Carregando Câmera...", width=640, height=480, bg="black", fg="white")
        self.video_label.pack()
        
        self.status_label = tk.Label(video_frame, text="Status: Aguardando...", fg="blue")
        self.status_label.pack(pady=5)
        
        # Botão para ligar/desligar a validação
        self.toggle_btn = tk.Button(video_frame, text="Ligar Validação", command=self.toggle_validation)
        self.toggle_btn.pack(pady=5)

        # 2. Frame de Controles CRUD (Direita)
        crud_frame = tk.Frame(main_frame)
        crud_frame.pack(side=tk.RIGHT, padx=10, fill=tk.Y)
        
        tk.Label(crud_frame, text="Gestão de Usuários", font=("Arial", 14, "bold")).pack(pady=10)
        
        # --- Controles de Cadastro (CREATE) ---
        tk.Label(crud_frame, text="Nome do Usuário:").pack(pady=5)
        self.name_entry = tk.Entry(crud_frame)
        self.name_entry.pack()
        
        tk.Label(crud_frame, text="Tipo de Perfil:").pack(pady=5)
        self.profile_var = tk.StringVar(crud_frame)
        
        # Usando os novos perfis (Nutricionista e Usuário)
        profiles_dict = db_operations.get_available_profiles()
        profiles = list(profiles_dict.values())
        self.profile_var.set(profiles[0]) # valor padrão
        
        self.profile_menu = tk.OptionMenu(crud_frame, self.profile_var, *profiles)
        self.profile_menu.pack()
        
        # Botão CREATE sem o termo (CREATE)
        self.create_btn = tk.Button(crud_frame, text="1. Cadastrar Novo Usuário", command=self.create_user, bg="green", fg="white")
        self.create_btn.pack(pady=10)
        
        # --- Controles de Leitura (READ) ---
        self.read_btn = tk.Button(crud_frame, text="2. Listar Todos os Usuários", command=self.read_all_users)
        self.read_btn.pack(pady=5)
        
        # --- Controles de Atualização (UPDATE) ---
        tk.Label(crud_frame, text="Nome para Atualizar Perfil:").pack(pady=5)
        self.update_name_entry = tk.Entry(crud_frame)
        self.update_name_entry.pack()
        
        tk.Label(crud_frame, text="Novo Tipo de Perfil:").pack(pady=5)
        self.update_profile_var = tk.StringVar(crud_frame)
        self.update_profile_var.set(profiles[1]) # Padrão para o segundo perfil
        self.update_profile_menu = tk.OptionMenu(crud_frame, self.update_profile_var, *profiles)
        self.update_profile_menu.pack()
        
        # Botão UPDATE sem o termo (UPDATE)
        self.update_btn = tk.Button(crud_frame, text="3. Atualizar Perfil", command=self.update_user, bg="orange", fg="white")
        self.update_btn.pack(pady=10)
        
        # --- Controles de Exclusão (DELETE) ---
        tk.Label(crud_frame, text="Nome para Excluir:").pack(pady=5)
        self.delete_name_entry = tk.Entry(crud_frame)
        self.delete_name_entry.pack()
        
        # Botão DELETE sem o termo (DELETE)
        self.delete_btn = tk.Button(crud_frame, text="4. Excluir Usuário", command=self.delete_user, bg="red", fg="white")
        self.delete_btn.pack(pady=10)

        # Inicia o loop de vídeo
        self.delay = 10 # 10ms delay para 100 FPS (aprox.)
        self.update_video()
        
        # Configura o fechamento da janela
        self.window.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.window.mainloop()

    # --- Lógica de Vídeo e Reconhecimento ---
    def update_video(self):
        global current_vec
        
        ok, frame = cap.read()
        if ok:
            # Processamento de reconhecimento facial
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            current_vec = None # Reset do vetor
            recognition_status = "Status: Aguardando..."

            # Somente tenta processar se o Dlib tiver sido carregado com sucesso
            if dlib_loaded:
                rects = detector(rgb, 1)
                
                for r in rects:
                    # AQUI ESTAVA O ERRO: shape = sp(rgb, r) só deve ser chamado se sp estiver definido
                    shape = sp(rgb, r)
                    chip = dlib.get_face_chip(rgb, shape)
                    current_vec = np.array(rec.compute_face_descriptor(chip), dtype=np.float32)
                    
                    # Desenha o retângulo no frame original
                    cv2.rectangle(frame, (r.left(), r.top()), (r.right(), r.bottom()), (255, 0, 0), 2)
                    
                    recognition_status = "Status: Face Detectada! Pronto para Cadastrar."

                    # Lógica de Validação (READ durante a execução)
                    if validando:
                        db = db_operations.get_db_for_recognition()
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
                        
                        # Atualiza o retângulo e o texto
                        cv2.rectangle(frame, (r.left(), r.top()), (r.right(), r.bottom()), color, 2)
                        
                        if nome != "Desconhecido":
                            texto = f"{nome} - {perfil}"
                            cv2.putText(frame, texto, (r.left(), r.top() - 10),
                                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
                            # Exibe a mensagem de boas-vindas do perfil (Nutricionista/Usuário)
                            recognition_status = f"Status: {messages.get(perfil, 'Bem-vindo!')}"
                        else:
                            cv2.putText(frame, "Desconhecido", (r.left(), r.top() - 10),
                                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
                            recognition_status = "Status: Face Desconhecida."
            else:
                # Caso o Dlib não tenha sido carregado
                recognition_status = "ERRO: Modelos Dlib não carregados. Verifique os arquivos .dat."
                cv2.putText(frame, recognition_status, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
            
            # Atualiza o status na GUI
            self.status_label.config(text=recognition_status)

            # Converte o frame do OpenCV para um formato que o Tkinter pode usar
            img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(img)
            self.photo = ImageTk.PhotoImage(image=img)
            self.video_label.config(image=self.photo)
        
        # Chama a si mesmo após um pequeno atraso para o loop de vídeo
        self.window.after(self.delay, self.update_video)

    def toggle_validation(self):
        global validando
        if not dlib_loaded:
            messagebox.showerror("Erro de Inicialização", "Não é possível ligar a validação. Os modelos do Dlib não foram carregados. Verifique se os arquivos .dat estão no diretório correto.")
            return

        validando = not validando
        if validando:
            self.toggle_btn.config(text="Desligar Validação", bg="red")
        else:
            self.toggle_btn.config(text="Ligar Validação", bg="green")
            self.status_label.config(text="Status: Validação Desligada.")

    # --- Funções de CRUD Integradas à GUI ---
    
    def create_user(self):
        if not dlib_loaded:
            messagebox.showerror("Erro de Inicialização", "Não é possível cadastrar. Os modelos do Dlib não foram carregados.")
            return
            
        nome = self.name_entry.get().strip()
        perfil = self.profile_var.get()
        
        if not nome:
            messagebox.showerror("Erro", "O campo Nome do Usuário não pode estar vazio.")
            return

        if current_vec is None:
            messagebox.showerror("Erro", "Nenhuma face detectada para cadastrar. Posicione-se em frente à câmera.")
            return

        if db_operations.create_user(nome, current_vec, perfil):
            messagebox.showinfo("Sucesso", f"Usuário '{nome}' ({perfil}) cadastrado com sucesso.")
            self.name_entry.delete(0, tk.END)
        else:
            messagebox.showerror("Erro", f"O usuário '{nome}' já existe no banco de dados.")

    def read_all_users(self):
        users = db_operations.read_all_users()
        if not users:
            messagebox.showinfo("Lista de Usuários", "O banco de dados está vazio.")
            return

        user_list = "--- Lista de Usuários ---\n"
        for nome, dados in users.items():
            user_list += f"Nome: {nome} | Perfil: {dados['perfil']}\n"
            
        # Usa um widget Text para exibir a lista formatada
        top = tk.Toplevel(self.window)
        top.title("Usuários Cadastrados")
        text_widget = tk.Text(top, height=20, width=50)
        text_widget.pack(padx=10, pady=10)
        text_widget.insert(tk.END, user_list)
        text_widget.config(state=tk.DISABLED) # Torna o texto somente leitura

    def update_user(self):
        nome = self.update_name_entry.get().strip()
        novo_perfil = self.update_profile_var.get()
        
        if not nome:
            messagebox.showerror("Erro", "O campo Nome para Atualização não pode estar vazio.")
            return

        if db_operations.update_user_profile(nome, novo_perfil):
            messagebox.showinfo("Sucesso", f"Perfil de '{nome}' atualizado para '{novo_perfil}'.")
            self.update_name_entry.delete(0, tk.END)
        else:
            messagebox.showerror("Erro", f"Erro: Usuário '{nome}' não encontrado.")

    def delete_user(self):
        nome = self.delete_name_entry.get().strip()
        
        if not nome:
            messagebox.showerror("Erro", "O campo Nome para Exclusão não pode estar vazio.")
            return
            
        if messagebox.askyesno("Confirmação", f"Tem certeza que deseja excluir o usuário '{nome}'?"):
            if db_operations.delete_user(nome):
                messagebox.showinfo("Sucesso", f"Usuário '{nome}' removido do banco de dados.")
                self.delete_name_entry.delete(0, tk.END)
            else:
                messagebox.showerror("Erro", f"Erro: Usuário '{nome}' não encontrado.")

    def on_closing(self):
        # Libera a câmera e fecha a janela
        if cap.isOpened():
            cap.release()
        self.window.destroy()

# --- Execução ---
if __name__ == "__main__":
    # Certifica-se de que os módulos necessários estão instalados
    try:
        from PIL import Image, ImageTk
    except ImportError:
        print("Erro: A biblioteca 'Pillow' (PIL) é necessária para a GUI.")
        print("Instale com: pip install Pillow")
        exit()
        
    root = tk.Tk()
    app = FaceCRUDApp(root, "Sistema de Acesso Nutricionista/Usuário (Reconhecimento Facial)")
