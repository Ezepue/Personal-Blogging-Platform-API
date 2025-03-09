import enum

# User roles
class UserRole(enum.Enum):
    SUPER_ADMIN = "super_admin"
    ADMIN = "admin"
    AUTHOR = "author"
    READER = "reader"

    def __str__(self):
        return self.value  # Ensures proper string conversion

# Article status
class ArticleStatus(enum.Enum):
    DRAFT = "draft"
    PUBLISHED = "published"
    DELETED = "deleted"

    def __str__(self):
        return self.value  # Ensures proper string conversion
