from awesome_sso.store.minio import MinioStore
import tempfile
import json


ACCESS_KEY = 'minioadmin'
SECRET_KEY = 'minioadmin'
BUCKET = 'test'
HOST = 'localhost:9000'
test_string = b'to grasp how wide and long and high and deep is the love of Christ'

object_store = MinioStore(host=HOST, bucket=BUCKET, access_key=ACCESS_KEY, secret_key=SECRET_KEY)


def test_bucket_creation():
    buckets = object_store.client.list_buckets()
    assert 'test' in buckets
    object_store.client.remove_bucket('test')
    #  make sure bucket creation work on first time as well as on second time
    MinioStore(host=HOST, bucket=BUCKET, access_key=ACCESS_KEY, secret_key=SECRET_KEY)
    MinioStore(host=HOST, bucket=BUCKET, access_key=ACCESS_KEY, secret_key=SECRET_KEY)
    buckets = object_store.client.list_buckets()
    assert 'test' in buckets


def test_fput():
    with tempfile.NamedTemporaryFile() as file:
        file.write(test_string)
        file.flush()
        object_store.fput(file.name, file.name)
    begotten = object_store.get(file.name)
    assert object_store.exists(file.name)
    assert begotten.read(len(test_string)) == test_string
    begotten.release_conn()

    with tempfile.TemporaryDirectory() as dir:
        with tempfile.NamedTemporaryFile(dir=dir) as file:
            file.write(test_string)
            file.flush()
            object_store.fput(dir, dir)
    assert object_store.exists(file.name)


def test_put():
    with tempfile.NamedTemporaryFile() as file:
        file.write(test_string)
        file.flush()
        file.seek(0)
        object_store.put(file.name, file)
    begotten = object_store.get(file.name)
    assert object_store.exists(file.name)
    assert begotten.read(len(test_string)) == test_string
    begotten.release_conn()


def test_put_as_json():
    test_dict = {'test_string': test_string.decode('utf-8')}
    object_store.put_as_json('dict.json', test_dict)
    assert object_store.exists('dict.json')
    begotten = object_store.get('dict.json')
    begotten_dict = json.load(begotten)
    assert begotten_dict['test_string'] == test_dict['test_string']
    begotten.release_conn()


def test_remove_object_and_dir():
    test_dict = {'test_string': test_string.decode('utf-8')}
    object_store.put_as_json('dict.json', test_dict)
    object_store.put_as_json('tmp/dict.json', test_dict)
    assert object_store.exists('dict.json')
    assert object_store.exists('tmp/dict.json')
    object_store.remove_object('dict.json')
    assert object_store.exists('dict.json') is False
    object_store.remove_dir('tmp')
    assert object_store.exists('tmp/dict.json') is False
