from fastapi import APIRouter

from webapp.api.crud.const import API_PREFIX

tour_router = APIRouter(prefix=f'{API_PREFIX}/tour', tags=['Tour'])
