# Documentacao Tecnica Completa - RoomFlow

## 1) Visao Geral
RoomFlow e um sistema Flask com persistencia 100% em arquivos `.txt` com JSON interno.
Nao usa banco de dados.

Fluxo central:
1. Usuario autentica (`auth/routes.py`).
2. Rotas chamam metodos de negocio (`storage/services.py`).
3. Servico le/escreve dados via `storage/filedb.py`.
4. UI e renderizada em templates Jinja (`app/templates/*`).

## 2) Arquitetura e Conexoes
- `run.py` -> chama `app.create_app()`.
- `app/__init__.py` -> cria Flask app, injeta `RoomFlowService`, registra blueprints.
- Blueprints:
  - `auth` -> login/logout/senha
  - `main` -> area do usuario comum
  - `admin` -> RH/Admin + Admin-only
- Camada de dominio/persistencia:
  - `storage/models.py` -> estruturas de dados
  - `storage/services.py` -> regras de negocio
  - `storage/filedb.py` -> lock + escrita atomica
  - `storage/security.py` -> hash de senha PBKDF2
  - `storage/validators.py` -> conversoes BR/ISO e hora

## 3) Estrutura de Dados (TXT/JSON)
- `data/users/*.txt` -> usuarios
- `data/rooms/*.txt` -> salas
- `data/sectors/*.txt` -> setores
- `data/bookings/YYYY-MM-DD_room_X.txt` -> reservas por dia+sala
- `data/requests/YYYY-MM.txt` -> solicitacoes por mes
- `data/blocks/room_X.txt` -> bloqueios por sala
- `data/notifications/u_XXXX.txt` -> notificacoes por usuario
- `data/logs/audit_YYYY-MM.txt` -> auditoria
- `data/_meta/config.txt` -> configuracoes runtime
- `data/_meta/counters.txt` -> contadores de IDs

## 4) Mapa de Arquivos Python

### Entrada e app factory
- `run.py`
  - inicia servidor Flask
  - le `FLASK_RUN_HOST`/`FLASK_RUN_PORT`
- `app/__init__.py`
  - monta app
  - instancia `FileDB` e `RoomFlowService`
  - registra blueprints
  - injeta variaveis globais para templates (`current_user`, `format_date_br`, `weekday_pt`)

### Config
- `app/config.py`
  - definicoes de seguranca, expediente, janelas e lock

### Auth
- `app/auth/__init__.py`
  - blueprint `auth`
- `app/auth/decorators.py`
  - `login_required`, `require_roles`
  - `load_logged_user` (carrega usuario da sessao para `g.user`)
- `app/auth/forms.py`
  - formularios de login e troca de senha
- `app/auth/routes.py`
  - `/login`, `/logout`, `/change-password`
  - redireciona por role para dashboard adequado

### Main (usuario)
- `app/main/__init__.py`
  - blueprint `main`
- `app/main/routes.py`
  - home e redirecionamento por role
  - visualizacao de salas e agenda
  - solicitacao de reserva
  - painel do usuario
  - minhas solicitacoes/reservas
  - check-in
  - notificacoes

### Admin/RH
- `app/admin/__init__.py`
  - blueprint `admin` com prefixo `/admin`
- `app/admin/forms.py`
  - formularios administrativos (legado e apoio)
- `app/admin/routes.py`
  - dashboard RH/Admin
  - solicitacoes (filtros, aprovar/negar, lote)
  - reservas (filtros, cancelamento)
  - emergencia
  - bloqueios
  - logs
  - usuarios (Admin-only)
  - setores (Admin-only)

### Storage e negocio
- `app/storage/__init__.py`
  - documenta modulos do pacote
- `app/storage/filedb.py`
  - `ensure_dirs`
  - `file_lock`
  - `read_json`
  - `write_json_atomic`
- `app/storage/models.py`
  - dataclasses: `User`, `Room`, `BookingRequest`, `Booking`, `Block`, `Notification`, `AuditEvent`
- `app/storage/security.py`
  - `hash_password`
  - `verify_password`
- `app/storage/validators.py`
  - `parse_date_br`, `format_date_br`
  - `parse_time_hhmm`, `time_to_minutes`, `minutes_to_time`
  - `weekday_pt`
- `app/storage/services.py`
  - seed e migracoes de dados
  - CRUD de usuario/setor
  - solicitacoes/recorrencia/aprovacao
  - reservas/conflitos/check-in/expiracao
  - bloqueios/agenda/sugestoes
  - notificacoes
  - auditoria

## 5) Mapa de Templates

### Base e parciais
- `templates/base.html` -> layout principal
- `templates/partials/navbar.html` -> topo + usuario/sino
- `templates/partials/sidebar.html` -> menu por role
- `templates/partials/flashes.html` -> mensagens flash

### Auth
- `templates/auth/login.html`
- `templates/auth/change_password.html`

### Main
- `templates/main/index.html` -> home
- `templates/main/rooms.html` -> cards de salas
- `templates/main/schedule_room.html` -> agenda da sala
- `templates/main/request_form.html` -> solicitacao
- `templates/main/my_dashboard.html` -> painel usuario
- `templates/main/my_requests.html`
- `templates/main/my_bookings.html`
- `templates/main/notifications.html`

### Admin
- `templates/admin/dashboard.html`
- `templates/admin/requests.html`
- `templates/admin/bookings.html`
- `templates/admin/emergency.html`
- `templates/admin/blocks.html`
- `templates/admin/users.html`
- `templates/admin/user_form.html`
- `templates/admin/sectors.html`
- `templates/admin/sector_detail.html`
- `templates/admin/logs.html`

### Erros
- `templates/errors/404.html`
- `templates/errors/500.html`

## 6) Fluxos de Negocio

### Solicitar sala
- Tela `main/request_form.html`
- Rota `main.room_request`
- Regra em `services.get_semaphore` + `services.create_request`
- Persistencia: `data/requests/YYYY-MM.txt`

### Aprovar solicitacao
- Tela `admin/requests.html`
- Rota `admin.request_approve`
- Regra: `services.approve_request`
- Cria reserva em `data/bookings/YYYY-MM-DD_room_X.txt`

### Check-in e expiracao
- Check-in: `services.checkin`
- Expiracao/status automatico: `services.expire_due_checkins`
- Status esperados: `ATIVA`, `EM_ANDAMENTO`, `EXPIRADA`, `CONCLUIDA`

### Bloqueios
- Tela `admin/blocks.html`
- Regra `services.create_block`
- Formato atual suporta:
  - data inicio/fim
  - hora inicio/fim
  - dias da semana (1..7)

### Emergencia RH/Admin
- Tela `admin/emergency.html`
- Regra `services.emergency_booking`
- Cancela reservas conflitantes como `CANCELADA_POR_EMERGENCIA`

## 7) Seguranca
- Senhas nunca em texto plano.
- Hash PBKDF2-HMAC SHA256 com salt random e iteracoes altas.
- Comparacao segura via `hmac.compare_digest`.

## 8) Integracoes entre camadas
- Rotas nunca gravam JSON diretamente.
- Toda escrita passa por `RoomFlowService` -> `FileDB.write_json_atomic`.
- Templates nao acessam disco; so consomem dados passados por rotas.

## 9) Observacao sobre comentarios em linha
Foi adotado padrao de documentacao por modulo, funcao e fluxo (mais sustentavel).
Comentar cada linha de codigo tornaria o projeto dificil de manter e com alto risco de divergencia.
Se quiser, posso fazer anotacao linha-a-linha em um arquivo especifico (por exemplo `storage/services.py`).
