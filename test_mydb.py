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

        def it_handles_filename_with_spaces(tmp_path):
            # Test edge case: filename with spaces
            db_path = tmp_path / "test file with spaces.dat"
            db = MyDB(str(db_path))
            
            assert db_path.exists()
            assert db.loadStrings() == []

        def it_handles_filename_with_special_characters(tmp_path):
            # Test boundary case: filename with special characters
            db_path = tmp_path / "test-db_123.dat"
            db = MyDB(str(db_path))
            
            assert db_path.exists()
            assert db.loadStrings() == []

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

        def it_handles_empty_list(tmp_path):
            # Test edge case: saving empty list
            db_path = tmp_path / "empty_list.dat"
            db = MyDB(str(db_path))

            db.saveStrings([])
            assert db.loadStrings() == []

        def it_handles_large_dataset(tmp_path):
            # Test boundary case: large number of strings
            db_path = tmp_path / "large_data.dat"
            db = MyDB(str(db_path))

            large_data = [f"item_{i}" for i in range(1000)]
            db.saveStrings(large_data)
            assert db.loadStrings() == large_data

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

        def it_handles_strings_with_special_characters(tmp_path):
            # Test edge case: strings with special characters
            db_path = tmp_path / "special.dat"
            special_data = ["hello\nworld", "test\tvalue", "path/to/file", "unicode: 你好"]
            with open(db_path, "wb") as f:
                pickle.dump(special_data, f)

            db = MyDB(str(db_path))
            assert db.loadStrings() == special_data

        def it_handles_very_long_strings(tmp_path):
            # Test boundary case: very long individual strings
            db_path = tmp_path / "long_strings.dat"
            long_string = "x" * 10000  # 10KB string
            long_data = [long_string, "normal", long_string]
            with open(db_path, "wb") as f:
                pickle.dump(long_data, f)

            db = MyDB(str(db_path))
            assert db.loadStrings() == long_data

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

        def it_handles_empty_string(tmp_path):
            # Test edge case: appending empty string
            db_path = tmp_path / "empty_string.dat"
            db = MyDB(str(db_path))

            db.saveStrings(["start"])
            db.saveString("")
            db.saveString("end")

            assert db.loadStrings() == ["start", "", "end"]

        def it_handles_strings_with_whitespace_and_special_chars(tmp_path):
            # Test boundary case: strings with various whitespace and special characters
            db_path = tmp_path / "whitespace.dat"
            db = MyDB(str(db_path))

            special_strings = ["  leading spaces", "trailing spaces  ", "\t\ntabs and newlines\n\t", "mixed\t\nchars"]
            for s in special_strings:
                db.saveString(s)

            assert db.loadStrings() == special_strings
