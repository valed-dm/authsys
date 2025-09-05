from django.contrib import admin
from django.urls import include
from django.urls import path
from drf_spectacular.views import SpectacularAPIView
from drf_spectacular.views import SpectacularRedocView
from drf_spectacular.views import SpectacularSwaggerView

from accounts.views_html import HomePageView
from core.config import settings


urlpatterns = [
    path("", HomePageView.as_view(), name="home"),
    path("admin/", admin.site.urls),
    path("accounts/", include("accounts.urls_html")),
    path("api/rbac/", include("rbac.urls")),
    path("api/mock/", include("mockapi.urls")),
    path("api/accounts/", include("accounts.urls_api")),
    # OpenAPI / Swagger / ReDoc
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "api/docs/swagger/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
    path(
        "api/docs/redoc/",
        SpectacularRedocView.as_view(url_name="schema"),
        name="redoc",
    ),
]

if settings.DEBUG:
    import debug_toolbar

    urlpatterns += [
        path("__debug__/", include(debug_toolbar.urls)),
    ]
