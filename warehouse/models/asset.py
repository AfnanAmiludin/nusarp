import logging

from django.db import models
from django.utils.translation import gettext_lazy as _

from warehouse import settings

from core.models import Base, History, Tracker, AdjacencyListTree
from core.fields import StatusField

logger = logging.getLogger(__name__)


class AssetSchema(
    AdjacencyListTree,
    Base,
):
    node_order_by = [
        "schema_id",
    ]
    schema_id = models.TextField(
        primary_key=True,
        verbose_name=_("schema id"),
        help_text=_("used for identity"),
    )
    schema_name = models.TextField(
        blank=False,
        null=False,
        verbose_name=_("stock schema name"),
        help_text=_("used for stock schema name"),
    )
    layer = models.IntegerField(
        default=None,
        blank=False,
        null=False,
        verbose_name=_("schema layer"),
        help_text=_("used for schema layer"),
    )
    parent = models.ForeignKey(
        to="self",
        on_delete=models.RESTRICT,
        related_name="children_set",
        blank=True,
        null=True,
        verbose_name=_("parent"),
        help_text=_("Used for hierarchy parent id"),
    )
    status = StatusField(
        transition=False,
    )
    tracker = Tracker()
    history = History(
        bases=[
            Base,
        ],
        table_name='"history"."{}_asset_schema"'.format(settings.SCHEMA),
        verbose_name=_("Used store history asset schema"),
        excluded_fields=[
            "modified",
        ],
    )

    class Meta:
        managed = True
        db_table = '"{}"."asset_schema"'.format(settings.SCHEMA)
        verbose_name = _("Used for asset schema")

    def get_children(self):
        return (
            super(AssetSchema, self)
            .get_children()
            .filter(
                parent=self,
                is_removed=False,
            )
            .order_by("schema_id")
        )

    @property
    def has_children(self):
        return len(self.get_children()) > 0


