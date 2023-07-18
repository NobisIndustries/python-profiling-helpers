from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional, Tuple, Union


class BaseFileSaver(ABC):
    @abstractmethod
    def save_profile(self, profile_binary: bytes, profile_file_name: str) -> None:
        """
        This method gets the bytes content of the profile file you want to save somewhere
        and the suggested file name. You can implement your own logic in a child class that
        saves the profile on the target you want.
        """
        raise NotImplementedError()


class LocalFileSaver(BaseFileSaver):
    def __init__(self, save_dir: Union[str, Path]):
        """
        Saves a file to a local dir.
        """
        save_dir = Path(save_dir)
        save_dir.mkdir(exist_ok=True, parents=True)
        self._save_dir = save_dir

    def save_profile(self, profile_binary: bytes, profile_file_name: str) -> None:
        save_path = Path(self._save_dir, profile_file_name)
        save_path.write_bytes(profile_binary)
        print(f"Profile saved at {save_path.as_posix()}")


class S3FileSaver(BaseFileSaver):
    def __init__(
        self, s3_save_dir: str, kms_key_id: Optional[str] = None, **kwargs
    ) -> None:
        """
        Uploads profile files to an S3 bucket. Additional keyword arguments are given to the boto3
        S3 client initialization.

        :param s3_save_dir: The base path of the file you want to upload, e.g. "s3://my-bucket/my/path/to/profiles/"
        :param kms_key_id: If your target bucket is encrypted with a KMS key, you can provide its ID here.
        """
        super().__init__()
        try:
            import boto3
        except ImportError:
            raise ImportError(
                "You do not have the optional dependencies installed to upload your profiles to an "
                "S3 bucket. Please install these with `pip install profiling-helpers[aws]`"
            )

        self._s3 = boto3.client("s3", **kwargs)
        self._s3_bucket, self._s3_prefix = self._split_s3_path(s3_save_dir)
        self._kms_key_id = kms_key_id

    @classmethod
    def _split_s3_path(cls, s3_path: str) -> Tuple[str, str]:
        # Normally we would use .removeprefix(), but we support Python 3.7 which doesn't have that yet
        if s3_path.startswith("s3://"):
            s3_path = s3_path[5:]
        s3_path = s3_path.rstrip("/")
        bucket_name, prefix = s3_path.split("/", 1)
        return bucket_name, prefix

    def save_profile(self, profile_binary: bytes, profile_file_name: str) -> None:
        save_key = f"{self._s3_prefix}/{profile_file_name}"
        extra_args = {}
        if self._kms_key_id:
            extra_args.update(
                {"ServerSideEncryption": "aws:kms", "SSEKMSKeyId": self._kms_key_id}
            )
        self._s3.put_object(
            Body=profile_binary, Bucket=self._s3_bucket, Key=save_key, **extra_args
        )
        print(f"Profile uploaded to s3://{self._s3_bucket}/{save_key}")
