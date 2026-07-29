from sqlalchemy import select, func

from geonature.utils.env import DB

from ..models import SfsSensor, SfsTransect


class SensorRepository:
    """
    Accès BDD pur pour les capteurs.
    """

    def get_by_id(self, id_sensor):
        return DB.session.get(SfsSensor, id_sensor)

    def get_sensor_detail(self, id_sensor):
        return DB.session.execute(
            select(SfsSensor, SfsTransect.transect_label)
            .filter_by(id_sensor=id_sensor)
            .outerjoin(SfsTransect, SfsSensor.id_transect == SfsTransect.id_transect)
        ).first()

    def get_by_transect_query(self, id_transect):
        return select(SfsSensor).filter_by(id_transect=id_transect)

    def count(self, query):
        return DB.session.scalar(select(func.count("*")).select_from(query))

    def save(self, sensor):
        DB.session.add(sensor)
        DB.session.commit()
        return sensor

    def merge(self, sensor):
        merged = DB.session.merge(sensor)
        DB.session.commit()
        return merged

    def delete(self, sensor):
        DB.session.delete(sensor)
        DB.session.commit()