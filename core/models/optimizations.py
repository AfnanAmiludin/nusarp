# core/models/optimizations.py
import logging
from django.db import models
from django.db.models.signals import post_save, post_migrate
from django.dispatch import receiver
from django.apps import apps

logger = logging.getLogger(__name__)

@receiver(post_migrate)
def create_optimizations(sender, **kwargs):
    """
    This will run after migrations are applied
    """
    # We don't do anything here directly - this just ensures 
    # that extensions are installed before optimizers run
    pass

class PostgresOptimizer:
    """
    Class to add PostgreSQL-specific optimizations to models
    """
    def __init__(self, schema='views', prefix=None, suffix=None, 
                 create_view=True, add_indexes=True, add_trigrams=True):
        self.schema = schema
        self.prefix = prefix
        self.suffix = suffix
        self.create_view = create_view
        self.add_indexes = add_indexes
        self.add_trigrams = add_trigrams
        
    def contribute_to_class(self, cls, name):
        """
        Hook for Django's model initialization that adds this feature to the model
        """
        self.model = cls
        setattr(cls, name, self)
        
        # Connect to post_save signal to create optimizations when migrations are applied
        post_migrate.connect(self._post_migrate_handler, sender=cls._meta.app_config)
        
    def _post_migrate_handler(self, sender, **kwargs):
        """
        Create all optimizations after migrations are applied
        """
        if self.create_view:
            self.create_schema_view()
        
        if self.add_indexes:
            self.create_indexes()
            
        if self.add_trigrams:
            self.create_trigram_indexes()
    
    def create_schema_view(self):
        """
        Create a view in the specified schema based on this model
        """
        from django.db import connection
        from datetime import datetime
        
        timestamp = datetime.now().strftime('%Y%m%d')
        model_name = self.model._meta.model_name
        app_label = self.model._meta.app_label
        
        # Get the actual table name from the model's Meta
        if hasattr(self.model._meta, 'db_table'):
            table_name = self.model._meta.db_table
        else:
            table_name = f"{app_label}_{model_name}"
        
        # Handle table name that might contain schema
        if '.' in table_name:
            # If there's a schema.table format, extract properly
            parts = table_name.split('.')
            if len(parts) == 2:
                # Remove any existing quotes
                schema_part = parts[0].replace('"', '')
                table_part = parts[1].replace('"', '')
                quoted_table_name = f'"{schema_part}"."{table_part}"'
            else:
                quoted_table_name = f'"{table_name}"'
        else:
            quoted_table_name = f'"{table_name}"'
        
        view_prefix = f"{self.prefix}_" if self.prefix else ""
        view_suffix = f"_{self.suffix}" if self.suffix else f"_{timestamp}"
        
        view_name = f"\"{self.schema}\".\"{view_prefix}{app_label}_{model_name}{view_suffix}\""
        
        columns = [f.column for f in self.model._meta.fields]
        columns_str = ', '.join([f'"{col}"' for col in columns])
        
        with connection.cursor() as cursor:
            # Create schema if not exists
            cursor.execute(f'CREATE SCHEMA IF NOT EXISTS "{self.schema}"')
            
            # Create view
            sql = f'CREATE OR REPLACE VIEW {view_name} AS SELECT {columns_str} FROM {quoted_table_name}'
            logger.info(f"Creating view: {sql}")
            cursor.execute(sql)
        
        return view_name

    def create_indexes(self):
        """
        Create database indexes for the model's fields based on field type
        """
        from django.db import connection
        
        table_name = self.model._meta.db_table
        
        # Handle table name for index naming
        safe_table_name = table_name.replace('"', '').replace('.', '_')
        
        with connection.cursor() as cursor:
            # Create indexes for foreign keys and frequently queried fields
            for field in self.model._meta.fields:
                if isinstance(field, models.ForeignKey) or field.db_index:
                    index_name = f"idx_{safe_table_name}_{field.column}"
                    
                    # Get properly quoted table name for the CREATE INDEX statement
                    if '.' in table_name:
                        parts = table_name.split('.')
                        if len(parts) == 2:
                            schema_part = parts[0].replace('"', '')
                            table_part = parts[1].replace('"', '')
                            quoted_table_name = f'"{schema_part}"."{table_part}"'
                        else:
                            quoted_table_name = f'"{table_name}"'
                    else:
                        quoted_table_name = f'"{table_name}"'
                    
                    sql = f'CREATE INDEX IF NOT EXISTS "{index_name}" ON {quoted_table_name} ("{field.column}")'
                    logger.info(f"Creating index: {sql}")
                    try:
                        cursor.execute(sql)
                    except Exception as e:
                        logger.error(f"Error creating index: {str(e)}")

    def create_trigram_indexes(self):
        """
        Create trigram indexes for text fields to speed up fuzzy searches
        """
        from django.db import connection
        
        table_name = self.model._meta.db_table
        
        # Handle table name for index naming
        safe_table_name = table_name.replace('"', '').replace('.', '_')
        
        with connection.cursor() as cursor:
            # Ensure pg_trgm extension is installed
            try:
                cursor.execute('CREATE EXTENSION IF NOT EXISTS pg_trgm')
            except Exception as e:
                logger.error(f"Error creating pg_trgm extension: {str(e)}")
                return
                
            # Create trigram indexes for text fields
            for field in self.model._meta.fields:
                if isinstance(field, (models.CharField, models.TextField)):
                    index_name = f"trgm_{safe_table_name}_{field.column}"
                    
                    # Get properly quoted table name for the CREATE INDEX statement
                    if '.' in table_name:
                        parts = table_name.split('.')
                        if len(parts) == 2:
                            schema_part = parts[0].replace('"', '')
                            table_part = parts[1].replace('"', '')
                            quoted_table_name = f'"{schema_part}"."{table_part}"'
                        else:
                            quoted_table_name = f'"{table_name}"'
                    else:
                        quoted_table_name = f'"{table_name}"'
                    
                    sql = f'CREATE INDEX IF NOT EXISTS "{index_name}" ON {quoted_table_name} USING gin ("{field.column}" gin_trgm_ops)'
                    logger.info(f"Creating trigram index: {sql}")
                    try:
                        cursor.execute(sql)
                    except Exception as e:
                        logger.error(f"Error creating trigram index: {str(e)}")

    def _post_migrate_handler(self, sender, **kwargs):
        """
        Create all optimizations after migrations are applied
        """
        try:
            if self.create_view:
                self.create_schema_view()
            
            if self.add_indexes:
                self.create_indexes()
                
            if self.add_trigrams:
                self.create_trigram_indexes()
        except Exception as e:
            logger.error(f"Error applying optimizations: {str(e)}")
            # Don't raise the exception to prevent migration failure
            # You can choose to raise it if you want migrations to fail on optimization errors


