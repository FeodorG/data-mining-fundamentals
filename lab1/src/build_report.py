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
    Image, PageBreak, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle
)


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "output" / "pdf" / "report_apriori.pdf"
FONT_DIR = Path("/System/Library/Fonts/Supplemental")
pdfmetrics.registerFont(TTFont("Arial", FONT_DIR / "Arial.ttf"))
pdfmetrics.registerFont(TTFont("Arial-Bold", FONT_DIR / "Arial Bold.ttf"))


def footer(canvas, doc):
    canvas.saveState()
    canvas.setFont("Arial", 9)
    canvas.setFillColor(colors.HexColor("#627d98"))
    canvas.drawString(2 * cm, 1.15 * cm, "Поиск частых наборов — Apriori")
    canvas.drawRightString(A4[0] - 2 * cm, 1.15 * cm, str(doc.page))
    canvas.restoreState()


def main():
    with (ROOT / "results" / "experiment_summary.csv").open(encoding="utf-8") as f:
        summary = list(csv.DictReader(f))
    with (ROOT / "results" / "itemsets_by_length.csv").open(encoding="utf-8") as f:
        lengths = list(csv.DictReader(f))

    styles = getSampleStyleSheet()
    base = ParagraphStyle("BodyRu", parent=styles["BodyText"], fontName="Arial", fontSize=10.5, leading=15, alignment=TA_JUSTIFY, textColor=colors.HexColor("#243b53"), spaceAfter=7)
    h1 = ParagraphStyle("H1Ru", parent=base, fontName="Arial-Bold", fontSize=19, leading=23, textColor=colors.HexColor("#17324d"), spaceBefore=8, spaceAfter=12)
    h2 = ParagraphStyle("H2Ru", parent=h1, fontSize=14, leading=17, spaceBefore=6, spaceAfter=7)
    caption = ParagraphStyle("Caption", parent=base, alignment=TA_CENTER, fontSize=9, leading=12, textColor=colors.HexColor("#486581"))
    title = ParagraphStyle("TitleRu", parent=base, alignment=TA_CENTER, fontName="Arial-Bold", fontSize=25, leading=30, textColor=colors.HexColor("#17324d"))

    doc = SimpleDocTemplate(str(OUT), pagesize=A4, rightMargin=2*cm, leftMargin=2*cm, topMargin=1.8*cm, bottomMargin=1.8*cm, title="Поиск частых наборов методом Apriori", author="Учебный проект")
    story = [Spacer(1, 3.2*cm), Paragraph("ОТЧЁТ О ВЫПОЛНЕНИИ ЗАДАНИЯ", title), Spacer(1, .7*cm), Paragraph("Поиск частых наборов объектов<br/>алгоритмом Apriori", ParagraphStyle("Subtitle", parent=title, fontSize=18, leading=23, textColor=colors.HexColor("#2864a8"))), Spacer(1, 2.4*cm)]
    box = Table([[Paragraph("Набор данных: <b>baskets.csv</b><br/>Число транзакций: <b>7501</b><br/>Исследованные пороги: <b>1%, 3%, 5%, 10%, 15%</b>", base)]], colWidths=[14*cm])
    box.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,-1),colors.HexColor("#eef5fb")),("BOX",(0,0),(-1,-1),1,colors.HexColor("#9fb3c8")),("LEFTPADDING",(0,0),(-1,-1),16),("RIGHTPADDING",(0,0),(-1,-1),16),("TOPPADDING",(0,0),(-1,-1),12),("BOTTOMPADDING",(0,0),(-1,-1),12)]))
    story += [box, Spacer(1, 4.2*cm), Paragraph("2026", ParagraphStyle("Year", parent=base, alignment=TA_CENTER, fontSize=12)), PageBreak()]

    story += [Paragraph("1. Формулировка задания", h1), Paragraph("Требуется разработать программу поиска частых наборов объектов в транзакционном наборе данных методом Apriori или его модификацией. Для каждого найденного набора необходимо указать поддержку. Входными параметрами служат набор данных, минимальный порог поддержки и способ сортировки результата: по убыванию поддержки или лексикографически.", base), Paragraph("Экспериментальная часть должна сравнивать время работы при разных порогах поддержки и показывать число частых наборов разной длины. Результаты необходимо представить диаграммами и объяснить наблюдаемые зависимости.", base)]
    repo_url = "https://github.com/FeodorG/data-mining-fundamentals"
    story += [Paragraph("2. Материалы проекта", h1), Paragraph(f'Каталог с исходным кодом, набором данных и результатами: <link href="{repo_url}" color="#2864a8"><u>{repo_url}</u></link>.', base)]
    story += [Paragraph("3. Методика", h1), Paragraph("Реализован классический поуровневый Apriori. На первом шаге подсчитывается поддержка отдельных товаров. Для каждого следующего уровня выполняются объединение частых наборов предыдущей длины, отсечение кандидатов с нечастыми подмножествами и один проход по транзакциям для подсчёта поддержки кандидатов.", base), Paragraph("Относительная поддержка набора X вычисляется как support(X) = |{t: X ⊆ t}| / N, где N — число транзакций. Абсолютный порог равен округлённому вверх произведению относительного порога на N. Время каждого опыта измерялось трижды; на диаграмме приведена медиана, менее чувствительная к случайным фоновым задержкам.", base), Paragraph("Программа автоматически читает UTF-8 и Windows-1251. Результат сохраняется в CSV с самим набором, его длиной, абсолютной и относительной поддержкой. Параметр <b>--order</b> принимает значения <b>support</b> и <b>lexicographic</b>.", base)]

    table_data = [["Порог", "Медиана, с", "Частых наборов", "Макс. длина"]]
    for r in summary:
        table_data.append([f"{float(r['threshold'])*100:.0f}%", f"{float(r['median_seconds']):.4f}", r["itemsets"], r["max_length"]])
    table = Table(table_data, colWidths=[3.1*cm,3.5*cm,4.0*cm,3.2*cm], repeatRows=1)
    table.setStyle(TableStyle([("FONTNAME",(0,0),(-1,0),"Arial-Bold"),("FONTNAME",(0,1),(-1,-1),"Arial"),("BACKGROUND",(0,0),(-1,0),colors.HexColor("#2864a8")),("TEXTCOLOR",(0,0),(-1,0),colors.white),("ALIGN",(0,0),(-1,-1),"CENTER"),("GRID",(0,0),(-1,-1),.5,colors.HexColor("#bcccdc")),("ROWBACKGROUNDS",(0,1),(-1,-1),[colors.white,colors.HexColor("#f5f8fa")]),("TOPPADDING",(0,0),(-1,-1),7),("BOTTOMPADDING",(0,0),(-1,-1),7)]))
    story += [Paragraph("4. Результаты экспериментов", h1), table, Spacer(1,.4*cm), Paragraph("Таблица 1 — Сводные результаты (3 запуска для каждого порога)", caption), Spacer(1,.2*cm), Image(str(ROOT / "results" / "runtime.png"), width=16.5*cm, height=9.9*cm), Paragraph("Рисунок 1 — Зависимость медианного времени работы от порога поддержки", caption), PageBreak()]
    story += [Paragraph("5. Распределение наборов по длине", h1), Image(str(ROOT / "results" / "itemsets_by_length.png"), width=16.5*cm, height=9.9*cm), Paragraph("Рисунок 2 — Количество частых наборов; цвет показывает длину набора", caption), Spacer(1,.3*cm)]
    matrix = {float(r["threshold"]): {} for r in summary}
    for r in lengths: matrix[float(r["threshold"])][int(r["length"])] = int(r["count"])
    max_len = max(k for v in matrix.values() for k in v)
    d = [["Порог"] + [f"Длина {i}" for i in range(1,max_len+1)] + ["Всего"]]
    for threshold, vals in matrix.items(): d.append([f"{threshold*100:.0f}%"] + [str(vals.get(i,0)) for i in range(1,max_len+1)] + [str(sum(vals.values()))])
    t2=Table(d,colWidths=[2.4*cm]+[2.8*cm]*max_len+[2.8*cm])
    t2.setStyle(TableStyle([("FONTNAME",(0,0),(-1,0),"Arial-Bold"),("FONTNAME",(0,1),(-1,-1),"Arial"),("BACKGROUND",(0,0),(-1,0),colors.HexColor("#2864a8")),("TEXTCOLOR",(0,0),(-1,0),colors.white),("ALIGN",(0,0),(-1,-1),"CENTER"),("GRID",(0,0),(-1,-1),.5,colors.HexColor("#bcccdc")),("ROWBACKGROUNDS",(0,1),(-1,-1),[colors.white,colors.HexColor("#f5f8fa")]),("TOPPADDING",(0,0),(-1,-1),6),("BOTTOMPADDING",(0,0),(-1,-1),6)]))
    story += [t2, Spacer(1,.3*cm), Paragraph("Таблица 2 — Число наборов каждой длины", caption)]
    story += [Paragraph("6. Интерпретация", h1), Paragraph("При повышении порога множество допустимых наборов монотонно сокращается: с 261 при 1% до 5 при 15%. Это прямое следствие определения частого набора: более строгому порогу удовлетворяет меньше товаров и комбинаций.", base), Paragraph("На пороге 1% преобладают пары (170 из 261), а также появляются 17 троек. При 3% остаются 19 пар, при 5% — только 3 пары. Начиная с 10% частыми являются лишь одиночные товары. Следовательно, совместные покупки имеют заметно меньшую поддержку, чем самые популярные отдельные товары.", base), Paragraph("Время работы уменьшается быстрее, чем число выдаваемых наборов. Низкий порог сохраняет больше наборов на каждом уровне, поэтому Apriori генерирует и проверяет существенно больше кандидатов. При высоких порогах процесс завершается уже после уровня одиночных товаров. Небольшие колебания времени между запусками объясняются состоянием операционной системы и не меняют общей зависимости.", base)]
    story += [Paragraph("7. Вывод", h1), Paragraph("Разработанная программа выполняет поиск частых наборов, рассчитывает абсолютную и относительную поддержку и поддерживает оба требуемых порядка сортировки. Эксперименты показывают ожидаемый компромисс: низкий порог позволяет выявить больше сложных сочетаний, но увеличивает вычислительные затраты; высокий порог оставляет только наиболее массовые товары и резко ускоряет поиск.", base), Paragraph("Для воспроизводимости в каталоге проекта сохранены исходный набор данных, код, CSV-файлы всех результатов, сводные таблицы и обе диаграммы.", base)]
    doc.build(story, onFirstPage=footer, onLaterPages=footer)
    print(OUT)


if __name__ == "__main__":
    main()
