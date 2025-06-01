#!/usr/bin/env python3
"""
FA-CMS Plugin Interface
======================

Core plugin interface for the Fractal Algebra-based Consciousness Modeling System.
Provides standardized APIs for integrating various consciousness and optimization subsystems.

Key Features:
- Standardized plugin lifecycle
- Message passing protocol
- Resource management
- State synchronization
- Performance monitoring

For Tenxsom AI's FA-CMS framework.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Callable, Tuple
from enum import Enum
import numpy as np
import time
import uuid
import queue
import threading
import json
from datetime import datetime


class MessageType(Enum):
    """Types of inter-plugin messages"""
    STATE_UPDATE = "state_update"
    COMMAND = "command"
    QUERY = "query"
    RESPONSE = "response"
    EVENT = "event"
    ERROR = "error"
    HEARTBEAT = "heartbeat"


class PluginStatus(Enum):
    """Plugin lifecycle states"""
    UNINITIALIZED = "uninitialized"
    INITIALIZING = "initializing"
    READY = "ready"
    PROCESSING = "processing"
    ERROR = "error"
    STOPPED = "stopped"


@dataclass
class PluginConfig:
    """Configuration for FA-CMS plugins"""
    name: str
    version: str
    priority: int = 5  # 1-10, higher = more priority
    max_memory_mb: int = 500
    timeout_seconds: float = 60.0
    enable_caching: bool = True
    debug_mode: bool = False
    custom_params: Dict[str, Any] = field(default_factory=dict)


@dataclass
class FAMessage:
    """Inter-plugin message format"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    source_id: str = ""
    target_id: str = ""
    message_type: MessageType = MessageType.STATE_UPDATE
    payload: Dict[str, Any] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)
    priority: int = 5
    requires_response: bool = False
    correlation_id: Optional[str] = None


@dataclass
class ChakraState:
    """Unified chakra state representation"""
    type: str
    frequency: float
    amplitude: float
    phase: float
    coherence: float
    active: bool = True
    modulation: Optional[Tuple[float, float]] = None  # (depth, frequency)


