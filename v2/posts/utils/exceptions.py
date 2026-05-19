class StorageError(Exception):
    """Base exception for storage operations."""

    pass


class RepoError(Exception):
    """Base exception for repository operations."""

    pass


class PostNotFoundError(Exception):
    pass


class SlugConflictError(Exception):
    pass


class PublishedAtError(Exception):
    pass


class SlugImmutableError(Exception):
    pass
