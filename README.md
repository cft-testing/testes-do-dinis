# CFT Trend Radar Newsletter

Sistema automatizado de newsletter semanal para o **Center for Transformation (CFT)** da Fidelidade. Recolhe, analisa e distribui notícias relevantes sobre tecnologia, inovação e tendências de mercado.

## Funcionalidades

- **Recolha Automatizada**: Pesquisa em múltiplas fontes de notícias confiáveis (RSS feeds e web scraping)
- **Análise Inteligente**: Utiliza AI (Claude/GPT) para avaliar a relevância de cada notícia
- **Avaliação Multi-dimensional**:
  - Business Relevance for Fidelidade
  - Disruptive Potential
  - Internal Know-How
  - Market Potential
  - Need for Action
  - Strategic Fit
  - Time to Market Impact
  - Trend Maturity Level
- **Contexto Histórico**: Evita conteúdo repetitivo comparando com newsletters anteriores
- **Categorização**: Organiza notícias em 3 secções (Mundial, Portugal, Ventures)
- **Newsletter HTML**: Geração automática de email formatado e responsivo
- **Agendamento**: Envio automático semanal configurável
- **Ventures**: Foco especial em tópicos relacionados com Sofia (AI assistant) e FIXO (home services)

## Estrutura do Projeto

```
trend-radar-newsletter/
├── src/                           # Código fonte
│   ├── __init__.py
│   ├── news_fetcher.py           # Recolha de notícias
│   ├── content_analyzer.py       # Análise de relevância com AI
│   ├── context_manager.py        # Gestão de histórico
│   ├── newsletter_generator.py   # Geração de HTML
│   ├── email_sender.py          # Envio de emails
│   └── scheduler.py             # Agendamento semanal
├── config/                       # Configurações
│   ├── sources.yaml             # Fontes de notícias
│   ├── topics.yaml              # Tópicos predefinidos
│   └── settings.yaml            # Configurações gerais
├── data/                        # Dados
│   └── newsletter_history.json  # Histórico de newsletters
├── requirements.txt             # Dependências Python
├── .env.example                # Exemplo de variáveis de ambiente
├── main.py                     # Script principal
└── README.md                   # Este ficheiro
```

## Instalação

### 1. Requisitos

- Python 3.8 ou superior
- Conta de email SMTP (Gmail, Outlook, etc.)
- API Key da Anthropic (Claude) ou OpenAI (GPT)

### 2. Instalar Dependências

```bash
# Criar ambiente virtual (recomendado)
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows

# Instalar dependências
pip install -r requirements.txt
```

### 3. Configuração

#### a) Criar ficheiro `.env`

```bash
cp .env.example .env
```

#### b) Editar `.env` com as suas credenciais

```env
# AI API (escolher uma)
ANTHROPIC_API_KEY=sk-ant-xxxxx
# ou
OPENAI_API_KEY=sk-xxxxx

# Email SMTP
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=seu_email@gmail.com
SMTP_PASSWORD=sua_password_ou_app_password
EMAIL_FROM=newsletter@fidelidade.pt
EMAIL_TO=team@fidelidade.pt,outro@fidelidade.pt

# Newsletter
NEWSLETTER_NAME=CFT Trend Radar
ORGANIZATION_NAME=Center for Transformation - Fidelidade

# Agendamento
SCHEDULE_DAY=monday
SCHEDULE_TIME=09:00
```

**Nota Gmail**: Para usar Gmail, ative a "Verificação em 2 passos" e crie uma "Palavra-passe de aplicação" específica.

#### c) Configurar Fontes de Notícias (opcional)

Edite `config/sources.yaml` para adicionar/remover fontes de notícias.

#### d) Configurar Tópicos (opcional)

Edite `config/topics.yaml` para ajustar os tópicos de interesse.

#### e) Ajustar Configurações (opcional)

Edite `config/settings.yaml` para ajustar thresholds, pesos de scoring, etc.

## Utilização

### Comandos Disponíveis

```bash
# Gerar newsletter (sem enviar)
python main.py generate

# Gerar e enviar newsletter
python main.py send

# Iniciar modo agendado (semanal automático)
python main.py schedule

# Gerar preview em HTML
python main.py preview --output newsletter.html

# Ver estatísticas
python main.py stats

# Enviar email de teste
python main.py test-email --test-recipient seu_email@example.com
```

