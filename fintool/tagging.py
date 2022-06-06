"""
This module provides a class to manage tags in the fintool db. Manage means to
create, retrieve, update and delete.
"""
import uuid

from fintool.db import DbFactory
from fintool.logging import LoggingHelper


class Error(Exception):
    """
    Base class for all errors in this module.
    """

class MissingTagArgumentError(Error):
    """
    Raised when trying to create a Tag instance and some required argument is
    missing.
    """

class InvalidTagObject(Error):
    """
    Raised when passing a non Tag instance to the transcation manager.
    """

class Tag:
    """
    A class to represent a tag-concept relationship. This type is useful for
    tagging transactions since we can keep track of corresponding tags for
    new transactions based in transaction's concept.
    """
    F_CONCEPT = 'concept'
    F_TAGS = 'tags'
    F_ID = 'id'

    def __init__(self, concept=None, tags_str=None, tag_id=None):
        """
        Initialize tag properties.
        """
        if not concept:
            raise MissingTagArgumentError(f'Missing {self.F_CONCEPT} arg')
        if not tags_str:
            raise MissingTagArgumentError(f'Missing {self.F_TAGS} arg')

        self.concept = concept
        self.tags = set(tags_str.split('|'))
        self.id = tag_id if tag_id else uuid.uuid4().hex

    def serialize(self):
        """
        Convert Tag instance into a dict instance.
        """
        return {
            self.F_ID: self.id,
            self.F_CONCEPT: self.concept,
            self.F_TAGS: '|'.join(self.tags)
        }

    def __str__(self):
        return f'{self.id}\t{self.concept}\t{self.tags}'


class TagManager:
    """
    A class to define the behavior of an object that knows how to manage
    transaction tags. That is create, delete, retrieve, and update tags. Also,
    the manager knows how to tag a transaction.
    """
    TAGS_COLLECTION = 'tags'

    def __init__(self):
        """
        Initialize tag manager.
        """
        self._db = DbFactory.get_db('csv')()
        self._logger = LoggingHelper.get_logger(self.__class__.__name__)
        self._tags = None

    @classmethod
    def create_tag(cls, data):
        """
        Create a Tag instance from a dict object.
        """
        return Tag(
            tag_id=data.get(Tag.F_ID, None),
            concept=data[Tag.F_CONCEPT],
            tags_str=data[Tag.F_TAGS]
        )

    def create_tag_list(self, dataset):
        """
        Convert dataset, which is a list of dicts, into a list of Tag
        instances.
        """
        return [self.create_tag(data) for data in dataset]

    def load_tags(self):
        """
        Load tags from db into memory.
        """
        self._tags = self.get_tags()

    def match_concpet(self, concept):
        """
        Return the corresponding tags for the given concept if exists,
        return None otherwise. It also loads the tags into memory to reduce
        I/O operations when performing multiple match operations using the same
        tag manager instance.
        """
        if not self._tags:
            self.load_tags()

        for tag in self._tags:
            if tag.concept == concept:
                return tag.tags

        return None

    def add_tag(self, tag):
        """
        Serialize a tag object and add it to tag db.
        """
        self._logger.debug('Adding tag to tag db')
        if not isinstance(tag, Tag):
            raise InvalidTagObject(f'Invalid tag object: {type(tag)}')
        self._db.add_record(tag.serialize(), self.TAGS_COLLECTION)

        # reload tags if already loaded into memory
        if self._tags:
            self.load_tags()

    def get_tag(self, id_value):
        """
        Return a specific tag from tags db.
        """
        self._logger.debug('Retrieving tag %s from tag db', id_value)
        for tag in self.get_tags():
            if tag.id == id_value:
                return tag
        return None

    def get_tags(self):
        """
        Retrieve all tags from tag db.
        """
        self._logger.debug('Retrieving tags from tag db')
        tags = self._db.get_records(self.TAGS_COLLECTION)
        return self.create_tag_list(tags)

    def update_tag(self, tag):
        """
        Update a tag record in db with the values provided by tag object.
        """
        self._logger.debug('Updating tag %s', tag.id)
        if not isinstance(tag, Tag):
            raise InvalidTagObject(f'Invalid tag object: {type(tag)}')
        self._db.edit_record(
            Tag.F_ID,
            tag.id,
            tag.serialize(),
            self.TAGS_COLLECTION
        )

        # reload tags if already loaded into memory
        if self._tags:
            self.load_tags()

    def delete_tag(self, tag):
        """
        Remove a tag from tags db.
        """
        self._logger.debug('Removing tag %s from db', tag.id)
        if not isinstance(tag, Tag):
            raise InvalidTagObject(f'Invalid tag object: {type(tag)}')
        self._db.remove_record(Tag.F_ID, tag.id, self.TAGS_COLLECTION)

        # reload tags if already loaded into memory
        if self._tags:
            self.load_tags()
