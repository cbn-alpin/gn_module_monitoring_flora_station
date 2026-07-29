from ..repositories.cover_repository import CoverRepository


class CoverService:
    """
    Règles métier pour le recouvrement (strates et substrats).
    """

    def __init__(self, cover_repo=None):
        self.cover_repo = cover_repo or CoverRepository()

    def list_strata(self, id_plot_survey):
        return self.cover_repo.get_strats_by_survey(id_plot_survey)

    def add_stratum(self, stratum):
        return self.cover_repo.save_stratum(stratum)

    def list_stratum_options(self):
        return [str(row[0]) for row in self.cover_repo.get_stratum_list()]

    def list_substrates(self, id_plot_survey):
        return self.cover_repo.get_substrates_by_survey(id_plot_survey)

    def add_substrate(self, substrate):
        return self.cover_repo.save_substrate(substrate)

    def list_substrate_options(self):
        return [str(row[0]) for row in self.cover_repo.get_substrate_list()]