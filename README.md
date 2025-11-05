# Sistema de Acesso por Reconhecimento Facial (CRUD)

## Integrantes:
Gabriel Souza Fiore – RM553710 

Guilherme Santiago – RM552321 

Miguel Leal Tasso – RM553009 

João Víctor Seixas – RM553888 

Lucca Enrico – RM553678 

## Descrição

Este projeto implementa um sistema de gerenciamento de usuários (CRUD - Create, Read, Update, Delete) integrado com **Reconhecimento Facial** em tempo real, utilizando as bibliotecas `dlib` e `OpenCV`. A interface gráfica (GUI) é construída com `tkinter`.

O sistema é projetado para diferenciar e gerenciar dois perfis principais: **Nutricionista** e **Usuário**.

## Funcionalidades

*   **Reconhecimento Facial em Tempo Real:** Utiliza a câmera para detectar e reconhecer faces.
*   **Cadastro (CREATE):** Permite cadastrar um novo usuário associando seu nome e perfil (Nutricionista ou Usuário) ao vetor facial capturado.
*   **Listagem (READ):** Exibe todos os usuários cadastrados.
*   **Atualização (UPDATE):** Permite alterar o perfil de um usuário existente.
*   **Exclusão (DELETE):** Remove um usuário do sistema.
*   **Validação de Acesso:** Um modo de validação pode ser ativado para identificar usuários em tempo real e exibir mensagens de boas-vindas específicas para cada perfil.

## Pré-requisitos

Para executar este projeto, você precisará ter o Python instalado e as seguintes bibliotecas.

### 1. Arquivos de Modelo do Dlib

O projeto requer dois arquivos de modelo pré-treinados do `dlib` para funcionar corretamente. Estes arquivos **devem** ser baixados e colocados no mesmo diretório de execução do script (`main_gui.py`):

1.  **`shape_predictor_5_face_landmarks.dat`**: Para detecção de 5 pontos faciais.
2.  **`dlib_face_recognition_resnet_model_v1.dat`**: O modelo ResNet para gerar o vetor facial (embedding).

Você pode encontrar links para download desses modelos na documentação oficial do Dlib ou em repositórios de projetos que os utilizam.

### 2. Bibliotecas Python

Instale as dependências usando `pip`:

```bash
pip install opencv-python dlib numpy Pillow
```

| Biblioteca | Propósito |
| :--- | :--- |
| `opencv-python` (`cv2`) | Captura de vídeo da câmera e processamento de imagem. |
| `dlib` | Detecção e reconhecimento facial (geração de vetores faciais). |
| `numpy` | Manipulação de vetores e cálculo de distância euclidiana. |
| `Pillow` (`PIL`) | Conversão de imagens do OpenCV para o formato compatível com `tkinter`. |
| `tkinter` | Interface Gráfica do Usuário (GUI) (Geralmente incluído na instalação padrão do Python). |

### 3. Persistência de Dados

O projeto utiliza o módulo `db_operations.py` para gerenciar o banco de dados de usuários. A persistência dos dados (nomes, perfis e vetores faciais) é feita em um arquivo local chamado **`db.pkl`** utilizando a biblioteca `pickle`.

## Passo a Passo de Uso

### 1. Configuração Inicial

1.  Certifique-se de que todos os **Pré-requisitos** (modelos `.dat` e bibliotecas Python) estão instalados e configurados.
2.  Coloque os arquivos `main_gui.py`, `db_operations.py` e os modelos `.dat` no mesmo diretório.

### 2. Execução

Execute o script principal (`main_gui.py`):

```bash
python main_gui.py
```

### 3. Utilização da GUI

Ao iniciar, a aplicação abrirá uma janela com a transmissão da sua câmera e um painel de controle CRUD.

#### A. Cadastro de Novo Usuário (CREATE)

1.  **Posicione-se** em frente à câmera. O sistema deve exibir a mensagem "Status: Face Detectada! Pronto para Cadastrar."
2.  No painel de controle, digite o **Nome do Usuário**.
3.  Selecione o **Tipo de Perfil** (Nutricionista ou Usuário).
4.  Clique no botão **"1. Cadastrar Novo Usuário"**.
5.  Uma mensagem de sucesso ou erro será exibida.

#### B. Validação de Acesso (Reconhecimento)

1.  Clique no botão **"Ligar Validação"** (ele mudará para "Desligar Validação" e ficará vermelho).
2.  O sistema tentará identificar a face detectada no banco de dados.
3.  Se a face for reconhecida (distância menor que o `THRESH` definido no código), o retângulo facial ficará verde, e o status exibirá o nome, perfil e a mensagem de boas-vindas.
4.  Se a face for desconhecida, o retângulo ficará vermelho e o status exibirá "Face Desconhecida".

#### C. Outras Operações CRUD

*   **Listar Usuários (READ):** Clique em **"2. Listar Todos os Usuários"** para abrir uma nova janela com a lista completa.
*   **Atualizar Perfil (UPDATE):** Digite o nome do usuário a ser atualizado, selecione o novo perfil e clique em **"3. Atualizar Perfil"**.
*   **Excluir Usuário (DELETE):** Digite o nome do usuário a ser excluído e clique em **"4. Excluir Usuário"**. Será solicitada uma confirmação.
