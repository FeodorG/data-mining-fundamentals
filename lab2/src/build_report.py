from __future__ import annotations

import csv
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    Image,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "output" / "pdf" / "report_association_rules.pdf"
FONT_DIR = Path("/System/Library/Fonts/Supplemental")
pdfmetrics.registerFont(TTFont("Arial", FONT_DIR / "Arial.ttf"))
pdfmetrics.registerFont(TTFont("Arial-Bold", FONT_DIR / "Arial Bold.ttf"))


def footer(canvas, doc):
    canvas.saveState()
    canvas.setFont("Arial", 9)
    canvas.setFillColor(colors.HexColor("#627d98"))
    canvas.drawString(2 * cm, 1.05 * cm, "Поиск ассоциативных правил - Apriori")
    canvas.drawRightString(A4[0] - 2 * cm, 1.05 * cm, str(doc.page))
    canvas.restoreState()


def table_style():
    return TableStyle(
        [
            ("FONTNAME", (0, 0), (-1, 0), "Arial-Bold"),
            ("FONTNAME", (0, 1), (-1, -1), "Arial"),
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2864a8")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("ALIGN", (1, 1), (-1, -1), "CENTER"),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#bcccdc")),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f5f8fa")]),
            ("TOPPADDING", (0, 0), (-1, -1), 6),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ("LEFTPADDING", (0, 0), (-1, -1), 6),
            ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ]
    )


