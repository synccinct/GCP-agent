# Pub/Sub event handling
from google.cloud import pubsub_v1
import json
import asyncio

class EventPublisher:
    """Publishes events to Pub/Sub topics"""
    
    def __init__(self, project_id: str):
        self.project_id = project_id
        self.publisher = pubsub_v1.PublisherClient()
    
    async def publish_event(self, topic_name: str, event_data: Dict[str, Any]):
        """Publish event to specified topic"""
        
        topic_path = self.publisher.topic_path(self.project_id, topic_name)
        
        # Serialize event data
        message_data = json.dumps(event_data).encode("utf-8")
        
        # Add metadata
        attributes = {
            "event_type": event_data.get("event_type", "unknown"),
            "source_service": event_data.get("source_service", "unknown"),
            "timestamp": str(datetime.utcnow())
        }
        
        # Publish message
        future = self.publisher.publish(
            topic_path, 
            message_data, 
            **attributes
        )
        
        return future.result()

class EventSubscriber:
    """Subscribes to and processes events from Pub/Sub"""
    
    def __init__(self, project_id: str, subscription_name: str):
        self.project_id = project_id
        self.subscription_name = subscription_name
        self.subscriber = pubsub_v1.SubscriberClient()
        self.subscription_path = self.subscriber.subscription_path(
            project_id, subscription_name
        )
    
    def start_listening(self, callback_function):
        """Start listening for messages"""
        
        def message_callback(message):
            try:
                # Decode message
                event_data = json.loads(message.data.decode("utf-8"))
                
                # Process event
                callback_function(event_data, message.attributes)
                
                # Acknowledge message
                message.ack()
                
            except Exception as e:
                print(f"Error processing message: {e}")
                message.nack()
        
        # Start pulling messages
        streaming_pull_future = self.subscriber.subscribe(
            self.subscription_path, 
            callback=message_callback
        )
        
        return streaming_pull_future

# Event-driven module integration
class ModuleIntegrationCoordinator:
    """Coordinates module integration via events"""
    
    def __init__(self, project_id: str):
        self.project_id = project_id
        self.publisher = EventPublisher(project_id)
        self.integration_status = {}
    
    async def handle_module_generated_event(self, event_data: Dict[str, Any]):
        """Handle module generation completion event"""
        
        module_id = event_data["module_id"]
        module_type = event_data["module_type"]
        project_id = event_data["project_id"]
        
        # Check if all required modules are ready
        if await self._all_modules_ready(project_id):
            # Trigger integration process
            await self.publisher.publish_event(
                "module-integration",
                {
                    "event_type": "StartIntegration",
                    "project_id": project_id,
                    "source_service": "integration-coordinator"
                }
            )
    
    async def handle_integration_request_event(self, event_data: Dict[str, Any]):
        """Handle integration request event"""
        
        project_id = event_data["project_id"]
        
        # Get all modules for project
        modules = await self._get_project_modules(project_id)
        
        # Generate integration code
        integration_result = await self._generate_integration_code(modules)
        
        # Publish integration complete event
        await self.publisher.publish_event(
            "module-integration",
            {
                "event_type": "IntegrationComplete",
                "project_id": project_id,
                "integration_result": integration_result,
                "source_service": "integration-coordinator"
            }
      )
      
