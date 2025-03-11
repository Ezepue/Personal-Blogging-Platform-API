import enum
from database import Base
from enum import Enum

# User roles
class UserRole(enum.Enum):
    SUPER_ADMIN = "SUPER_ADMIN"
    ADMIN = "ADMIN"
    AUTHOR = "AUTHOR"
    READER = "READER"


    def __str__(self):
        return self.value

    def __repr__(self):
        return f"<UserRole.{self.name}: {self.value}>"

    @classmethod
    def to_dict(cls):
        """Returns a dictionary of roles for easy serialization."""
        return {role.value: role.name for role in cls}

    @classmethod
    def from_str(cls, role_str):
        """Convert a string to a UserRole enum, or raise ValueError if invalid."""
        try:
            return cls(role_str)
        except ValueError:
            raise ValueError(f"Invalid role: {role_str}. Choose from {list(cls.to_dict().keys())}")
        
class NotificationType(str, Enum):
    LIKE = "like"
    COMMENT = "comment"
    SYSTEM = "system"
    FOLLOW = "follow"
    MENTION = "mention"

# Article status
class ArticleStatus(enum.Enum):
    DRAFT = "draft"
    PUBLISHED = "published"
    DELETED = "deleted"

    def __str__(self):
        return self.value

    def __repr__(self):
        return f"<ArticleStatus.{self.name}: {self.value}>"

    @classmethod
    def to_dict(cls):
        """Returns a dictionary of statuses for easy serialization."""
        return {status.value: status.name for status in cls}

    @classmethod
    def from_str(cls, status_str):
        """Convert a string to an ArticleStatus enum, or raise ValueError if invalid."""
        try:
            return cls(status_str)
        except ValueError:
            raise ValueError(f"Invalid status: {status_str}. Choose from {list(cls.to_dict().keys())}")