@dataclass
class UnifiedState:
    """Unified state across all FA-CMS subsystems"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: float = field(default_factory=time.time)
    
    # Core state components
    optimization_params: Dict[str, float] = field(default_factory=dict)
    chakra_states: List[ChakraState] = field(default_factory=list)
    fractal_dimension: float = 1.0
    coherence_matrix: Optional[np.ndarray] = None
    quantum_state: Optional[np.ndarray] = None
    
    # Metadata
    metadata: Dict[str, Any] = field(default_factory=dict)
    processing_history: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            'id': self.id,
            'timestamp': self.timestamp,
            'optimization_params': self.optimization_params,
            'chakra_states': [
                {
                    'type': c.type,
                    'frequency': c.frequency,
                    'amplitude': c.amplitude,
                    'phase': c.phase,
                    'coherence': c.coherence,
                    'active': c.active
                } for c in self.chakra_states
            ],
            'fractal_dimension': self.fractal_dimension,
            'coherence_matrix': self.coherence_matrix.tolist() if self.coherence_matrix is not None else None,
            'quantum_state': self.quantum_state.tolist() if self.quantum_state is not None else None,
            'metadata': self.metadata,
            'processing_history': self.processing_history
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'UnifiedState':
        """Create from dictionary"""
        state = cls()
        state.id = data.get('id', state.id)
        state.timestamp = data.get('timestamp', state.timestamp)
        state.optimization_params = data.get('optimization_params', {})
        
        # Reconstruct chakra states
        state.chakra_states = [
            ChakraState(**cs) for cs in data.get('chakra_states', [])
        ]
        
        state.fractal_dimension = data.get('fractal_dimension', 1.0)
        
        # Reconstruct numpy arrays
        if data.get('coherence_matrix'):
            state.coherence_matrix = np.array(data['coherence_matrix'])
        if data.get('quantum_state'):
            state.quantum_state = np.array(data['quantum_state'])
        
        state.metadata = data.get('metadata', {})
        state.processing_history = data.get('processing_history', [])
        
        return state


class FAPlugin(ABC):
    """Base class for FA-CMS plugins"""
    
    def __init__(self, config: PluginConfig):
        self.id = str(uuid.uuid4())
        self.config = config
        self.status = PluginStatus.UNINITIALIZED
        self.metrics = {
            'processed_count': 0,
            'error_count': 0,
            'total_processing_time': 0.0,
            'last_processing_time': 0.0,
            'memory_usage_mb': 0.0
        }
        self._start_time = time.time()
        self._message_queue = queue.Queue()
        self._response_handlers = {}
        
    @abstractmethod
    def initialize(self) -> bool:
        """
        Initialize plugin resources.
        Returns True if successful, False otherwise.
        """
        pass
    
    @abstractmethod
    def process(self, state: UnifiedState) -> UnifiedState:
        """
        Process state through plugin logic.
        Returns modified state.
        """
        pass
    
    @abstractmethod
    def get_metrics(self) -> Dict[str, Any]:
        """Get plugin performance and health metrics"""
        pass
    
    @abstractmethod
    def shutdown(self):
        """Clean shutdown of plugin resources"""
        pass
    
    def get_status(self) -> PluginStatus:
        """Get current plugin status"""
        return self.status
    
    def get_info(self) -> Dict[str, Any]:
        """Get plugin information"""
        return {
            'id': self.id,
            'name': self.config.name,
            'version': self.config.version,
            'status': self.status.value,
            'uptime': time.time() - self._start_time,
            'metrics': self.get_metrics()
        }
    
    def send_message(self, message: FAMessage):
        """Send message to message queue"""
        self._message_queue.put(message)
    
    def receive_message(self, timeout: Optional[float] = None) -> Optional[FAMessage]:
        """Receive message from queue"""
        try:
            return self._message_queue.get(timeout=timeout)
        except queue.Empty:
            return None
    
    def _update_metrics(self, processing_time: float, error: bool = False):
        """Update internal metrics"""
        self.metrics['processed_count'] += 1
        if error:
            self.metrics['error_count'] += 1
        self.metrics['total_processing_time'] += processing_time
        self.metrics['last_processing_time'] = processing_time


class PluginManager:
    """Manages FA-CMS plugins and their interactions"""
    
    def __init__(self):
        self.plugins: Dict[str, FAPlugin] = {}
        self.message_router = MessageRouter()
        self.state_manager = StateManager()
        self._running = False
        self._worker_thread = None
        
    def register_plugin(self, plugin: FAPlugin) -> bool:
        """Register a new plugin"""
        if plugin.id in self.plugins:
            return False
        
        # Initialize plugin
        plugin.status = PluginStatus.INITIALIZING
        if not plugin.initialize():
            plugin.status = PluginStatus.ERROR
            return False
        
        plugin.status = PluginStatus.READY
        self.plugins[plugin.id] = plugin
        
        print(f"Registered plugin: {plugin.config.name} (ID: {plugin.id})")
        return True
    
    def unregister_plugin(self, plugin_id: str) -> bool:
        """Unregister and shutdown plugin"""
        if plugin_id not in self.plugins:
            return False
        
        plugin = self.plugins[plugin_id]
        plugin.shutdown()
        del self.plugins[plugin_id]
        
        print(f"Unregistered plugin: {plugin.config.name}")
        return True
    
    def process_state(self, state: UnifiedState, 
                     plugin_chain: Optional[List[str]] = None) -> UnifiedState:
        """Process state through plugin chain"""
        if plugin_chain is None:
            # Use all plugins sorted by priority
            plugin_chain = sorted(
                self.plugins.keys(),
                key=lambda pid: self.plugins[pid].config.priority,
                reverse=True
            )
        
        # Process through each plugin
        for plugin_id in plugin_chain:
            if plugin_id not in self.plugins:
                continue
            
            plugin = self.plugins[plugin_id]
            if plugin.status != PluginStatus.READY:
                continue
            
            try:
                plugin.status = PluginStatus.PROCESSING
                start_time = time.time()
                
                state = plugin.process(state)
                state.processing_history.append(plugin_id)
                
                processing_time = time.time() - start_time
                plugin._update_metrics(processing_time)
                
                plugin.status = PluginStatus.READY
                
            except Exception as e:
                plugin._update_metrics(0, error=True)
                plugin.status = PluginStatus.ERROR
                print(f"Error in plugin {plugin.config.name}: {e}")
        
        return state
    
    def broadcast_message(self, message: FAMessage):
        """Broadcast message to all plugins"""
        for plugin in self.plugins.values():
            plugin.send_message(message)
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get overall system status"""
        return {
            'plugin_count': len(self.plugins),
            'plugins': {
                pid: plugin.get_info() 
                for pid, plugin in self.plugins.items()
            },
            'system_uptime': time.time() - self.state_manager._start_time,
            'total_states_processed': self.state_manager.get_state_count()
        }
    
    def start(self):
        """Start plugin manager background tasks"""
        self._running = True
        self._worker_thread = threading.Thread(target=self._worker_loop)
        self._worker_thread.daemon = True
        self._worker_thread.start()
    
    def stop(self):
        """Stop plugin manager"""
        self._running = False
        if self._worker_thread:
            self._worker_thread.join()
        
        # Shutdown all plugins
        for plugin_id in list(self.plugins.keys()):
            self.unregister_plugin(plugin_id)
    
    def _worker_loop(self):
        """Background worker for handling messages and maintenance"""
        while self._running:
            # Process messages from plugins
            for plugin in self.plugins.values():
                message = plugin.receive_message(timeout=0.01)
                if message:
                    self.message_router.route_message(message, self.plugins)
            
            # Send heartbeats
            if int(time.time()) % 30 == 0:  # Every 30 seconds
                heartbeat = FAMessage(
                    source_id="system",
                    message_type=MessageType.HEARTBEAT,
                    payload={'timestamp': time.time()}
                )
                self.broadcast_message(heartbeat)
            
            time.sleep(0.1)


