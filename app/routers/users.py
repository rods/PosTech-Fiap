import boto3
import os
from app.internal.database import dynamodb, table
from boto3.dynamodb.conditions import Attr
from fastapi import APIRouter
from fastapi import Request
import json
import logging
import uuid

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/v1",
    tags=["v1"],
)

@router.post("/users/create")
def criar_usuario(username: str, email:str, password:str ):
    
    if not username or not email or not password:
        return {"error": "Todos os campos são obrigatórios"}
  
    user_exist = table.scan(FilterExpression=Attr('username').eq(username))
    if user_exist['Items']:
        return {"error": "Usuário já existe"}
    else:
        response = table.put_item(
            Item={
                'id': str(uuid.uuid4()),
                'username': username,
                'email': email,
                'password': password
            }
        )
        return response

@router.get("/users/list/{username}")
def listar_usuario(username: str):
    if not username :
        return {"error": "Todos os campos são obrigatórios"}

    user_exist = table.scan(FilterExpression=Attr('username').eq(username))
    ProjectionExpression='username, id, email'
    if user_exist['Items']:
        return {"User": user_exist['Items']}
    else:
        return {"Usuário não encontrado"}
