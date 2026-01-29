# FIXO - Agente de Inteligência Competitiva

Agente automatizado de tracking competitivo para a equipa FIXO. Monitoriza mudanças em empresas de serviços domésticos: **FIXO**, **Oscar (Oscar App)**, **TaskRabbit** e **Webel**.

## O que monitoriza

- **Serviços** - novos serviços adicionados ou removidos
- **Preços** - alterações nos preços base ou modelos de preço
- **Localizações** - novas zonas de operação ou retirada de locais
- **Promoções** - cupões de desconto, ofertas especiais, campanhas
- **Modelo de negócio** - mudanças na estratégia, parcerias, posicionamento

## Instalação

```bash
pip install -r requirements.txt
```

## Utilização

```bash
# Scan completo de todas as empresas
python run.py scan

# Scan de empresas específicas
python run.py scan --companies fixo oscar

# Relatório em markdown
python run.py scan --format markdown

# Ver estado atual
python run.py status
python run.py status --company taskrabbit

# Modo agendado (scan automático periódico)
python run.py schedule --interval 12
```

## Estrutura

```
├── run.py                    # CLI principal
├── config/
│   ├── companies.json        # Configuração das empresas monitorizadas
│   └── settings.json         # Configurações gerais do agente
├── tracker/
│   ├── agent.py              # Agente coordenador principal
│   ├── change_detector.py    # Motor de deteção de mudanças
│   ├── storage.py            # Armazenamento de snapshots
│   ├── models/
│   │   ├── snapshot.py       # Modelo de snapshot de empresa
│   │   └── change.py         # Modelo de mudança detetada
│   ├── scrapers/
│   │   ├── base.py           # Scraper base (classe abstrata)
│   │   ├── fixo.py           # Scraper FIXO
│   │   ├── oscar.py          # Scraper Oscar App
│   │   ├── taskrabbit.py     # Scraper TaskRabbit
│   │   └── webel.py          # Scraper Webel
│   └── reports/
│       └── generator.py      # Gerador de relatórios (terminal/md/json)
└── data/
    ├── snapshots/            # Histórico de snapshots por empresa
    └── reports/              # Relatórios gerados
```

## Como funciona

1. **Scraping** - Os scrapers acedem aos websites de cada empresa e extraem informação sobre serviços, preços, localizações e promoções
2. **Snapshot** - Os dados extraídos são guardados como snapshots com timestamp
3. **Comparação** - O motor de deteção compara o snapshot atual com o anterior
4. **Relatório** - As mudanças são compiladas num relatório por empresa e categoria

## Adicionar uma nova empresa

1. Criar um novo scraper em `tracker/scrapers/` (herda de `BaseScraper`)
2. Registar o scraper em `tracker/scrapers/__init__.py`
3. Adicionar a configuração em `config/companies.json`