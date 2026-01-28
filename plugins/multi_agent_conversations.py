"""
AAS-285: Multi-Agent Conversations
Implements multi-agent conversation coordination and message routing
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
import uuid


class MessageType(Enum):
    """Message types in conversation"""
    STATEMENT = "statement"
    QUERY = "query"
    RESPONSE = "response"
    CONTROL = "control"


class AgentRole(Enum):
    """Agent roles in conversation"""
    COORDINATOR = "coordinator"
    PARTICIPANT = "participant"
    OBSERVER = "observer"


@dataclass
class Message:
    """Message in conversation"""
    id: str
    sender_id: str
    content: str
    message_type: MessageType
    timestamp: datetime
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Agent:
    """Agent in conversation"""
    agent_id: str
    name: str
    role: AgentRole
    enabled: bool = True
    message_history: List[Message] = field(default_factory=list)


class ConversationManager:
    """Manages multi-agent conversations"""

    def __init__(self, coordinator_id: str) -> None:
        """Initialize conversation manager"""
        self.conversation_id = str(uuid.uuid4())
        self.coordinator_id = coordinator_id
        self.agents: Dict[str, Agent] = {}
        self.messages: List[Message] = []
        self.active: bool = True

    def add_agent(self, agent_id: str, name: str,
                  role: AgentRole) -> Dict[str, Any]:
        """Add agent to conversation"""
        if agent_id in self.agents:
            return {'error': f'Agent {agent_id} already exists'}

        agent = Agent(
            agent_id=agent_id,
            name=name,
            role=role
        )
        self.agents[agent_id] = agent
        return {
            'success': True,
            'agent_id': agent_id,
            'role': role.value
        }

    def remove_agent(self, agent_id: str) -> Dict[str, Any]:
        """Remove agent from conversation"""
        if agent_id not in self.agents:
            return {'error': f'Agent {agent_id} not found'}

        if agent_id == self.coordinator_id:
            return {'error': 'Cannot remove coordinator'}

        del self.agents[agent_id]
        return {'success': True, 'removed': agent_id}

    def post_message(self, sender_id: str, content: str,
                     message_type: MessageType = MessageType.STATEMENT,
                     metadata: Optional[Dict] = None) -> Dict[str, Any]:
        """Post message to conversation"""
        if sender_id not in self.agents:
            return {'error': f'Sender {sender_id} not found'}

        if not self.active:
            return {'error': 'Conversation is inactive'}

        agent = self.agents[sender_id]
        if not agent.enabled:
            return {'error': f'Agent {sender_id} is disabled'}

        message = Message(
            id=str(uuid.uuid4()),
            sender_id=sender_id,
            content=content,
            message_type=message_type,
            timestamp=datetime.now(),
            metadata=metadata or {}
        )

        self.messages.append(message)
        agent.message_history.append(message)

        return {
            'success': True,
            'message_id': message.id,
            'total_messages': len(self.messages)
        }

    def get_agent_messages(self, agent_id: str) -> Dict[str, Any]:
        """Get messages from specific agent"""
        if agent_id not in self.agents:
            return {'error': f'Agent {agent_id} not found'}

        agent = self.agents[agent_id]
        messages_data = [
            {
                'id': msg.id,
                'content': msg.content,
                'type': msg.message_type.value,
                'timestamp': msg.timestamp.isoformat()
            }
            for msg in agent.message_history
        ]

        return {
            'agent_id': agent_id,
            'message_count': len(messages_data),
            'messages': messages_data
        }

    def get_conversation_summary(self) -> Dict[str, Any]:
        """Get conversation summary"""
        message_stats = {'statement': 0, 'query': 0, 'response': 0,
                         'control': 0}
        for msg in self.messages:
            msg_type = msg.message_type.value
            if msg_type in message_stats:
                message_stats[msg_type] += 1

        participants = [
            {
                'agent_id': agent.agent_id,
                'name': agent.name,
                'role': agent.role.value,
                'enabled': agent.enabled,
                'messages_sent': len(agent.message_history)
            }
            for agent in self.agents.values()
        ]

        return {
            'conversation_id': self.conversation_id,
            'total_messages': len(self.messages),
            'total_agents': len(self.agents),
            'active': self.active,
            'message_stats': message_stats,
            'participants': participants
        }

    def enable_agent(self, agent_id: str) -> Dict[str, Any]:
        """Enable agent participation"""
        if agent_id not in self.agents:
            return {'error': f'Agent {agent_id} not found'}

        self.agents[agent_id].enabled = True
        return {'success': True, 'agent_id': agent_id, 'enabled': True}

    def disable_agent(self, agent_id: str) -> Dict[str, Any]:
        """Disable agent participation"""
        if agent_id not in self.agents:
            return {'error': f'Agent {agent_id} not found'}

        self.agents[agent_id].enabled = False
        return {'success': True, 'agent_id': agent_id, 'enabled': False}

    def close_conversation(self) -> Dict[str, Any]:
        """Close conversation"""
        if not self.active:
            return {'error': 'Conversation already closed'}

        self.active = False
        return {
            'success': True,
            'conversation_id': self.conversation_id,
            'final_message_count': len(self.messages),
            'final_agent_count': len(self.agents)
        }

    def route_message_to_agents(self, sender_id: str, content: str,
                                target_roles: List[AgentRole]
                                ) -> Dict[str, Any]:
        """Route message to specific agent roles"""
        results = {'routed': 0, 'failed': 0, 'skipped': 0}

        for agent in self.agents.values():
            if agent.agent_id == sender_id:
                continue

            if agent.role in target_roles and agent.enabled:
                message = Message(
                    id=str(uuid.uuid4()),
                    sender_id=sender_id,
                    content=content,
                    message_type=MessageType.STATEMENT,
                    timestamp=datetime.now(),
                    metadata={'routed': True}
                )
                self.messages.append(message)
                agent.message_history.append(message)
                results['routed'] += 1
            elif agent.role in target_roles and not agent.enabled:
                results['skipped'] += 1
            else:
                results['failed'] += 1

        return {'success': True, 'results': results}

    def get_status(self) -> Dict[str, Any]:
        """Get manager status"""
        return {
            'conversation_id': self.conversation_id,
            'active': self.active,
            'total_messages': len(self.messages),
            'total_agents': len(self.agents),
            'coordinator_id': self.coordinator_id
        }
