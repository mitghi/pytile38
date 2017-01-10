from .base import *
from credis import Connection

class CMDTypes(object):
  __slots__ = ('key', 'types')  
  def __init__(self, key, *args, **kwargs):
    self.key = key    
    self.types = kwargs.get("types", [])

  def validate(self, objtype, instance, **kwargs):
    raise NotImplementedError()

  def is_oftypes(self, instance):
    result = False
    for objtype in self.types:
      if isistance(instance, objtype):
        result = True
        break

    return result

class Optional(CMDTypes):
  pass

class Must(CMDTypes):
  pass

class Conditional(CMDTypes):
  pass
    
class CompundConditional(CMDTypes):
  pass

class OptionalKVPairs(CMDTypes):
  pass

class OptionalCondition(CMDTypes):
  pass

class Flag(CMDTypes): # optional
  pass

class Echo(CMDTypes):
  pass

class AttrType(object): #TODO
  def __init__(self, *args, **kwargs):
    self.args = args
    
  def value(self):
    return self.args[0]


class Result(object):
  __slots__ = ("result", "kwargs", "command")
  def __init__(self, result, kwargs, command):
    self.result = result
    self.kwargs = kwargs
    self.command = command
  
class RedisEndPoint(EndPointMeta):
  def __init__(self, *args, **kwargs):
    super(RedisEndPoint, self).__init__(*args, **kwargs)
    self.connection = kwargs.get("connection", None)
    self.callbacks = kwargs.get("callbacks", {})
    self.commands = kwargs.get("commands", {})
    self.setup(*args, **kwargs) 

  def setup(self, *args, **kwargs):
    raise NotImplementedError()
  
  @EndPointMeta.connection.setter
  def connection(self, value):
    self._connection = value

  @EndPointMeta.callbacks.setter
  def callbacks(self, value):
    self._callbacks = value

  @EndPointMeta.commands.setter
  def commands(self, value):
    self._commands = value

  @EndPointMeta.protocol.setter
  def protocol(self, value):
    self._protocol = value

  def register_callback(self, *args, **kwargs):
    pass

  def remove_callback(self, *args, **kwargs):
    pass

  def configure(self, *args, **kwargs):
    pass

  def receive(self, *args, **kwargs):
    pass

  def send(self, *args, **kwargs):
    raise NotImplementedError()

  def command_builder(self, command=None, scheme=None, **kwargs):
    raise NotImplementedError()

  def _command_builder(self, command=None, schemestr=None, instance=None, **kwargs):
    command_args = []
    cmds = []
    try:
      cmds = self.commands.get(command, {})[schemestr]
    except :
      raise KeyError("Invalid command or arguments ( command={}, scheme={} )".format(command or "", schemestr or ""))
    
    for cmdarg in cmds:
      cmdkey = cmdarg.key
      cmdvalue = None
      if isinstance(cmdarg, Optional):                
        cmdvalue = kwargs.get(cmdkey, None) or getattr(instance, cmdkey, None)
        if not cmdvalue:
          continue
      elif isinstance(cmdarg, Must):
        cmdvalue = kwargs.get(cmdkey, getattr(instance, cmdkey, None))
        if cmdvalue == None:
          raise ValueError("Argument '{}'' is not given".format(cmdkey))
      elif isinstance(cmdarg, Conditional) or isinstance(cmdarg, OptionalCondition):
        iscond = True if isinstance(cmdarg, Conditional) else False
        cmdvalue = kwargs.get(cmdkey, getattr(instance, cmdkey, None))
        if cmdvalue == None and iscond:
          raise KeyError("Invalid command or arguments ( command={}, scheme={} )".format(command or "", schemestr or ""))
        elif cmdvalue == None and not iscond:
          continue
        condkey = "".join([schemestr, ":", str(kwargs.get(cmdkey, getattr(instance, cmdkey, "")))])
        condresult = None
        for cond in [condkey, "".join([schemestr, ":", "_", cmdkey])]:
          try:
            condresult = self._command_builder(command, cond, instance, **kwargs)
            break
          except KeyError:
            if iscond:
              raise
            else:
              continue

        if iscond and condresult == None:
          raise KeyError("Invalid command or arguments ( command={}, scheme={} )".format(command or "", schemestr or ""))
        elif not iscond and condresult == None:
          continue

        if condresult:
          command_args += condresult
        continue
      elif isinstance(cmdarg, OptionalKVPairs):
        cmdvalue = kwargs.get(cmdkey, None) or getattr(instance, cmdkey, None)
        if not cmdvalue:
          continue
      elif isinstance(cmdarg, Flag):
        cmdvalue = kwargs.get(cmdkey, None)
        if cmdvalue:
          new_cmdvalue = AttrType(cmdarg.key)         
          cmdvalue = new_cmdvalue
        else:
          continue
      elif isinstance(cmdarg, Echo):
        cmdvalue = kwargs.get(cmdkey, None)

      if cmdvalue and isinstance(cmdvalue, AttrType):
        cmdvalue = cmdvalue.value()
      command_args.append((cmdkey, cmdvalue))
      
    return command_args

  def command_builder(self, command=None, scheme=None, instance=None, **kwargs):
    if not self.commands.get(command, None):
      raise ValueError("Invalid command for collect_args")
    scheme = "scheme"
    statement = self._command_builder(command, scheme, instance, **kwargs)
    statement.insert(0, ("command", command))
    result = []
    for k, v in statement:
      if k == "fields":
        newv = list(map(lambda x: ["field"] + list(x), v))
        for nv in newv:
          result += nv
        continue
      result.append(v)

    return result

  def dispatch(self, command=None, instance=None, **kwargs):
    if not command:
        raise ValueError("command is empty")    
    command = command.lower()
    cmd = self.commands.get(command, None)
    if not cmd:
      raise ValueError("command is not available")
    specialhandler = cmd.get("handler", None)
    scheme = "scheme"
    data = None
    result = None

    if specialhandler:
      data = specialhandler(command=command, scheme=scheme, instance=instance, **kwargs)
    else:
      data = self.command_builder(command=command, scheme=scheme, instance=instance,  **kwargs)
    result = self.connection.send(data=data)
    
    return Result(result, kwargs, command)


