import enum

# User roles
class UserRole(enum.Enum):
    super_admin = "super_admin"
    admin = "admin"
    author = "author"
    reader = "reader"

# Article status
class ArticleStatus(enum.Enum):
    DRAFT = "draft"
    PUBLISHED = "published"
    DELETED = "deleted"