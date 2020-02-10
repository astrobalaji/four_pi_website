from django.contrib import admin
from django.urls import path, include
from homepage import views as home_v
from coming_soon import views as cs_views
from signup.views import SignUpView, ActivateAccount
from confirm_reg import views as conf_email_views
from amateurOnboarding.views import AmaOBViews
from proOnboarding.views import proOBViews
from eduOnboarding.views import eduOBViews
from user_home import views as home_view


urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),
    path('', cs_views.index),
    path('landingpage/',  home_v.index),
    path('signup/', SignUpView.as_view(), name='signup'),
    path('activate/<uidb64>/<token>/', ActivateAccount.as_view(), name='activate'),
    path('signup/activate/confirm_email', conf_email_views.index),
    path('activate/dir_sel/', conf_email_views.init_sel),
    path('onboarding/amateur/', AmaOBViews.as_view()),
    path('user/home/', home_view.index),
    path('onboarding/professional/', proOBViews.as_view()),
    path('onboarding/educators/', eduOBViews.as_view())
]
