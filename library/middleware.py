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


# shows a maintenance page to regular users when the admin toggles it on
class MaintenanceModeMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # always let admin and static files through
        path = request.path
        if path.startswith('/admin/') or path.startswith('/static/') or path.startswith('/media/'):
            return self.get_response(request)

        # staff can still access the site so they can turn maintenance off
        if hasattr(request, 'user') and request.user.is_authenticated and request.user.is_staff:
            return self.get_response(request)

        try:
            from .models import SiteSettings
            settings = SiteSettings.load()
            if settings.maintenance_mode:
                return render(request, 'maintenance.html', status=503)
        except Exception:
            pass

        return self.get_response(request)
