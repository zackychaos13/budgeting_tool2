from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect,HttpResponse, Http404
from django.contrib.auth import logout,login,authenticate
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.core.paginator import Paginator, EmptyPage, InvalidPage
from .models import Category, Budget, FundsAllocation, Transaction
from .forms import CategoryForm, CustomUserCreationForm, FundsAllocationForm, BudgetForm, TransactionForm


# Create your views below:

def registrationView(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # create initial misc category for new users
            Category.objects.create(user=user, name="Miscellaneous")
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=password)
            login(request, user)
            return HttpResponseRedirect('/')
    else:
        form = CustomUserCreationForm()
    return render(request, 'registration/register.html', {'form': form})


@login_required
def viewCategories(request):
    # grab all categories for logged in user
    categories = Category.objects.filter(user=request.user).order_by('id')

    if request.GET.get('err') == "1":
        error = "Error! Unable to delete category. All users must have at least one category for their account!"
    else:
        error = None

    ############
    # pagination:
    ############
    paginator = Paginator(categories, 4)
    try:
        page = int(request.GET.get('page', '1'))
    except:
        page = 1

    try:
        categories = paginator.page(page)
    except(EmptyPage, InvalidPage):
        categories = paginator.page(1)

    # Get the index of the current page
    index = categories.number - 1  # edited to something easier without index
    # This value is maximum index of your pages, so the last page - 1
    max_index = len(paginator.page_range)
    # calculate where to slice the list
    start_index = index - 3 if index >= 3 else 0
    end_index = index + 3 if index <= max_index - 3 else max_index
    # Get our new page range. In the latest versions of Django page_range
    # returns an iterator. Thus pass it to list, to make our slice possible
    # again.
    page_range = list(paginator.page_range)[start_index:end_index]

    context = {
        'categories': categories,
        'error': error,
        'page_range': page_range
    }
    return render(request, 'budget_app/categories.html', context=context)


# View Budgets view:
@login_required
def viewBudgets(request):
    '''
    Function provides user with an overview of budgets
    Use of objects.filter to get user's budgets; ordered by monthYear
    Calculate fundsSpent, fundsRemaining, and percentSpent
    Lists all data
    '''

    # gets all budgets
    budgets = Budget.objects.filter(user=request.user).order_by('-monthYear')
    budgetsList = []

    ############
    # pagination:
    ############
    paginator = Paginator(budgets, 4)
    try:
        page = int(request.GET.get('page', '1'))
    except:
        page = 1

    try:
        budgets = paginator.page(page)
    except(EmptyPage, InvalidPage):
        budgets = paginator.page(1)

    # Get the index of the current page
    index = budgets.number - 1  # edited to something easier without index
    # This value is maximum index of your pages, so the last page - 1
    max_index = len(paginator.page_range)
    # calculate where to slice the list for page range
    start_index = index - 3 if index >= 3 else 0
    end_index = index + 3 if index <= max_index - 3 else max_index
    # Get our new page range. In the latest versions of Django page_range
    # returns an iterator. Thus pass it to list, to make our slice possible
    # again.
    page_range = list(paginator.page_range)[start_index:end_index]

    ###################
    # build budgetsList:
    ###################

    for budget in budgets:
        transactions = Transaction.objects.filter(budget=budget)
        # calculations of fundsSpent, fundsRemaining, & percentSpent
        fundsSpent = 0.0
        for transaction in transactions:
            fundsSpent += float(transaction.amount)
        fundsRemaining = float(budget.fundsToBudget)-fundsSpent
        percentSpent = (fundsSpent/float(budget.fundsToBudget)) * 100
        # list budget items
        budgetsList.append({
            'id': budget.id,
            'monthYear': budget.monthYear,
            'fundsToBudget': budget.fundsToBudget,
            'fundsSpent': fundsSpent,
            'fundsRemaining': fundsRemaining,
            'percentSpent': percentSpent
        })

    context = {
        'budgets': budgetsList,
        'budgetsPaginator': budgets,
        'page_range': page_range
    }

    return render(request, 'budget_app/budgets.html', context=context)


