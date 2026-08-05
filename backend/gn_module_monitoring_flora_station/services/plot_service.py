from werkzeug.exceptions import NotFound

from ..repositories.plot_repository import PlotRepository


class PlotService:
    """
    Règles métier pour les placettes et sous-mailles.
    """

    def __init__(self, plot_repo=None):
        self.plot_repo = plot_repo or PlotRepository()

    def get_plot(self, id_plot):
        return self.plot_repo.get_by_id(id_plot)

    def list_plots_by_transect(self, id_transect):
        return self.plot_repo.get_by_transect(id_transect)

    def update_plot(self, plot):
        return self.plot_repo.merge(plot)

    def delete_plot(self, id_plot):
        plot = self.plot_repo.get_by_id(id_plot)
        if plot is None:
            raise ValueError(f"Placette {id_plot} introuvable")
        children = self.plot_repo.get_children(id_plot)
        if children:
            raise ValueError(
                f"Impossible de supprimer la placette {id_plot} : elle a des sous-mailles rattachées"
            )
        self.plot_repo.delete(plot)

    def get_plot_depth(self, id_parent):
        depth = 1
        current_id = id_parent
        while current_id is not None:
            parent = self.plot_repo.get_by_id(current_id)
            if parent is None:
                break
            current_id = parent.id_parent
            depth += 1
        return depth

    def build_hierarchy(self, plots, parent_id=None):
        sub_plots = [p for p in plots if p.id_parent == parent_id]
        if not sub_plots:
            return []
        result = []
        for plot in sub_plots:
            plot_dict = plot.as_dict()
            plot_dict["sub_plots"] = self.build_hierarchy(plots, parent_id=plot.id_plot)
            result.append(plot_dict)
        return result

    def create_plot(self, plot_data, max_plot_depth):
        from ..models import MfsPlot

        sub_plots = plot_data.pop("sub_plots", [])
        plot_data.pop("temp_id", None)

        transect = self.plot_repo.get_transect_by_id(plot_data.get("id_transect"))
        if transect is None:
            raise NotFound(f"Transect {plot_data.get('id_transect')} does not exist")

        if plot_data.get("id_parent"):
            parent_plot = self.plot_repo.get_by_id(plot_data.get("id_parent"))
            if parent_plot is None:
                raise NotFound("Parent plot not found")
            if parent_plot.id_transect != plot_data.get("id_transect"):
                raise ValueError("Parent plot does not belong to the same transect")
            depth = self.get_plot_depth(plot_data.get("id_parent"))
            if depth > max_plot_depth:
                raise ValueError(f"La profondeur maximale de {max_plot_depth} niveaux est atteinte")

        plot = MfsPlot(**plot_data)
        self.plot_repo.save(plot)

        for sub_plot_data in sub_plots:
            sub_plot_data["id_parent"] = plot.id_plot
            sub_plot_data["id_transect"] = plot.id_transect
            self.create_plot(sub_plot_data, max_plot_depth)

        return plot