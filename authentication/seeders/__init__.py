from .seed_users import seed as seed_user
from .seed_groups import seed as seed_group

SEEDERS = [
    seed_user,
    seed_group,
]
