#!/usr/bin/env python3
"""
FIXO Competitive Intelligence Agent - CLI Runner

Agente de acompanhamento competitivo para a equipa FIXO.
Monitoriza: FIXO, Oscar (Oscar App), TaskRabbit, Webel.

Uso:
    python run.py scan                      # Scan completo de todas as empresas
    python run.py scan --companies fixo oscar  # Scan de empresas específicas
    python run.py scan --format markdown    # Scan com output em markdown
    python run.py status                    # Ver estado atual de todas as empresas
    python run.py status --company fixo     # Ver estado de uma empresa
    python run.py schedule                  # Correr em modo agendado (contínuo)
"""

import argparse
import json
import logging
import sys
import time
from datetime import datetime

from tracker.agent import CompetitiveAgent


def setup_logging(verbose: bool = False):
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )


def cmd_scan(args):
    """Executa um scan."""
    agent = CompetitiveAgent(config_dir=args.config_dir)

    companies = args.companies if args.companies else None
    agent.run_scan(company_ids=companies, report_format=args.format)


def cmd_status(args):
    """Mostra o estado atual."""
    agent = CompetitiveAgent(config_dir=args.config_dir)

    if args.company:
        status = agent.get_company_status(args.company)
        if status:
            print(json.dumps(status, ensure_ascii=False, indent=2))
        else:
            print(f"Sem dados para a empresa: {args.company}")
            print("Execute primeiro: python run.py scan")
    else:
        all_status = agent.get_all_status()
        print(json.dumps(all_status, ensure_ascii=False, indent=2))


def cmd_schedule(args):
    """Corre em modo agendado."""
    agent = CompetitiveAgent(config_dir=args.config_dir)
    interval_hours = args.interval

    print(f"Modo agendado iniciado - scan a cada {interval_hours}h")
    print("Pressione Ctrl+C para parar\n")

    while True:
        try:
            print(f"\n--- Scan iniciado: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ---\n")
            agent.run_scan(report_format=args.format)
            print(f"\nPróximo scan em {interval_hours}h...")
            time.sleep(interval_hours * 3600)
        except KeyboardInterrupt:
            print("\nAgendamento parado pelo utilizador.")
            break


def main():
    parser = argparse.ArgumentParser(
        description="FIXO Competitive Intelligence Agent",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos:
  python run.py scan                          Scan completo
  python run.py scan --companies fixo oscar   Scan específico
  python run.py scan --format markdown        Output em markdown
  python run.py status                        Estado de todas as empresas
  python run.py status --company taskrabbit   Estado de uma empresa
  python run.py schedule --interval 12        Scan automático a cada 12h
        """,
    )

    parser.add_argument(
        "--config-dir", default="config", help="Diretório de configuração"
    )
    parser.add_argument(
        "-v", "--verbose", action="store_true", help="Output detalhado"
    )

    subparsers = parser.add_subparsers(dest="command", help="Comandos disponíveis")

    # scan
    scan_parser = subparsers.add_parser("scan", help="Executar scan de empresas")
    scan_parser.add_argument(
        "--companies",
        nargs="+",
        choices=["fixo", "oscar", "taskrabbit", "webel"],
        help="Empresas específicas para scan",
    )
    scan_parser.add_argument(
        "--format",
        choices=["terminal", "markdown", "json"],
        default="terminal",
        help="Formato do relatório",
    )

    # status
    status_parser = subparsers.add_parser("status", help="Ver estado atual")
    status_parser.add_argument(
        "--company",
        choices=["fixo", "oscar", "taskrabbit", "webel"],
        help="Empresa específica",
    )

    # schedule
    schedule_parser = subparsers.add_parser(
        "schedule", help="Correr em modo agendado"
    )
    schedule_parser.add_argument(
        "--interval",
        type=float,
        default=24,
        help="Intervalo entre scans em horas (default: 24)",
    )
    schedule_parser.add_argument(
        "--format",
        choices=["terminal", "markdown", "json"],
        default="terminal",
        help="Formato do relatório",
    )

    args = parser.parse_args()
    setup_logging(args.verbose)

    if args.command is None:
        parser.print_help()
        sys.exit(1)

    commands = {
        "scan": cmd_scan,
        "status": cmd_status,
        "schedule": cmd_schedule,
    }

    commands[args.command](args)


if __name__ == "__main__":
    main()
