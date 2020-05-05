from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views

from homepage import views as home_v
from coming_soon import views as cs_views
from signup.views import SignUpView, ActivateAccount
from confirm_reg import views as conf_email_views
from amateurOnboarding.views import AmaOBViews
from proOnboarding.views import proOBViews
from eduOnboarding.views import eduOBViews
from user_home import views as home_view
from obs_propose.views import ObsPropViews, ObsPropEdit
from prof_obs_sel.views import obs_sel_views
from prof_obs_sel.views import SelectObservatory
from prof_obs_overview.views import Obs_Overview_views, remove_obser
from observability_calc.views import obs_calc_views
from ama_obs_overview.views import *
from logout_account import views as logoutview
from error_pages import views as err_views



urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),
    path('', cs_views.index),
    path('landingpage/',  home_v.index),
    path('signup/', SignUpView.as_view(), name='signup'),
    path('activate/<uidb64>/<token>/', ActivateAccount.as_view(), name='activate'),
    path('signup/activate/confirm_email', conf_email_views.index),
    path('activate/dir_sel/', conf_email_views.init_sel),
    path('onboarding/amateur/', AmaOBViews.as_view(), name = 'onboarding_amateur'),
    path('amateur/', AmaOBViews.as_view(), name = 'post_ob_amateur'),
    path('onboarding/professional/', proOBViews.as_view(), name = 'professional_onboarding'),
    path('onboarding/educators/', eduOBViews.as_view(), name = 'educator_onboarding'),
    path('user/home/', home_view.index),
    path('obsprop/', ObsPropViews.as_view()),
    path('obsprop/edit/<pk>', ObsPropEdit.as_view()),
    path('obs_sel/<pk>',obs_sel_views.as_view()),
    path(r'obssel/<slug>-<pk>/', SelectObservatory.as_view(), name='obs_sel'),
    path('obs/overview/<pk>', Obs_Overview_views.as_view()),
    path(r'obs_calc/<slug>-<pk>', obs_calc_views.as_view(), name = 'obs_calc'),
    path(r'obs_rev_ama/<pk>', ama_overview_views.as_view()),
    path(r'accept/<slug>-<pk>', accept_obs.as_view()),
    path(r'reject/<slug>-<pk>', reject_obs.as_view()),
    path(r'accounts/logout', logoutview.logout_view),
    path(r'delobs/<pk>', home_view.delete_obs),
    path(r'obs/overview/delete/<slug>-<pk>', remove_obser.as_view()),

]


urlpatterns = urlpatterns + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


handler404 = err_views.handler404
handler500 = err_views.handler500
#handler502 = err_views.handler502
