import csv
from typing import List
from fastapi import status, HTTPException
from models.category import Category as CategoryModel
from uuid import UUID

CATEGORIES_PATH = "data/categories.csv"


def get_all_categories() -> List[CategoryModel]:
    try:
        with open(CATEGORIES_PATH, "r") as f:
            reader = csv.DictReader(f)
            rows = []
            for row in reader:
                rows.append(CategoryModel(**row))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )

    return rows


def get_all_category_ids() -> List[UUID]:
    categories = get_all_categories()
    category_ids = []
    for category in categories:
        category_ids.append(category.id)

    return category_ids
