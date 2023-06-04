from ..BaseImporter import BaseImporter
from ..ImporterManager import ImporterManager
from ..AndroidQq import AndroidQq

@ImporterManager.register
class AndroidTim(AndroidQq):
    pretty_name = "importer.android_tim"
    tim_mode = True
