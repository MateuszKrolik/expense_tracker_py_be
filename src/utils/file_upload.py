import json
from typing import Union
from google.cloud import storage
from fastapi import File, Form, HTTPException, UploadFile
import os
from datetime import datetime

from src.dtos.expense import ExpenseCreateRequest
from src.models.expense import ExpenseBase


async def upload_to_gcs(
    file: UploadFile, user_id: str, bucket_name: str = os.getenv("GCS_BUCKET")
) -> str:
    """Uploads file to GCS and returns public URL"""
    try:
        credentials = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
        if credentials:
            client = storage.Client.from_service_account_json(credentials)
        else:
            client = storage.Client()
        bucket = client.bucket(bucket_name)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"expenses/{user_id}/{timestamp}-{file.filename}"

        blob = bucket.blob(filename)
        blob.upload_from_file(file.file, content_type=file.content_type)
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Unexpected exception occurred: {str(e)}"
        )

    return f"https://storage.googleapis.com/{bucket_name}/{filename}"


async def parse_expense_create_request(
    expense_base: str = Form(
        ...,
        description="""
        Example JSON:
        {
            "name": "string",
            "amount": 0,
            "category_id": "5af1f98c-bb7d-4b73-aa17-738577283bd2",
            "is_offline": false,
            "is_public": false,
            "timestamp": "2025-05-27"
        }
        """,
    ),
    image: Union[UploadFile, str, None] = File(default=None),
) -> ExpenseCreateRequest:
    # Fix empty string file inputs
    if isinstance(image, str) and image == "":
        image = None
    try:
        expense_data = json.loads(expense_base)
        return ExpenseCreateRequest(
            expense_base=ExpenseBase(**expense_data), image=image
        )
    except json.JSONDecodeError as e:
        raise HTTPException(status_code=400, detail=f"Invalid JSON: {str(e)}")
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Unexpected exception occurred: {str(e)}"
        )
