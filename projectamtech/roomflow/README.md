# RoomFlow

Sistema web em Flask para gestão de salas de reunião com persistência **sem banco de dados**, usando apenas arquivos `.txt` com JSON estruturado.

## Stack
- Python + Flask (App Factory + Blueprints)
- Jinja2 templates
- Bootstrap 5 via CDN

## Documentacao Tecnica
- Documento completo por arquivo, conexoes e fluxos:
  - `docs/DOCUMENTACAO_TECNICA_COMPLETA.md`

## Principais funcionalidades
- Autenticação com senha em hash PBKDF2 (`sha256`, salt aleatório, iterações >= 200k).
- Perfis: `ADMIN`, `RH`, `USER`.
- Agenda por sala e data com privacidade para usuário comum.
- Solicitações com semáforo de conflito:
  - Verde: sem conflito
  - Amarelo: conflito com reserva ativa
  - Vermelho: conflito com bloqueio/fora do expediente (não envia)
- Aprovação/negação RH/Admin (individual e em lote por `recurrence_group_id`).
- Reserva recorrente semanal (N ocorrências).
- Check-in de 15 minutos com expiração automática (`EXPIRADA`).
- Emergência RH/Admin com cancelamento de conflitos (`CANCELADA_POR_EMERGENCIA`).
- Bloqueios por sala/horário (`blocks`).
- Sugestões automáticas de horários livres.
- Notificações in-app (`notifications`).
- Logs de auditoria mensais (`logs/audit_YYYY-MM.txt`).

## Formatos
- Exibição na UI: data `DD/MM/AAAA`, hora `HH:MM`.
- Armazenamento interno: data ISO `YYYY-MM-DD`.

## Estrutura de dados TXT/JSON

```
data/
  users/
  rooms/
  sectors/
  bookings/
  requests/
  notifications/
  blocks/
  logs/
  _meta/
  _backup/
```

## Usuários seed
- `admin / admin123`
- `rh / rh123`
- `dev1 / dev123`
- `eng1 / eng123`
- `ti1 / ti123`

## Como rodar

```bash
cd roomflow
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python run.py
```

Acesso local: `http://127.0.0.1:5000`  
Acesso rede/IP externo: `http://SEU_IP:5000`

## Rotas principais

### Auth
- `GET/POST /login`
- `GET /logout`
- `GET/POST /change-password`

### Usuário
- `GET /`
- `GET /rooms`
- `GET /room/<room_id>/schedule`
- `GET/POST /room/<room_id>/request`
- `GET /my`
- `GET /my/requests`
- `POST /my/requests/<id>/cancel`
- `GET /my/bookings`
- `POST /my/bookings/<id>/cancel`
- `POST /booking/<id>/checkin`
- `GET /my/notifications`
- `POST /my/notifications/<id>/read`
- `POST /my/notifications/read-all`

### RH/Admin
- `GET /admin/dashboard`
- `GET /admin/requests`
- `POST /admin/requests/<id>/approve`
- `POST /admin/requests/<id>/deny`
- `POST /admin/requests/group/<recurrence_group_id>/approve`
- `POST /admin/requests/group/<recurrence_group_id>/deny`
- `GET /admin/bookings`
- `POST /admin/bookings/<id>/cancel`
- `GET/POST /admin/emergency`
- `GET/POST /admin/blocks`
- `POST /admin/blocks/<id>/disable`
- `GET /admin/logs`

### Admin
- `GET /admin/users`
- `GET/POST /admin/users/new`
- `GET/POST /admin/users/<id>/edit`
- `POST /admin/users/<id>/reset-password`
