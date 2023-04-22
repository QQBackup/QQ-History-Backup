import json
import os
import app.Config
import app.HistoryBackup as HB
filename = 'code_by_json_config.json'
if not os.path.exists(filename):
    print(f'Config file {filename} not found')
    exit()
config_json = json.load(open(filename, encoding='utf-8'))
config = Config()
config.load(config_json)
HB(config).run()

