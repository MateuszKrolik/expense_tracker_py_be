from typing import List, TypeAlias, Union

from models.budget import BudgetBase
from models.category import CategoryBase
from models.expense import ExpenseBase

OfflineEntity: TypeAlias = Union[ExpenseBase, BudgetBase, CategoryBase]


def are_entities_offline(expenses_base: List[OfflineEntity]) -> bool:
    for expense_base in expenses_base:
        if expense_base.is_offline is not True:
            return False
    return True
