# Jupy Agenda (Versão em Português Brasileiro)

Bem-vindo à Jupy Agenda! Uma aplicação web completa e versátil, desenvolvida com Flask, projetada para ser sua assistente pessoal definitiva. Com a Jupy Agenda, você pode organizar sua vida digital de forma eficiente, gerenciando desde seus compromissos e tarefas diárias até materiais de estudo, ideias e projetos de programação. Nossa missão é fornecer uma ferramenta intuitiva e poderosa para otimizar sua produtividade e manter tudo sob controle, em um só lugar.

## Funcionalidades Principais

A Jupy Agenda oferece um conjunto robusto de funcionalidades para atender às suas necessidades de organização:

### 1. Autenticação de Usuários
*   **Login e Registro:** Crie sua conta pessoal de forma segura ou acesse sua agenda existente.
*   **Logout:** Encerre sua sessão com segurança.
*   **Gerenciamento de Perfil:** Visualize seus dados de usuário.

### 2. Calendário e Eventos
*   **Visualização Mensal:** Navegue facilmente pelo calendário para ver seus eventos por mês.
*   **Adicionar Eventos:** Crie novos eventos com título, descrição, data e hora de início e término.
*   **Editar e Remover Eventos:** Modifique ou exclua eventos existentes diretamente no calendário.
*   **Lembretes Automáticos:** Configure lembretes por email para seus eventos (veja "Lembretes e Notificações").

### 3. Lista de Tarefas (To-Do List)
*   **Criação de Tarefas:** Adicione tarefas com descrição detalhada, data de vencimento e nível de prioridade (Baixa, Média, Alta).
*   **Gerenciamento de Status:** Marque tarefas como "Pendente" ou "Concluída".
*   **Edição e Remoção:** Modifique ou exclua tarefas conforme necessário.
*   **Filtros e Ordenação:** Visualize suas tarefas filtrando por status (pendentes, concluídas) ou ordenando por prioridade, data de vencimento ou data de criação.
*   **Lembretes Automáticos:** Configure lembretes por email para suas tarefas com data de vencimento (veja "Lembretes e Notificações").

### 4. Locais para Organizar Atividades
*   **Cadastro de Locais:** Salve locais importantes com nome, endereço, descrição e coordenadas geográficas (latitude e longitude).
*   **Gerenciamento:** Edite ou exclua locais salvos. Ideal para planejar eventos ou simplesmente manter um registro de lugares frequentes.

### 5. Espaços para Diagramar e Programar
    
*   **Notas para Diagramas:**
    *   Um espaço dedicado para criar e armazenar notas textuais que podem representar diagramas (ex: ASCII art para fluxogramas, mapas mentais em texto) ou qualquer anotação que exija um formato de texto livre e amplo.
    *   Crie, edite e organize suas notas de diagrama com títulos e conteúdo.
*   **Fragmentos de Código (Code Snippets):**
    *   Guarde trechos de código, pseudocódigo ou comandos úteis.
    *   Organize-os com títulos e indique a linguagem (ex: Python, JavaScript, SQL) para referência futura.
    *   Visualize e edite seus snippets facilmente.

### 6. Lembretes e Notificações por Email
*   **Lembretes de Eventos:** Ao criar ou editar um evento, um lembrete por email é automaticamente agendado para ser enviado 1 hora antes do início do evento (se o evento estiver no futuro).
*   **Lembretes de Tarefas:** Ao criar ou editar uma tarefa com data de vencimento, um lembrete por email é agendado para as 09:00 no dia do vencimento (se a data for hoje ou no futuro).
*   **Processamento:** Os lembretes são processados por um comando CLI (`flask send-reminders`) que deve ser agendado para execução periódica no ambiente de produção.

### 7. Gerenciador de Materiais Didáticos
*   **Upload de Arquivos:** Faça upload de seus materiais de estudo (PDFs, documentos, imagens, apresentações, etc.).
*   **Download:** Baixe os materiais enviados a qualquer momento.
*   **Gerenciamento:** Organize seus materiais com título, descrição, categoria/assunto e data de upload. Edite ou exclua materiais conforme necessário.
*   **Armazenamento Seguro:** Os arquivos são armazenados de forma segura no servidor, em um diretório específico para cada usuário.

