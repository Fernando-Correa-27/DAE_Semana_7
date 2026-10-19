"""Model-level tests: relations, the explicit through model and validation."""
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.test import TestCase

from blog.models import ArticleTag, Author, Category, Comment, Post, Profile, Tag


class AuthorProfileTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user("ana", password="x")

    def test_author_links_to_a_login_account(self):
        author = Author.objects.create(name="Ana", user=self.user)
        self.assertEqual(self.user.author, author)
        self.assertEqual(author.user, self.user)

    def test_deleting_the_user_keeps_the_author(self):
        Author.objects.create(name="Ana", user=self.user)
        self.user.delete()
        self.assertTrue(Author.objects.filter(name="Ana").exists())
        self.assertIsNone(Author.objects.get(name="Ana").user)

    def test_profile_is_one_to_one_with_author(self):
        author = Author.objects.create(name="Ana")
        profile = Profile.objects.create(author=author, country="Peru")
        self.assertEqual(author.profile, profile)


class ArticleTagThroughTests(TestCase):
    def setUp(self):
        self.author = Author.objects.create(name="Ana")
        self.post = Post.objects.create(title="Hola", author=self.author)
        self.tag = Tag.objects.create(name="django")

    def test_post_and_tag_share_the_through_rows(self):
        link = ArticleTag.objects.create(article=self.post, tag=self.tag)
        self.assertIn(self.tag, self.post.tags.all())
        self.assertIn(self.post, self.tag.posts.all())
        self.assertEqual(link.added_at is not None, True)

    def test_duplicate_pair_is_rejected(self):
        ArticleTag.objects.create(article=self.post, tag=self.tag)
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                ArticleTag.objects.create(article=self.post, tag=self.tag)

    def test_deleting_the_post_removes_its_links(self):
        ArticleTag.objects.create(article=self.post, tag=self.tag)
        self.post.delete()
        self.assertEqual(ArticleTag.objects.count(), 0)
        self.assertTrue(Tag.objects.filter(pk=self.tag.pk).exists())


class CommentValidationTests(TestCase):
    def setUp(self):
        self.author = Author.objects.create(name="Ana")
        self.post = Post.objects.create(title="Hola", author=self.author)

    def test_blank_text_is_invalid(self):
        comment = Comment(post=self.post, author_name="Ana", text="   ")
        with self.assertRaises(ValidationError):
            comment.full_clean()

    def test_valid_comment_passes_validation(self):
        comment = Comment(post=self.post, author_name="Ana", text="Buen post")
        comment.full_clean()
        comment.save()
        self.assertEqual(self.post.comments.count(), 1)


class CategoryDeletionTests(TestCase):
    def test_deleting_a_category_keeps_the_post(self):
        category = Category.objects.create(name="Noticias")
        author = Author.objects.create(name="Ana")
        post = Post.objects.create(title="Hola", author=author, category=category)
        category.delete()
        post.refresh_from_db()
        self.assertIsNone(post.category)
