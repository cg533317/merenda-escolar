import logging
import sys
from typing import Optional


def setup_logging(
    name: str = "AquaBot",
    level: int = logging.INFO,
    log_format: Optional[str] = None
) -> logging.Logger:
    """
    Configura e retorna um logger para o AquaBot.
    
    Args:
        name: Nome do logger (padrão: "AquaBot")
        level: Nível de logging (padrão: logging.INFO)
        log_format: Formato personalizado para os logs (opcional)
    
    Returns:
        Logger configurado
    """
    if log_format is None:
        log_format = "[%(name)s] %(levelname)s - %(message)s"
    
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Remove handlers existentes para evitar duplicação
    logger.handlers.clear()
    
    # Handler para stdout
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(level)
    formatter = logging.Formatter(log_format)
    handler.setFormatter(formatter)
    
    logger.addHandler(handler)
    
    return logger


def get_logger(name: str = "AquaBot") -> logging.Logger:
    """
    Retorna um logger existente ou cria um novo.
    
    Args:
        name: Nome do logger
    
    Returns:
        Logger configurado
    """
    logger = logging.getLogger(name)
    
    # Se o logger não tiver handlers, configura-o
    if not logger.handlers:
        return setup_logging(name)
    
    return logger


# Logger padrão do AquaBot
logger = get_logger("AquaBot")