from geonature.utils.env import DB

from ..models import SfsPlot, SfsTransect


class PlotRepository:
    """
    Accès BDD pur pour les placettes et sous-mailles.
    """

    def get_by_id(self, id_plot):
        return DB.session.get(SfsPlot, id_plot)

    def get_by_transect(self, id_transect):
        return DB.session.query(SfsPlot).filter_by(id_transect=id_transect).all()

    def get_children(self, id_plot):
        return DB.session.query(SfsPlot).filter_by(id_parent=id_plot).all()

    def get_transect_by_id(self, id_transect):
        return DB.session.get(SfsTransect, id_transect)

    def save(self, plot):
        DB.session.add(plot)
        DB.session.flush()
        return plot

    def merge(self, plot):
        merged = DB.session.merge(plot)
        DB.session.commit()
        return merged

    def delete(self, plot):
        DB.session.delete(plot)
        DB.session.commit()