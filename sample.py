from pytile38.tilebase import Key, TilePointBase, Value


# Creating a custom serializer for Tile commnands
class Serializer:
    @classmethod
    def is_valid(cls, response):
        return response.result

    @classmethod
    def get(cls, instance=None, response=None, id=None, **kwargs):
        result = response.result
        fields = result[1] if (isinstance(result, list) and len(result) > 1) else None
        instance = instance()
        lat, lon = 0.0, 0.0
        if response.kwargs.get("withfields"):
            instance.fields = [tuple(fields[i : i + 2]) for i in range(0, len(fields), 2)]
            result = result[0]
        if response.kwargs.get("type") == "point":
            lon, lat = list(map(float, result))
        elif response.kwargs.get("type") is None:
            lon, lat = list(map(float, result.get("coordinates")))
        instance.lat = lat
        instance.lon = lon
        instance.id = id

        return instance

    @classmethod
    def ids(cls, response=None, **kwargs):
        data = response.result[1]
        result = []
        for d in data:
            name, _info = d[0:2]
            result.append(name)

        return result

    @classmethod
    def nearby(cls, response=None, **kwargs):
        data = response.result[1]
        result = []
        for d in data:
            name, info = d[0:2]
            lat, lon = info.get("coordinates")[::-1]
            coordinates = {"lat": lat, "long": lon}
            item = {"name": name, "coordinates": coordinates}
            result.append(item)

        return result


# Models can be directly queried
# either by creating the object and using Tile command
# or using class instance for manual querying
class Shop(TilePointBase):
    serializer = Serializer
    identifier = Key("shop")

    id = Value("")
    lat = Value(0.0)
    lon = Value(0.0)


class Customer(TilePointBase):
    serializer = Serializer
    identifier = Key("customer")

    id = Value("")
    lat = Value(0.0)
    lon = Value(0.0)


class CustomerNeighbours(TilePointBase):
    serializer = Serializer
    identifier = Key("shop")

    id = Value("")
    lat = Value(0.0)
    lon = Value(0.0)

    def set(self, **kwargs):
        raise NotImplementedError()

    # override default implementations
    def nearby(self, **kwargs):
        result = {}
        neighbours = super(CustomerNeighbours, self).nearby(**kwargs)
        myinfo = dict(self)
        result[myinfo.get("id")] = neighbours

        return result

    def geinfo(self):
        result = {}
        myinfo = dict(self)
        result["name"] = myinfo.get("id")
        result["coordinates"] = {"lat": myinfo.get("lat"), "long": myinfo.get("lon")}

        return result
