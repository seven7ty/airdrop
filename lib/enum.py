import enum as lib_enum

__all__: tuple = ('AirDropInteractionType',)


class AirDropInteractionType(lib_enum.Enum):
    JOIN: str = 'airdrop_join'