### Fluxo de Trabalho Típico

1. **Teste a configuração de email**:
   ```bash
   python main.py test-email --test-recipient seu_email@fidelidade.pt
   ```

2. **Gere um preview para verificar o formato**:
   ```bash
   python main.py preview
   # Abra preview.html no browser
   ```

3. **Envie a primeira newsletter**:
   ```bash
   python main.py send
   ```

4. **Configure para execução automática semanal**:
   ```bash
   python main.py schedule
   ```

## Como Funciona

### Pipeline de Geração

1. **Fetch News** (news_fetcher.py)
   - Recolhe notícias de múltiplas fontes (RSS + web scraping)
   - Filtra por data (última semana)
   - Extrai conteúdo completo dos artigos

2. **Context Check** (context_manager.py)
   - Verifica histórico de newsletters passadas
   - Remove URLs duplicadas
   - Remove títulos similares (>75% similaridade)

3. **AI Analysis** (content_analyzer.py)
   - Analisa cada artigo com AI (Claude ou GPT)
   - Atribui scores em 8 dimensões
   - Calcula score global ponderado
   - Filtra artigos com score < 6.0

4. **Newsletter Generation** (newsletter_generator.py)
   - Agrupa artigos por secção (Mundial, Portugal, Ventures)
   - Só inclui secções com conteúdo relevante
   - Gera HTML responsivo e versão texto

5. **Email Sending** (email_sender.py)
   - Envia por SMTP com HTML + texto
   - Suporta múltiplos destinatários

6. **History Update** (context_manager.py)
   - Guarda newsletter em histórico
   - Mantém últimas 52 semanas

### Critérios de Avaliação

Cada artigo é avaliado em 8 dimensões (0-10):

| Critério | Peso | Descrição |
|----------|------|-----------|
| Business Relevance | 20% | Relevância para o negócio da Fidelidade |
| Disruptive Potential | 15% | Potencial de disrupção na indústria |
| Internal Know-How | 10% | Expertise interna existente |
| Market Potential | 15% | Oportunidade de mercado |
| Need for Action | 10% | Urgência de ação |
| Strategic Fit | 15% | Alinhamento estratégico |
| Time to Market Impact | 10% | Rapidez de implementação |
| Trend Maturity | 5% | Maturidade da tendência |

**Score Total** = Soma ponderada (mínimo 6.0 para inclusão)

### Acções Recomendadas

A AI sugere uma ação para cada artigo:

- **IGNORE**: Não relevante
- **MONITOR**: Acompanhar desenvolvimentos
- **EXPLORE**: Investigar mais
- **PILOT**: Testar/prototipar
- **IMPLEMENT**: Agir já

## Configuração de Fontes

### Adicionar Fonte RSS

Edite `config/sources.yaml`:

```yaml
worldwide:
  - name: Nome da Fonte
    url: https://example.com
    rss: https://example.com/feed.xml
    type: rss
```

### Adicionar Fonte Web (Scraping)

```yaml
portugal:
  - name: Nome da Fonte
    url: https://example.com/tecnologia
    type: web
```

### Ventures - Keywords

```yaml
ventures:
  keywords:
    - "keyword relevante"
    - "outro keyword"
```

## Agendamento Automático

### Opção 1: Script em Background

```bash
# Iniciar em background
nohup python main.py schedule > newsletter.log 2>&1 &

# Ver log
tail -f newsletter.log
```

### Opção 2: Systemd Service (Linux)

Criar `/etc/systemd/system/trend-radar.service`:

```ini
[Unit]
Description=CFT Trend Radar Newsletter
After=network.target

[Service]
Type=simple
User=seu_usuario
WorkingDirectory=/caminho/para/trend-radar-newsletter
Environment="PATH=/caminho/para/venv/bin"
ExecStart=/caminho/para/venv/bin/python main.py schedule
Restart=always

[Install]
WantedBy=multi-user.target
```

Ativar:

```bash
sudo systemctl enable trend-radar
sudo systemctl start trend-radar
sudo systemctl status trend-radar
```

### Opção 3: Cron Job

