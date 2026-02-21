import enum


class GenderEnum(str, enum.Enum):
    MALE = "Male"
    FEMALE = "Female"
    OTHER = "Other"

    @classmethod
    def _missing_(cls, value):
        if not isinstance(value, str):
            return None
        normalized = value.lower()
        mapping = {"m": cls.MALE, "male": cls.MALE, "f": cls.FEMALE, "female": cls.FEMALE, "other": cls.OTHER, "o": cls.OTHER}
        return mapping.get(normalized)