@login_required
def viewFundsAllocations(request, budgetID):
    '''
    View funds allocations view (a.k.a. budget overiew)
    '''
    # 404 if invalid budget
    budget = get_object_or_404(Budget, user=request.user, pk=budgetID)
    # all FundsAllocations for specific budget
    fundsAllocations = FundsAllocation.objects.filter(budget=budget)

    totalAllocated = 0.0  # set to 0 intially
    totalSpent = 0.0  # set to 0 intially

    #######################
    # FundsAllocations List
    #######################
    allocationsList = []
    for allocation in fundsAllocations:
        totalAllocated += float(allocation.amount)
        transactions = Transaction.objects.filter(
            budget=budgetID,
            category=allocation.category
        )
        amountSpent = 0.0
        for transaction in transactions:
            amountSpent += float(transaction.amount)
        amountRemaining = float(allocation.amount) - amountSpent
        # prevent division by zero error.
        if allocation.amount == 0:
            percentSpent = 0
        else:
            percentSpent = (amountSpent / float(allocation.amount)) * 100
        allocationsList.append({
            'id': allocation.id,
            'category': allocation.category,
            'amountAllocated': allocation.amount,
            'amountSpent': amountSpent,
            'amountRemaining': amountRemaining,
            'percentSpent': percentSpent
        })
        totalSpent += amountSpent

    #######################
    # Total Percent Spent
    #######################
    # if no allocations yet, prevent a division by 0 error below
    if totalAllocated == 0:
        totalPercentSpent = 0
    else:
        totalPercentSpent = (totalSpent/totalAllocated)*100

    context = {
        'budget': budget,
        'fundsAllocations': allocationsList,
        'totalAllocated': totalAllocated,
        'totalSpent': totalSpent,
        'totalRemaining': totalAllocated-totalSpent,
        'totalPercentSpent': totalPercentSpent
    }
    return render(request, 'budget_app/fundsAllocations.html', context=context)


@login_required
def viewTransactions(request):
    '''
    view transactions view:
    '''
    budgets = Budget.objects.filter(user=request.user)
    categories = Category.objects.filter(user=request.user)
    categoryID = request.GET.get('c')
    budgetID = request.GET.get('b')

    ###################
    # Filtered Budget/Category
    # throws 404 errors if user tries to filter by/access budget/category
    # that doesnt exist or is not theirs.
    ###################
    budget = None
    category = None
    if budgetID:
        budget = get_object_or_404(Budget, user=request.user, pk=budgetID)
    if categoryID:
        category = get_object_or_404(
            Category,
            user=request.user,
            pk=categoryID
        )

    ###################
    # Funds Allocation
    ###################
    if (category and budget):
        fundsAllocation = FundsAllocation.objects.filter(
            budget=budget, category=category
        ).first()
    else:
        fundsAllocation = None

    ###################
    # Transactions
    ###################
    if category and budget:
        transactions = Transaction.objects.filter(
            user=request.user,
            category=category,
            budget=budget
        )
    elif category:
        transactions = Transaction.objects.filter(
            user=request.user,
            category=category
        )
    elif budget:
        transactions = Transaction.objects.filter(
            user=request.user,
            budget=budget
        )
    else:
        transactions = Transaction.objects.filter(user=request.user)

    ###################
    # Totals
    ###################
    totalSpent = sum([each.amount for each in transactions])
    if fundsAllocation:
        percentSpent = (totalSpent/fundsAllocation.amount)*100
        amountRemaining = fundsAllocation.amount - totalSpent
    else:
        percentSpent = None
        amountRemaining = None

    ############
    # pagination:
    ############
    paginator = Paginator(transactions.order_by('-date'), 15)
    try:
        page = int(request.GET.get('page', '1'))
    except:
        page = 1

    try:
        transactions = paginator.page(page)
    except(EmptyPage, InvalidPage):
        transactions = paginator.page(1)

    # Get the index of the current page
    index = transactions.number - 1  # edited to something easier without index
    # This value is maximum index of your pages, so the last page - 1
    max_index = len(paginator.page_range)
    # calculate where to slice the list
    start_index = index - 3 if index >= 3 else 0
    end_index = index + 3 if index <= max_index - 3 else max_index
    # Get our new page range. In the latest versions of Django page_range
    # returns an iterator. Thus pass it to list, to make our slice possible
    # again.
    page_range = list(paginator.page_range)[start_index:end_index]

    context = {
        'budgets': budgets,
        'categories': categories,
        'fundsAllocation': fundsAllocation,
        'transactions': transactions,
        'totalSpent': totalSpent,
        'amountRemaining': amountRemaining,
        'percentSpent': percentSpent,
        'filteredCategory': category,
        'filteredBudget': budget,
        'page_range': page_range
    }
    return render(request, 'budget_app/transactions.html', context=context)


