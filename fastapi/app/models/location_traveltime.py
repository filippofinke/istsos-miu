from .database import Base, SCHEMA_NAME
from sqlalchemy.sql.schema import Column
from sqlalchemy.sql.sqltypes import Integer, Text, String
from sqlalchemy.inspection import inspect
from sqlalchemy.dialects.postgresql.json import JSON
from sqlalchemy.dialects.postgresql.ranges import TSTZRANGE
from geoalchemy2 import Geometry

class LocationTravelTime(Base):
    __tablename__ = 'Location_traveltime'
    __table_args__ = {'schema': SCHEMA_NAME}
    
    id = Column(Integer, primary_key=True)
    self_link = Column("@iot.selfLink", Text)
    things_navigation_link = Column("Things@iot.navigationLink", Text)
    historical_locations_navigation_link = Column("HistoricalLocations@iot.navigationLink", Text)
    name = Column(String(255), unique=True, nullable=False)
    description = Column(Text, nullable=False)
    encoding_type = Column("encodingType", String(100), nullable=False)
    location = Column(Geometry(geometry_type='GEOMETRY', srid=4326), nullable=False)
    location_geojson = Column(JSON)
    properties = Column(JSON)
    system_time_validity = Column(TSTZRANGE)

    def _serialize_columns(self):
        """Serialize model columns to a dict, applying naming transformations."""
        rename_map = {
            "id": "@iot.id",
            "self_link": "@iot.selfLink",
            "things_navigation_link": "Things@iot.navigationLink",
            "historical_locations_navigation_link": "HistoricalLocations@iot.navigationLink",
            "encoding_type": "encodingType",
        }
        serialized_data = {
            rename_map.get(column.key, column.key): getattr(self, column.key)
            for column in self.__class__.__mapper__.column_attrs
            if column.key not in inspect(self).unloaded
        }
        if 'location' in serialized_data and self.location is not None:
            serialized_data['location'] = self.location_geojson
            serialized_data.pop('location_geojson', None)
        return serialized_data

    def to_dict_expand(self):
        """Serialize the LocationTravelTime model to a dict, excluding 'system_time_validity'."""
        data = self._serialize_columns()
        data.pop('system_time_validity', None)
        return data