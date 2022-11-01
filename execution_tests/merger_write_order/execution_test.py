from pathlib import Path
import subprocess
import sys
import unittest

from spinedb_api import DatabaseMapping, from_database, import_functions


class MergerWriteOrder(unittest.TestCase):
    _root_path = Path(__file__).parent
    _source_database_1_path = _root_path / ".spinetoolbox" / "items" / "first_source" / "source 1.sqlite"
    _source_database_2_path = _root_path / ".spinetoolbox" / "items" / "second_source" / "source 2.sqlite"
    _sink_database_path = _root_path / ".spinetoolbox" / "items" / "sink" / "sink.sqlite"

    def setUp(self):
        source_paths = (self._source_database_1_path, self._source_database_2_path)
        for database_path in source_paths + (self._sink_database_path,):
            database_path.parent.mkdir(parents=True, exist_ok=True)
            if database_path.exists():
                database_path.unlink()
        spoon_volumes = {
            self._source_database_1_path: 1.0,
            self._source_database_2_path: 99.0
        }
        for database_path, spoon_volume in spoon_volumes.items():
            url = "sqlite:///" + str(database_path)
            db_map = DatabaseMapping(url, create=True)
            import_functions.import_object_classes(db_map, ("Widget",))
            import_functions.import_objects(db_map, (("Widget", "spoon"),))
            import_functions.import_object_parameters(db_map, (("Widget", "volume"),))
            import_functions.import_object_parameter_values(db_map, (("Widget", "spoon", "volume", spoon_volume, "Base"),))
            db_map.commit_session("Add test data.")
            db_map.connection.close()
        self._sink_url = "sqlite:///" + str(self._sink_database_path)
        db_map = DatabaseMapping(self._sink_url, create=True)
        db_map.connection.close()

    def test_execution(self):
        this_file = Path(__file__)
        completed = subprocess.run((sys.executable, "-m", "spinetoolbox", "--execute-only", str(this_file.parent)))
        self.assertEqual(completed.returncode, 0)
        db_map = DatabaseMapping(self._sink_url)
        value_rows = db_map.query(db_map.object_parameter_value_sq).all()
        self.assertEqual(len(value_rows), 1)
        self.assertEqual(value_rows[0].object_class_name, "Widget")
        self.assertEqual(value_rows[0].object_name, "spoon")
        self.assertEqual(value_rows[0].parameter_name, "volume")
        self.assertEqual(value_rows[0].alternative_name, "Base")
        self.assertEqual(from_database(value_rows[0].value, value_rows[0].type), 99.0)
        db_map.connection.close()


if __name__ == '__main__':
    unittest.main()
