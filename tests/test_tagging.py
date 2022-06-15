"""
Set of unit tests for the tagging module.
"""
import unittest
import pathlib

from fintool.tagging import Tag, TagManager
from fintool.db import CsvDb

class TestTagging(unittest.TestCase):
    """
    A set of tests to validate tagging mechanism and tag management.
    """

    @classmethod
    def setUpClass(cls):
        cls.DB_DIR = pathlib.Path('~/.fintool').expanduser()
        cls.TAGS_FILE = cls.DB_DIR.joinpath("tags.csv")
        cls.SAMPLE_TAGS = [
            Tag(concept='a', tags_str='a|b|c'),
            Tag(concept='b', tags_str='b|c|d'),
            Tag(concept='c', tags_str='c|d|e')
        ]

    def setUp(self):
        """
        Clean database on each test execution.
        """
        try:
            for f in self.DB_DIR.glob("*"):
                f.unlink()

            self.DB_DIR.rmdir()
        except FileNotFoundError:
            pass  # db doesn't exists
        self.tag_manager = TagManager()

    def add_tags(self, tags):
        """
        Add tags to db.
        """
        for tag in tags:
            self.tag_manager.add_tag(tag)

    def match_tags(self, tag_a, tag_b, ignore_id=False):
        """
        Match tag fields but id.
        """
        if ignore_id:
            return tag_a.concept == tag_b.concept and tag_a.tags == tag_b.tags

        return tag_a.concept == tag_b.concept and \
                tag_a.tags == tag_b.tags and \
                tag_a.id == tag_b.id

    def test_create_tag(self):
        """
        Make sure that TagManager creates a Tag instance from a dict.
        """
        expected = Tag(concept='a', tags_str='a|b|c', tag_id=None)
        data = {'concept': 'a', 'tags': 'a|b|c'}
        actual = TagManager.create_tag(data)
        self.assertTrue(
            self.match_tags(actual, expected, ignore_id=True),
            'tags not equal'
        )


    def test_create_tag_list(self):
        """
        Make sure that TagManager creates a list of Tag instances from a list
        of dicts.
        """
        expected = self.SAMPLE_TAGS
        data = [
            {'concept': 'a', 'tags': 'a|b|c'},
            {'concept': 'b', 'tags': 'b|c|d'},
            {'concept': 'c', 'tags': 'c|d|e'}
        ]
        actual = self.tag_manager.create_tag_list(data)

        for i, tag in enumerate(actual):
            self.assertTrue(
                self.match_tags(tag, expected[i], ignore_id=True),
                'tags not equal'
            )

    def test_add_tag(self):
        """
        Make sure that TagManager can add tags to db.
        """
        tag = Tag(concept='a', tags_str='a|b|c')
        expected = tag.serialize()
        self.tag_manager.add_tag(tag)
        db = CsvDb()
        actual = db.get_records('tags')

        self.assertTrue(len(actual) == 1)
        self.assertTrue(actual[0] == expected)

    def test_delete_tag(self):
        """
        Make sure that TagManager can delete tags from the db.
        """
        tag = Tag(concept='a', tags_str='a|b|c')
        self.tag_manager.add_tag(tag)
        self.tag_manager.delete_tag(tag.id)
        tags = self.tag_manager.get_tags()
        self.assertEqual(len(tags), 0)

    def test_get_tag(self):
        """
        Make sure that TagManager can retrieve a specific tag from db.
        """
        expected = self.SAMPLE_TAGS
        self.add_tags(expected)
        actual = self.tag_manager.get_tag(expected[2].id)
        self.assertIsNotNone(actual)
        self.assertTrue(self.match_tags(
            actual,
            expected[2]
        ), 'tags not equal')

    def test_get_tags(self):
        """
        Make sure that TagManager can retrieve all tags from db.
        """
        expected = self.SAMPLE_TAGS
        self.add_tags(self.SAMPLE_TAGS)
        actual = self.tag_manager.get_tags()
        self.assertEqual(len(actual), len(expected))
        for a, e in zip(actual, expected):
            self.assertTrue(self.match_tags(a, e), 'tags not equal')

    def test_update_tag(self):
        """
        Make sure that TagManager can update a tag in db.
        """
        expected = Tag(concept='a', tags_str='a|b|c')
        self.tag_manager.add_tag(expected)
        expected.concept = 'abcd'
        expected.tags = set(['1','2','3'])
        self.tag_manager.update_tag(expected)
        actual = self.tag_manager.get_tag(expected.id)
        self.assertIsNotNone(actual)
        self.assertTrue(self.match_tags(actual, expected), 'tags not equal')

    def test_match_concept(self):
        """
        Make sure that TagManager can return the corresponding set of tags
        for a given concept if a matching record exists.
        """
        expected = set(['c', 'd', 'e'])
        self.add_tags(self.SAMPLE_TAGS)
        actual = self.tag_manager.match_concpet(self.SAMPLE_TAGS[2].concept)

        self.assertEqual(actual, expected)

    def test_match_concept_no_match(self):
        """
        Make sure that TagManager returns None when there is no tag matching
        the given concept.
        """
        expected = None
        self.add_tags(self.SAMPLE_TAGS)
        actual = self.tag_manager.match_concpet('d')

        self.assertEqual(actual, expected)
