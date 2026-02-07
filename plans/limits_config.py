"""
Конфигурация лимитов по тарифам.
Используется при инициализации БД и для гостей (без БД).
"""

PLANS_CONFIG = {
    'free': {
        'name': 'Free',
        'conversions_per_day': 3,
        'max_file_size_mb': 25,
        'max_video_seconds': 30,
        'is_guest_plan': True,
        'is_available': True,
    },
    'basic': {
        'name': 'Basic',
        'conversions_per_day': 20,
        'max_file_size_mb': 200,
        'max_video_seconds': 180,
        'is_guest_plan': False,
        'is_available': True,
    },
    'pro': {
        'name': 'Pro',
        'conversions_per_day': 100,
        'max_file_size_mb': 1024,
        'max_video_seconds': 0,
        'is_guest_plan': False,
        'is_available': False,
    },
}
