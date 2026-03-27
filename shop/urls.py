from django.urls import path
from . import views

app_name = 'shop'

urlpatterns = [
    path('', views.product_list, name='product_list'),
    path('search/', views.product_search, name='product_search'),
    path('new-arrivals/', views.new_arrivals_view, name='new_arrivals'),
    path('collections/', views.collections_overview, name='collections'),
    path('about/', views.company_about, name='about'),
    path('careers/', views.company_careers, name='careers'),
    path('press/', views.company_press, name='press'),
    path('support/contact/', views.support_contact, name='support_contact'),
    path('support/shipping-returns/', views.support_shipping_returns, name='shipping_returns'),
    path('support/hub/', views.support_overview, name='support_overview'),
    path('telemetry/', views.telemetry_event, name='telemetry_event'),
    path('<slug:category_slug>/', views.product_list, name='product_list_by_category'),
    path('<int:id>/<slug:slug>/', views.product_detail, name='product_detail'),
]
