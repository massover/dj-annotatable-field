# dj-annotatable-field

A single field populated by a query annotation or calculated in python.

## Installation

```
pip install dj-annotatable-field
```

## Quickstart

```python
from django.contrib.auth.models import AbstractUser
from django.db.models.functions import Concat
from dj_annotatable_field import AnnotatableField, AnnotatableFieldsManager

class User(AbstractUser):
    full_name = AnnotatableField(Concat("first_name", "last_name"))

    objects = AnnotatableFieldsManager()
    
    @full_name.source
    def full_name_source(self):
        return f"{self.first_name} {self.last_name}"

user = User.objects.annotate_fields().get()
user.full_name # from db annotation
user._full_name # the annotated field

user = User.objects.get()
user.full_name # calculated in python
getattr(user, '_full_name', "I'm not annotated!")
```

## Why?

```python
from django.db import models

class Owner(models.Model):
    @property
    def dog_count(self):
        return self.dogs.count()   

class Dog(models.Model):
    owner = models.ForeignKey(Owner, on_delete=models.DO_NOTHING, related_name="dogs")
```

The `dog_count` python calculated property is subject to `n+1` issues without proper prefetching/logic or checking for an annotation. 
However, the calculated property is definitely convenient to have declared on the object (if they're already prefetched, or 
working in the shell, or on a test, etc). One solution is the following:

1. check for a db annotation first 
2. if no db annotation calculate result in python

```python
from django.db import models
from django.db.models import Count

class Owner(models.Model):
    @property
    def dog_count(self):
        count = getattr(self, '_dog_count', None)
        if count is not None:
            return count
        return self.dogs.count()

Owner.objects.annotate(_dog_count=Count('dogs'))
```

This library contains the `AnnotatedField` to encapsulate this pattern

```python
from django.db import models
from django.db.models import Count
from dj_annotatable_field import AnnotatableField, AnnotatableFieldsManager

class Owner(models.Model):
    dog_count = AnnotatableField(Count('dogs'))
    
    objects = AnnotatableFieldsManager()
    
    @dog_count.source
    def dog_count_source(self):
        return self.dogs.count()

Owner.objects.annotate_fields()
```

## Usage

### AnnotatableField

```python
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import F, Value as V
from django.db.models.functions import Concat, Coalesce
from dj_annotatable_field import AnnotatableField

class Profile(models.Model):
    username = models.TextField(default="")

class User(AbstractUser):
    profile = models.OneToOneField(Profile, on_delete=models.DO_NOTHING, null=True)
    
    # from decorator
    full_name = AnnotatableField(Concat("first_name", "last_name"))
    @full_name.source
    def full_name_source(self):
        return f"{self.first_name} {self.last_name}"
    
    # path to attribute
    profile_username = AnnotatableField(F("profile__username"), source="profile.username")

    # callable
    profile_username = AnnotatableField(
        F("profile__username"), 
        source=lambda obj: obj.profile.username if hasattr(obj, 'profile') else None
    )

    # with default
    profile_username = AnnotatableField(Coalesce(F("profile__username"), V("")), source="profile.username", default="")

    # custom annotation name
    profile_username = AnnotatableField(F("profile__username"), annotation_name="_anything_else")
```

**source**

Source can be callable, a path to an attribute, or it can be set via a decorator

**default**

If the source is a string, the field will return `default` if the source is not found.

**annotation_name**

By default the annotation_name will be `_{name}`, eg `_full_name`.

### AnnotatableFieldManager / Queryset / Mixin

```python
from django.contrib.auth.models import AbstractUser
from django.db.models.functions import Concat, Coalesce
from dj_annotatable_field import AnnotatableField, AnnotatableFieldsManager

class User(AbstractUser):
    full_name = AnnotatableField(Concat("first_name", "last_name"))

    objects = AnnotatableFieldsManager()
```

### annotate_fields

```python

# annotate all AnnotabledFields on the model
user = User.objects.annotate_fields().get()

# include fields by name as args
User.objects.annotate_fields('full_name')

# set an exclude list of fields by name
User.objects.annotate_fields(exclude=["profile_username"])
```

**args**

Field names to include in annotation

**exclude**

List of field names to exclude