from django.shortcuts import render


# logs every page visit to the database for analytics
class VisitLoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        # skip static and media files so we only track real page visits
        path = request.path
        if path.startswith('/static/') or path.startswith('/media/'):
            return response

        try:
            from .models import VisitLog
            ip = request.META.get('REMOTE_ADDR', '')
            VisitLog.objects.create(
                path=path,
                method=request.method,
                ip_address=ip,
            )
        except Exception:
            pass

        return response


# maintenance mode — toggled from the admin dashboard (SiteSettings model)
# /admin/ and /login/ are always accessible so staff never gets locked out
class MaintenanceModeMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        path = request.path

        # always let admin and login through
        if path.startswith('/admin/') or path.startswith('/login/') or path.startswith('/static/') or path.startswith('/media/'):
            return self.get_response(request)

        # staff bypass maintenance entirely
        if hasattr(request, 'user') and request.user.is_authenticated and request.user.is_staff:
            return self.get_response(request)

        try:
            from .models import SiteSettings
            if SiteSettings.load().maintenance_mode:
                return render(request, 'maintenance.html', status=503)
        except Exception:
            pass

        return self.get_response(request)
