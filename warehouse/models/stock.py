import logging

from django.db import models
from django.utils.translation import gettext_lazy as _

from warehouse import settings

from core.models import Base, History, Tracker, AdjacencyListTree

logger = logging.getLogger(__name__)


class StockSchema(
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
    tracker = Tracker()
    history = History(
        bases=[
            Base,
        ],
        table_name='"history"."{}_stock_schema"'.format(settings.SCHEMA),
        verbose_name=_("Used store history stock schema"),
        excluded_fields=[
            "modified",
        ],
    )

    class Meta:
        managed = True
        db_table = '"{}"."stock_schema"'.format(settings.SCHEMA)
        verbose_name = _("Used for stock schema")

    def get_children(self):
        return (
            super(StockSchema, self)
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


class Stock(
    Base,
):
    stock_id = models.TextField(
        primary_key=True,
        verbose_name=_("stock id"),
        help_text=_("used for stock id"),
    )
    stock_name = models.TextField(
        blank=True,
        null=False,
        verbose_name=_("stock name"),
        help_text=_("used for stock name"),
    )
    price = models.DecimalField(
        max_digits=17,
        decimal_places=4,
        blank=True,
        null=True,
        verbose_name=_("stock value"),
        help_text=_("used for stock value"),
    )
    hpp = models.DecimalField(
        max_digits=17,
        decimal_places=4,
        blank=True,
        null=True,
        verbose_name=_("stock hpp"),
        help_text=_("used for stock hpp"),
    )
    on_hand = models.DecimalField(
        max_digits=17,
        decimal_places=4,
        blank=True,
        null=True,
        verbose_name=_("stock on hand"),
        help_text=_("used for stock on hand"),
    )
    allocated = models.DecimalField(
        max_digits=17,
        decimal_places=4,
        blank=True,
        null=True,
        verbose_name=_("stock allocated"),
        help_text=_("used for stock allocated"),
    )
    temp_allocated = models.DecimalField(
        max_digits=17,
        decimal_places=4,
        blank=True,
        null=True,
        verbose_name=_("stock temp allocated"),
        help_text=_("used for stock temp allocated"),
    )
    price_allocated = models.DecimalField(
        max_digits=17,
        decimal_places=4,
        blank=True,
        null=True,
        verbose_name=_("stock value allocated"),
        help_text=_("used for stock value allocated"),
    )
    reorder = models.BooleanField(
        default=False,
        blank=True,
        null=True,
        verbose_name=_("stock reorder"),
        help_text=_("used for stock reorder"),
    )
    out_stock_purchase = models.DecimalField(
        max_digits=17,
        decimal_places=4,
        blank=True,
        null=True,
        verbose_name=_("stock out stock purchase"),
        help_text=_("used for stock out stock purchase"),
    )
    out_stock_sales = models.DecimalField(
        max_digits=17,
        decimal_places=4,
        blank=True,
        null=True,
        verbose_name=_("stock out stock sales"),
        help_text=_("used for stock out stock sales"),
    )
    uninvoiced = models.DecimalField(
        max_digits=17,
        decimal_places=4,
        blank=True,
        null=True,
        verbose_name=_("stock uninvoiced"),
        help_text=_("used for stock uninvoiced"),
    )
    hold = models.BooleanField(
        default=False,
        verbose_name=_("stock hold"),
        help_text=_("used for stock hold"),
    )
    last_hpp = models.DecimalField(
        max_digits=17,
        decimal_places=4,
        blank=True,
        null=True,
        verbose_name=_("stock last hpp"),
        help_text=_("used for stock last hpp"),
    )
    last_price = models.DecimalField(
        max_digits=17,
        decimal_places=4,
        blank=True,
        null=True,
        verbose_name=_("stock last price"),
        help_text=_("used for stock last price"),
    )
    picture = models.ImageField(
        blank=True,
        null=True,
        upload_to=None,
        height_field=None,
        width_field=None,
        max_length=None,
    )
    note = models.TextField(
        blank=True,
        null=True,
        verbose_name=_("stock note"),
        help_text=_("used for stock note"),
    )
    is_product = models.BooleanField(
        default=False,
        blank=True,
        null=True,
        verbose_name=_("stock is product"),
        help_text=_("used for stock is product"),
    )
    stock_schema = models.ForeignKey(
        to=StockSchema,
        on_delete=models.RESTRICT,
        related_name="stock_schema",
        blank=True,
        null=True,
        verbose_name=_("stock schema id"),
        help_text=_("Used for hierarchy stock schema id"),
    )
    division = models.TextField(
        default=None,
        blank=True,
        null=True,
        verbose_name=_("stock division"),
        help_text=_("used for stock division"),
    )
    # division = models.ForeignKey(
    #     to="common.Division",
    #     on_delete=models.PROTECT,
    #     blank=True,
    #     null=True,
    #     related_name="%(app_label)s_%(class)s",
    #     verbose_name=_("stock division"),
    #     help_text=_("used for stock division"),
    # )
    tracker = Tracker()
    history = History(
        bases=[
            Base,
        ],
        table_name='"history"."{}_stock"'.format(settings.SCHEMA),
        verbose_name=_("Used store history stock"),
        excluded_fields=[
            "modified",
        ],
    )

    class Meta:
        managed = True
        db_table = '"{}"."stock"'.format(settings.SCHEMA)
        verbose_name = _("Used for stock")
        permissions = [
            ("add_stock_permission", _("Can add stock permission")),
            ("delete_stock_permission", _("Can delete stock permission")),
            ("update_stock_permission", _("Can update stock permission")),
        ]


class StockAttribute(
    Base,
):
    TYPE_CHOICES = [
        ("COLOR", _("Color")),
        ("WEIGHT", _("Weight")),
        ("UNIT", _("Unit")),
        ("VOLUME", _("Volume")),
    ]
    attribute_id = models.AutoField(
        primary_key=True,
        verbose_name=_("stock attribute id"),
        help_text=_("used for stock attribute id"),
    )
    attribute_name = models.TextField(
        blank=False,
        null=False,
        verbose_name=_("stock attribute name"),
        help_text=_("used for stock attribute name"),
    )
    type = models.CharField(
        choices=TYPE_CHOICES,
        blank=True,
        null=True,
        verbose_name=_("stock attribute type"),
        help_text=_("used for stock attribute type"),
    )
    value = models.TextField(
        blank=False,
        null=False,
        verbose_name=_("stock attribute value"),
        help_text=_("used for stock attribute value"),
    )
    tracker = Tracker()
    history = History(
        bases=[
            Base,
        ],
        table_name='"history"."{}_stock_attribute"'.format(settings.SCHEMA),
        verbose_name=_("Used store history stock attribute"),
        excluded_fields=[
            "modified",
        ],
    )

    class Meta:
        managed = True
        db_table = '"{}"."stock_attribute"'.format(settings.SCHEMA)
        verbose_name = _("Used for stock attribute")


class StockService(
    Base,
):
    service_id = models.TextField(
        primary_key=True,
        verbose_name=_("service id"),
        help_text=_("used for service id"),
    )
    service_name = models.TextField(
        blank=False,
        null=False,
        verbose_name=_("service name"),
        help_text=_("used for service name"),
    )
    price = models.DecimalField(
        max_digits=17,
        decimal_places=4,
        blank=True,
        null=True,
        verbose_name=_("service cost"),
        help_text=_("used for service cost"),
    )
    tracker = Tracker()
    history = History(
        bases=[
            Base,
        ],
        table_name='"history"."{}_stock_service"'.format(settings.SCHEMA),
        verbose_name=_("Used store history stock service"),
        excluded_fields=[
            "modified",
        ],
    )

    class Meta:
        managed = True
        db_table = '"{}"."stock_service"'.format(settings.SCHEMA)
        verbose_name = _("Used for stock service")
        permissions = [
            ("add_stock_service_permission", _("Can add stock service permission")),
            (
                "delete_stock_service_permission",
                _("Can delete stock service permission"),
            ),
            (
                "update_stock_service_permission",
                _("Can update stock service permission"),
            ),
        ]
