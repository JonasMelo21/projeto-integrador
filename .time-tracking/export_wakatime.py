#!/usr/bin/env python3
"""
Script de exportação de horas WakaTime por projeto.

Exporta dados dos últimos 7 dias do WakaTime e salva em arquivo JSON local
para posterior sincronização com Azure DevOps.

Usage:
    python export_wakatime.py
    python export_wakatime.py --api-key YOUR_KEY --days 14
    python export_wakatime.py --sync-devops  # (futuro)

Docs: https://wakatime.com/developers
"""

import json
import requests
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Optional
import sys
import os
from dotenv import load_dotenv


# Carrega .env se existir
load_dotenv()

WAKATIME_API_KEY = os.getenv("WAKATIME_API_KEY")
WAKATIME_API_BASE = "https://wakatime.com/api/v1"
TIME_TRACKING_DIR = Path(__file__).parent
ARCHIVE_DIR = TIME_TRACKING_DIR / "archive"


def get_wakatime_stats(
    days: int = 7, 
    api_key: Optional[str] = None
) -> Dict[str, Dict]:
    """
    Fetch time tracking data from WakaTime API.
    
    Args:
        days: Number of days to fetch (default 7)
        api_key: WakaTime API key (uses env var if not provided)
    
    Returns:
        Dict organized by project/file with hours data
    
    Raises:
        ValueError: Se API key não configurada
        requests.RequestException: Se falha ao chamar API
    """
    if not api_key:
        api_key = WAKATIME_API_KEY
    
    if not api_key:
        raise ValueError(
            "WAKATIME_API_KEY não configurada. "
            "Defina em .env ou passe --api-key"
        )
    
    headers = {"Authorization": f"Bearer {api_key}"}
    stats = {}
    
    print(f"📊 Exportando últimos {days} dias do WakaTime...")
    
    for i in range(days):
        date = (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d")
        
        # Endpoint: /users/current/summaries?date=YYYY-MM-DD&range=Last 7 Days
        url = f"{WAKATIME_API_BASE}/users/current/summaries?date={date}"
        
        try:
            resp = requests.get(url, headers=headers, timeout=10)
            resp.raise_for_status()
            
            data = resp.json()
            
            # Cumulative total para o dia
            cumulative = data.get("cumulative_total", {})
            total_seconds = cumulative.get("total_seconds", 0)
            
            # Breakdown por projeto
            projects = data.get("projects", [])
            
            if date not in stats:
                stats[date] = {
                    "total_seconds": 0,
                    "total_hours": 0.0,
                    "projects": {}
                }
            
            stats[date]["total_seconds"] = total_seconds
            stats[date]["total_hours"] = round(total_seconds / 3600, 2)
            
            # Agrupa por projeto
            for proj in projects:
                project_name = proj.get("name", "unknown")
                proj_seconds = proj.get("total_seconds", 0)
                
                if project_name not in stats[date]["projects"]:
                    stats[date]["projects"][project_name] = {
                        "seconds": 0,
                        "hours": 0.0,
                        "percent": 0.0
                    }
                
                stats[date]["projects"][project_name]["seconds"] = proj_seconds
                stats[date]["projects"][project_name]["hours"] = round(proj_seconds / 3600, 2)
                
                if total_seconds > 0:
                    stats[date]["projects"][project_name]["percent"] = round(
                        (proj_seconds / total_seconds) * 100, 1
                    )
            
            print(f"  ✓ {date}: {stats[date]['total_hours']}h")
        
        except requests.exceptions.RequestException as e:
            print(f"  ✗ {date}: Erro na API - {e}")
            continue
    
    return stats


def save_archive(stats: Dict[str, Dict]) -> Path:
    """
    Salva dados em arquivo de arquivo JSON.
    
    Args:
        stats: Dados de estatísticas do WakaTime
    
    Returns:
        Path do arquivo criado
    """
    ARCHIVE_DIR.mkdir(exist_ok=True, parents=True)
    
    filename = ARCHIVE_DIR / f"wakatime-{datetime.now().strftime('%Y%m%d')}.json"
    
    # Merge com arquivo existente se houver
    existing_data = {}
    if filename.exists():
        with open(filename) as f:
            existing_data = json.load(f)
    
    existing_data.update(stats)
    
    with open(filename, "w") as f:
        json.dump(existing_data, f, indent=2)
    
    print(f"\n✅ Dados salvos em: {filename.relative_to(TIME_TRACKING_DIR.parent)}")
    
    return filename


def print_summary(stats: Dict[str, Dict]) -> None:
    """Imprime resumo formatado das horas."""
    print("\n" + "="*70)
    print("📈 RESUMO DE HORAS POR PROJETO")
    print("="*70)
    
    all_projects = {}
    total_hours = 0
    
    for date, day_data in stats.items():
        total_hours += day_data["total_hours"]
        
        for proj_name, proj_data in day_data.get("projects", {}).items():
            if proj_name not in all_projects:
                all_projects[proj_name] = {"hours": 0.0, "days": 0}
            
            all_projects[proj_name]["hours"] += proj_data["hours"]
            all_projects[proj_name]["days"] += 1
    
    # Sort by hours descending
    sorted_projects = sorted(
        all_projects.items(),
        key=lambda x: x[1]["hours"],
        reverse=True
    )
    
    print(f"\n{'Projeto':<30} {'Horas':>10} {'Dias':>8}")
    print("-" * 50)
    
    for proj_name, proj_data in sorted_projects:
        print(
            f"{proj_name[:28]:<30} "
            f"{proj_data['hours']:>10.2f}h "
            f"{proj_data['days']:>8}"
        )
    
    print("-" * 50)
    print(f"{'TOTAL':<30} {total_hours:>10.2f}h")
    print("="*70 + "\n")


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Exportar dados de tempo WakaTime por projeto"
    )
    parser.add_argument(
        "--api-key",
        help="WakaTime API key (ou use WAKATIME_API_KEY env var)"
    )
    parser.add_argument(
        "--days",
        type=int,
        default=7,
        help="Número de dias a exportar (default 7)"
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Modo silencioso (sem resumo)"
    )
    
    args = parser.parse_args()
    
    try:
        stats = get_wakatime_stats(days=args.days, api_key=args.api_key)
        
        if not stats:
            print("❌ Nenhum dado encontrado")
            return 1
        
        save_archive(stats)
        
        if not args.quiet:
            print_summary(stats)
        
        return 0
    
    except ValueError as e:
        print(f"❌ Erro de configuração: {e}")
        return 1
    except Exception as e:
        print(f"❌ Erro: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
