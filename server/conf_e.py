DEBUG = True
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": "marketing_system",
        "USER": "root",
        # "PASSWORD": "Ru,6e.4vu4wj/3",
        "HOST": "localhost",
        "PORT": "3306",
        "OPTIONS": {
            "sql_mode": "traditional",
            "charset": "utf8mb4"
        }
    }
}