### 8. Anotações Rápidas
*   **Criação Rápida:** Anote ideias, insights ou qualquer informação de forma rápida.
*   **Categorização:** Organize suas notas com categorias personalizadas para facilitar a busca.
*   **Busca e Filtro:** Encontre notas específicas pesquisando por palavras-chave no conteúdo ou na categoria, ou filtrando por uma categoria existente.

### 9. Estatísticas e Relatórios
*   **Visão Geral:** Acesse uma página com estatísticas sobre suas atividades.
*   **Gráficos:** Visualize dados como:
    *   Status de conclusão de tarefas (pizza).
    *   Distribuição de eventos (passados vs. futuros - pizza).
    *   Criação de tarefas e eventos por mês (barras, últimos 6 meses).
*   **Dados Numéricos:** Veja contagens totais de tarefas (concluídas, pendentes, atrasadas) e eventos.

## Estrutura do Projeto

```
jupy_agenda/
├── app/                     # Pacote principal da aplicação
│   ├── __init__.py          # Fábrica da aplicação (create_app)
│   ├── models.py            # Modelos do banco de dados
│   ├── forms.py             # Definições de WTForms
│   ├── services/            # Lógica de negócios (ex: estatísticas, notificações)
│   ├── static/              # Arquivos estáticos (CSS, JS, imagens)
│   ├── templates/           # Templates HTML (organizados por funcionalidade)
│   │   ├── auth/
│   │   ├── calendar/
│   │   ├── code_snippets/
│   │   ├── diagrams/
│   │   ├── email/
│   │   ├── locations/
│   │   ├── materials/
│   │   ├── notes/
│   │   ├── stats/
│   │   └── base.html        # Template base
│   ├── auth_routes.py       # Blueprints de autenticação
│   ├── calendar_routes.py   # Blueprints do calendário
│   └── ... (outros arquivos de rotas específicos de funcionalidades)
├── database/                # Local padrão para o arquivo do banco de dados SQLite (se usado localmente)
├── instance/                # Pasta de instância (para uploads, configurações específicas da instância)
│   ├── uploads/             # Arquivos enviados pelo usuário
│   └── .gitignore           # Ignora o conteúdo da instância
├── tests/                   # Testes unitários e funcionais
│   ├── __init__.py
│   ├── base_test.py
│   ├── test_config.py
│   ├── functional/
│   └── unit/
├── .gitignore               # Arquivo .gitignore principal
├── Procfile                 # Para Heroku/Gunicorn
├── README.md                # Este arquivo (versão em inglês)
├── README_pt-BR.md          # Este arquivo (versão em Português Brasileiro)
├── requirements.txt         # Dependências Python
└── run.py                   # Executor da aplicação, comandos CLI (testes, lembretes)
```

## Configuração do Ambiente de Desenvolvimento Local

Siga estas instruções para configurar e executar a Jupy Agenda em seu ambiente local:

1.  **Clone o repositório:**
    ```bash
    git clone <url_do_repositorio>
    cd jupy_agenda_project_root # O diretório que contém a pasta jupy_agenda
    ```

2.  **Crie e ative um ambiente virtual:**
    Recomendamos o uso de um ambiente virtual para gerenciar as dependências do projeto de forma isolada.
    ```bash
    python -m venv venv
    source venv/bin/activate  # No Windows: venv\Scripts\activate
    ```

3.  **Instale as dependências:**
    Todas as dependências necessárias estão listadas no arquivo `requirements.txt`.
    ```bash
    pip install -r jupy_agenda/requirements.txt
    ```

