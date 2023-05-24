class AutoDetectImporter:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._importers = []

    def add_importer(self, importer):
        self._importers.append(importer)

    def import_file(self, file_path):
        for importer in self._importers:
            if importer.can_import(file_path):
                return importer.import_file(file_path)
        raise Exception('No importer found for file: {}'.format(file_path))