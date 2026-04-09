#!/usr/bin/env python3
"""
Script de verificação: testa se WakaTime está configurado corretamente.

Usage:
    python .time-tracking/test_wakatime.py
"""

import os
from pathlib import Path
from dotenv import load_dotenv
import requests
import sys


def check_configuration():
    """Verifica se WakaTime está configurado."""
    print("\n🔍 Verificando configuração de WakaTime...\n")
    
    # Carrega .env
    env_path = Path(__file__).parent.parent / ".env"
    load_dotenv(env_path)
    
    api_key = os.getenv("WAKATIME_API_KEY")
    
    # Check 1: API Key existe?
    if not api_key:
        print("❌ WAKATIME_API_KEY não configurada")
        print("   📍 Adicione em .env: WAKATIME_API_KEY=sua-chave-aqui")
        print("   📍 Obtenha em: https://wakatime.com → Settings → API Key\n")
        return False
    
    if api_key == "paste-your-api-key-here-depois-salve":
        print("❌ WAKATIME_API_KEY ainda contém placeholder")
        print("   📍 Edite .env e adicione sua chave real\n")
        return False
    
    print(f"✅ API Key configurada: {api_key[:10]}...{api_key[-4:]}")
    
    # Check 2: Chave é válida?
    print("🔗 Testando conexão com WakaTime API...")
    
    headers = {"Authorization": f"Bearer {api_key}"}
    
    try:
        response = requests.get(
            "https://wakatime.com/api/v1/users/current",
            headers=headers,
            timeout=5
        )
        
        if response.status_code == 200:
            user_data = response.json()
            user = user_data.get("data", {})
            print(f"✅ Conectado como: {user.get('display_name', user.get('email', 'Unknown'))}")
            return True
        
        elif response.status_code == 401:
            print("❌ API Key inválida ou expirada")
            print("   📍 Verifique em: https://wakatime.com → Settings → API Key\n")
            return False
        
        else:
            print(f"❌ Erro na API: {response.status_code}")
            print(f"   Mensagem: {response.text}\n")
            return False
    
    except requests.exceptions.RequestException as e:
        print(f"❌ Erro de conexão: {e}\n")
        return False


def check_extension():
    """Verifica se extensão VS Code está instalada."""
    print("\n🔍 Verificando VS Code Extension...\n")
    
    # Não conseguimos verificar automaticamente se a extensão está instalada no VS Code
    # Mas podemos dar instruções
    print("📦 Extensão WakaTime:")
    print("   ℹ️  Para verif: Extensions → Search 'WakaTime' → Deve aparecer 'Installed'\n")
    
    return True


def main():
    """Main entry point."""
    print("="*60)
    print("🚀 Verificação de Configuração - WakaTime + Time Tracking")
    print("="*60)
    
    config_ok = check_configuration()
    check_extension()
    
    print("="*60)
    
    if config_ok:
        print("\n✅ Tudo configurado! Próximos passos:")
        print("   1. Instale dependências: uv sync --group time-tracking")
        print("   2. Use V.S Code normalmente (WakaTime rastreia)")
        print("   3. Faça commits: git commit -m 'msg'")
        print("   4. Git hook exporta horas automaticamente ✨\n")
        return 0
    else:
        print("\n❌ Configuração incompleta. Siga as instruções acima.\n")
        return 1


if __name__ == "__main__":
    sys.exit(main())
