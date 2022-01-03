import json
import tempfile

from fastapi import UploadFile


def test_bucket_creation(minio_store):
    buckets = minio_store.client.list_buckets()
    assert 'test' in buckets


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
        with tempfile.NamedTemporaryFile(dir=dir) as file:
            file.write(test_string)
            file.flush()
            minio_store.fput(dir, dir)
    assert minio_store.exists(file.name)


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
    minio_store.put_as_json('dict.json', test_dict)
    assert minio_store.exists('dict.json')
    begotten = minio_store.get_json('dict.json')
    assert begotten['test_string'] == test_dict['test_string']
    begotten = minio_store.get_json('non_exist.json')
    assert len(begotten) == 0


def test_remove_object_and_dir(minio_store, test_dict):
    minio_store.put_as_json('dict.json', test_dict)
    minio_store.put_as_json('tmp/dict.json', test_dict)
    assert minio_store.exists('dict.json')
    assert minio_store.exists('tmp/dict.json')
    minio_store.remove_object('dict.json')
    assert minio_store.exists('dict.json') is False
    minio_store.remove_dir('tmp')
    assert minio_store.exists('tmp/dict.json') is False


def test_upload_and_get_df(minio_store, test_dataframe):
    minio_store.upload_df(test_dataframe, "test.csv")
    df = minio_store.get_df("test.csv")
    assert df.shape[0] == 100
    df = minio_store.get_df("test.csv", date_column="column_4_date")
    assert df.shape[0] == 100
    df = minio_store.get_df("not_exist.csv", date_column="column_4_date")
    assert df is None


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
