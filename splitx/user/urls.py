from django.urls import path
from . import views

urlpatterns = [
    path("login/", views.login, name="login"),
    path("signup/", views.signup, name="signup"),
    path("refresh/", views.refresh, name="refresh"),
    path("user/", views.user, name="user-list"),
    path("expense/", views.expense, name="expense-list"),
    path("expense/create", views.create_expense, name="expense-create"),
    path("expense/split", views.expense_split, name="expense-spit"),
    path("settlement/", views.settlement, name="settlement"),
    # path("settlement/settle", views.settle, name="settle"),
    path("stats/monthly", views.stats_monthly, name="monthly-stats"),
    # path("smart-bill/", views.smart_bill, name="smart-bill"),
    # path("group/", views.group, name="group"),
    
]