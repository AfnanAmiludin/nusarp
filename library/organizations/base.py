# -*- coding: utf-8 -*-

import uuid

from django.conf import settings
from django.core.exceptions import FieldDoesNotExist
from django.db import models
from django.db.models.base import ModelBase
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

import six

from organizations import signals
from organizations.managers import ActiveOrgManager
from organizations.managers import OrgManager

USER_MODEL = getattr(settings, "AUTH_USER_MODEL", "auth.User")


class UnicodeMixin:
    """
    Python 2 and 3 string representation support.

    Legacy cruft. Removing entirely even from migrations affects the
    meta class creation.
    """


class OrgMeta(ModelBase):
    """
    Base metaclass for dynamically linking related organization models.

    This is particularly useful for custom organizations that can avoid
    multitable inheritance and also add additional attributes to the
    organization users especially.

    The `module_registry` dictionary is used to track the architecture across
    different Django apps. If more than one application makes use of these
    base models, the extended models will share class relationships, which is
    clearly undesirable. This ensures that the relationships between models
    within a module using these base classes are from other organization models.

    """

    module_registry = {}

    def __new__(cls, name, bases, attrs):  # noqa
        # Borrowed from Django-polymorphic
        # Workaround compatibility issue with six.with_metaclass() and custom
        # Django model metaclasses:
        if not attrs and name == "NewBase":
            return super(OrgMeta, cls).__new__(cls, name, bases, attrs)

        base_classes = ["OrgModel", "OrgUserModel", "OrgOwnerModel", "OrgInviteModel"]
        model = super(OrgMeta, cls).__new__(cls, name, bases, attrs)
        module = model.__module__
        if not cls.module_registry.get(module):
            cls.module_registry[module] = {
                "OrgModel": None,
                "OrgUserModel": None,
                "OrgOwnerModel": None,
                "OrgInviteModel": None,
            }
        for b in bases:
            key = None
            if b.__name__ in ["AbstractOrganization", "OrganizationBase"]:
                key = "OrgModel"
            elif b.__name__ in ["AbstractOrganizationUser", "OrganizationUserBase"]:
                key = "OrgUserModel"
            elif b.__name__ in ["AbstractOrganizationOwner", "OrganizationOwnerBase"]:
                key = "OrgOwnerModel"
            elif b.__name__ in [
                "AbstractOrganizationInvitation",
                "OrganizationInvitationBase",
            ]:
                key = "OrgInviteModel"
            if key:
                cls.module_registry[module][key] = model

        if all([cls.module_registry[module][klass] for klass in base_classes]):
            model.update_org(module)
            model.update_org_users(module)
            model.update_org_owner(module)
            model.update_org_invite(module)

        return model

    def update_org(cls, module):
        """
        Adds the `users` field to the organization model
        """
        try:
            cls.module_registry[module]["OrgModel"]._meta.get_field("users")
        except FieldDoesNotExist:
            cls.module_registry[module]["OrgModel"].add_to_class(
                "users",
                models.ManyToManyField(
                    USER_MODEL,
                    through=cls.module_registry[module]["OrgUserModel"].__name__,
                    related_name="%(app_label)s_%(class)s",
                ),
            )

        cls.module_registry[module]["OrgModel"].invitation_model = cls.module_registry[
            module
        ]["OrgInviteModel"]

    def update_org_users(cls, module):
        """
        Adds the `user` field to the organization user model and the link to
        the specific organization model.
        """
        try:
            cls.module_registry[module]["OrgUserModel"]._meta.get_field("user")
        except FieldDoesNotExist:
            cls.module_registry[module]["OrgUserModel"].add_to_class(
                "user",
                models.ForeignKey(
                    USER_MODEL,
                    related_name="%(app_label)s_%(class)s",
                    on_delete=models.CASCADE,
                ),
            )
        try:
            cls.module_registry[module]["OrgUserModel"]._meta.get_field("organization")
        except FieldDoesNotExist:
            cls.module_registry[module]["OrgUserModel"].add_to_class(
                "organization",
                models.ForeignKey(
                    cls.module_registry[module]["OrgModel"],
                    related_name="organization_users",
                    on_delete=models.CASCADE,
                ),
            )

    def update_org_owner(cls, module):
        """
        Creates the links to the organization and organization user for the owner.
        """
        try:
            cls.module_registry[module]["OrgOwnerModel"]._meta.get_field(
                "organization_user"
            )
        except FieldDoesNotExist:
            cls.module_registry[module]["OrgOwnerModel"].add_to_class(
                "organization_user",
                models.OneToOneField(
                    cls.module_registry[module]["OrgUserModel"],
                    on_delete=models.CASCADE,
                ),
            )
        try:
            cls.module_registry[module]["OrgOwnerModel"]._meta.get_field("organization")
        except FieldDoesNotExist:
            cls.module_registry[module]["OrgOwnerModel"].add_to_class(
                "organization",
                models.OneToOneField(
                    cls.module_registry[module]["OrgModel"],
                    related_name="owner",
                    on_delete=models.CASCADE,
                ),
            )

    def update_org_invite(cls, module):
        """
        Adds the links to the organization and to the organization user
        """
        try:
            cls.module_registry[module]["OrgInviteModel"]._meta.get_field("invited_by")
        except FieldDoesNotExist:
            cls.module_registry[module]["OrgInviteModel"].add_to_class(
                "invited_by",
                models.ForeignKey(
                    USER_MODEL,
                    related_name="%(app_label)s_%(class)s_sent_invitations",
                    on_delete=models.CASCADE,
                ),
            )
        try:
            cls.module_registry[module]["OrgInviteModel"]._meta.get_field("invitee")
        except FieldDoesNotExist:
            cls.module_registry[module]["OrgInviteModel"].add_to_class(
                "invitee",
                models.ForeignKey(
                    USER_MODEL,
                    null=True,
                    blank=True,
                    related_name="%(app_label)s_%(class)s_invitations",
                    on_delete=models.CASCADE,
                ),
            )
        try:
            cls.module_registry[module]["OrgInviteModel"]._meta.get_field(
                "organization"
            )
        except FieldDoesNotExist:
            cls.module_registry[module]["OrgInviteModel"].add_to_class(
                "organization",
                models.ForeignKey(
                    cls.module_registry[module]["OrgModel"],
                    related_name="organization_invites",
                    on_delete=models.CASCADE,
                ),
            )


