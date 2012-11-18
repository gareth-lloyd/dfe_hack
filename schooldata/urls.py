from django.conf.urls import patterns, url

urlpatterns = patterns('schooldata.views',
    url(r'^plot/$', 'plot_json', name='plot-json'),
    url(r'^showplot/$', 'show_plot', name='show-plot'),

    url(r'^lea/(?P<id>\d+)/(?P<stat>\w+)/$', 'lea', name='lea'),
    url(r'^leas/$', 'leas', name='leas'),
)
