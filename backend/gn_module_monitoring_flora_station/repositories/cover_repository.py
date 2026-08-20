from sqlalchemy import select

from geonature.utils.env import DB
from pypnnomenclature.models import TNomenclatures, BibNomenclaturesTypes

from ..models import MfsPlotSurveyStratum, MfsPlotSurveySubstrate


class CoverRepository:
    """
    Accès BDD pur pour le recouvrement (strates et substrats).
    """

    # Strates

    def get_strats_by_survey(self, id_plot_survey):
        return (
            DB.session.query(MfsPlotSurveyStratum)
            .filter_by(id_plot_survey=id_plot_survey)
            .all()
        )

    def save_stratum(self, stratum):
        DB.session.add(stratum)
        DB.session.commit()
        return stratum

    def get_stratum_list(self):
        query = select(TNomenclatures.label_default).join(
            BibNomenclaturesTypes, BibNomenclaturesTypes.id_type == TNomenclatures.id_type
        ).where(BibNomenclaturesTypes.mnemonique == "STRATE_VEGETATION_MFS")
        return DB.session.execute(query).all()

    # Substrats

    def get_substrates_by_survey(self, id_plot_survey):
        return (
            DB.session.query(MfsPlotSurveySubstrate)
            .filter_by(id_plot_survey=id_plot_survey)
            .all()
        )

    def save_substrate(self, substrate):
        DB.session.add(substrate)
        DB.session.commit()
        return substrate

    def get_substrate_list(self):
        query = select(TNomenclatures.label_default).join(
            BibNomenclaturesTypes, BibNomenclaturesTypes.id_type == TNomenclatures.id_type
        ).where(BibNomenclaturesTypes.mnemonique == "SUBSTRAT_PLACETTE")
        return DB.session.execute(query).all()