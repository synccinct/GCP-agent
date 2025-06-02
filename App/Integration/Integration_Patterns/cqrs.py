# CQRS pattern implementation
from dataclasses import dataclass
from typing import Union
import asyncio

@dataclass
class Command:
    """Base command class"""
    command_id: str
    timestamp: str
    user_id: str

@dataclass
class Query:
    """Base query class"""
    query_id: str
    timestamp: str
    user_id: str

@dataclass
class GenerateModuleCommand(Command):
    """Command to generate a new module"""
    module_type: str
    specifications: Dict[str, Any]
    project_id: str

@dataclass
class GetModuleQuery(Query):
    """Query to retrieve module information"""
    module_id: str
    include_code: bool = False

class CommandHandler:
    """Handles write operations (commands)"""
    
    def __init__(self, event_store, module_generator):
        self.event_store = event_store
        self.module_generator = module_generator
    
    async def handle_generate_module(self, command: GenerateModuleCommand):
        """Handle module generation command"""
        
        # Generate module
        result = await self.module_generator.generate(
            command.module_type,
            command.specifications
        )
        
        # Store event
        event = {
            "event_type": "ModuleGenerated",
            "module_id": result["module_id"],
            "module_type": command.module_type,
            "timestamp": command.timestamp,
            "user_id": command.user_id
        }
        
        await self.event_store.append_event(event)
        return result

class QueryHandler:
    """Handles read operations (queries)"""
    
    def __init__(self, read_store):
        self.read_store = read_store
    
    async def handle_get_module(self, query: GetModuleQuery):
        """Handle module retrieval query"""
        
        module_data = await self.read_store.get_module(query.module_id)
        
        if query.include_code:
            module_data["code"] = await self.read_store.get_module_code(
                query.module_id
            )
        
        return module_data

# Event sourcing for CQRS
class EventStore:
    """Event store for CQRS pattern"""
    
    def __init__(self, firestore_client):
        self.db = firestore_client
        self.events_collection = "events"
    
    async def append_event(self, event: Dict[str, Any]):
        """Append event to event store"""
        
        doc_ref = self.db.collection(self.events_collection).document()
        event["event_id"] = doc_ref.id
        doc_ref.set(event)
        
        # Trigger read model update
        await self._update_read_model(event)
    
    async def get_events(self, aggregate_id: str) -> List[Dict[str, Any]]:
        """Get events for specific aggregate"""
        
        events = []
        docs = self.db.collection(self.events_collection)\
                     .where("aggregate_id", "==", aggregate_id)\
                     .order_by("timestamp")\
                     .stream()
        
        for doc in docs:
            events.append(doc.to_dict())
        
        return events
      
