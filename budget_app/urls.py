from django.urls import path
from django.views.generic.base import RedirectView
from . import views
from .forms import LoginForm
from django.contrib.auth import views as auth_views

# urls for our app:
urlpatterns = [
    path('', RedirectView.as_view(pattern_name='viewBudgets', permanent=False), name='siteIndex'), #homepage redirects to view categories for now
    path('login/', auth_views.LoginView.as_view(authentication_form=LoginForm),name='login'),
    path('categories/',views.viewCategories, name='viewCategories'),
    path('budgets/',views.viewBudgets, name='viewBudgets'),
    path('budgets/<int:budgetID>',views.viewFundsAllocations, name='viewFundsAllocations'),
    path('transactions/',views.viewTransactions, name='viewTransactions'),
    path('new/category/',views.newCategory,name='newCategory'),
    path('new/budget/',views.newBudget,name='newBudget'),
    path('new/allocation/',views.newFundsAllocation,name='newFundsAllocation'),
    path('new/transaction/',views.newTransaction,name='newTransaction'),
    path('edit/category/<int:categoryID>',views.editCategory,name='editCategory'),
    path('edit/budget/<int:budgetID>',views.editBudget,name='editBudget'),
    path('edit/allocation/<int:allocationID>',views.editFundsAllocation,name='editFundsAllocation'),
    path('edit/transaction/<int:transactionID>',views.editTransaction,name='editTransaction'),
    path('delete/category/<int:categoryID>',views.deleteCategory,name='deleteCategory'),
    path('delete/budget/<int:budgetID>',views.deleteBudget,name='deleteBudget'),
    path('delete/allocation/<int:allocationID>',views.deleteFundsAllocation,name='deleteFundsAllocation'),
    path('delete/transaction/<int:transactionID>',views.deleteTransaction,name='deleteTransaction'),
    path('visualize/',views.visualizeSpending, name='visualizeSpending'),
    path('logout/',views.logout_view,name='logout'),
    path('register/',views.registrationView,name='register'),
]