4.  **Configure as Variáveis de Ambiente (Opcional para execução local básica com padrões):**
    Para desenvolvimento local, a aplicação utiliza valores padrão para a maioria das configurações. No entanto, para uma configuração mais robusta ou para testar funcionalidades como envio de email, você pode configurar variáveis de ambiente. Crie um arquivo `.env` na raiz da pasta `jupy_agenda` (onde `run.py` está localizado) ou defina-as diretamente no seu shell:

    Exemplo de arquivo `.env` (localizado em `jupy_agenda/.env`):
    ```env
    # FLASK_APP="run.py" # Não estritamente necessário se executar run.py diretamente
    FLASK_ENV="development"     # Habilita o modo de depuração e outras funcionalidades de desenvolvimento
    SECRET_KEY="uma_chave_muito_secreta_apenas_para_desenvolvimento" 
    
    # SQLALCHEMY_DATABASE_URI="sqlite:///../database/agenda.db" 
    # O padrão já aponta para um arquivo SQLite na pasta 'database/' na raiz do projeto.
    # Para PostgreSQL local, por exemplo:
    # SQLALCHEMY_DATABASE_URI="postgresql://usuario:senha@localhost:5432/jupy_agenda_db"

    # Configuração de Email (para desenvolvimento com MailHog ou similar, ou para imprimir no console)
    MAIL_SERVER="localhost"
    MAIL_PORT=1025
    # MAIL_USE_TLS=false
    # MAIL_USE_SSL=false
    # MAIL_USERNAME=""      # Deixe em branco para usar o console/MailHog se MAIL_SUPPRESS_SEND estiver configurado adequadamente
    # MAIL_PASSWORD=""
    MAIL_DEFAULT_SENDER="dev-noreply@jupy.agenda" 
    # MAIL_SUPPRESS_SEND=True # Se MAIL_USERNAME não estiver definido e FLASK_ENV=development, a supressão é automática.
    ```
    **Importante:** Se você criar um arquivo `.env`, certifique-se de que `python-dotenv` esteja listado em `requirements.txt` e que seu script `run.py` (ou `app/__init__.py`) o carregue no início. Atualmente, o `run.py` não carrega `.env` explicitamente; portanto, exporte as variáveis no seu terminal ou configure-as na sua IDE.

5.  **Inicialize o banco de dados:**
    O banco de dados (SQLite por padrão) e as pastas de upload são criados automaticamente quando a aplicação é iniciada pela primeira vez através da função `create_app()`.

6.  **Execute o servidor de desenvolvimento:**
    Navegue para a pasta `jupy_agenda` (onde `run.py` está localizado), se você estiver na raiz do projeto.
    ```bash
    # Assumindo que você está na pasta 'jupy_agenda'
    python run.py 
    ```
    A aplicação deverá estar disponível em `http://127.0.0.1:5000/`.

## Executando os Testes

Para garantir a qualidade e o correto funcionamento da aplicação, execute a suíte de testes:

1.  Certifique-se de que seu ambiente virtual esteja ativado e todas as dependências de desenvolvimento (`requirements.txt`) estejam instaladas.
2.  Navegue até a pasta `jupy_agenda` (onde `run.py` está localizado).
3.  Execute o seguinte comando no terminal:
    ```bash
    python run.py test
    ```
    Este comando descobrirá e executará todos os testes unitários e funcionais localizados na pasta `jupy_agenda/tests`.

## Deployment (Exemplo com Gunicorn)

Esta aplicação é configurada para ser implantada usando um servidor WSGI como Gunicorn.

1.  **Instale as Dependências de Produção:**
    No seu ambiente de produção, certifique-se de que todas as dependências, incluindo Gunicorn, estejam instaladas:
    ```bash
    pip install -r jupy_agenda/requirements.txt 
    ```