@login_required
def newCategory(request):
    '''
    New category view. Shows CategoryForm and handles its POST data.
    (login required):
    '''
    # handle submitted form data
    if request.method == 'POST':
        form = CategoryForm(request.user, request.POST)
        if form.is_valid():
            # get_or_create used below so we don't create duplicate categories
            # (can't set category name to unique because then multiple users
            # couldnt have the same category names)
            # so basically if category exists, do nothing, otherwise create it
            Category.objects.get_or_create(
                user=request.user,
                name=form.cleaned_data['name']
            )
            # redirect back to view categories page
            return HttpResponseRedirect(reverse('viewCategories'))
    # no form submitted, show new category form/page:
    else:
        form = CategoryForm(request.user)
    return render(request, 'budget_app/new_category.html', {'form': form})


@login_required
def newBudget(request):
    if request.method == "POST":
        form = BudgetForm(request.user, request.POST)
        if form.is_valid():
            Budget.objects.create(
                user=request.user,
                monthYear=form.cleaned_data["monthYear"],
                fundsToBudget=form.cleaned_data["fundsToBudget"])
            return HttpResponseRedirect(reverse('viewBudgets'))
    else:
        form = BudgetForm(request.user)
    return render(request, 'budget_app/new_budget.html', {'form': form})


@login_required
def newFundsAllocation(request):
    '''
    New FundsAllocation view. Shows FundsAllocationForm and handles its POST
    data.
    '''
    budgetID = request.GET.get('b')
    # 404 if invalid budget
    budget = get_object_or_404(Budget, user=request.user, pk=budgetID)
    # handle submitted form data
    if request.method == 'POST':
        form = FundsAllocationForm(request.user, request.POST)
        if form.is_valid():
            budget = Budget.objects.get(
                user=request.user,
                pk=form.cleaned_data['budgetID']
            )
            FundsAllocation.objects.create(
                budget=budget,
                category=form.cleaned_data['category'],
                amount=form.cleaned_data['amount']
            )
            # redirect back to budget overview (viewFundsAllocations) page
            return HttpResponseRedirect(reverse(
                'viewFundsAllocations',
                kwargs={'budgetID': budget.id}
            ))
    else:  # no form submitted, show new allocation form/page:
        form = FundsAllocationForm(request.user)
    return render(
        request,
        'budget_app/new_fundsAllocation.html',
        {'form': form, 'budget': budget}
    )


@login_required
def newTransaction(request):
    if request.method == "POST":
        form = TransactionForm(request.user, request.POST)
        if form.is_valid():
            Transaction.objects.create(
                user=request.user,
                budget=form.cleaned_data["budget"],
                category=form.cleaned_data["category"],
                date=form.cleaned_data["date"],
                description=form.cleaned_data["description"],
                amount=form.cleaned_data["amount"]
            )
            return HttpResponseRedirect(reverse('viewTransactions')+"?c="+str(form.cleaned_data['category'].id)+"&b="+str(form.cleaned_data['budget'].id)) #redirect back to view transactions page for budget/category
    else:
        categoryID = request.GET.get('c')
        budgetID = request.GET.get('b')
        # pre-populate budget/category in new transaction form:
        if(categoryID or budgetID):
            form = TransactionForm(
                request.user,
                initial={'category': categoryID, 'budget': budgetID}
            )
        else:
            form = TransactionForm(request.user)
    return render(request, 'budget_app/new_transaction.html', {'form': form})


@login_required
def editCategory(request, categoryID):
    '''
    edit/"rename" category view (login required)
    category ID is past from URL (see urls.py)
    '''
    # find specified category by id (limit view to user's categories only)
    category = Category.objects.filter(id=categoryID, user=request.user)
    if request.method == 'POST':  # handle submitted form data:
        form = CategoryForm(request.user, request.POST)
        if form.is_valid():
            category.update(name=form.cleaned_data['name'])
            return HttpResponseRedirect(reverse('viewCategories'))
    else:
        # category not found (maybe user tried to specify ID in url that
        # wasn't theirs)
        if not category:
            # if cant find category, redirect to view categories
            return HttpResponseRedirect(reverse('viewCategories'))
        # show edit form/page:
        form = CategoryForm(request.user, instance=category[0])
    return render(
        request,
        'budget_app/edit_category.html',
        {'form': form, 'category': category[0]}
    )


