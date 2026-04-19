= Комплексная таблица

Таблица с colspan, rowspan, stroke, fill и align:

#table(
  columns: 4,
  stroke: (x: 1pt, y: 0.5pt),
  fill: (x, y) => if calc.odd(y) { rgb("#f0f0f0") } else { white },
  align: (x, y) => if x == 0 { left } else { center },
  table.header([Заголовок 1][Заголовок 2][Заголовок 3][Заголовок 4]),
  [Ячейка 1][Ячейка 2][Ячейка 3][Ячейка 4],
  [Ячейка с colspan, colspan: 3][Ячейка 10],
  [Ячейка 11][Ячейка 12][Ячейка 13][Ячейка 14],
  table.cell(colspan: 2, [Объединённая 1])[Ячейка 17][Ячейка 18],
  [Ячейка 19][Ячейка 20][Ячейка 21][Ячейка 22],
)

Таблица с rowspan:

#table(
  columns: 3,
  table.header([H1][H2][H3]),
  [Row 1 Col 1, rowspan: 2][Row 1 Col 2][Row 1 Col 3],
  [Row 2 Col 2][Row 2 Col 3],
  [Row 3 Col 1][Row 3 Col 2][Row 3 Col 3],
)

Простая таблица для сравнения:

#table(
  columns: 2,
  [A][B],
  [C][D],
)
