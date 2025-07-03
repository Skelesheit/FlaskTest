from enum import StrEnum

class UserType(StrEnum):
    Individual = 'Физ. лицо'
    LegalEntity = 'ИП'
    LegalEntityProfile = 'Юр. лицо'