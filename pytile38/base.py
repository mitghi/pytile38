from abc import (
  ABCMeta,
  abstractmethod,
  abstractproperty
)

class EndPointMeta(metaclass=ABCMeta):
  @property
  def protocol(self):
    return self._protocol

  @protocol.setter
  @abstractmethod
  def protocol(self, value):
    self._protocol = value
    
  @property
  def connection(self):
    return self._connection
  
  @connection.setter
  @abstractmethod
  def connection(self, value):
    self._connection = value

  @property
  def callbacks(self):
    return self._callbacks

  @callbacks.setter
  @abstractmethod
  def callbacks(self, value):
    self._callbacks = value

  @abstractmethod
  def register_callback(self, *args, **kwargs):
    pass

  @abstractmethod
  def remove_callback(self, *args, **kwargs):
    pass
  
  @property
  def commands(self):
    return self._commands

  @commands.setter
  @abstractmethod
  def commands(self, value):
    self._commands = value
    
  @abstractmethod
  def configure(self, *args, **kwargs):
    pass

  @abstractmethod
  def receive(self, *args, **kwargs):
    pass

  @abstractmethod
  def send(self, *args, **kwargs):
    pass

  @abstractmethod
  def command_builder(self, command=None, scheme=None, **kwargs):
    pass

  @abstractmethod
  def dispatch(self, command=None, scheme=None, **kwargs):
    pass

  @abstractmethod
  def setup(self, *args, **kwargs):
    pass

class EndPointProtocolMeta(metaclass=ABCMeta):
  @property
  def protocol(self):
    return self._protocol

  @protocol.setter
  @abstractmethod
  def protocol(self, value):
    self._protocol = value

  @abstractmethod
  def format_command(self, *args, **kwargs):
    pass

  @abstractmethod
  def parse_command(self, *args, **kwargs):
    pass

  @abstractmethod
  def parse_response(self, *args, **kwargs):
    pass

  @abstractmethod
  def format_response(self, *args, **kwargs):
    pass
  
class EndPointConnectionMeta(metaclass=ABCMeta):
  
  @property
  def protocol(self):
    return self._protocol

  @protocol.setter
  @abstractmethod
  def protocol(self, value):
    self._protocol = value

  @abstractmethod
  def set_connection(self, *args, **kwargs):
    pass

  @abstractmethod
  def failover_callback(self, *args, **kwargs):
    pass

  @abstractmethod
  def authenticate(self, *args, **kwargs):
    pass

  @property
  def connection(self):
    return self._connection

  @connection.setter
  @abstractmethod
  def connection(self, value):
    self._connection = value

  @property
  def host(self):
    return self._host

  @host.setter
  @abstractmethod
  def host(self, value):
    self._host = value

  @property
  def port(self):
    return self._port

  @port.setter
  @abstractmethod
  def port(self, value):
    self._port = value

  @abstractmethod
  def health(self, *args, **kwargs):
    pass

  @abstractmethod
  def connect(self, *args, **kwargs):
    pass

  @abstractmethod
  def disconnect(self, *args, **kwargs):
    pass

  @abstractmethod
  def reconnect(self, *args, **kwargs):
    pass

  @abstractmethod
  def send(self, *args, **kwargs):
    pass

  @abstractmethod
  def receive(self, *args, **kwargs):
    pass

  @abstractmethod
  def configure(self, *args, **kwargs):
    pass

  @abstractmethod
  def setup(self, *args, **kwargs):
    pass
  
  @abstractmethod
  def serialize(self, *args, **kwargs):
    pass

  @abstractmethod
  def deserialize(self, *args, **kwargs):
    pass
  
