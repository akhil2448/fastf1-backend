from .wake_profiles import WAKE_PROFILES


class WakeProfileService:

    def get_profile(
        self,
        season: int,
    ):

        return WAKE_PROFILES[season]