class AbstractBaseOrganization(models.Model):
    """
    The umbrella object with which users can be associated.

    An organization can have multiple users but only one who can be designated
    the owner user.
    """

    name = models.CharField(max_length=200, help_text=_("The name of the organization"))
    is_active = models.BooleanField(default=True)

    objects = OrgManager()
    active = ActiveOrgManager()

    class Meta:
        abstract = True
        ordering = ["name"]

    def __str__(self):
        return self.name

    @property
    def user_relation_name(self):
        """
        Returns the string name of the related name to the user.

        This provides a consistent interface across different organization
        model classes.
        """
        return "{0}_{1}".format(
            self._meta.app_label.lower(), self.__class__.__name__.lower()
        )

    def is_member(self, user):
        return True if user in self.users.all() else False


class OrganizationBase(six.with_metaclass(OrgMeta, AbstractBaseOrganization)):
    class Meta(AbstractBaseOrganization.Meta):
        abstract = True

    @property
    def _org_user_model(self):
        return self.__class__.module_registry[self.__class__.__module__]["OrgUserModel"]

    def add_user(self, user, **kwargs):
        org_user = self._org_user_model.objects.create(
            user=user, organization=self, **kwargs
        )
        signals.user_added.send(sender=self, user=user)
        return org_user


class AbstractBaseOrganizationUser(models.Model):
    """
    ManyToMany through field relating Users to Organizations.

    It is possible for a User to be a member of multiple organizations, so this
    class relates the OrganizationUser to the User model using a ForeignKey
    relationship, rather than a OneToOne relationship.

    Authentication and general user information is handled by the User class
    and the contrib.auth application.
    """

    class Meta:
        abstract = True
        ordering = ["organization", "user"]
        unique_together = ("user", "organization")

    def __str__(self):
        return "{name} {org}".format(
            name=self.name if self.user.is_active else self.user.email,
            org=self.organization.name,
        )

    @property
    def name(self):
        """
        Returns the connected user's full name or string representation if the
        full name method is unavailable (e.g. on a custom user class).
        """
        try:
            return self.user.get_full_name()
        except AttributeError:
            return str(self.user)


class OrganizationUserBase(six.with_metaclass(OrgMeta, AbstractBaseOrganizationUser)):
    class Meta(AbstractBaseOrganizationUser.Meta):
        abstract = True


class AbstractBaseOrganizationOwner(models.Model):
    """
    Each organization must have one and only one organization owner.
    """

    class Meta:
        abstract = True

    def __str__(self):
        return "{0}: {1}".format(self.organization, self.organization_user)


class OrganizationOwnerBase(six.with_metaclass(OrgMeta, AbstractBaseOrganizationOwner)):
    class Meta(AbstractBaseOrganizationOwner.Meta):
        abstract = True


class AbstractBaseInvitation(models.Model):
    """
    Tracks invitations to organizations

    This tracks *users* specifically, rather than OrganizationUsers, as it's
    considered *more critical* to know who invited or joined even if they
    are no longer members of the organization.
    """

    guid = models.UUIDField(editable=False)
    invitee_identifier = models.CharField(
        max_length=1000,
        help_text=_(
            "The contact identifier for the invitee, email, phone number, social media handle, etc."
        ),
    )

    class Meta:
        abstract = True

    def __str__(self):
        return "{0}: {1}".format(self.organization, self.invitee_identifier)

    def save(self, **kwargs):
        if not self.guid:
            self.guid = str(uuid.uuid4())
        return super().save(**kwargs)

    def get_absolute_url(self):
        """Returns the invitation URL"""
        return reverse("invitations_register", kwargs={"guid": self.guid})

    def activation_kwargs(self):
        """Override this to add kwargs to add_user on activation"""
        return {}

    def activate(self, user):
        """
        Updates the `invitee` value and saves the instance

        Provided as a way of extending the behavior.

        Args:
            user: the newly created user

        Returns:
            the linking organization user

        """
        org_user = self.organization.add_user(user, **self.activation_kwargs())
        self.invitee = user
        self.save()
        return org_user

    def invitation_token(self):
        """
        Returns a unique token for the user

        Hash based on identification, account id, time invitited, and secret key of site
        """
        raise NotImplementedError


class OrganizationInvitationBase(six.with_metaclass(OrgMeta, AbstractBaseInvitation)):
    class Meta(AbstractBaseInvitation.Meta):
        abstract = True
