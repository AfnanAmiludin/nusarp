"""
Explain the source for settings values loaded via the YAMLCONF module.
"""
from __future__ import unicode_literals
from yamlconfig import explain
from yamlconfig.management.commands import YCBaseCommand


class Command(YCBaseCommand):
    """
    Implementation class for the "ycexplain" Django management command.
    """

    def add_arguments(self, parser):
        """
        Add the command line options for "ycexplain"
        """
        super(Command, self).add_arguments(parser)
        parser.add_argument(
            'attribute',
            nargs="+",
            help="Attribute to explain"
        )

    def handle(self, *args, **options):
        """
        Handle, i.e., execute, the command given the command line arguments
        "args" and "options".
        """
        super(Command, self).handle(*args, **options)
        for name in options['attribute']:
            explain(name, stream=self.stdout)
