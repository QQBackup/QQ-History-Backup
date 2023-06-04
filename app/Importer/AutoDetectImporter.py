from app.i18n import t
from .ImporterManager import ImporterManager

@ImporterManager.register
class AutoDetectImporter:
    pretty_name: str = "importer.auto_detect"
    def __new__(cls, *args, **kwargs):
        possible_list = []
        for i in ImporterManager.all_importer_list:
            possible_list.append((i, i.detect_possibility_of_import(*args, **kwargs)))
        possible_list.sort(key=lambda x: x[1], reverse=True)
        possible_list = [i for i in possible_list if i[1] > 0]
        if len(possible_list) == 0:
            raise ValueError(
                t("importer.auto_detect.failed").format(possible_list=possible_list)
            )
