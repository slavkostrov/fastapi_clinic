from enum import Enum
from typing import List
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse, Response
from pydantic import BaseModel

app = FastAPI()


class DogType(str, Enum):
    terrier = "terrier"
    bulldog = "bulldog"
    dalmatian = "dalmatian"


class Dog(BaseModel):
    name: str
    pk: int
    kind: DogType


class Timestamp(BaseModel):
    id: int
    timestamp: int


dogs_db = {
    0: Dog(name='Bob', pk=0, kind='terrier'),
    1: Dog(name='Marli', pk=1, kind="bulldog"),
    2: Dog(name='Snoopy', pk=2, kind='dalmatian'),
    3: Dog(name='Rex', pk=3, kind='dalmatian'),
    4: Dog(name='Pongo', pk=4, kind='dalmatian'),
    5: Dog(name='Tillman', pk=5, kind='bulldog'),
    6: Dog(name='Uga', pk=6, kind='bulldog')
}

post_db = [
    Timestamp(id=0, timestamp=12),
    Timestamp(id=1, timestamp=10)
]


def _get_dog_by_pk(pk: int) -> Dog | None:
    dog: Dog | None = dogs_db.get(pk)
    if dog is None:
        raise HTTPException(
            status_code=409,
            detail=f"Specified PK ({pk}) doesn't exist."
        )
    return dog


@app.get(
    path="/",
    summary="Root",
)
def root() -> Response:
    """Service root with empty json as response."""
    return JSONResponse(content={})


@app.post(
    path="/post",
    summary="Get Post",
)
def post(timestamp: Timestamp) -> Timestamp:
    """Save timestamp to storage and return it."""
    post_db.append(timestamp)
    return timestamp


@app.get(path="/dog")
def get_dogs(kind: DogType | None = None) -> List[Dog]:
    dogs_list = list(dogs_db.values())
    if kind:
        dogs_list = list(filter(lambda dog: dog.kind == kind.value, dogs_list))
    return dogs_list


@app.post(path="/dog")
def create_dog(dog: Dog) -> Dog:
    """Create new dog and store it into storage."""
    if dog.pk in dogs_db:
        raise HTTPException(
            status_code=409,
            detail=f"Specified PK ({dog.pk}) already exists."
        )
    dogs_db[dog.pk] = dog
    return dog
   

@app.get(path="/dog/{pk}")
def get_dog_by_pk(pk: int) -> Dog:
    """Return dog by pk if exists, else raise error with 409 status_code."""
    return _get_dog_by_pk(pk=pk)


@app.patch(path="/dog/{pk}")
def update_dog(pk: int, dog: Dog) -> Dog:
    """Update dog with given primary key.
    
    If pk isn't equal to dog pk, raise error.
    If pk isn't exist, raise error.
    
    Return dog if success.
    """
    if pk != dog.pk:
        raise HTTPException(
            status_code=409,
            detail="Input PK isn't equal to Dog object `pk` attribute."
        )
    old_dog = _get_dog_by_pk(pk=pk)
    dogs_db[old_dog.pk] = dog
    return dog

