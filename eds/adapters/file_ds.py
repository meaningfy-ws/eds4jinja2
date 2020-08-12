"""
file_ds.py
Date:  07/08/2020
Author: Eugeniu Costetchi
Email: costezki.eugen@gmail.com 
"""
import json
import pathlib
import yaml
import toml
import pandas as pd

from eds.adapters.base_data_source import DataSource, UnsupportedRepresentation

TABULAR_EXTENSIONS = [".csv", ".tsv", ".xlsx", ".xls", ]
TREE_EXTENSIONS = [".json", ".yaml", ".yml", ".toml", ".json-ld", ".jsonld"]


class FileDataSource(DataSource):
    """

    """

    def __init__(self, file_path):
        self.file_path = pathlib.Path(file_path)

    def _file_extension(self):
        return str(self.file_path.suffix).lower()

    def _can_be_tree(self) -> bool:
        return self._file_extension() in TREE_EXTENSIONS

    def _can_be_tabular(self) -> bool:
        return self._file_extension() in TABULAR_EXTENSIONS

    def _fetch_tree(self):
        if self._file_extension() in [".json", ".json-ld", ".jsonld"]:
            return json.loads(self.file_path.read_bytes())
        elif self._file_extension() in [".yaml", ".yml"]:
            return yaml.load(self.file_path.read_bytes())
        elif self._file_extension() in [".toml"]:
            return toml.loads(self.file_path.read_bytes())
        raise UnsupportedRepresentation(f"Unsupported tree file type: {self._file_extension()}")

    def _fetch_tabular(self):
        if self._file_extension() in [".csv", ]:
            return pd.read_csv(self.file_path)
        elif self._file_extension() in [".xlsx", ".xls"]:
            return pd.read_excel(self.file_path)
        elif self._file_extension() in [".tsv", ]:
            return pd.read_table(self.file_path)
        raise UnsupportedRepresentation(f"Unsupported tabular file type: {self._file_extension()}")