class RedisConnectionBase(EndPointConnectionMeta):
  def __init__(self, *args, **kwargs):
    super(RedisConnectionBase, self).__init__()
    self.host = kwargs.get("host", "127.0.0.1")
    self.port = kwargs.get("port", 6379)
    self.protocol = kwargs.get("protocol", RedisProtocolBase)
    self.connection = kwargs.get("connection", None)
    self.authentication = kwargs.get("authentication", None)
    self.setup(*args, **kwargs)

  def setup(self, *args, **kwargs):
    raise NotImplementedError
  
  @EndPointConnectionMeta.connection.setter
  def connection(self, value):
    self._connection = value

  @EndPointConnectionMeta.host.setter
  def host(self, value):
    self._host = value

  @EndPointConnectionMeta.port.setter
  def port(self, value):
    self._port = value

  @EndPointConnectionMeta.protocol.setter
  def protocol(self, value):
    self._protocol = value

  def set_connection(self, *args, **kwargs):
    connection = kwargs.get("connection")
    raise NotImplementedError()

  def failover_callback(self, *args, **kwargs):
    raise NotImplementedError()

  def authenticate(self, *args, **kwargs):
    raise NotIMplementedError()

  def health(self, *args, **kwargs):
    raise NotImplementedError()

  def connect(self, *args, **kwargs):
    try:
      self.connection.connect()
    except:
      raise ValueError("Cannot connect to endpoint")

  def disconnect(self, *args, **kwargs):
    raise NotImplementedError()

  def reconnect(self, *args, **kwargs):
    raise NotImplementedError()

  def send(self, *args, **kwargs):
    pass

  def receive(self, *args, **kwargs):
    pass

  def configure(self, *args, **kwargs):
    pass


class RedisProtocolBase(EndPointProtocolMeta):
  def __init__(self, *args, **kwargs):
    #TODO
    self.protocol = "redis"
    
  @EndPointProtocolMeta.protocol.setter
  def protocol(self, value):
    self._protocol = value

  def format_command(self, *args, **kwargs):
    command = kwargs.get("command", None)
    return command

  def parse_command(self, *args, **kwargs):
    command = kwargs.get("command", None)
    return command
  
  def parse_response(self, *args, **kwargs):
    command = kwargs.get("command", None)
    return command

  def format_response(self, *args, **kwargs):   
    command = kwargs.get("command", None)
    return command  

