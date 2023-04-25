from django.db import models
from django.contrib.auth.models import AbstractUser


# Custom user model (best practice)
class User(AbstractUser):
    pass


class Category(models.Model):
    '''
    User(ForeignKey)
    name
    '''
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    name = models.CharField(max_length=100, unique=False)

    def __str__(self):
        return "User: %s, Category: %s" % (self.user, self.name)


class Budget(models.Model):
    '''
    User(ForeignKey)
    monthYear
    fundsToBudget
    '''
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    monthYear = models.DateField()
    fundsToBudget = models.DecimalField(decimal_places=2, max_digits=99)

    def __str__(self):
        return "User: %s, monthYear: %s, fundsToBudget: %.02f" % (
            self.user, self.monthYear, self.fundsToBudget
        )


class Transaction(models.Model):
    '''
    user(ForeignKey)
    budget(ForeignKey)
    category(ForeignKey)
    date
    description
    amount
    '''
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    budget = models.ForeignKey(Budget, on_delete=models.CASCADE, null=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, null=True)
    date = models.DateField()
    description = models.CharField(max_length=100, unique=False)
    amount = models.DecimalField(decimal_places=2,  max_digits=99)

    def __str__(self):
        return "budget: %s, category: %s, date: %s, description \"%s\", amount: %.02f" % (
            self.budget.monthYear,
            self.category.name,
            self.date,
            self.description,
            self.amount
        )


class FundsAllocation(models.Model):
    '''
    budget(ForeignKey)
    category(ForeignKey)
    amount
    '''
    budget = models.ForeignKey(Budget, on_delete=models.CASCADE, null=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, null=True)
    amount = models.DecimalField(decimal_places=2, max_digits=99)

    def __str__(self):
        return "budget: %s, category: %s, amount: %.02f" % (
            self.budget.monthYear,
            self.category.name,
            self.amount
        )