```bash
# Editar crontab
crontab -e

# Adicionar linha (exemplo: Segunda às 9h)
0 9 * * 1 cd /caminho/para/trend-radar-newsletter && /caminho/para/venv/bin/python main.py send >> /var/log/trend-radar.log 2>&1
```

### Opção 4: Docker + Docker Compose

Criar `Dockerfile`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "main.py", "schedule"]
```

Criar `docker-compose.yml`:

```yaml
version: '3.8'

services:
  trend-radar:
    build: .
    env_file: .env
    volumes:
      - ./data:/app/data
    restart: unless-stopped
```

Executar:

```bash
docker-compose up -d
```

## Personalização

### Ajustar Threshold de Relevância

Edite `config/settings.yaml`:

```yaml
relevance:
  min_score: 6.0  # Aumentar para ser mais seletivo
```

### Ajustar Pesos dos Critérios

```yaml
relevance:
  weights:
    business_relevance: 0.25  # Aumentar importância
    disruptive_potential: 0.20
    # ... etc (total deve ser 1.0)
```

### Mudar Modelo de AI

```yaml
ai:
  provider: anthropic  # ou openai
  model: claude-3-5-sonnet-20241022  # ou gpt-4-turbo-preview
  temperature: 0.3
```

### Ajustar Número de Artigos por Secção

```yaml
newsletter:
  sections:
    - id: worldwide
      max_items: 5  # Máximo de artigos
      min_items: 1  # Mínimo para incluir secção
```

## Troubleshooting

### Erro: "ANTHROPIC_API_KEY not set"

Verifique que o ficheiro `.env` existe e contém a API key correta.

### Erro: Email não enviado

1. Verifique credenciais SMTP no `.env`
2. Para Gmail, use "Palavra-passe de aplicação"
3. Teste com: `python main.py test-email -t seu_email@example.com`

### Erro: "No relevant content found"

- Notícias podem já ter sido cobertas em newsletters anteriores
- Ajuste `min_score` em `config/settings.yaml` para ser menos restritivo
- Adicione mais fontes de notícias em `config/sources.yaml`

### Erro: Rate limit da API

- Reduza `articles_per_source` em `config/settings.yaml`
- Adicione delays entre pedidos
- Use um modelo mais barato (haiku em vez de sonnet)

## Manutenção

### Limpar Histórico Antigo

O sistema mantém automaticamente as últimas 52 newsletters. Para limpar manualmente:

```python
from src.context_manager import ContextManager

context = ContextManager()
context.clear_old_history(keep_count=26)  # Manter apenas 6 meses
```

### Backup do Histórico

```bash
# Backup
cp data/newsletter_history.json data/newsletter_history_backup_$(date +%Y%m%d).json

# Restaurar
cp data/newsletter_history_backup_YYYYMMDD.json data/newsletter_history.json
```

## Segurança

- **NUNCA** commit o ficheiro `.env` para Git
- Use `.gitignore` para proteger credenciais
- Considere usar secrets management (AWS Secrets Manager, Azure Key Vault, etc.)
- Rotacione API keys regularmente
- Use "Palavras-passe de aplicação" para email, não a password principal

## Custos Estimados

### API AI (por newsletter)

- **Anthropic Claude**: ~$0.10-0.50 por newsletter (depende do número de artigos)
- **OpenAI GPT-4**: ~$0.20-1.00 por newsletter

### Otimização de Custos

- Use Claude Haiku em vez de Sonnet (-80% custo)
- Limite `articles_per_source` em `config/settings.yaml`
- Aumente `min_score` para analisar menos artigos

## Roadmap Futuro

- [ ] Interface web para configuração
- [ ] Dashboard com analytics
- [ ] Suporte para múltiplas línguas
- [ ] Integração com Slack/Teams
- [ ] A/B testing de formatos
- [ ] Recomendações personalizadas por utilizador
- [ ] Integração com API do Google News
- [ ] Suporte para podcasts e vídeos

## Contribuir

Para sugerir melhorias ou reportar bugs, contacte a equipa CFT.

## Licença

Propriedade da Fidelidade - Center for Transformation (CFT). Uso interno apenas.

---

**Desenvolvido para o CFT - Center for Transformation**
Fidelidade - Companhia de Seguros, S.A.
