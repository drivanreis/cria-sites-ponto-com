# Roteiro / Guia de Desenvolvimento:

## Visão Geral, Objetivos, Restrições e Papéis

### Visão Geral
Construir uma aplicação conteinerizada (Docker) com Frontend (React+Vite/TS) e Backend (Python+FastAPI) que utiliza a Lógica de Orquestração do Backend para interagir com diferentes APIs de IAs gratuitas/freemium ("funcionários" / Papéis da IA) e um banco de dados MySQL/MariaDB persistente. O sistema automatiza a coleta do briefing de criação de sites através de fluxos guiados por botões e IA, inclui autenticação para usuários/administradores e uma área administrativa para gerenciar o sistema, usuários e briefings, encerrando o fluxo automatizado com a notificação admin sobre o briefing pronto para revisão manual.

### Objetivos
Implementar o fluxo de atendimento inicial e pós-login com botões e áudio estático, a entrevista automatizada com Papéis da IA para coletar o briefing, a notificação ao cliente sobre a conclusão do briefing, a notificação aos administradores (Email/SMS), o sistema de autenticação de usuário (Login Social via Google/GitHub, Cadastro Local com email/telefone e 2FA TOTP) e administrador (login separado, gerenciamento) e a área administrativa para revisão do briefing e inserção manual do roteiro de desenvolvimento.

### Restrições
* Uso exclusivo de níveis gratuitos/freemium de APIs de IA e plataformas de hospedagem (foco inicial em AWS/GCP Free Tier).
* Sem necessidade de hardware local potente.
* Aplicação conteinerizada com scripts `cria-container.bat`/`.sh`.
* Automação encerra após notificar administradores sobre o briefing pronto.

### Papéis
* **EU:** O Sócio Majoritário, Desenvolvedor Full Stack, e o responsável manual por criar o roteiro de desenvolvimento e o próprio site após receber o briefing. Interage com a área administrativa para obter o briefing e inserir o roteiro/orçamento.
* **Lógica de Orquestração do Backend:** Implementada no código Python/FastAPI. Gerencia o fluxo de botões, sessões, determina qual Papel da IA entrevistar, chama APIs de IA (via Camada de Comunicação - Fase 1.5), salva histórico/briefing no DB, atualiza status, envia notificação final ao cliente e envia Email/SMS aos administradores.
* **"Funcionários" (Papéis da IA de Entrevista/Consulta):** Modelos de IA (configurados via tabela `employees`) para agir como `chatbot-pessoa`, `chatbot-ja-empresa`, `chatbot-new-empresa`. Focam em conduzir entrevistas e coletar/estruturar informações para o briefing.
* **`bot-cria-site`:** **NÃO é mais um agente de execução de código.** É o **estado final/transição** do briefing automatizado.

## Estrutura do Banco de Dados (MySQL/MariaDB, Revisada com Autenticação e Admin)

### Sistema de Banco de Dados Escolhido
MySQL ou MariaDB.

### Tabelas
* **`users`** (Usuários/Clientes): Contas, login social, cadastro local, 2FA, status.
    * `id` (PK)
    * `email` (VARCHAR, UNIQUE, NULLABLE)
    * `email_verified` (BOOLEAN)
    * `phone_number` (VARCHAR, NULLABLE)
    * `password_hash` (VARCHAR, NULLABLE)
    * `name` (VARCHAR)
    * `google_id` (VARCHAR, UNIQUE, NULLABLE)
    * `github_id` (VARCHAR, UNIQUE, NULLABLE)
    * `two_factor_secret` (VARCHAR, NULLABLE - para 2FA TOTP)
    * `is_two_factor_enabled` (BOOLEAN)
    * `status` (VARCHAR/TEXT, default 'active'): Ex: 'active', 'blocked'.
    * `creation_date` (TIMESTAMP)
    * `last_login` (TIMESTAMP)
* **`admin_users`** (Usuários Administradores): Nova tabela para gerenciar contas de administrador.
    * `id` (PK)
    * `username` (VARCHAR, UNIQUE): Nome de usuário para login admin.
    * `password_hash` (VARCHAR): Hash da senha admin.
    * `name` (VARCHAR, NULLABLE)
    * `role` (VARCHAR/TEXT, default 'admin')
    * `creation_date` (TIMESTAMP)
    * `last_login` (TIMESTAMP)
* **`employees`** (Funcionários IA): Configuração dos Papéis da IA (Entrevista/Consulta). Gerenciável via área admin.
    * `id` (PK)
    * `role` (VARCHAR/TEXT)
    * `ai_service` (VARCHAR/TEXT)
    * `endpoint` (VARCHAR/TEXT)
    * `api_key` (VARCHAR/TEXT - **Ressalva de Segurança: carregar chaves sensíveis via variáveis de ambiente no Backend**).
    * `initial_pre_prompt` (TEXT)
    * `context_instructions` (TEXT, nullable=True)
    * `creation_date` (TIMESTAMP)
    * `update_date` (TIMESTAMP)
* **`briefings`** (Briefings): Dados coletados, ligados ao usuário, com campo para o roteiro de desenvolvimento MANUAL. Visualizável/Editável via área admin.
    * `id` (PK)
    * `user_id` (FK para `users.id`)
    * `type` (VARCHAR/TEXT)
    * `content` (JSON/TEXT): Conteúdo do briefing gerado pela IA.
    * `status` (VARCHAR/TEXT, default 'Em Construção'): Ex: 'Pronto para Revisão'.
    * `development_roteiro` (TEXT/JSON, NULLABLE): Armazenará o roteiro/orçamento manual criado pelo administrador.
    * `creation_date` (TIMESTAMP)
    * `update_date` (TIMESTAMP)
* **`conversation_history`** (Histórico de Conversa): Mensagens, ligadas ao usuário. Pode ser visualizável via área admin.
    * `id` (PK)
    * `user_id` (FK para `users.id`)
    * `employee_role` (VARCHAR/TEXT)
    * `speaker` (VARCHAR/TEXT): 'user' ou 'bot'.
    * `text` (TEXT)
    * `timestamp` (TIMESTAMP)