@login_required
def editBudget(request, budgetID):
    '''Edit Budget view. Coming soon, hard coded data for now:'''
    budget = Budget.objects.filter(id=budgetID, user=request.user)
    if request.method == "POST":
        form = BudgetForm(request.user, request.POST)
        if form.is_valid():
            budget.update(fundsToBudget=form.cleaned_data["fundsToBudget"])
            return HttpResponseRedirect(reverse('viewBudgets'))
    else:
        # budget not found
        if not budget:
            # if cant find budget, redirect to view budgets
            return HttpResponseRedirect(reverse('viewBudgets'))
        # show edit form/page:
        form = BudgetForm(request.user, instance=budget[0])
    return render(
        request,
        'budget_app/edit_budget.html',
        {'form': form, 'budget': budget[0]}
    )


@login_required
def editFundsAllocation(request, allocationID):
    '''
    Edit FundsAllocation view. Shows FundsAllocationForm and handles its POST
    data.
    '''
    fundsAllocation = FundsAllocation.objects.filter(id=allocationID)
    # make sure fundsAllocation belongs to logged in user
    budget = get_object_or_404(
        Budget,
        user=request.user,
        pk=fundsAllocation[0].budget.id
    )
    # handle submitted form data:
    if request.method == 'POST':
        form = FundsAllocationForm(request.user, request.POST)
        if form.is_valid():
            fundsAllocation.update(
                category=form.cleaned_data['category'],
                amount=form.cleaned_data['amount']
            )
            return HttpResponseRedirect(reverse(
                'viewFundsAllocations',
                kwargs={'budgetID': budget.id}
            ))
    else:
        # fundsAllocation not found
        if not fundsAllocation:
            # if cant find allocation, redirect to budget overview
            return HttpResponseRedirect(reverse(
                'viewFundsAllocations',
                kwargs={'budgetID': budget.id})
            )
        # show edit form/page:
        form = FundsAllocationForm(request.user, instance=fundsAllocation[0])
    return render(
        request,
        'budget_app/edit_fundsAllocation.html',
        {'form': form, 'budget': budget, 'fundsAllocation': fundsAllocation[0]}
    )


@login_required
def editTransaction(request, transactionID):
    # finds transaction by id
    transaction = Transaction.objects.filter(
        id=transactionID,
        user=request.user
    )
    if request.method == "POST":  # handle form data
        form = TransactionForm(request.user, request.POST)
        if form.is_valid():
            # update budget, date, category, description, and amount
            transaction.update(
                budget=form.cleaned_data['budget'],
                date=form.cleaned_data["date"],
                category=form.cleaned_data["category"],
                description=form.cleaned_data["description"],
                amount=form.cleaned_data["amount"]
            )
            return HttpResponseRedirect(reverse('viewTransactions')+"?c="+str(form.cleaned_data['category'].id)+"&b="+str(form.cleaned_data['budget'].id))
    else:
        if not transaction:  # transaction not found
            raise Http404("Transaction not found")
        # shows form
        form = TransactionForm(request.user, instance=transaction[0])
    return render(
        request,
        'budget_app/edit_transaction.html',
        {'form': form, 'transaction': transaction[0]}
    )


@login_required
def deleteCategory(request, categoryID):
    '''
    category ID is past from URL (see urls.py)
    '''
    # find category by id (limit to user)
    category = Category.objects.filter(id=categoryID, user=request.user)
    if request.method == 'POST':  # if form submitted
        form = CategoryForm(request.user, request.POST)
        if Category.objects.filter(user=request.user).count() == 1:
            # redirect to view categories page to show error about not allowing
            # user to delete ALL categories
            return HttpResponseRedirect(reverse('viewCategories')+"?err=1")
        else:
            # delete specified category. note we didnt check form.is_valid(),
            # this is because it would come back as invalid due to not
            # specifying a category name (we're deleting by ID)
            category.delete()
            # redirect to view categories page
            return HttpResponseRedirect(reverse('viewCategories'))
    else:
        # category not found (maybe user tried to specify ID in url that
        # wasn't theirs)
        if not category:
            # if cant find category, redirect
            return HttpResponseRedirect(reverse('viewCategories'))
        # show delete form/page:
        form = CategoryForm(request.user, instance=category[0])
    return render(
        request,
        'budget_app/delete_category.html',
        {'form': form, 'category': category[0]}
    )


