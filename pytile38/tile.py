from .redisbase import (
  RedisEndPoint,
  RedisConnectionBase,
  Echo,
  Must,
  Optional,
  Conditional,
  OptionalKVPairs,
  OptionalCondition,
  Flag,
  AttrType)

from credis import Connection as CRedisConnection
import json
import six

class ConnectionManager(object):
  connection = None

  @classmethod
  def get(cls):
    if cls.connection == None:
      cls.connection = SimpleConnection()
    return cls.connection

class TileInstance(object):
  _instance = None

  @classmethod
  def get(cls):
    if cls._instance == None:
      cls._instance = Tile()
    return cls._instance

class SimpleConnection(RedisConnectionBase):
  def __init__(self, *args, **kwargs):
    kwargs.setdefault("port", 9851)
    kwargs.setdefault("connection", CRedisConnection)
    super(SimpleConnection, self).__init__(*args, **kwargs)

  def setup(self, *args, **kwargs):
    host, port = (self.host, self.port)
    authentication = kwargs.get("authentication", None)     
    connection = self.connection
    try:
      connection = connection(host=host, port=port)
    except:
      raise
    finally:
      self.connection = connection

  def send(self, *args, **kwargs):
    #TODO
    # handle exceptions
    data = self.serialize(kwargs.get("data"))
    result = self.connection.execute(*data)
    return self.deserialize(result)

  def serialize(self, arg):
    return arg

  def _traverse(self, item):
    if isinstance(item, list):
      transform = [self._traverse(i) for i in item]
    elif isinstance(item, bytes):
      value = item.decode()
      try:
        value = json.loads(value)
      except:
        pass
      return value
    else:
      return item

    return transform

  def deserialize(self, arg):
    #TODO
    if not arg:
      return
    if isinstance(arg, list):
      return self._traverse(arg)
    if isinstance(arg, (dict, int, float, complex)):
      return arg
    arg = arg.decode()
    if arg == "OK":
      return True
    elif arg == "ERR":
      return False
    result = json.loads(arg)

    return result

class TileBase(RedisEndPoint):
  def __init__(self, *args, **kwargs):
    super(TileBase, self).__init__(*args, **kwargs)
    self.connection = SimpleConnection()
    
  def setup(self, *args, **kwargs):
    pass
  
  def send(self, *args, **kwargs):
    result = None
    cmdname, command = kwargs.get("command")
    action = self.commands.get(cmdname, None)
    if action == None:
      raise ValueError("Empty command") #TODO, create exceptions and refactor these
    try:
      result = action(command)
    except Exception: # !
      raise
    finally:
      return result

class Tile(TileBase):
  def __init__(self, *args, **kwargs):
    super(Tile, self).__init__(*args, **kwargs)
    
  def setup(self, *args, **kwargs):
    self.commands = Tile.get_commands()

  @classmethod
  def get_commands(cls):
    commands = {
      "get": {
        "scheme": [Must("key"), Must("id"), Flag("withfields"), OptionalCondition("type")],
        "scheme:point": [Echo("type")],
        "scheme:object": [Echo("type")],
        "scheme:bounds": [Echo("type")],
        "scheme:hash": [Echo("type"), Must("percision")]
      },
      "scan": {
        "scheme": [Must("key")],
      },
      "set": {
        "scheme": [Must("key"), Must("id"), OptionalKVPairs("fields"), OptionalCondition("ex"), Must("type"), Conditional("type")],
        "scheme:point": [Must("lat"), Must("lon"), Optional("z")],
        "scheme:string": [Must("value")],
        "scheme:bounds": [Must("minlat"), Must("minlon"), Must("maxlat"), Must("maxlon")],
        "scheme:_ex": [Flag("ex"), Must("ex"), Flag("nx"), Flag("xx")]
      },
      "nearby": {
        "scheme": [Must("key"), Must("type"), Conditional("type")],
        "scheme:point": [Must("lat"), Must("lon"), Must("radius")]
      },
      "ttl": {
        "scheme": [Must("key"), Must("id")]
      },
      "expire": {
        "scheme": [Must("key"), Must("id"), Must("kttl")]
      },
      "fset": {
        "scheme": [Must("key"), Must("id"), Must("fkey"), Must("fvalue")]
      },
      "del": {
        "scheme": [Must("key"), Must("id")]
      },
      "drop": {
        "scheme": [Must("key")]
      },
      "persist": {
        "scheme": [Must("key"), Must("id")]
      }
    }

    return commands
