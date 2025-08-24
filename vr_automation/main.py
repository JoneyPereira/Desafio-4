"""
Script principal para execução da aplicação VR/VA
"""

import sys
import os
import logging
from pathlib import Path

# Adicionar diretório raiz ao path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from config.settings import settings
from utils.excel_handler import ExcelHandler
from utils.business_rules import BusinessRules

# Configurar logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def main():
    """Função principal"""
    
    try:
        logger.info("🚀 Iniciando Sistema de Automação VR/VA")
        
        # Verificar se estamos no diretório correto
        if not os.path.exists("app.py"):
            logger.error("❌ Arquivo app.py não encontrado. Execute este script do diretório raiz do projeto.")
            return 1
        
        # Verificar dependências
        check_dependencies()
        
        # Inicializar componentes
        initialize_components()
        
        # Executar aplicação
        run_application()
        
        return 0
        
    except Exception as e:
        logger.error(f"❌ Erro na execução: {str(e)}")
        return 1


def check_dependencies():
    """Verificar dependências necessárias"""
    
    logger.info("🔍 Verificando dependências...")
    
    required_packages = [
        'streamlit',
        'pandas',
        'openpyxl',
        'pydantic',
        'plotly'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
            logger.info(f"✅ {package} - OK")
        except ImportError:
            missing_packages.append(package)
            logger.error(f"❌ {package} - Não encontrado")
    
    if missing_packages:
        logger.error(f"❌ Pacotes faltando: {', '.join(missing_packages)}")
        logger.info("💡 Execute: pip install -r requirements.txt")
        raise ImportError(f"Pacotes necessários não encontrados: {missing_packages}")
    
    logger.info("✅ Todas as dependências estão instaladas")


def initialize_components():
    """Inicializar componentes do sistema"""
    
    logger.info("🔧 Inicializando componentes...")
    
    try:
        # Criar diretórios necessários
        create_directories()
        
        # Testar handlers
        test_handlers()
        
        logger.info("✅ Componentes inicializados com sucesso")
        
    except Exception as e:
        logger.error(f"❌ Erro na inicialização: {str(e)}")
        raise


def create_directories():
    """Criar diretórios necessários"""
    
    directories = [
        "data/temp",
        "data/cache",
        "logs"
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        logger.info(f"📁 Diretório criado/verificado: {directory}")


def test_handlers():
    """Testar handlers principais"""
    
    try:
        # Testar ExcelHandler
        excel_handler = ExcelHandler()
        logger.info("✅ ExcelHandler - OK")
        
        # Testar BusinessRules
        business_rules = BusinessRules()
        logger.info("✅ BusinessRules - OK")
        
    except Exception as e:
        logger.error(f"❌ Erro ao testar handlers: {str(e)}")
        raise


def run_application():
    """Executar aplicação Streamlit"""
    
    logger.info("🌐 Iniciando aplicação Streamlit...")
    
    try:
        import subprocess
        import sys
        
        # Comando para executar Streamlit
        cmd = [sys.executable, "-m", "streamlit", "run", "app.py"]
        
        logger.info(f"🚀 Executando: {' '.join(cmd)}")
        logger.info("📱 Aplicação disponível em: http://localhost:8501")
        logger.info("⏹️  Pressione Ctrl+C para parar")
        
        # Executar aplicação
        subprocess.run(cmd)
        
    except KeyboardInterrupt:
        logger.info("⏹️  Aplicação interrompida pelo usuário")
    except Exception as e:
        logger.error(f"❌ Erro ao executar aplicação: {str(e)}")
        raise


def show_help():
    """Mostrar ajuda"""
    
    help_text = """
🤖 Sistema de Automação VR/VA

Uso:
    python main.py          # Executar aplicação
    python main.py --help   # Mostrar esta ajuda

Comandos disponíveis:
    run                     # Executar aplicação (padrão)
    test                    # Executar testes
    install                 # Instalar dependências
    setup                   # Configurar ambiente

Exemplos:
    python main.py run
    python main.py test
    python main.py install

Para mais informações, consulte o README.md
"""
    
    print(help_text)


def run_tests():
    """Executar testes"""
    
    logger.info("🧪 Executando testes...")
    
    try:
        import subprocess
        import sys
        
        cmd = [sys.executable, "-m", "pytest", "tests/", "-v"]
        subprocess.run(cmd)
        
    except Exception as e:
        logger.error(f"❌ Erro ao executar testes: {str(e)}")
        return 1
    
    return 0


def install_dependencies():
    """Instalar dependências"""
    
    logger.info("📦 Instalando dependências...")
    
    try:
        import subprocess
        import sys
        
        cmd = [sys.executable, "-m", "pip", "install", "-r", "requirements.txt"]
        subprocess.run(cmd)
        
        logger.info("✅ Dependências instaladas com sucesso")
        
    except Exception as e:
        logger.error(f"❌ Erro ao instalar dependências: {str(e)}")
        return 1
    
    return 0


if __name__ == "__main__":
    # Verificar argumentos da linha de comando
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == "--help" or command == "-h":
            show_help()
        elif command == "test":
            sys.exit(run_tests())
        elif command == "install":
            sys.exit(install_dependencies())
        elif command == "run":
            sys.exit(main())
        else:
            print(f"❌ Comando desconhecido: {command}")
            show_help()
            sys.exit(1)
    else:
        # Executar aplicação por padrão
        sys.exit(main())
