import glob
import json
from io import BytesIO, StringIO
from logging import Logger
from os import path
from pathlib import Path
from typing import IO, List, Optional

import pandas as pd
from fastapi import UploadFile
from fastapi.logger import logger
from minio import Minio, S3Error
from minio.deleteobjects import DeleteObject

from awesome_sso.exceptions import UnprocessableEntity


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

    def list_buckets(self):
        """List information of all accessible buckets with text."""
        return [x.name for x in self.client.list_buckets()]

    def list_objects(self, prefix: str = None, recursive: bool = False):
        """Lists object information of a bucket with text."""
        return [
            x.object_name
            for x in self.client.list_objects(
                self.bucket, prefix=prefix, recursive=recursive
            )
        ]

    def fput(self, name: str, file_path: str, exclude_files: List[str] = []):
        """Uploads data from a file/folder to an object in a bucket."""
        if path.isdir(file_path):
            for local_file in glob.glob(file_path + "/**"):
                file_name = Path(local_file).name
                remote_path = path.join(name, file_name)

                if file_name in exclude_files:
                    self.logger.info(f"exclude: {local_file}")
                    continue

                if not path.isfile(local_file):
                    self.fput(remote_path, local_file, exclude_files)
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
        """Uploads data from a stream to an object in a bucket."""
        if not length:
            length = len(data.read())
            data.seek(0)

        self.client.put_object(
            self.bucket, name, data, length, content_type=content_type
        )

    def put_as_json(self, name: str, data: dict):
        """Uploads data from a json to an object in a bucket."""
        data_bytes = json.dumps(data).encode("utf-8")
        data_byte_stream = BytesIO(data_bytes)

        self.put(name, data_byte_stream, content_type="application/json")

    def get(self, name: str):
        """Gets data of an object."""
        return self.client.get_object(self.bucket, name)

    def exists(self, name: str) -> bool:
        """Check if object or bucket exist."""
        try:
            self.client.stat_object(self.bucket, name)
            return True
        except Exception:
            return False

    def remove_dir(self, folder: str):
        """Remove folder."""
        self.logger.warning("removing %s", folder)
        objects_to_delete = self.list_objects(prefix=folder, recursive=True)
        self.logger.warning("Removing: %s", objects_to_delete)
        self.remove_objects(objects_to_delete)

    def remove_object(self, name: str):
        """Remove an object."""
        self.client.remove_object(self.bucket, name)

    def upload_df(self, name: str, data: pd.DataFrame):
        """Uploads data from a pandas dataframe to an object in a bucket."""
        data_bytes = data.to_csv(index=False).encode("utf-8")
        data_byte_stream = BytesIO(data_bytes)

        self.put(name, data_byte_stream, content_type="application/csv")

    def fget_df(
        self,
        file: UploadFile,
        column_types: dict = {},
        date_columns: List[str] = [],
    ) -> Optional[pd.DataFrame]:
        try:
            file_io = StringIO(str(file.file.read(), "utf-8"))
            df = pd.read_csv(file_io, dtype=column_types, parse_dates=date_columns)
            file_io.close()
        except Exception as e:
            self.logger.warning(UnprocessableEntity("unable to read csv %s" % str(e)))
            return None
        return df

    def get_json(self, name: str) -> dict:
        """Gets data of an object and return a json."""
        try:
            file_obj = self.get(name)
        except S3Error as e:
            self.logger.warning(e)
            return {}
        result = json.load(file_obj)
        file_obj.close()
        file_obj.release_conn()
        return result

    def get_df(
        self,
        name: str,
        column_types: dict = {},
        date_columns: List[str] = [],
    ) -> Optional[pd.DataFrame]:
        """Gets data of an object and return a dataframe."""
        try:
            file_obj = self.get(name)
        except S3Error as e:
            self.logger.warning(e)
            return None

        if not date_columns:
            df = pd.read_csv(file_obj, dtype=column_types)
        else:
            df = pd.read_csv(file_obj, parse_dates=date_columns, dtype=column_types)
        file_obj.close()
        file_obj.release_conn()
        return df

    def remove_objects(self, names: list):
        """Remove objects."""
        objects_to_delete = [DeleteObject(name) for name in names]
        for del_err in self.client.remove_objects(self.bucket, objects_to_delete):
            self.logger.warning("Deletion Error: %s", del_err)

    def download(self, name: str, file_path: str):
        """Downloads data of an object to file."""
        self.client.fget_object(self.bucket, name, file_path)
