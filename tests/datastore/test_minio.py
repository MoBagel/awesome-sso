import json
import tempfile


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


def test_put_as_json(minio_store, test_dict):
    minio_store.put_as_json('dict.json', test_dict)
    assert minio_store.exists('dict.json')
    begotten = minio_store.get('dict.json')
    begotten_dict = json.load(begotten)
    assert begotten_dict['test_string'] == test_dict['test_string']
    begotten.release_conn()


def test_remove_object_and_dir(minio_store, test_dict):
    minio_store.put_as_json('dict.json', test_dict)
    minio_store.put_as_json('tmp/dict.json', test_dict)
    assert minio_store.exists('dict.json')
    assert minio_store.exists('tmp/dict.json')
    minio_store.remove_object('dict.json')
    assert minio_store.exists('dict.json') is False
    minio_store.remove_dir('tmp')
    assert minio_store.exists('tmp/dict.json') is False
