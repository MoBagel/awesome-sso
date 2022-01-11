import os
import tempfile

from fastapi import UploadFile


def test_bucket_creation(minio_store):
    buckets = minio_store.list_buckets()
    assert "test" in buckets


def test_fput(minio_store, test_string):
    with tempfile.NamedTemporaryFile() as file:
        file.write(test_string)
        file.flush()
        minio_store.fput(file.name, file.name)
    begotten = minio_store.get(file.name)
    assert minio_store.exists(file.name)
    assert begotten.read(len(test_string)) == test_string
    begotten.release_conn()

    with tempfile.TemporaryDirectory() as dir:
        with tempfile.NamedTemporaryFile(dir=dir) as file1:
            file1.write(test_string)
            file1.flush()
            with tempfile.NamedTemporaryFile(dir=dir) as file2:
                file_name2 = file2.name[1 + len(dir) :]
                file2.write(test_string)
                file2.flush()
                with tempfile.TemporaryDirectory(dir=dir) as tmp_dir:
                    minio_store.fput(dir, dir, exclude_files=[file_name2])

    assert minio_store.exists(file1.name)
    assert minio_store.exists(file2.name) is False


def test_put(minio_store, test_string):
    with tempfile.NamedTemporaryFile() as file:
        file.write(test_string)
        file.flush()
        file.seek(0)
        minio_store.put(file.name, file)
    begotten = minio_store.get(file.name)
    assert minio_store.exists(file.name)
    assert begotten.read(len(test_string)) == test_string
    begotten.release_conn()


def test_put_and_get_json(minio_store, test_dict):
    minio_store.put_as_json("dict.json", test_dict)
    assert minio_store.exists("dict.json")
    begotten = minio_store.get_json("dict.json")
    assert begotten["test_string"] == test_dict["test_string"]
    begotten = minio_store.get_json("non_exist.json")
    assert len(begotten) == 0


def test_put_get_and_download_df(minio_store, test_dataframe):
    minio_store.upload_df("test.csv", test_dataframe)
    df = minio_store.get_df("test.csv")
    assert df.shape[0] == 100
    df = minio_store.get_df("test.csv", date_column_list=["column_4_date"])
    assert df.shape[0] == 100
    df = minio_store.get_df("not_exist.csv", date_column_list=["column_4_date"])
    assert df is None

    minio_store.download("test.csv", "test.csv")
    assert os.path.exists("test.csv")
    os.remove("test.csv")


def test_remove_object_objects_and_dir(minio_store, test_dict):
    for i in range(3):
        minio_store.put_as_json(f"dict{i}.json", test_dict)
    minio_store.put_as_json("tmp/dict.json", test_dict)

    for i in range(3):
        assert minio_store.exists(f"dict{i}.json")
    assert minio_store.exists("tmp/dict.json")

    # test remove object
    minio_store.remove_object("dict0.json")
    assert minio_store.exists("dict0.json") is False

    # test remove objects
    minio_store.remove_objects(["dict1.json", "dict2.json", "dict3.json"])

    assert minio_store.exists("dict1.json") is False
    assert minio_store.exists("dict2.json") is False

    # test remove directory
    minio_store.remove_dir("tmp")
    assert minio_store.exists("tmp/dict.json") is False


async def test_fget_df(minio_store, test_dataframe):
    with tempfile.NamedTemporaryFile() as temp:
        test_dataframe.to_csv(temp.name, index=False)
        upload_file = UploadFile(temp.name, temp)
        df = minio_store.fget_df(upload_file)
        assert df.shape[0] == 100
        await upload_file.seek(0)
        df = minio_store.fget_df(upload_file, date_column="column_4_date")
        assert df.shape[0] == 100
        upload_file = UploadFile("non_exist")
        df = minio_store.fget_df(upload_file, date_column="column_4_date")
        assert df is None
