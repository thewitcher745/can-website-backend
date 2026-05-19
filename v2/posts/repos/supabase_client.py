import os
from typing import Any, cast
import httpx
from supabase import ClientOptions, create_client
from dotenv import dotenv_values

from ..utils.exceptions import StorageError


class SupabaseClient:
    def __init__(self):
        self.url = self._get_supabase_url()
        self.key = self._get_supabase_key()

        options = ClientOptions()

        proxy = dotenv_values(".env.local").get("HTTP_PROXY", None)
        if proxy is not None:
            httpx_client = httpx.Client(proxy=proxy)
            options = ClientOptions(httpx_client=httpx_client)

        self._client = create_client(self.url, self.key, options)

    @staticmethod
    def _get_supabase_url() -> str:
        url = os.environ.get("NEXT_PUBLIC_SUPABASE_URL")

        if not url:
            raise RuntimeError("NEXT_PUBLIC_SUPABASE_URL is not set")

        return url.rstrip("/")

    @staticmethod
    def _get_supabase_key() -> str:
        key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")

        if not key:
            raise RuntimeError("Supabase key is not set")

        return key

    def list_filenames(self, bucket_name: str, folder: str) -> list[str]:
        """
        Returns a list of filenames in the given Supabase bucket and folder.

        Args:
            bucket_name: Name of the bucket
            folder: Folder name within bucket

        Returns:
            List of filenames in the given bucket and folder.
        """
        try:
            filenames = [
                item["name"]
                for item in self._client.storage.from_(bucket_name).list(path=folder)
                if item["name"].endswith(".json")
            ]

            return filenames

        except Exception as e:
            raise StorageError(f"Error listing files in bucket: {e}")

    def download_file(self, bucket_name: str, folder: str, filename: str) -> bytes:
        """
        Downloads a JSON
        Args:
            bucket_name: Name of the bucket
            folder: Folder name within bucket
            filename: name of the file to download with the .json extension

        Returns:
            The JSON file contents parsed to a dict
        """
        file_path = f"{folder}/{filename}"

        try:
            data = self._client.storage.from_(bucket_name).download(file_path)

            return data

        except httpx.ConnectError as e:
            raise StorageError(f"Connection error: {e}") from e

        except httpx.ReadTimeout:
            raise TimeoutError("Connection to Supabase timed out.")

        except Exception as e:
            error_str = str(e)

            if "'statusCode': 404" in error_str or "not_found" in error_str.lower():
                raise FileNotFoundError(f"File not found: {file_path}")

            raise StorageError(f"Error downloading file {file_path}: {e}")

    def upload_file(
        self, bucket_name: str, folder: str, filename: str, data: bytes
    ) -> None:
        """
        Upload a file to Supabase storage.

        Args:
            bucket_name: Name of the bucket
            folder: Destination folder within bucket
            filename: Name of the destination file
            data: File contents as bytes
        """
        file_path = f"{folder}/{filename}"

        try:
            self._client.storage.from_(bucket_name).upload(
                file_path,
                data,
                file_options={"content-type": "application/json", "upsert": "true"},
            )

        except httpx.ConnectError as e:
            raise StorageError(f"Connection error: {e}") from e

        except httpx.ReadTimeout:
            raise TimeoutError("Connection to Supabase timed out.")

        except Exception as e:
            raise StorageError(f"Error uploading file {file_path}: {e}")

    def delete_file(self, bucket_name: str, folder: str, filename: str) -> None:
        """
        Deletes a file on Supabase.

        Args:
            bucket_name: Name of the bucket
            folder: Destination folder within bucket
            filename: Name of the destination file
        """
        file_path = f"{folder}/{filename}"

        try:
            self._client.storage.from_(bucket_name).remove(
                [file_path],
            )

        except httpx.ConnectError as e:
            raise StorageError(f"Connection error: {e}") from e

        except httpx.ReadTimeout:
            raise TimeoutError("Connection to Supabase timed out.")

        except Exception as e:
            raise StorageError(f"Error deleting file {file_path}: {e}")

    def db_select(
        self,
        table: str,
        filters: dict[str, Any] | None = None,
        limit: int | None = None,
    ) -> list[dict[str, Any]]:
        """Generic SELECT query."""
        query = self._client.table(table).select("*")
        if filters:
            for key, value in filters.items():
                query = query.eq(key, value)

        if limit is not None:
            query = query.limit(limit)

        result = query.execute()

        return cast(list[dict[str, Any]], result.data)

    def db_insert(self, table: str, data: dict[str, Any]) -> None:
        """Generic INSERT."""
        self._client.table(table).insert(data).execute()

    def db_upsert(
        self, table: str, data: dict[str, Any], conflict_column: str = "id"
    ) -> None:
        """Generic UPSERT (insert or update)."""
        self._client.table(table).upsert(data, on_conflict=conflict_column).execute()

    def db_update(
        self, table: str, data: dict[str, Any], filters: dict[str, Any]
    ) -> None:
        """Generic UPDATE with filters."""
        query = self._client.table(table).update(data)

        for key, value in filters.items():
            query = query.eq(key, value)

        query.execute()

    def db_delete(self, table: str, filters: dict[str, Any]) -> None:
        """Generic DELETE with filters."""
        query = self._client.table(table).delete()

        for key, value in filters.items():
            query = query.eq(key, value)

        query.execute()
