import pytest

from tests.users.models import Profile
from tests.users.models import User


class TestSource:
    def test_full_name_from_method(self):
        user = User(first_name="john", last_name="smith")
        assert user.full_name_from_method == "john smith"

    def test_username_from_attr(self):
        user = User(first_name="john", last_name="smith")
        profile = Profile(username="jsmith")
        user.profile = profile
        assert user.username_from_attr == "jsmith"

    def test_username_from_attr_no_default(self):
        user = User(first_name="john", last_name="smith")
        assert user.username_from_attr is None

    def test_username_from_callable(self):
        user = User(first_name="john", last_name="smith")
        profile = Profile(username="jsmith")
        user.profile = profile
        assert user.username_from_callable is "jsmith"

    def test_username_with_default(self):
        user = User(first_name="john", last_name="smith")
        assert user.username_with_default is ""


class TestAnnotatableFieldsManager:
    @pytest.mark.django_db
    def test_annotate_fields_by_name(self):
        user = User.objects.create(first_name="john", last_name="smith")
        assert user.full_name_from_annotate == "from source"
        user = User.objects.annotate_fields("full_name_from_annotate").get()
        assert user._full_name_from_annotate == "from annotate"
        assert user.full_name_from_annotate == "from annotate"

    @pytest.mark.django_db
    def test_annotate_fields_by_exclude(self):
        User.objects.create(first_name="john", last_name="smith")
        user = User.objects.annotate_fields(exclude=["full_name_from_method"]).get()
        assert hasattr(user, "_full_name_from_method") is False
