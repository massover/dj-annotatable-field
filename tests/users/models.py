# from django.db import models
# from django.db.models import Count
# from django.db.models import F
# from django.db.models import TextField
# from django.db.models import Value as V
# from django.db.models.functions import Coalesce
# from django.db.models.functions import Concat
#
# from dj_annotatable_field import AnnotatableField
# from dj_annotatable_field import AnnotatableFieldsManager
#
#
# class Cat(models.Model):
#     name = models.TextField()
#     owner = models.OneToOneField("dogs.Owner", on_delete=models.DO_NOTHING)
#
#
# class Owner(models.Model):
#     first_name = models.TextField()
#     last_name = models.TextField()
#     dogs_count = AnnotatableField(Count("dogs"), source=lambda obj: obj.dogs.count())
#     full_name = AnnotatableField(
#         Concat("first_name", V(" "), "last_name", output_field=TextField())
#     )
#
#     custom_annotation_name = AnnotatableField(
#         Count("dogs"),
#         source=lambda obj: obj.dogs.count(),
#         annotation_name="_custom_dogs_count",
#     )
#     cat_name = AnnotatableField(F("cat__name"), source="cat.name")
#
#     objects = AnnotatableFieldsManager()
#
#     @full_name.source
#     def full_name_source(self):
#         return f"{self.first_name} {self.last_name}"
#
#
# class Dog(models.Model):
#     name = models.TextField()
#     owner = models.ForeignKey(
#         Owner, on_delete=models.DO_NOTHING, related_name="dogs", null=True
#     )
#     owner_first_name = AnnotatableField(
#         Coalesce(F("owner__first_name"), V(""), output_field=TextField()),
#         source="owner.first_name",
#         default="",
#     )
#     objects = AnnotatableFieldsManager()


from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import F
from django.db.models import Value as V
from django.db.models.functions import Coalesce
from django.db.models.functions import Concat

from dj_annotatable_field import AnnotatableField
from dj_annotatable_field import AnnotatableFieldsManager


class Profile(models.Model):
    username = models.TextField(default="")


class User(AbstractUser):
    full_name_from_method = AnnotatableField(
        Concat("first_name", V(" ", output_field=models.TextField()), "last_name")
    )
    full_name_from_annotate = AnnotatableField(
        V("from annotate"),
        source=lambda obj: "from source",
    )

    username_from_attr = AnnotatableField(
        F("profile__username"), source="profile.username"
    )
    username_from_callable = AnnotatableField(
        F("profile__username"),
        source=lambda obj: obj.profile.username if hasattr(obj, "profile") else None,
    )

    username_with_default = AnnotatableField(
        Coalesce(F("profile__username"), V("", output_field=models.TextField())),
        source="profile.username",
        default="",
    )
    username_custom_annotation_name = profile_username = AnnotatableField(
        F("profile__username"), annotation_name="_anything_else"
    )
    profile = models.OneToOneField(Profile, on_delete=models.DO_NOTHING, null=True)
    objects = AnnotatableFieldsManager()

    @full_name_from_method.source
    def from_method_source(self):
        return f"{self.first_name} {self.last_name}"
