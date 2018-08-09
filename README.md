# pytile38

Simple python client for [Tile38](https://github.com/tidwall/tile38).
Currently, only a subset of commands are supported. However, you can manually add new commands by defining a scheme ( look at tile.py ).

Commands are built from instance properties or keyword arguments, therefore each command only requires missing attributes. 

# Models

Each model instance represents an entry in Tile38.

```python
    class Shop(TilePointBase):
        serializer = Serializer
        identifier = Key("shop")
	
        id = Value("")
        lat = Value(0.0)
        lon = Value(0.0)
```

Serializer is responsible for serializing/parsing data ( both for class methods and instance methods ).

```python
	class Serializer(object):
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
				instance.fields = [tuple(fields[i:i+2]) for i in range(0, len(fields), 2)]
				result = result[0]
			if response.kwargs.get("type") == "point":
				lon, lat = list(map(float, result))			
			elif response.kwargs.get("type") == None:
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
				name, info = d[0:2]
				name = name
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
				item = {"name":name, "coordinates": coordinates}
				result.append(item)

			return result

```

# Example

```python
    shop1 = Shop.create(lat=45.02695, lon=-77.431641, id="modula")
    shop1.set(type="point") # alternatively, you can add this property to Shop class

    shop2 = Shop.create(lat=43.516689, lon=-74.794922, id="bellissimo", type="point")
    shop2.set(type="point")

    shop3 = Shop.create(lat=51.835778, 
                        lon=9.931641,
                        id="metzgereiinübereinstimmungmitrindfleischetikettierungsüberwachungsaufgabenübertragungsgesetz",
                        type="point",
                        fields=[('hat_gelesen', 0),('agb_seiten', 100000000), ('wird_im_x_tagen_gesendet', 3900), ('oh_neue_agb', 1), ('neu_dazukommende_agb_seiten', 19590713256714671346890), ('kunde_muss_nochmal_bestätigen', 1)])
    shop3.set(type="point", ex=60) # set expiration


    shop4 = Shop.get(id="metzgereiinübereinstimmungmitrindfleischetikettierungsüberwachungsaufgabenübertragungsgesetz", withfields=True) # get point with associated fields

    shop4.fields
    >>> [('agb_seiten', 100000000), ('kunde_muss_nochmal_bestätigen', 1), ('neu_dazukommende_agb_seiten', 19590713256714670000000), ('oh_neue_agb', 1), ('wird_im_x_tagen_gesendet', 3900)]

    shop4.lat = 33.33
    shop4.set(type="point") # update this point with new data
    dict(shop4)
    >>> {'lat': 33.33, 'lon': 9.931641, 'id': 'metzgereiinübereinstimmungmitrindfleischetikettierungsüberwachungsaufgabenübertragungsgesetz'}

    # check ttl
    shop3.ttl().result
    >>> 59

    # remove expiration
    shop3.persist().result 
    >>> True

    Shop.ids()
    # >>> ['modula', 'bellissimo', 'metzgereiinübereinstimmungmitrindfleischetikettierungsüberwachungsaufgabenübertragungsgesetz']    
```

#### dependencies
- [credis](https://github.com/yihuang/credis) ( requires Cython )
