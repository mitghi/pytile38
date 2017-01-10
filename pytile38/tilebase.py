from inspect import (
  isfunction,
  isdatadescriptor,
  isclass
)

from .tile import Tile

from .redisbase import (
  Optional,
  Must,
  Conditional,
  AttrType
)

import json

class Key(AttrType):
  pass

class Value(AttrType):
  pass

class DynamicValue(AttrType):
  pass
  
def get_members(clsdict):
  result = {"methods": [], "properties": [], "other": []} 
  for k, v in clsdict.items():
    if isfunction(v):
      result.get("methods").append(k)
    elif isdatadescriptor(v):
      result.get("properties").append(k)
    elif not isclass(v):
      result.get("other").append(k)

  return result
    
class MT(type):
  def __new__(mcs, name, bases, attrs, *kw):
    newtype = type.__new__(mcs, name, bases, attrs)
    if not bases:
      return newtype
    args = get_members(attrs)
    properties = list(
      filter(lambda i: not i.startswith("__"), args.get("properties"))
    )
    other = list(
      filter(lambda i: not i.startswith("__"), args.get("other"))
    )
    key = None
    attributes = []
    found_key = False
    attr_map = []
    for k in other:
      v = attrs.get(k)      
      if found_key == False:
        is_key = isinstance(v, Key)
        if is_key:
          found_key = True
          key = (k, v)
          continue
      attributes.append((k, v))
    else:
      if found_key:
        newtype.key = key[1]
        newtype.key_identifier = key[0]
    newtype.__fields__ = {"properties": properties, "other": other}

    return newtype

class It(metaclass=MT):
  # TODO
  def __iter__(self):
    identifier = self.key_identifier    
    for key in self.__fields__["other"]:
      if key == identifier:
        continue
      yield key, getattr(self, key)
    for key in self.__fields__["properties"]:
      if key == identifier:
        continue
      yield key, getattr(self, key)
  
class TilePointSerializer(object):
  @classmethod
  def is_valid(cls, response):
    if response.result:
      return True
    return False

  @classmethod
  def get(cls, instance=None, response=None, id=None, **kwargs):
    result = response.result
    fields = result[1] if (isinstance(result, list) and len(result) > 1) else None
    instance = instance()
    lat, lon = 0.0, 0.0
    if response.kwargs.get("withfields"):
      instance.fields = fields
      result = result[0]
    if response.kwargs.get("type") == "point":
      lat, lon = list(map(float, result))     
    elif response.kwargs.get("type") == None:
      lat, lon = list(map(float, result.get("coordinates")))
    instance.lat = lat
    instance.lon = lon
    instance.id = id
    
    return instance
  
  @classmethod
  def ids(cls, response=None, **kwargs):
    data = response.result[1]
    result = []
    for d in data:
      name, info = d[0:2]
      result.append(name)

    return result

class TilePointBase(It):
  tile = Tile()

  def dispatch_command(self, command=None, **kwargs):
    alias = ( kwargs.get("alias", None) and kwargs.pop("alias") ) or None
    instance = self
    result = self.tile.dispatch(command=command, instance=instance,  **kwargs)
    is_valid = self.serializer.is_valid(result)
    if not is_valid: # TODO
      return         # execute callback instead
    if hasattr(self.serializer, alias or command):
      serializer_action = getattr(self.serializer, alias or command)
      return serializer_action(instance=instance, response=result, **kwargs)
  
    return result

  @classmethod
  def create(cls, *args, **kwargs):
    instance = cls()
    for k, v in kwargs.items():
      setattr(instance, k, v)
    return instance

  @classmethod
  def get(cls, **kwargs):
    kwargs.setdefault("command", "get")
    return cls.dispatch_command(cls, **kwargs)

  def set(self, **kwargs):
    kwargs.setdefault("command", "set")
    return self.dispatch_command(**kwargs)
  
  @classmethod
  def ids(cls, **kwargs):
    kwargs.setdefault("command", "scan")
    kwargs.setdefault("alias", "ids")
    return cls.dispatch_command(cls, **kwargs)

  def nearby(self, **kwargs):
    kwargs.setdefault("command", "nearby")
    return self.dispatch_command(**kwargs)

  @classmethod
  def drop(cls, **kwargs):
    kwargs.setdefault("command", "drop")    
    return cls.dispatch_command(cls, **kwargs)

  @classmethod
  def create(cls, *args, **kwargs):
    instance = cls()
    for k, v in kwargs.items():
      setattr(instance, k, v)
    return instance     

  def ttl(self, **kwargs):
    kwargs.setdefault("command", "ttl")
    return self.dispatch_command(**kwargs)
    
  def expire(self, **kwargs):
    kwargs.setdefault("command", "expire")
    return self.dispatch_command(**kwargs)
  
  def fset(self, **kwargs):
    kwargs.setdefault("command", "fset")
    return self.dispatch_command(**kwargs)

  def delete(self, **kwargs):
    kwargs.setdefault("command", "del")
    return self.dispatch_command(**kwargs)

  def persist(self, **kwargs):
    kwargs.setdefault("command", "persist")
    return self.dispatch_command(**kwargs)
