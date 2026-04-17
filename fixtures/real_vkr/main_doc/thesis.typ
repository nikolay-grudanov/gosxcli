#import "@preview/modern-g7-32:0.2.0": gost, abstract, appendixes

#show: gost.with(
  ministry: "Министерство науки и высшего образования Российской Федерации",
  organization: (
    full: "Национальный исследовательский ядерный университет «МИФИ»",
    short: "НИЯУ МИФИ"
  ),
  about: "МАГИСТЕРСКАЯ ДИССЕРТАЦИЯ",
  research: "Модель и алгоритмы имитации поведенческих паттернов жителей города с использованием гибридных интеллектуальных систем",
  manager: (
    name: "Смирнов Д.С.",
    position: "к.э.-м.н., доцент",
    title: "Научный руководитель"
  ),
  performers: (
    (name: "Груданов Н.А.", position: "Студент гр. М24-525"),
  ),
  city: "Москва",
  year: "2026",
)

// Оглавление
#outline()


// Настройки основного текста 
// Перенос слов в таблице
#set text(hyphenate: true)
// Делаем текст в первой строке (шапке) жирным
#show table.cell.where(y: 0): set text(weight: "bold")


// Введение
#include "chapters/00-vvedenie.typ"

// Глава 1: Литературный обзор
#include "chapters/01-literature-review.typ"

// Глава 2: Моделирование и проектирование
#include "chapters/02-modeling-design.typ"

// Глава 3: Выбор технологического стека
#include "chapters/03-vybor-steka.typ"

// Список литературы
#bibliography("refs.bib")