@login_required
def deleteBudget(request, budgetID):
    budget = Budget.objects.filter(id=budgetID, user=request.user)
    if request.method == 'POST':
        form = BudgetForm(request.user, request.POST)
        budget.delete()
        return HttpResponseRedirect(reverse('viewBudgets'))
    else:
        # budget not found
        if not budget:
            # if cant find budget, redirect
            return HttpResponseRedirect(reverse('viewBudgets'))
        form = BudgetForm(request.user, instance=budget[0])
    return render(
        request,
        'budget_app/delete_budget.html',
        {'form': form, 'budget': budget[0]}
    )


@login_required
def deleteFundsAllocation(request, allocationID):
    '''
    Delete FundsAllocation view. Shows FundsAllocationForm and handles its POST
    data.
    '''
    fundsAllocation = FundsAllocation.objects.filter(id=allocationID)
    if not fundsAllocation:
        raise Http404("Allocation Does Not Exist")
    # make sure fundsAllocation belongs to logged in user
    budget = get_object_or_404(
        Budget,
        user=request.user,
        pk=fundsAllocation[0].budget.id
    )
    if request.method == 'POST':  # if form submitted
        form = FundsAllocationForm(request.user, request.POST)
        fundsAllocation.delete()  # delete specified allocation.
        # redirect to view budgets page
        return HttpResponseRedirect(reverse(
            'viewFundsAllocations',
            kwargs={'budgetID': budget.id}
        ))
    else:
        if not fundsAllocation:
            # if cant find allocation, redirect
            return HttpResponseRedirect(reverse(
                'viewFundsAllocations', kwargs={'budgetID': budget.id}
            ))
        # show delete form/page:
        form = FundsAllocationForm(request.user, instance=fundsAllocation[0])
    return render(
        request,
        'budget_app/delete_fundsAllocation.html',
        {'form': form, 'budget': budget, 'fundsAllocation': fundsAllocation[0]}
    )


@login_required
def deleteTransaction(request, transactionID):
    # finds transaction by id
    transaction = Transaction.objects.filter(
        id=transactionID,
        user=request.user
    )
    if request.method == 'POST':
        form = TransactionForm(request.user, request.POST)
        # for redirection variables
        budgetRedirectID = str(transaction[0].budget.id)
        # for redirection variables
        categoryRedirectID = str(transaction[0].category.id)
        transaction.delete()
        return HttpResponseRedirect(reverse(
            'viewTransactions'
        )+"?b="+budgetRedirectID+"&c="+categoryRedirectID)
    else:
        if not transaction:
            raise Http404("Transaction not found")
        form = TransactionForm(request.user, instance=transaction[0])
    return render(
        request,
        'budget_app/delete_transaction.html',
        {'form': form, 'transaction': transaction[0]}
    )

@login_required
def visualizeSpending(request):
    '''
    visualize spending view:
    '''    
    budgets=Budget.objects.filter(user = request.user)
    budgetID=request.GET.get('b')
    

    ###################  
    # Filtered Budget/Category
    # throws 404 errors if user tries to filter by/access budget
    # that doesnt exist or is not theirs.
    ###################
    budget=None
    if budgetID:
        budget = get_object_or_404(Budget, user=request.user, pk=budgetID) 

    ###########################
    # Build spentByCategoryDict
    ###########################
    if budget:
        transactions=Transaction.objects.filter(user=request.user, budget=budget)
    else:
        transactions=Transaction.objects.filter(user=request.user)
        
    spentByCategoryDict = {}
    for transaction in transactions:
        if transaction.category.name not in spentByCategoryDict:
            spentByCategoryDict[transaction.category.name] = transaction.amount
        else:
            spentByCategoryDict[transaction.category.name] += transaction.amount

    context = {
        'budgets': budgets,
        'filteredBudget': budget,
        'spentByCategoryDict':spentByCategoryDict,
    }
    return render(request,'budget_app/visualize.html',context=context)

#logout "view":
def logout_view(request):
    logout(request)  # log user out
    return HttpResponseRedirect('/')
