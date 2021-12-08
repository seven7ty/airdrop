"""
Certain values are stored as environment variables due to their added confidentiality (keys, tokens, etc).
This module provides a way to easily access values that are less sensitive (stored in resources/config.json),
and an alias to get the ENV ones as well.
"""

import os
import json
from dotenv import load_dotenv
from typing import Optional

__all__: tuple = ('CONFIG',)


class _Config:
    def __init__(self):
        self.lib_root = os.path.dirname(os.path.abspath(__file__))
        self.root_directory: str = self.lib_root[:self.lib_root.rindex(os.sep)]
        self.abi: list = json.load(open(os.path.join(self.root_directory, 'resources', 'token.abi')))
        self.raw_config: dict = {}
        load_dotenv()
        self._load_config()

    def _load_config(self):
        for filename in os.listdir(os.path.join(self.root_directory, 'resources/config')):
            if filename.endswith('.json'):
                with open(os.path.join(self.root_directory, f'resources/config/{filename}')) as fp:
                    raw_config_append: dict = json.load(fp)
                    for k, v in self.raw_config.items():
                        print(k)
                        if isinstance(v, str) and v.startswith('#'):
                            setattr(self, k, int(v[1:], 16))
                        else:
                            setattr(self, k, v)
                    self.raw_config.update(raw_config_append)

    def reload(self):
        self._load_config()

    def get(self, key: str) -> Optional[str]:
        return self.raw_config.get(key)

    def env(self, key: str) -> Optional[str]:
        return os.environ.get(key)


CONFIG: _Config = _Config()
