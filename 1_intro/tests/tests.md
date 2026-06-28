# Проверка знаний Python

## 1. Что выведет `bool([0])`? Почему?

## 2. Какая ошибка есть в этом коде?

```python
def append_item(val, lst=[]):
    lst.append(val)
    return lst
```

## 3. Что выведет этот код?

```python
a = [1, 2, 3]
b = a
b.append(4)

print(a)
```

## 4. Что выведет этот код?

```python
x = "hello"

def f(print_result: str):
    print(print_result)

f(x)
```

## 5. Что выведет этот код?

```python
print(7 // 2)
print(7 / 2)
```

Объясните разницу между операторами `//` и `/`.

## 6. Что выведет этот код?

```python
print(7 % 2)
print(10 % 3)
print(8 % 4)
```

Что делает оператор `%`?

## 7. Что выведет этот код?

```python
a = [1, 2]
b = [1, 2]

print(a == b)
print(a is b)
```

Объясните разницу между `==` и `is`.

## 8. Что выведет этот код?

```python
print(5 == 5.0)
print(type(5))
print(type(5.0))
```

Почему результат именно такой?

## 9. Что выведет этот код?

```python
x = 256
y = 256

print(x is y)
```

Почему так происходит?

## 10. Что выведет этот код?

```python
print(bool(""))
print(bool(" "))
print(bool(0))
print(bool(1))
```

Какие значения в Python считаются ложными (*falsy*)?