import os
import pickle
import pytest

from mydb import MyDB


def describe_MyDB():
    def describe___init__():
        def it_creates_file_if_missing(tmp_path):
            db_path = tmp_path / "test_data.dat"
            assert not db_path.exists()

            db = MyDB(str(db_path))

            assert db_path.exists()
            # Verify empty persistent state via public API
            assert db.loadStrings() == []

        def it_preserves_existing_file_contents(tmp_path):
            db_path = tmp_path / "test_data.dat"
            initial_data = ["alpha", "beta"]
            # Pre-populate file to simulate existing database
            with open(db_path, "wb") as f:
                pickle.dump(initial_data, f)

            db = MyDB(str(db_path))

            assert db_path.exists()
            assert db.loadStrings() == initial_data

    def describe_saveStrings():
        def it_overwrites_existing_content(tmp_path):
            db_path = tmp_path / "db.dat"
            db = MyDB(str(db_path))

            first = ["one", "two"]
            second = ["red", "blue"]

            db.saveStrings(first)
            db.saveStrings(second)

            assert db.loadStrings() == second

        def it_persists_across_reopen(tmp_path):
            db_path = tmp_path / "db.dat"
            db = MyDB(str(db_path))

            data = ["persist", "me"]
            db.saveStrings(data)

            # Reopen a new instance and verify persistence
            db2 = MyDB(str(db_path))
            assert db2.loadStrings() == data

    def describe_loadStrings():
        def it_returns_empty_list_for_new_db(tmp_path):
            db_path = tmp_path / "empty.dat"
            db = MyDB(str(db_path))

            assert db.loadStrings() == []

        def it_reads_prepopulated_data(tmp_path):
            db_path = tmp_path / "pre.dat"
            expected = ["a", "b", "c"]
            with open(db_path, "wb") as f:
                pickle.dump(expected, f)

            db = MyDB(str(db_path))
            assert db.loadStrings() == expected

    def describe_saveString():
        def it_appends_one_item(tmp_path):
            db_path = tmp_path / "append.dat"
            db = MyDB(str(db_path))

            db.saveStrings(["start"])
            db.saveString("next")

            assert db.loadStrings() == ["start", "next"]

        def it_appends_in_order_over_multiple_calls(tmp_path):
            db_path = tmp_path / "append_many.dat"
            db = MyDB(str(db_path))

            values = ["a", "b", "c", "d"]
            for value in values:
                db.saveString(value)

            assert db.loadStrings() == values
