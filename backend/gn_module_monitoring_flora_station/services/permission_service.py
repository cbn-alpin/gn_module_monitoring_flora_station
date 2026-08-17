from pypnusershub.db.tools import InsufficientRightsError
from pypnusershub.db.models import User
from geonature.utils.env import DB


class PermissionService:
    """
    Règles de droits d'accès (CRUVED) sur les visites.
    """

    def check_user_cruved_visit(self, user, visit, cruved_level):
        """
        Vérifie si l'utilisateur a le droit d'agir sur une visite selon son niveau CRUVED.
        Lève une erreur 403 si non autorisé.
        """
        is_allowed = False

        if cruved_level == "1":
            for role in visit.observers:
                if role.id_role == user.id_role:
                    is_allowed = True
                    break
            if not is_allowed and visit.id_digitiser == user.id_role:
                is_allowed = True
            if not is_allowed:
                raise InsufficientRightsError(
                    f'User "{user.id_role}" cannot update visit number {visit.id_base_visit}',
                    403,
                )

        elif cruved_level == "2":
            for role in visit.observers:
                if role.id_role == user.id_role:
                    is_allowed = True
                    break
                elif role.id_organisme == user.id_organisme:
                    is_allowed = True
                    break
            if not is_allowed and visit.id_digitiser == user.id_role:
                is_allowed = True
            if not is_allowed and visit.id_digitiser:
                digitiser = DB.session.get(User, visit.id_digitiser)
                if digitiser and digitiser.id_organisme == user.id_organisme:
                    is_allowed = True
            if not is_allowed:
                raise InsufficientRightsError(
                    f'User "{user.id_role}" cannot update visit number {visit.id_base_visit}',
                    403,
                )

    def check_user_cruved_transect(self, user, transect, cruved_level, digitiser=None):
        """
        Vérifie si l'utilisateur a le droit de modifier un transect selon son niveau CRUVED.
        Lève une erreur 403 si non autorisé.
        """
        is_allowed = False

        if cruved_level == "1":
            if transect.t_base_site.id_digitiser == user.id_role:
                is_allowed = True

        elif cruved_level == "2":
            if transect.t_base_site.id_digitiser == user.id_role:
                is_allowed = True
            elif digitiser and digitiser.id_organisme == user.id_organisme:
                is_allowed = True

        elif cruved_level == "3":
            is_allowed = True

        if not is_allowed:
            raise InsufficientRightsError(
                f'User "{user.id_role}" cannot update transect number {transect.id_transect}',
                403,
            )