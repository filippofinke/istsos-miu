from .database import Base, SCHEMA_NAME
from sqlalchemy.sql.schema import Column, PrimaryKeyConstraint
from sqlalchemy.sql.sqltypes import Integer, Text, String
from sqlalchemy.inspection import inspect
from sqlalchemy.dialects.postgresql.json import JSON
from sqlalchemy.dialects.postgresql.ranges import TSTZRANGE
from geoalchemy2 import Geometry

class FeaturesOfInterestTravelTime(Base):
    __tablename__ = 'FeaturesOfInterest_traveltime'

    id = Column(Integer)
    self_link = Column("@iot.selfLink", Text)
    observation_navigation_link = Column("Observations@iot.navigationLink", Text)
    name = Column(String(255), nullable=False)
    description = Column(String(255), nullable=False)
    encoding_type = Column("encodingType", String(100), nullable=False)
    feature = Column(Geometry(geometry_type='GEOMETRY', srid=4326), nullable=False)
    feature_geojson = Column(JSON)
    properties = Column(JSON)
    system_time_validity = Column(TSTZRANGE)

    __table_args__ = (PrimaryKeyConstraint(id, system_time_validity), {'schema': SCHEMA_NAME })
    
    def _serialize_columns(self):
        """Serialize model columns to a dict, applying naming transformations."""
        rename_map = {
            "id": "@iot.id",
            "self_link": "@iot.selfLink",
            "observation_navigation_link": "Observations@iot.navigationLink",
            "encoding_type": "encodingType",
        }
        serialized_data = {
            rename_map.get(attr.key, attr.key): getattr(self, attr.key)
            for attr in self.__class__.__mapper__.column_attrs
            if attr.key not in inspect(self).unloaded
        }
        if 'feature' in serialized_data:
            if self.feature is not None:
                serialized_data['feature'] = self.feature_geojson
            serialized_data.pop('feature_geojson', None)
        if 'system_time_validity' in serialized_data and self.system_time_validity is not None:
            serialized_data['system_time_validity'] = self._format_datetime_range(self.system_time_validity)
        return serialized_data

    def to_dict_expand(self):
        """Serialize the FeaturesOfInterestTravelTime model to a dict, excluding 'system_time_validity'."""
        return self._serialize_columns()

    def _format_datetime_range(self, range_obj):
        if range_obj:
            lower = getattr(range_obj, 'lower', None)
            upper = getattr(range_obj, 'upper', None)
            return f"{lower.isoformat()}/{upper.isoformat()}"
        return None