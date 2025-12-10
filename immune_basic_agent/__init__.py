from . import agent  # ADK descubre el agente importando este módulo

# Expone root_agent en el paquete para que ADK lo detecte con seguridad
root_agent = agent.root_agent
agent = agent.root_agent

__all__ = ["root_agent", "agent"]