class MessageRouter:
    """Routes messages between plugins"""
    
    def route_message(self, message: FAMessage, plugins: Dict[str, FAPlugin]):
        """Route message to appropriate plugin(s)"""
        if message.target_id == "broadcast":
            # Broadcast to all plugins except source
            for plugin_id, plugin in plugins.items():
                if plugin_id != message.source_id:
                    plugin.send_message(message)
        
        elif message.target_id in plugins:
            # Direct message
            plugins[message.target_id].send_message(message)
        
        # Log message for debugging
        if message.message_type != MessageType.HEARTBEAT:
            print(f"Routed message: {message.message_type.value} "
                  f"from {message.source_id} to {message.target_id}")


class StateManager:
    """Manages unified state persistence and versioning"""
    
    def __init__(self):
        self._states: Dict[str, UnifiedState] = {}
        self._state_history: List[str] = []
        self._max_history = 100
        self._start_time = time.time()
    
    def save_state(self, state: UnifiedState) -> str:
        """Save state and return ID"""
        self._states[state.id] = state
        self._state_history.append(state.id)
        
        # Limit history
        if len(self._state_history) > self._max_history:
            old_id = self._state_history.pop(0)
            if old_id in self._states:
                del self._states[old_id]
        
        return state.id
    
    def get_state(self, state_id: str) -> Optional[UnifiedState]:
        """Retrieve state by ID"""
        return self._states.get(state_id)
    
    def get_latest_state(self) -> Optional[UnifiedState]:
        """Get most recent state"""
        if self._state_history:
            return self._states.get(self._state_history[-1])
        return None
    
    def get_state_count(self) -> int:
        """Get total number of states processed"""
        return len(self._state_history)


# Example implementation of a simple plugin
class EchoPlugin(FAPlugin):
    """Example plugin that echoes state with modifications"""
    
    def initialize(self) -> bool:
        """Initialize echo plugin"""
        print(f"Initializing {self.config.name}")
        return True
    
    def process(self, state: UnifiedState) -> UnifiedState:
        """Add echo metadata to state"""
        state.metadata['echo_timestamp'] = time.time()
        state.metadata['echo_plugin_id'] = self.id
        
        # Simulate some processing
        time.sleep(0.01)
        
        return state
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get echo plugin metrics"""
        return {
            **self.metrics,
            'plugin_specific': {
                'echo_count': self.metrics['processed_count']
            }
        }
    
    def shutdown(self):
        """Shutdown echo plugin"""
        print(f"Shutting down {self.config.name}")


def demo_plugin_system():
    """Demonstrate the FA-CMS plugin system"""
    print("FA-CMS Plugin System Demo")
    print("=" * 60)
    
    # Create plugin manager
    manager = PluginManager()
    manager.start()
    
    # Create and register example plugin
    echo_config = PluginConfig(
        name="EchoPlugin",
        version="1.0.0",
        priority=5
    )
    echo_plugin = EchoPlugin(echo_config)
    manager.register_plugin(echo_plugin)
    
    # Create test state
    test_state = UnifiedState(
        optimization_params={'x': 1.0, 'y': 2.0},
        chakra_states=[
            ChakraState(
                type="root",
                frequency=256.0,
                amplitude=0.5,
                phase=0.0,
                coherence=0.8
            )
        ],
        fractal_dimension=1.618
    )
    
    print("\nProcessing state through plugin system...")
    processed_state = manager.process_state(test_state)
    
    print(f"\nProcessed state ID: {processed_state.id}")
    print(f"Processing history: {processed_state.processing_history}")
    print(f"Echo metadata: {processed_state.metadata}")
    
    # Get system status
    status = manager.get_system_status()
    print(f"\nSystem status:")
    print(f"  Plugin count: {status['plugin_count']}")
    print(f"  States processed: {status['total_states_processed']}")
    
    # Cleanup
    manager.stop()
    print("\n✅ Plugin system demo complete!")


if __name__ == "__main__":
    demo_plugin_system()