def main():
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with (ROOT / "results" / "association_rule_summary.csv").open(encoding="utf-8") as stream:
        summary = list(csv.DictReader(stream))
    with (ROOT / "results" / "rules_upto7.csv").open(encoding="utf-8") as stream:
        rules = list(csv.DictReader(stream))

    rules_by_confidence = sorted(rules, key=lambda row: -float(row["confidence"]))
    max_confidence = float(rules_by_confidence[0]["confidence"])

    styles = getSampleStyleSheet()
    base = ParagraphStyle(
        "BodyRu",
        parent=styles["BodyText"],
        fontName="Arial",
        fontSize=10.2,
        leading=14.5,
        alignment=TA_JUSTIFY,
        textColor=colors.HexColor("#243b53"),
        spaceAfter=7,
    )
    h1 = ParagraphStyle(
        "H1Ru",
        parent=base,
        fontName="Arial-Bold",
        fontSize=18,
        leading=22,
        textColor=colors.HexColor("#17324d"),
        spaceBefore=8,
        spaceAfter=10,
    )
    caption = ParagraphStyle(
        "Caption",
        parent=base,
        alignment=TA_CENTER,
        fontSize=9,
        leading=12,
        textColor=colors.HexColor("#486581"),
    )
    title = ParagraphStyle(
        "TitleRu",
        parent=base,
        alignment=TA_CENTER,
        fontName="Arial-Bold",
        fontSize=24,
        leading=29,
        textColor=colors.HexColor("#17324d"),
    )
    cell = ParagraphStyle("Cell", parent=base, fontSize=8.6, leading=10.5, spaceAfter=0)
    header_cell = ParagraphStyle(
        "HeaderCell", parent=cell, fontName="Arial-Bold", textColor=colors.white, alignment=TA_CENTER
    )

    doc = SimpleDocTemplate(
        str(OUT),
        pagesize=A4,
        rightMargin=2 * cm,
        leftMargin=2 * cm,
        topMargin=1.8 * cm,
        bottomMargin=1.8 * cm,
        title="Поиск ассоциативных правил методом Apriori",
        author="Учебный проект",
    )

    story = [
        Spacer(1, 3.0 * cm),
        Paragraph("ОТЧЁТ О ВЫПОЛНЕНИИ ЗАДАНИЯ", title),
        Spacer(1, 0.7 * cm),
        Paragraph(
            "Поиск ассоциативных правил<br/>на основе алгоритма Apriori",
            ParagraphStyle(
                "Subtitle",
                parent=title,
                fontSize=18,
                leading=23,
                textColor=colors.HexColor("#2864a8"),
            ),
        ),
        Spacer(1, 2.2 * cm),
    ]
    info = Table(
        [[Paragraph(
            "Набор данных: <b>baskets.csv</b><br/>"
            "Число транзакций: <b>7501</b><br/>"
            "Минимальная поддержка: <b>1%</b><br/>"
            "Пороги достоверности: <b>25%, 30%, 35%, 40%, 45%, 50%</b>",
            base,
        )]],
        colWidths=[14 * cm],
    )
    info.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#eef5fb")),
                ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#9fb3c8")),
                ("LEFTPADDING", (0, 0), (-1, -1), 16),
                ("RIGHTPADDING", (0, 0), (-1, -1), 16),
                ("TOPPADDING", (0, 0), (-1, -1), 12),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 12),
            ]
        )
    )
    story += [
        info,
        Spacer(1, 3.8 * cm),
        Paragraph("2026", ParagraphStyle("Year", parent=base, alignment=TA_CENTER, fontSize=12)),
        PageBreak(),
    ]

    story += [
        Paragraph("1. Формулировка задания", h1),
        Paragraph(
            "Необходимо доработать программу поиска частых наборов: добавить построение "
            "ассоциативных правил в форме «антецедент → консеквент», вычисление поддержки "
            "и достоверности, параметр минимальной достоверности и два способа сортировки "
            "результата - по убыванию поддержки и лексикографически.",
            base,
        ),
        Paragraph(
            "Экспериментальная часть должна исследовать время поиска и число правил при "
            "фиксированной поддержке и меняющейся достоверности. Также требуется подготовить "
            "список правил суммарной длиной не более семи объектов и объяснить их содержательный смысл.",
            base,
        ),
        Paragraph("2. Материалы проекта", h1),
        Paragraph(
            'Каталог репозитория с исходным кодом, данными и результатами: '
            '<link href="https://github.com/FeodorG/data-mining-fundamentals/tree/main/lab2" '
            'color="#2864a8"><u>github.com/FeodorG/data-mining-fundamentals/tree/main/lab2</u></link>.',
            base,
        ),
        Paragraph("3. Методика", h1),
        Paragraph(
            "Сначала алгоритм Apriori находит все наборы с поддержкой не ниже 1%. Для каждого "
            "частого набора X длиной не менее двух перебираются все непустые собственные "
            "подмножества A. Они образуют правило A → X\\A. Повторное чтение транзакций не "
            "требуется: поддержки всех нужных подмножеств уже найдены Apriori.",
            base,
        ),
        Paragraph(
            "Поддержка правила A → B равна доле транзакций, содержащих одновременно A и B. "
            "Достоверность вычисляется как confidence(A → B) = support(A, B) / support(A) и показывает, "
            "в какой доле корзин с антецедентом встречается консеквент.",
            base,
        ),
        Paragraph(
            "Предварительная проверка показала, что максимальная достоверность на этом наборе "
            f"данных равна {max_confidence:.2%}. Поэтому примерный диапазон 70-95% дал бы шесть "
            "одинаковых нулевых результатов. Для содержательного эксперимента выбран диапазон "
            "25-50% с шагом 5%. Для каждого порога время генерации правил измерялось 100 раз; "
            "ниже приведена медиана.",
            base,
        ),
    ]

    summary_data = [
        [
            Paragraph("Достоверность", header_cell),
            Paragraph("Медиана, мс", header_cell),
            Paragraph("Правил", header_cell),
        ]
    ]
    for row in summary:
        summary_data.append(
            [
                f"{float(row['confidence_threshold']):.0%}",
                f"{float(row['median_seconds']) * 1000:.3f}",
                row["rules"],
            ]
        )
    table = Table(summary_data, colWidths=[4.7 * cm, 4.7 * cm, 4.7 * cm], repeatRows=1)
    table.setStyle(table_style())
    story += [
        Paragraph("4. Результаты экспериментов", h1),
        table,
        Spacer(1, 0.2 * cm),
        Paragraph("Таблица 1 - Сводные результаты при поддержке 1%", caption),
        Spacer(1, 0.2 * cm),
        Image(str(ROOT / "results" / "rules_runtime.png"), width=16.2 * cm, height=9.72 * cm),
        Paragraph("Рисунок 1 - Время генерации и фильтрации правил", caption),
        PageBreak(),
        Image(str(ROOT / "results" / "rules_count.png"), width=15.5 * cm, height=9.3 * cm),
        Paragraph("Рисунок 2 - Число правил при изменении порога достоверности", caption),
        Spacer(1, 0.25 * cm),
        Paragraph(
            "Количество правил монотонно уменьшается с 99 до 2: повышение порога только "
            "отбрасывает ранее допустимые правила и не может создавать новые. Время также "
            f"слегка сокращается - с примерно {float(summary[0]['median_seconds']) * 1000:.3f} "
            f"до {float(summary[-1]['median_seconds']) * 1000:.3f} мс, поскольку при высоком пороге "
            "меньше строк добавляется в результат. Основной перебор кандидатов остаётся тем же, "
            "поэтому различие во времени невелико.",
            base,
        ),
    ]

    top_rules = rules_by_confidence[:8]
    rule_data = [
        [
            Paragraph("Правило", header_cell),
            Paragraph("Поддержка", header_cell),
            Paragraph("Достоверность", header_cell),
        ]
    ]
    for row in top_rules:
        antecedent = row["antecedent"].replace("; ", ", ")
        consequent = row["consequent"].replace("; ", ", ")
        rule_data.append(
            [
                Paragraph(f"{{{antecedent}}} → {{{consequent}}}", cell),
                f"{float(row['support']):.2%}",
                f"{float(row['confidence']):.2%}",
            ]
        )
    rules_table = Table(rule_data, colWidths=[9.7 * cm, 2.2 * cm, 2.9 * cm], repeatRows=1)
    rules_table.setStyle(table_style())
    story += [
        Paragraph("5. Правила длиной не более семи объектов", h1),
        Paragraph(
            "При поддержке 1% максимальная длина частого набора равна трём. Следовательно, "
            "все 99 правил при достоверности 25% автоматически удовлетворяют ограничению "
            "«не более семи объектов». Полный список сохранён в results/rules_upto7.csv. "
            "Ниже приведены восемь правил с наибольшей достоверностью.",
            base,
        ),
        rules_table,
        Spacer(1, 0.2 * cm),
        Paragraph("Таблица 2 - Наиболее достоверные правила", caption),
        Paragraph("6. Содержательная интерпретация", h1),
        Paragraph(
            "Самое достоверное правило связывает совместную покупку говяжьего фарша и яиц "
            "с минеральной водой: консеквент встречается примерно в половине таких корзин. "
            "Похожий результат наблюдается для сочетания фарша с молоком. Это делает минеральную "
            "воду естественным кандидатом для совместной выкладки или рекомендации к продуктам "
            "основной корзины.",
            base,
        ),
        Paragraph(
            "Правила «суп → минеральная вода» и «оливковое масло → минеральная вода» имеют "
            "достоверность около 46% и 42%. Они проще для практического применения, потому что "
            "их антецедент содержит один товар. При этом поддержку нужно учитывать вместе с "
            "достоверностью: редкое, но уверенное правило затрагивает меньше покупателей, чем "
            "чуть менее уверенная связь с большей поддержкой.",
            base,
        ),
        Paragraph(
            "Направление правила существенно. Например, «макароны → минеральная вода» имеет "
            "достоверность около 32,6%, а обратное правило - около 25,7%, хотя поддержка у них "
            "одинакова. Причина в разных частотах антецедентов. Наконец, ассоциативное правило "
            "описывает совместную встречаемость, но само по себе не доказывает причинную связь.",
            base,
        ),
        Paragraph("7. Вывод", h1),
        Paragraph(
            "Программа дополнена полным поиском ассоциативных правил, выводом в читаемом виде, "
            "сохранением поддержки и достоверности, порогом достоверности, ограничением размера "
            "и двумя режимами сортировки. Эксперимент подтвердил ожидаемую зависимость: рост "
            "минимальной достоверности резко сокращает число правил, но лишь немного влияет на "
            "время их генерации. Полученные связи пригодны как гипотезы для рекомендаций и "
            "мерчандайзинга при обязательном учёте поддержки и отсутствия причинной интерпретации.",
            base,
        ),
    ]

    doc.build(story, onFirstPage=footer, onLaterPages=footer)
    print(OUT)


if __name__ == "__main__":
    main()
