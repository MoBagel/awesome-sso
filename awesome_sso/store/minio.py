import glob
import io
import json
from logging import Logger
from os import path
from typing import IO, Optional

from minio import Minio
from minio.deleteobjects import DeleteObject


class MinioStore:
    bucket: str
    client: Minio
    logger: Logger

    def __init__(
        self,
        host: str,
        bucket: str,
        access_key: str,
        secret_key: str,
        secure: bool = False,
        logger: Optional[Logger] = None,
    ):
        self.bucket = bucket
        self.client = Minio(
            host, access_key=access_key, secret_key=secret_key, secure=secure
        )
        self.logger = logger if logger is not None else Logger("minio")
        found = self.client.bucket_exists(self.bucket)
        if not found:
            self.logger.warning("bucket not exist, creating it")
            self.client.make_bucket(self.bucket)
        else:
            self.logger.info("bucket '%s' exists", self.bucket)

    def fput(self, name: str, file_path: str):
        if path.isdir(file_path):
            for local_file in glob.glob(file_path + "/**"):
                if not path.isfile(local_file):
                    self.fput(local_file, name + "/" + path.basename(local_file))
                else:
                    remote_path = path.join(name, local_file[1 + len(file_path) :])
                    self.client.fput_object(self.bucket, remote_path, local_file)
        else:
            self.client.fput_object(self.bucket, name, file_path)

    def put(
        self,
        name: str,
        data: IO,
        length: Optional[int] = None,
        content_type: str = "application/octet-stream",
    ):
        if not length:
            length = len(data.read())
            data.seek(0)
        self.client.put_object(
            self.bucket, name, data, length, content_type=content_type
        )

    def put_as_json(self, name: str, data: dict):
        data_json = json.dumps(data)
        data_bytes = data_json.encode("utf-8")
        data_byte_stream = io.BytesIO(data_bytes)
        length = len(data_byte_stream.read())
        data_byte_stream.seek(0)
        self.client.put_object(
            self.bucket, name, data_byte_stream, length, content_type="application/json"
        )

    def get(self, name: str):
        return self.client.get_object(self.bucket, name)

    def exists(self, name: str) -> bool:
        try:
            self.client.stat_object(self.bucket, name)
            return True
        except Exception:
            return False

    def remove_dir(self, folder: str):
        self.logger.warning("removing %s", folder)
        objects_to_delete = self.client.list_objects(
            self.bucket, prefix=folder, recursive=True
        )
        object_names_to_delete = [x.object_name for x in objects_to_delete]
        delete_objects = [DeleteObject(name) for name in object_names_to_delete]
        self.logger.warning("Removing: %s", object_names_to_delete)
        for del_err in self.client.remove_objects(self.bucket, delete_objects):
            self.logger.warning("Deletion Error: %s", del_err)

    def remove_object(self, name: str):
        self.client.remove_object(self.bucket, name)
