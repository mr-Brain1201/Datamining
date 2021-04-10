import datetime as dt
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

from sqlalchemy import Column, Integer, String, ForeignKey, Table, DateTime


Base = declarative_base()


class IdMixin:
    id = Column(Integer, primary_key=True, autoincrement=True)


class NameMixin:
    name = Column(String, nullable=False)


class UrlMixin:
    url = Column(String, nullable=False, unique=True)


tag_post = Table(
    "tags_posts",
    Base.metadata,
    Column("post_id", Integer, ForeignKey("posts.id")),
    Column("tag_id", Integer, ForeignKey("tags.id")),
)


class Post(Base, UrlMixin):
    __tablename__ = "posts"
    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    image_url = Column(String, nullable=False)
    date = Column(DateTime, nullable=False)
    writer_id = Column(Integer, ForeignKey("writers.id"))
    writer = relationship("Writer")
    tags = relationship("Tag", secondary=tag_post)
    comments = relationship("Comment")


class Writer(Base, IdMixin, NameMixin, UrlMixin):
    __tablename__ = "writers"
    posts = relationship("Post")


class Tag(Base, IdMixin, NameMixin, UrlMixin):
    __tablename__ = "tags"
    posts = relationship("Post", secondary=tag_post)


class Comment(Base):
    __tablename__ = "comments"
    id = Column(Integer, primary_key=True)
    parent_id = Column(Integer, ForeignKey("comments.id"), nullable=True)
    body = Column(String)
    created_at = Column(DateTime, nullable=False)
    writer_id = Column(Integer, ForeignKey("writers.id"))
    writer = relationship("Writer")
    post_id = Column(Integer, ForeignKey("posts.id"))

    def __init__(self, **kwargs):
        self.id = kwargs["id"]
        self.parent_id = kwargs["parent_id"]
        self.body = kwargs["body"]
        self.created_at = dt.datetime.fromisoformat(kwargs["created_at"])
        self.writer = kwargs["writers"]