class Asset(
    Base,
):
    STATUS_CHOICES = {
        AVAILABLE: _("Available"),
        LOANED: _("Laned"),
        SOLD: _("Sold"),
    }
    asset_id = models.TextField(
        primary_key=True,
        verbose_name=_("asset id"),
        help_text=_("used for identity"),
    )
    asset_name = models.TextField(
        blank=False,
        null=False,
        verbose_name=_("asset name"),
        help_text=_("used for asset name"),
    )
    pack = models.TextField(
        blank=True,
        null=True,
        verbose_name=_("asset pack"),
        help_text=_("used for asset pack"),
    )
    order_date = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name=_("asset order date"),
        help_text=_("used for asset order date"),
    )
    quantity = models.IntegerField(
        blank=True,
        null=True,
        verbose_name=_("asset quantity"),
        help_text=_("used for asset quantity"),
    )
    price = models.DecimalField(
        max_digits=17,
        decimal_places=4,
        blank=True,
        null=True,
        verbose_name=_("asset price"),
        help_text=_("used for asset price"),
    )
    age = models.IntegerField(
        blank=True,
        null=True,
        verbose_name=_("asset age"),
        help_text=_("used for asset age"),
    )
    depreciation_value = models.DecimalField(
        max_digits=17,
        decimal_places=4,
        blank=True,
        null=True,
        verbose_name=_("asset depreciation"),
        help_text=_("used for asset depreciation"),
    )
    depreciation_quantity = models.DecimalField(
        max_digits=17,
        decimal_places=4,
        blank=True,
        null=True,
        verbose_name=_("asset depreciation quantity"),
        help_text=_("used for asset depreciation quantity"),
    )
    accumulative_value = models.DecimalField(
        max_digits=17,
        decimal_places=4,
        blank=True,
        null=True,
        verbose_name=_("asset accumulative value"),
        help_text=_("used for asset accumulative value"),
    )
    asset_status = models.CharField(
        choices=STATUS_CHOICES,
        default=AVAILABLE,
        verbose_name=_("asset status"),
        help_text=_("used for asset status"),
    )
    open_balance_status = models.BooleanField(
        default=False,
        verbose_name=_("asset open balance status"),
        help_text=_("used for asset open balance status"),
    )
    accumulative_depreciation = models.DecimalField(
        max_digits=17,
        decimal_places=4,
        blank=True,
        null=True,
        verbose_name=_("asset accumulative depreciation"),
        help_text=_("used for asset accumulative depreciation"),
    )
    depreciation_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        blank=True,
        null=True,
        verbose_name=_("asset depreciation percentage"),
        help_text=_("used for asset depreciation percentage"),
    )
    branch = models.TextField(
        blank=True,
        null=True,
        verbose_name=_("asset branch"),
        help_text=_("used for asset branch"),
    )
    location = models.TextField(
        blank=True,
        null=True,
        verbose_name=_("asset location"),
        help_text=_("used for asset location"),
    )
    department = models.TextField(
        default=None,
        blank=True,
        null=True,
        verbose_name=_("asset department"),
        help_text=_("used for asset department"),
    )
    sub_department = models.TextField(
        default=None,
        blank=True,
        null=True,
        verbose_name=_("asset sub department"),
        help_text=_("used for asset sub department"),
    )
    room = models.TextField(
        blank=True,
        null=True,
        verbose_name=_("asset room"),
        help_text=_("used for asset room"),
    )
    rack = models.TextField(
        blank=True,
        null=True,
        verbose_name=_("asset rack"),
        help_text=_("used for asset rack"),
    )
    reference = models.TextField(
        blank=True,
        null=True,
        verbose_name=_("asset reference"),
        help_text=_("used for asset reference"),
    )
    created_year = models.DateField(
        auto_now=True,
        verbose_name=_("asset created year"),
        help_text=_("used for asset created year"),
    )
    brand = models.TextField(
        blank=True,
        null=True,
        verbose_name=_("asset brand"),
        help_text=_("used for asset brand"),
    )
    other_specific = models.TextField(
        blank=True,
        null=True,
        verbose_name=_("asset other specific"),
        help_text=_("used for asset other specific"),
    )
    other_situation = models.TextField(
        blank=True,
        null=True,
        verbose_name=_("asset situation"),
        help_text=_("used for asset situation"),
    )
    is_product = models.BooleanField(
        default=False,
        blank=True,
        null=True,
        verbose_name=_("asset is product"),
        help_text=_("used for asset is product"),
    )
    supplier = models.ForeignKey(
        to="common.Supplier",
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        related_name="%(app_label)s_%(class)s",
        verbose_name=_("asset supplier id"),
        help_text=_("used for asset supplier id"),
    )
    cost_center = models.ForeignKey(
        to="common.Department",
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        related_name="%(app_label)s_%(class)s",
        verbose_name=_("asset department id"),
        help_text=_("used for asset department id"),
    )
    asset_schema = models.ForeignKey(
        to=AssetSchema,
        on_delete=models.RESTRICT,
        related_name="asset_schema",
        blank=True,
        null=True,
        verbose_name=_("asset schema id"),
        help_text=_("Used for hierarchy asset schema id"),
    )
    status = StatusField(
        transition=False,
    )
    tracker = Tracker()
    history = History(
        bases=[
            Base,
        ],
        table_name='"history"."{}_asset"'.format(settings.SCHEMA),
        verbose_name=_("Used store history asset"),
        excluded_fields=[
            "modified",
        ],
    )

    class Meta:
        managed = True
        db_table = '"{}"."asset"'.format(settings.SCHEMA)
        verbose_name = _("Used for asset")
        permissions = [
            ("add_asset_permission", _("Can add asset permission")),
            ("delete_asset_permission", _("Can delete asset permission")),
            ("add_asset_group", _("Can add asset group")),
            ("delete_asset_group", _("Can delete asset group")),
            ("change_asset_password", _("Can change asset password")),
        ]
