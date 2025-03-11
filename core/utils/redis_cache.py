import logging
from django.core.cache import cache
import json

logger = logging.getLogger(__name__)

CACHE_TIMEOUT = 300  # 5 menit

class RedisCacheMixin:
    """
    Mixin untuk caching otomatis pada ViewSet di Django Rest Framework.
    """

    def get_queryset(self):
        """Gunakan caching pada queryset"""
        cache_key = f"{self.__class__.__name__}_queryset"
        cached_data = cache.get(cache_key)
        print('ASUU')
        if cached_data:
            print('ASUUUUUUUUUUU: ', cached_data)
            return cached_data

        logger.info(f"Cache MISS: {cache_key}, fetching from DB")
        queryset = super().get_queryset()
        serialized_queryset = list(queryset.values())  # Konversi queryset ke list agar bisa disimpan di Redis
        cache.set(cache_key, serialized_queryset, CACHE_TIMEOUT)
        return queryset

    def clear_cache(self):
        """Hapus cache khusus queryset ini."""
        cache_key = f"{self.__class__.__name__}_queryset"
        cache.delete(cache_key)
        logger.info(f"Cache cleared: {cache_key}")

    def create(self, request, *args, **kwargs):
        """Hapus cache setelah create."""
        response = super().create(request, *args, **kwargs)
        self.clear_cache()
        return response

    def update(self, request, *args, **kwargs):
        """Hapus cache setelah update."""
        print('JUANCOKKKKK')
        response = super().update(request, *args, **kwargs)
        self.clear_cache()
        return response

    def destroy(self, request, *args, **kwargs):
        """Hapus cache setelah delete."""
        response = super().destroy(request, *args, **kwargs)
        self.clear_cache()
        return response
