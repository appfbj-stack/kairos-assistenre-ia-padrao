from dataclasses import dataclass, field
from typing import Optional, Callable, Any
from enum import Enum


class AgentCapability(str, Enum):
    FINANCE = "finance"
    CHURCH = "church"
    WORKSHOP = "workshop"
    REAL_ESTATE = "real_estate"
    GLAZIER = "glazier"
    GENERAL = "general"


@dataclass
class AgentDef:
    id: str
    name: str
    description: str
    capability: AgentCapability
    system_prompt: str = ""
    tools: list[str] = field(default_factory=list)
    is_active: bool = True
    executor: Optional[Callable] = None

    def can_handle(self, intent: str) -> bool:
        keywords = {
            AgentCapability.FINANCE: ["financeiro", "dinheiro", "gasto", "receita", "pagamento"],
            AgentCapability.CHURCH: ["igreja", "membro", "culto", "evento", "ministerio"],
            AgentCapability.WORKSHOP: ["oficina", "servico", "cliente", "peca", "veiculo"],
            AgentCapability.REAL_ESTATE: ["imovel", "aluguel", "venda", "proprietario", "inquilino"],
            AgentCapability.GLAZIER: ["vidro", "vidracaria", "corte", "orcamento"],
        }
        words = self.capability
        return any(kw in intent.lower() for kw in keywords.get(words, []))
