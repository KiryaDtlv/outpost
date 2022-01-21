from uuid import uuid4
from .exceptions import ValidationError
from .types import Outpost, OutpostProvider
from .alchemy import AlchemyFieldGenerator
from typing import Iterable, Optional
from dataclasses import dataclass
from datetime import datetime
from models import Phone, User



class PhoneValidator(Outpost):
    op = OutpostProvider.from_model(Phone)
    

dataset = {
    'id': "raiders",
    'deleted': 'False',
    'user_id': 1,
    'number': '9634343434'
}

def pretty_print_model(instance):
    print(f'{instance.__class__.__name__}(')
    for field in AlchemyFieldGenerator(instance.__class__).all_fields():
        print(f'\t{field}={getattr(instance, field)}')

    print(')')


try:
    a = PhoneValidator.create_model(dataset)
except ValidationError as e:
    print(f'({a.__class__.__name__}) {a}')
else:
    pretty_print_model(a)



# @dataclass
# class Phone:
#     number: int


# @dataclass
# class User:
#     id: int
#     name: Optional[str]
#     hash: Optional[str]
#     phone: Phone

# class PhoneValidator(Outpost):
#     config = OutpostProvider.from_model(Phone)
#     config.requirements = config.fields.number
#     # config.require(config.fields.number)

#     @config.validator(config.fields.number)
#     def number(value):
#         st = str(value).strip()
#         if st.startswith('+'):
#             st = st.replace('+', '')

#         if not st.isnumeric():
#             raise ValidationError('phone number can`t contain letters')

#         if st.startswith('7'):
#             st = st.replace('7', '8')
        
#         if len(st) < 11:
#             raise ValidationError('phone number is too small. 11 symbols required.')

#         return int(st)

# class CreatePhoneValidator(PhoneValidator):
#     config = PhoneValidator.config
    
    

# class UserValidator(Outpost):
#     config = OutpostProvider.from_model(User)
#     config.validator(config.fields.phone, PhoneValidator)
#     config.missing_value = None

# class UpdateUserValidator(UserValidator):
#     config = UserValidator.config
#     config.raise_readonly = True
#     config.require(config.fields.id & (
#         config.fields.hash |
#         config.fields.name |
#         config.fields.phone
#     ))

# class SomeUserValidator(UpdateUserValidator):
#     config = UpdateUserValidator.config
    
# class CreateUserValidator(UserValidator):
#     config = UserValidator.config
#     config.validator(config.fields.phone, CreatePhoneValidator)

#     # config.readonly = [config.fields.id]

#     config.require(
#         config.fields.name &
#         (config.fields.hash |
#         config.fields.id) &
#         config.fields.phone
#         )

#     config.defaults[config.fields.name] = "Default user"

    
#     ...

# create_dataset = {
#     'id': '12',
#     'name': True,
#     'phone': {
#         "number": "+79639499629"
#     }
# }

# update_dataset = {
#     'id': 'vigor',
#     'name': 'Vigor',
#     'phone': [
#         {'number': '+79639499629'}
#     ]

# }

# try:
#     start = datetime.now()
#     a = CreateUserValidator.defaults({CreateUserValidator.fields.hash: str(uuid4()) }).validate(create_dataset).map()
# except ValidationError as e:
#     a = e

# print(datetime.now() - start)
# print('create:', a)

# # try:
# #     print(CreateUserValidator.validation_results(create_dataset))
# #     a = CreateUserValidator.create_model(create_dataset)
# # except ValidationError as e:
# #     a = e

# # print('create:', a)

# # try:
# #     a = UpdateUserValidator.create_model(update_dataset)
# # except ValidationError as e:
# #     a = e

# # print('update:', a)