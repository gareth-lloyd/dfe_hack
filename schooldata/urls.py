from django.conf.urls import patterns, include, url

urlpatterns = patterns('schooldata.views',
    url(r'^plot/$', 'plot_json', name='plot-json'),
    url(r'^showplot/$', 'show_plot', name='show-plot'),
)
