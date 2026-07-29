from pypnusershub.db.tools import InsufficientRightsError


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
                elif visit.id_digitiser == user.id_role:
                    is_allowed = True
                    break
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
                elif visit.id_digitiser == user.id_role:
                    is_allowed = True
                    break
                elif role.id_organisme == user.id_organisme:
                    is_allowed = True
                    break
            if not is_allowed:
                raise InsufficientRightsError(
                    f'User "{user.id_role}" cannot update visit number {visit.id_base_visit}',
                    403,
                )