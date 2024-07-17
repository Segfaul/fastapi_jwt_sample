from typing import Optional

from pydantic._internal._model_construction import ModelMetaclass


class _AllOptionalMeta(ModelMetaclass):
    '''
    AllOptional metaclass based on Pydantic MetaClass model

    Makes all fields in a model optional (used for PATCH requests)
    '''
    def __new__(self, name, bases, namespaces, **kwargs):
        annotations = namespaces.get('__annotations__', {})
        for base in bases:
            annotations.update(base.__annotations__)
        for field in annotations:
            if not field.startswith('__'):
                annotations[field] = Optional[annotations[field]]
                namespaces[field] = None
        namespaces['__annotations__'] = annotations
        return super().__new__(self, name, bases, namespaces, **kwargs)
