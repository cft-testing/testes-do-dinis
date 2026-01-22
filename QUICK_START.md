# Quick Start Guide

Guia rápido para começar a usar o CFT Trend Radar Newsletter em 5 minutos.

## Passo 1: Configuração Inicial (2 min)

```bash
# Clone ou navegue para o repositório
cd testes-do-dinis

# Criar ambiente virtual
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# ou: venv\Scripts\activate  # Windows

# Instalar dependências
pip install -r requirements.txt
```

## Passo 2: Configurar Credenciais (2 min)

```bash
# Copiar exemplo de configuração
cp .env.example .env

# Editar com as suas credenciais
nano .env  # ou usar outro editor
```

**Mínimo necessário no .env:**
```env
ANTHROPIC_API_KEY=sk-ant-your-key-here
SMTP_USERNAME=seu_email@gmail.com
SMTP_PASSWORD=sua_app_password
EMAIL_TO=destinatario@fidelidade.pt
```

## Passo 3: Teste Rápido (1 min)

```bash
# Testar configuração de email
python main.py test-email --test-recipient seu_email@fidelidade.pt

# Gerar preview HTML
python main.py preview

# Abrir preview.html no browser para ver o resultado
```

## Passo 4: Primeira Newsletter

```bash
# Gerar e enviar newsletter
python main.py send
```

## Passo 5: Ativar Automação

```bash
# Opção A: Modo agendado (mantém terminal aberto)
python main.py schedule

# Opção B: Background (Linux/Mac)
nohup python main.py schedule > newsletter.log 2>&1 &

# Opção C: Docker
docker-compose up -d
```

## Comandos Úteis

```bash
# Ver estatísticas
python main.py stats

# Só gerar (não enviar)
python main.py generate

# Ver logs (se em background)
tail -f newsletter.log

# Parar Docker
docker-compose down
```

## Troubleshooting Rápido

**Erro de API Key:**
- Verifique que `.env` existe e tem a chave correta

**Email não enviado:**
- Gmail: Use "App Password" (não a password normal)
- Verifique SMTP_USERNAME e SMTP_PASSWORD no .env

**Sem conteúdo relevante:**
- Normal na primeira execução
- Ajuste `min_score` em `config/settings.yaml` para 5.0

**Rate limit:**
- Use modelo mais barato: edite `config/settings.yaml`
- Mude `model: claude-3-haiku-20240307`

## Próximos Passos

1. Personalize `config/sources.yaml` com fontes preferidas
2. Ajuste `config/topics.yaml` com tópicos específicos
3. Configure `config/settings.yaml` (scores, limites, etc.)
4. Configure automação permanente (systemd, cron, ou docker)

## Suporte

Consulte README.md completo ou contacte equipa CFT.
