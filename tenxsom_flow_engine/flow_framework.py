"""
Flow Framework Implementation
Compatible implementation of Google Flow structure for video generation
"""

import time
import uuid
import json
import asyncio
import logging
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Callable
from datetime import datetime
from functools import wraps

# Configure production logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class FlowEvent:
    """Represents a single execution event in the flow"""
    id: str
    name: str
    start_time: float
    end_time: Optional[float] = None
    inputs: Dict[str, Any] = field(default_factory=dict)
    result: Any = None
    error: Optional[str] = None
    parent_id: Optional[str] = None


@dataclass
class History:
    """Flow execution history containing all events"""
    events: List[FlowEvent] = field(default_factory=list)
    root_event: Optional[FlowEvent] = None
    
    def get_events(self) -> List[FlowEvent]:
        """Get all events in execution order"""
        return self.events
    
    def get_root_events(self) -> List[FlowEvent]:
        """Get root level events"""
        if self.root_event:
            return [self.root_event]
        return [e for e in self.events if e.parent_id is None]


class FlowContext:
    """Context for flow execution tracking"""
    
    def __init__(self):
        self.events: List[FlowEvent] = []
        self.current_event: Optional[FlowEvent] = None
        
    def start_event(self, name: str, inputs: Dict[str, Any]) -> FlowEvent:
        """Start a new execution event"""
        event = FlowEvent(
            id=str(uuid.uuid4()),
            name=name,
            start_time=time.time(),
            inputs=inputs.copy(),
            parent_id=self.current_event.id if self.current_event else None
        )
        self.events.append(event)
        return event
    
    def end_event(self, event: FlowEvent, result: Any = None, error: str = None):
        """End an execution event"""
        event.end_time = time.time()
        event.result = result
        event.error = error


# Global context for flow execution
_flow_context = FlowContext()


def func(fn: Callable = None) -> Callable:
    """Decorator to mark functions as flow functions"""
    
    def decorator(fn: Callable) -> Callable:
        @wraps(fn)
        async def async_wrapper(*args, **kwargs):
            # Create event for this function call
            inputs = {
                'args': args,
                'kwargs': kwargs
            }
            
            event = _flow_context.start_event(fn.__name__, inputs)
            old_current = _flow_context.current_event
            _flow_context.current_event = event
            
            try:
                # Execute the function
                if asyncio.iscoroutinefunction(fn):
                    result = await fn(*args, **kwargs)
                else:
                    result = fn(*args, **kwargs)
                
                _flow_context.end_event(event, result)
                return result
                
            except Exception as e:
                _flow_context.end_event(event, error=str(e))
                raise
            finally:
                _flow_context.current_event = old_current
        
        @wraps(fn)
        def sync_wrapper(*args, **kwargs):
            # Create event for this function call
            inputs = {
                'args': args,
                'kwargs': kwargs
            }
            
            event = _flow_context.start_event(fn.__name__, inputs)
            old_current = _flow_context.current_event
            _flow_context.current_event = event
            
            try:
                result = fn(*args, **kwargs)
                _flow_context.end_event(event, result)
                return result
                
            except Exception as e:
                _flow_context.end_event(event, error=str(e))
                raise
            finally:
                _flow_context.current_event = old_current
        
        # Return appropriate wrapper based on function type
        if asyncio.iscoroutinefunction(fn):
            return async_wrapper
        else:
            return sync_wrapper
    
    # Handle both @fl.func and @fl.func() usage
    if fn is None:
        return decorator
    else:
        return decorator(fn)


async def run(main_function: Callable, *args, **kwargs) -> History:
    """Run a flow and return execution history"""
    global _flow_context
    
    # Reset context for new run
    _flow_context = FlowContext()
    
    try:
        # Execute main function
        if asyncio.iscoroutinefunction(main_function):
            result = await main_function(*args, **kwargs)
        else:
            result = main_function(*args, **kwargs)
        
        # Create history object
        history = History(events=_flow_context.events)
        if _flow_context.events:
            history.root_event = _flow_context.events[0]
            
        return history
        
    except Exception as e:
        logger.error(f"Flow execution failed: {e}")
        # Still return history with error information
        history = History(events=_flow_context.events)
        if _flow_context.events:
            history.root_event = _flow_context.events[0]
        return history


# Alias for compatibility
fl = type('FlowModule', (), {
    'func': func,
    'run': run,
    'History': History,
    'FlowEvent': FlowEvent
})()