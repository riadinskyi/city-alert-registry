from enum import Enum


class TerritorialOrganization(str, Enum):
    """
    Всі можливі варіанти для групування
    """

    OBLAST = "oblast"
    RAION = "raion"
    HROMADA = "hromada"
    CITY = "city"
