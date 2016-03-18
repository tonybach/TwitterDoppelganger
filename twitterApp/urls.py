from django.conf.urls import url

from . import views

app_name = 'twitterApp'
urlpatterns = [
	#ex: /polls/
	url(r'^$', views.IndexView.as_view(), name='index'),

	url(r'^signIn$', views.signIn, name='signIn'),

	url(r'^signedIn$', views.SignedInView.as_view(), name='signedIn'),

	url(r'^submitEmail$', views.submitEmail, name='submitEmail'),

	url(r'^emailSubmitted$', views.EmailSubmittedView.as_view(), name='emailSubmitted')
]