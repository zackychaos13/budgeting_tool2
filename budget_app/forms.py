from django import forms
from django.core import validators
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from .models import User, Category, FundsAllocation, Budget, Transaction
from django.db.models import Sum


class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = UserCreationForm.Meta.fields


class LoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super(LoginForm, self).__init__(*args, **kwargs)
    username = forms.CharField(widget=forms.TextInput())
    password = forms.CharField(widget=forms.PasswordInput())


class BudgetForm(forms.ModelForm):
    # hidden field to determine whether we are creating or editing.
    editing = forms.CharField(required=False)

    class Meta:
        model = Budget
        fields = ['monthYear', 'fundsToBudget']

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)

    def clean(self):
        '''overriden clean method'''
        # use built in cleans, plus our added stuff below:
        cleaned_data = super(BudgetForm, self).clean()
        if not self.cleaned_data.get('monthYear'):
            raise forms.ValidationError("Error! Month / Year Field Required!")
        if self.cleaned_data.get('editing'):
            return cleaned_data
        budget_exists = Budget.objects.filter(
            user=self.user,
            monthYear=cleaned_data['monthYear']
        )
        # if specified budget exists, throw form error.
        if budget_exists:
            raise forms.ValidationError(
                "Error! Budget for \"%s\" Already Exists"
                % cleaned_data['monthYear']
            )
        # if no errors raised, return cleaned_data
        return cleaned_data


class CategoryForm(forms.ModelForm):
    '''
    category form, handles creating/editing/deleting categories.
    '''
    class Meta:
        model = Category
        fields = ['name']

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)

    def clean(self):
        '''overriden clean method'''
        # use built in cleans, plus our added stuff below:
        cleaned_data = super(CategoryForm, self).clean()
        category_exists = Category.objects.filter(
            user=self.user,
            name=cleaned_data['name']
        )
        # if specified category name exists, throw form error.
        if category_exists:
            raise forms.ValidationError("Error! Category Name Already Exists")
        else:
            return cleaned_data


class CategoryModelChoiceField(forms.ModelChoiceField):
    '''
    Custom ModelChoiceField for displaying category names as selection choices
    in FundsAllocationForm and TransactionForm
    '''

    def label_from_instance(self, obj):
        return obj.name


class FundsAllocationForm(forms.ModelForm):
    '''
    FundsAllocation form, handles creating/editing/deleting FundsAllocations.
    '''
    # extra fields:
    # hidden field to determine whether we are creating or editing.
    editing = forms.CharField(required=False)
    budgetID = forms.IntegerField(required=False)
    allocationID = forms.IntegerField(required=False)

    class Meta:
        model = FundsAllocation
        fields = ['category', 'amount']

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)
        self.fields["category"] = CategoryModelChoiceField(
            Category.objects.filter(user=self.user)
        )

    def clean(self):
        '''overriden clean method'''
        # use built in cleans, plus our added stuff below:
        cleaned_data = super(FundsAllocationForm, self).clean()
        budget = Budget.objects.get(
            user=self.user,
            pk=cleaned_data['budgetID']
        )
        allocation_exists = FundsAllocation.objects.filter(
            budget=budget,
            category=cleaned_data['category']
        )
        if not budget:
            raise forms.ValidationError("Error! Invalid Budget!")
        # if specified allocation exists, throw form error. (unless editing
        # existing allocation)
        elif allocation_exists and not self.cleaned_data.get('editing'):
            raise forms.ValidationError(
                "Error! Allocation Already Exists For This Category & Budget!"
            )
        elif allocation_exists and self.cleaned_data.get('editing') and allocation_exists[0].id != self.cleaned_data.get('allocationID'): #if editing/changing category to one where an allocation already exists, throw error.
            raise forms.ValidationError(
                "Error! Allocation Already Exists For This Category & Budget!"
            )
        else:
            if self.cleaned_data.get('editing'):
                allocations = FundsAllocation.objects.filter(budget=budget).exclude(pk=self.cleaned_data['allocationID'])
            else:
                allocations = FundsAllocation.objects.filter(budget=budget)
            aggregatedAllocations = allocations.aggregate(Sum('amount')).get('amount__sum') or 0
            if (aggregatedAllocations + self.cleaned_data['amount']) > budget.fundsToBudget:
                raise forms.ValidationError("Error! Cumulative funds allocations for this budget exceed total amount of funds to budget!")
            return cleaned_data


class BudgetModelChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return obj.monthYear.strftime('%B %Y')


class TransactionForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = ['budget', 'category', 'date', 'description', 'amount']

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)
        self.fields["category"] = CategoryModelChoiceField(
            Category.objects.filter(user=self.user)
        )
        self.fields["budget"] = BudgetModelChoiceField(
            Budget.objects.filter(user=self.user)
        )
