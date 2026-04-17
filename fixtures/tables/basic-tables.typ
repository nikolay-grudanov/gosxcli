= Тест таблиц

Простая таблица 2x2:

#table(
  columns: 2,
  [A][B],
  [C][D],
)

Таблица 3x2:

#table(
  columns: 2,
  [1][2],
  [3][4],
  [5][6],
)

Таблица с заголовком:

#table(
  columns: 2,
  table.header([Имя][Значение]),
  [Alpha][1],
  [Beta][2],
)

Таблица 4x1:

#table(
  columns: 1,
  [X],
  [Y],
  [Z],
  [W],
)
