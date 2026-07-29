from geonature.utils.env import DB

from ..repositories.sensor_repository import SensorRepository


class SensorService:
    """
    Règles métier pour les capteurs.
    """

    def __init__(self, sensor_repo=None):
        self.sensor_repo = sensor_repo or SensorRepository()

    def get_sensor(self, id_sensor):
        return self.sensor_repo.get_by_id(id_sensor)

    def build_sensor_detail(self, id_sensor):
        data = self.sensor_repo.get_sensor_detail(id_sensor)
        if not data:
            return None
        sensor = data[0].as_dict()
        if data[1]:
            sensor["transect_label"] = str(data[1])
        return sensor

    def list_sensors_by_transect(self, id_transect, items_per_page):
        query = self.sensor_repo.get_by_transect_query(id_transect)
        total_items = self.sensor_repo.count(query)
        data = DB.session.scalars(query).unique().all()

        page_info = {
            "totalItems": total_items,
            "itemsPerPage": items_per_page,
        }
        if data:
            return [page_info, [d.as_dict() for d in data]]
        return None

    def create_sensor(self, sensor_data):
        from ..models import SfsSensor

        sensor = SfsSensor(**sensor_data)
        return self.sensor_repo.save(sensor)

    def update_sensor(self, sensor):
        return self.sensor_repo.merge(sensor)

    def delete_sensor(self, id_sensor):
        sensor = self.sensor_repo.get_by_id(id_sensor)
        if sensor is None:
            raise ValueError(f"Capteur {id_sensor} introuvable")
        self.sensor_repo.delete(sensor)