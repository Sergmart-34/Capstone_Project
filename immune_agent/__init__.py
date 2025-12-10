from . import agent  # ADK descubrirá el agente importando este módulo

# Expone root_agent (y alias agent) en el paquete para que ADK lo detecte
root_agent = agent.agent  # en agent.py se asigna agent = root_agent
agent = root_agent

__all__ = ["root_agent", "agent"]