class SchemaView:
    """
    Creates a view in a specified schema for the model
    Usage: schema_view = SchemaView(schema='analytics')
    """
    def __init__(self, schema='views', suffix=None, prefix=None):
        self.schema = schema
        self.suffix = suffix
        self.prefix = prefix
        
    def contribute_to_class(self, cls, name):
        optimizer = PostgresOptimizer(
            schema=self.schema,
            suffix=self.suffix,
            prefix=self.prefix,
            create_view=True,
            add_indexes=False,
            add_trigrams=False
        )
        optimizer.contribute_to_class(cls, name)


class Trigrams:
    """
    Adds trigram indexes to text fields in the model
    Usage: trigrams = Trigrams()
    """
    def contribute_to_class(self, cls, name):
        optimizer = PostgresOptimizer(
            create_view=False,
            add_indexes=False,
            add_trigrams=True
        )
        optimizer.contribute_to_class(cls, name)


class IndexOptimizer:
    """
    Adds smart indexes to the model
    Usage: indexes = IndexOptimizer()
    """
    def contribute_to_class(self, cls, name):
        optimizer = PostgresOptimizer(
            create_view=False,
            add_indexes=True,
            add_trigrams=False
        )
        optimizer.contribute_to_class(cls, name)


class FullOptimizer:
    """
    Applies all optimizations: views, indexes, and trigram indexes
    Usage: optimizer = FullOptimizer(schema='analytics')
    """
    def __init__(self, schema='views', suffix=None, prefix=None):
        self.schema = schema
        self.suffix = suffix
        self.prefix = prefix
        
    def contribute_to_class(self, cls, name):
        optimizer = PostgresOptimizer(
            schema=self.schema,
            suffix=self.suffix,
            prefix=self.prefix,
            create_view=True,
            add_indexes=True,
            add_trigrams=True
        )
        optimizer.contribute_to_class(cls, name)