2.  **Configure as Variáveis de Ambiente para Produção:**
    Para um ambiente de produção, as seguintes variáveis de ambiente **devem** ser configuradas:
    *   `FLASK_ENV="production"`: Desabilita o modo de depuração e outras funcionalidades de desenvolvimento.
    *   `SECRET_KEY`: Uma chave forte, única e secreta. **Não utilize a chave padrão de desenvolvimento.** Gere uma chave segura (ex: `python -c 'import secrets; print(secrets.token_hex(32))'`).
    *   `SQLALCHEMY_DATABASE_URI`: A string de conexão para seu banco de dados de produção (ex: PostgreSQL, MySQL).
        *   Exemplo para PostgreSQL: `postgresql://usuario:senha@host:porta/nome_do_banco`
    *   `MAIL_SERVER`: Endereço do seu servidor SMTP.
    *   `MAIL_PORT`: Porta do seu servidor SMTP (ex: 587 para TLS, 465 para SSL).
    *   `MAIL_USE_TLS` / `MAIL_USE_SSL`: Defina um como `true` dependendo dos requisitos do seu servidor SMTP.
    *   `MAIL_USERNAME`: Seu nome de usuário SMTP.
    *   `MAIL_PASSWORD`: Sua senha SMTP.
    *   `MAIL_DEFAULT_SENDER`: O endereço "de" padrão para emails enviados pela aplicação (ex: `noreply@seudominio.com`).
    *   `UPLOAD_FOLDER`: (Opcional, o padrão é `instance/uploads/learning_materials`) Defina se precisar de um caminho personalizado. Garanta que este caminho seja gravável pelo processo do servidor da aplicação.

3.  **Execute com Gunicorn:**
    A partir do diretório que contém a pasta `jupy_agenda` (ou seja, a raiz do projeto):
    ```bash
    gunicorn "jupy_agenda.app:create_app()"
    ```
    Você pode personalizar as configurações do Gunicorn (workers, host, porta, etc.):
    ```bash
    # Exemplo com 4 workers, escutando em todas as interfaces na porta 8000
    gunicorn --workers 4 --bind 0.0.0.0:8000 "jupy_agenda.app:create_app()"
    ```

4.  **Tarefa de Envio de Lembretes:**
    O comando `flask send-reminders` precisa ser agendado para execução periódica (ex: usando cron, systemd timers, ou um serviço de agendamento fornecido pela sua plataforma de hospedagem).
    
    Para que o comando `flask` funcione corretamente, a variável de ambiente `FLASK_APP` deve ser definida para apontar para o seu script `run.py` que contém a instância da aplicação Flask e os comandos CLI.
    Exemplo de configuração de `FLASK_APP`:
    ```bash
    export FLASK_APP=jupy_agenda.run 
    # Ou, se run.py estiver na raiz do projeto e jupy_agenda for um pacote:
    # export FLASK_APP=run:app # (se 'app' for a instância Flask em run.py)
    ```
    Assumindo que `FLASK_APP` está configurado para `jupy_agenda.run:app` (ou similar, dependendo de como `app` é exposto em `run.py` para o CLI do Flask), um exemplo de job cron (executa a cada 5 minutos) seria:
    ```cron
    */5 * * * * /caminho/para/seu/projeto/venv/bin/flask send-reminders >> /var/log/jupy_agenda_reminders.log 2>&1
    ```
    Ajuste os caminhos e a configuração de `FLASK_APP` conforme necessário para o seu ambiente. Se `run.py` não expõe `app` diretamente para o CLI do Flask, você pode precisar de um arquivo `wsgi.py` ou ajustar o comando. A forma como o comando `flask send-reminders` foi adicionado em `run.py` (`@app.cli.command`) significa que `FLASK_APP` deve apontar para o módulo onde `app` (a instância de `create_app()`) é acessível. Se `run.py` é o ponto de entrada, `FLASK_APP=jupy_agenda.run` (se `run.py` está dentro do pacote `jupy_agenda`) ou `FLASK_APP=run.py` (se `run.py` está na raiz e o CWD é a raiz) seria o caminho.
    
    Dado que `run.py` está em `jupy_agenda/run.py`, e `app` é criado lá, para o CLI do Flask, `FLASK_APP=jupy_agenda.run` (quando executado da raiz do projeto) ou `FLASK_APP=run.py` (quando executado de dentro da pasta `jupy_agenda`) é o mais provável.

## Contribuições
Contribuições são bem-vindas! Por favor, faça um fork do repositório, crie um branch para sua funcionalidade e envie um pull request.

## Licença
Este projeto é licenciado sob a Licença MIT. (Um arquivo `LICENSE` formal será adicionado).
