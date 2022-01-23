# outpost
Powerful python data validation module

Предоставляет функуионал валидация и маппинга входящих данных по описанным моделям.

## Почему не pydantic
- pydantic не обеспечивает достаточного функционала (см ниже)

----
## Функционал
- Автоматическое приведение к типам с поддержкой модуля typing
- Сложные логические правила для обязательных полей
- Сложные правила валидации
- Валидация вложенных моделей
- Описание readonly полей
- Указание значений по-умолчанию
- !Валиация комбинаций полей (WIP)
- Наследование правил с возможностью модификации
- Несколько режимов валидации:
  - Упрощенный: простой маппинг модели по входящему набору данных
  - Расширенный: ручное выполнение с помощью chain-методов c базовой локальной модификацией правил валидации
  - Сложный: Контекстная валидация с возможностью полной локальной модификации правил валидации

## Поддержка моделей данных
- dataclasses
- модели sqlalchemy.DeclarativeMeta 

## Использование
### Базовые и ситуативные валидаторы
Базовый валидатор - это статический класс, унаследованный от Oupost, с определенными в нем правилами валидации\
(поле для хранения правил валидации может называться как угодно)
```python
# Создание нового валидатора
class SomeValidator(Outpost):
    # создание правил валидации на основе ранее описанной модели данных
    custom_configuration_name = OutpostProvider.from_model(Some)
```
Базовый валидатор выполняет только проверку типов данных в соответствии с указанными в модели

Ситуативный валидатор - это статический класс, унаследованный от базового валидатора,\
в котором правила валидации унаследованы явно, а так же указаны более строгие правила валидации данных (если необходимо)
```python
# Создание валидатора для кейса "создание" модели Some
class SomeCreateValidator(SomeValidator):
    # явное наследование правил валидации для возможности модификации
    op = SomeValidator.custom_configuration_name
    # указание обязательного поля
    op.requiremets = op.fields.name
    
    # ПРИМЕР НЕПРАВИЛЬНОГО ИСПОЛЬЗОВАНИЯ
    # В рамках иерархии валидаторов уже существуют базовые правила валидации.
    # Не создавайте новые, используйте старые и расширяйте их
    op = OutpostProvider.from_model(Some)

```


Рекомендуется создавать базовый валидатор для каждой валидируемой модели, и на его основе создавать ситуативные.\
Однако в базовом валидаторе технически могут быть описаны сколь угодно сложные правила валидации.\
Поступайте так, если валидация данных необходима в одном единственном случае использования модели.

## Функционал описания правил валидации (OutpostProvider)
Для описания правил валидации используется Generic класс OutpostProvider, который инифиализируется с помощью специального статического метода: `.from_model(model:Union[dataclass, DeclarativeBase])`\
### Провайдер полей модели
Созданный на основе модели OutpostProvider содержит провайдер полей модели - `fields`, содержащий перечисляемый тип ModelField, описывающий все пригодные для валидации поля описанной модели\
(Для датаклассов это поля, содержащие аннотацию типа, для sqlalchemy это колонки и relationship's)

```python
# модель данных
@dataclass
class Some:
    name: str
    value: Optional(int)
    
# параметры валидации на основе модели данных
op = OutpostProvider.from_model(Some)

# обращения к полям модели данных
op.fields.name
op.fields.value
```
Дальнейшее описание всех правил валидации основано на использовании провайдера полей модели

### Функционал определения обязательных полей (requirements)
Параметры валидации позволяют указать сложные логические правила для обязательных полей модели данных.\
Для этого экземпляр OutpostProvider предоставляет метод `.require`, или свойство `requirements`\
В метод или свойство могут быть записаны отдельные ModelField, или их логические комбинации.\
Используйте синтаксис логических и/или для определения.\
Множественный вызов метода `.require` объединит все переданные поля логическим И.\
Аналогично условием И объединяются правила в случае наследования валидаторов.

```python
# Определение обязательность полей   name AND value
op.require(op.fields.name & op.fields.value)

# Эквивалентная запись
op.require(op.fields.name)
op.require(op.fields.value)

# Эквивалентная запись, но для определения условия ИЛИ
op.requirements = op.fields.name | op.fields.value
```
Так-же возможно использование описательных классов из oupost.rules.[Require, OR, AND, NOT]

### Функционал определения readonly полей
Список readonly полей может быть указан в свойстве `.readonly` параметров валидации

```python
# Определение readonly поля value
op.readonly = [op.fields.value]
```
По-умолчанию readonly поля, переданные во входящем наборе данных будут отфильтрованы.\
Однако если установить `op.raise_readonly = True`, то при получении значения для readonly поля будет поднято исключение.\
Так-же существует схожий параметр: `op.raise_unnecessary`, при установке которого в True будет поднято исключение в случае передачи\
во входящем наборе данных полей, не определенных в модели.

### Функционал определения значений по-умолчанию
Значения по-умолчанию для полей модели могут быть записаны в свойство `op.defaults`
```python
# Определение значений по-умолчанию для полей name и value
op.defaults = {
  op.fields.name: "John",
  op.fields.values: 0
}
```
**Внимание! Значения по-умолчанию подлежат валидации типов.**
Так-же есть возможность определить специальное значение для всех полей, которые не были переданы во входящем наборе данных для случая,\
когда создание модели невозможно без указания значений всем ее полям (например dataclass)\
В примере ниже показано как задать значение None для всех остутствующих полей\
`op.missing_value = None`

### Функционал определения сложных правил валидации для поля
#### Для простых полей
Используйте метод `.validator` как декоратор, в аргумент которого передайте ModelField соответствующего поля.\
Декорируемая функция должна поднять ValidationError в случае ошибки, или вернуть провалидированное и нормальзованное значение.
```python
@op.validator(op.fields.name)
def name_validator(value):
  if len(name) < 3:
    raise ValidationError("Name is too short")
  return value
```
По-умолчанию значения, полученные в результате сложной валидации дополнительно проходят проверку типа, однако ее можно отключить:
```python
# отключение проверки типа для результата
@op.validator(op.fields.name, check_result_type=False)
def name_validator(value):
  if len(name) < 3:
    raise ValidationError("Name is too short")
  return SomeOther(value)
```
#### Для вложенных моделей
Используйте метод `.validator` для определения Outpost валидатора для вложенной модели.
Рассмотрим пример:
```python
# Описание модели Phone
@dataclass
class Phone:
    number: int


# Описание модели User
@dataclass
class User:
    id: int
    name: Optional[str]
    hash: Optional[str]
    # Используем ранее определенную модель Phone
    # Тип Iterable будет корректно обработан
    phones: Iterable[Phone]
    
    
# Определение валидатора для Phone с обязательным полем number
class PhoneValidator(Outpost):
    config = OutpostProvider.from_model(Phone)
    config.requirements = config.fields.number
    
# Определение валидатора для User
class UserValidator(Outpost):
    config = OutpostProvider.from_model(User)
    
    # Указание валидатора PhoneValidator для поля phones
    config.validator(config.fields.phones, PhoneValidator)
```