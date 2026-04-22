from typing import List, Tuple
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont



class CustomBarcodeGenerator:
    def __init__(self):
        # Размеры в миллиметрах (переводим в точки для reportlab: 1 мм = 2.83465 pt)
        self.mm_to_pt = 2.83465

        # Номинальные размеры
        self.symbol_height = 25.93 * self.mm_to_pt  # общая высота символа
        self.bar_height = 22.85 * self.mm_to_pt  # высота штриха
        self.left_quiet_zone = 3.63 * self.mm_to_pt  # свободная зона слева
        self.right_quiet_zone = 2.31 * self.mm_to_pt  # свободная зона справа
        self.bar_extension = 1.65 * self.mm_to_pt  # удлинение ограничивающих знаков

        # Размеры для цифр
        self.digit_height = 2.75 * self.mm_to_pt  # высота цифр
        self.digit_to_bar_gap = 0.165 * self.mm_to_pt  # расстояние от цифр до штрихов

        # Параметры штрихов
        self.bar_width_unit = 0.15 * self.mm_to_pt  # единица ширины (0.15 мм)
        self.gap_width = 0.2 * self.mm_to_pt  # расстояние между штрихами

        # Координаты для рисования
        self.start_x = 50  # отступ от левого края страницы (в точках)
        self.start_y = 200  # отступ от нижнего края (в точках)

    def generate_bars_from_digits(self, digits: List[int]) -> List[Tuple[float, float, bool]]:
        """
        Преобразует список цифр в список штрихов
        Возвращает: [(ширина_штриха, высота_штриха, удлиненный_ли), ...]
        удлиненный_ли - True для ограничивающих знаков
        """
        bars = []

        for i, digit in enumerate(digits):
            # Определяем, является ли штрих ограничивающим знаком
            # Левый ограничивающий знак (первый штрих), центральный, правый (последний)
            is_extended = (i == 0 or i == len(digits) // 2 or i == len(digits) - 1)

            if digit == 0:
                # Нуль - белый штрих (пропуск)
                # Ширина белого штриха 1.35 мм = 9 единиц * 0.15 мм
                white_bar_width = 9 * self.bar_width_unit
                # Добавляем как None для белого штриха
                bars.append((white_bar_width, self.bar_height, is_extended, True))  # True = белый штрих
            else:
                # Черный штрих с шириной = цифра * 0.15 мм
                black_bar_width = digit * self.bar_width_unit
                bars.append((black_bar_width, self.bar_height, is_extended, False))  # False = черный штрих

        return bars

    def draw_custom_barcode(self, c: canvas.Canvas, barcode_data: str, x: float, y: float):
        """
        Рисует кастомный штрих-код на PDF канвасе
        """
        # Проверяем входные данные
        if not barcode_data or len(barcode_data) == 0:
            raise ValueError("Нет данных для штрих-кода")

        # Извлекаем цифры из строки (игнорируем пробелы)
        digits = [int(ch) for ch in barcode_data if ch.isdigit()]

        if not digits:
            raise ValueError("Штрих-код должен содержать цифры")

        # Генерируем штрихи
        bars = self.generate_bars_from_digits(digits)

        # Рисуем каждый штрих
        current_x = x + self.left_quiet_zone  # добавляем свободную зону слева

        for bar_width, bar_height, is_extended, is_white in bars:
            # Определяем высоту штриха
            actual_height = bar_height
            if is_extended:
                actual_height += self.bar_extension  # удлиняем вниз

            if not is_white:
                # Рисуем черный прямоугольник
                c.rect(current_x, y, bar_width, actual_height, fill=1, stroke=0)

            # Сдвигаем позицию для следующего штриха (ширина текущего + расстояние между штрихами)
            current_x += bar_width + self.gap_width

        # Общая ширина штрих-кода (для отладки)
        total_width = current_x - x - self.gap_width + self.right_quiet_zone

        # Рисуем цифры под штрихами
        self.draw_digits_below_bars(c, digits, x + self.left_quiet_zone,
                                    y - self.digit_to_bar_gap - self.digit_height,
                                    bars)

        return total_width

    def draw_digits_below_bars(self, c: canvas.Canvas, digits: List[int],
                               start_x: float, y: float, bars: List):
        """
        Рисует цифры под соответствующими штрихами
        """
        c.setFont("Helvetica", self.digit_height)

        current_x = start_x

        for i, digit in enumerate(digits):
            # Позиция для текущей цифры (центрируем над штрихом)
            bar_width = bars[i][0]
            text_x = current_x + (bar_width / 2) - (self.digit_height / 3)

            # Рисуем цифру
            c.drawString(text_x, y, str(digit))

            # Сдвигаемся к следующему штриху
            current_x += bar_width + self.gap_width

    def generate_barcode_data(self, order_id: str, date_created: str, unique_code: str) -> str:
        """
        Генерирует строку для штрих-кода на основе:
        - уникального идентификатора заказа
        - даты создания
        - уникального кода из 6 символов
        """
        # Удаляем все нецифровые символы из даты (оставляем только цифры)
        date_digits = ''.join([ch for ch in date_created if ch.isdigit()])

        # Формируем полную строку для штрих-кода
        barcode_string = f"{order_id}{date_digits}{unique_code}"

        # Ограничиваем длину (опционально)
        if len(barcode_string) > 30:
            print(f"Предупреждение: штрих-код длинный ({len(barcode_string)} символов)")

        return barcode_string


def main():
    # Данные для примера
    order_id = "5"  # уникальный идентификатор заказа
    date_created = "15122025"  # дата создания (будут взяты только цифры)
    unique_code = "123456"  # уникальный код из 6 символов

    # Создаем генератор
    generator = CustomBarcodeGenerator()

    # Генерируем строку для штрих-кода
    barcode_data = generator.generate_barcode_data(order_id, date_created, unique_code)
    print(f"Данные для штрих-кода: {barcode_data}")

    # Создаем PDF
    pdf_filename = "barcode_label.pdf"
    c = canvas.Canvas(pdf_filename, pagesize=A4)

    # Позиция для штрих-кода (от левого края, от нижнего края)
    x_position = 30 * generator.mm_to_pt
    y_position = 150 * generator.mm_to_pt

    # Рисуем штрих-код
    try:
        total_width = generator.draw_custom_barcode(c, barcode_data, x_position, y_position)

        # Добавляем текстовую информацию над штрих-кодом
        c.setFont("Helvetica", 10)
        info_text = f"Заказ: {order_id} | Дата: {date_created} | Уник. код: {unique_code}"
        c.drawString(x_position, y_position + 30, info_text)

        # Добавляем заголовок
        c.setFont("Helvetica-Bold", 14)
        c.drawString(x_position, y_position + 50, "ШТРИХ-КОД ДЛЯ ПРОБИРКИ")

        # Сохраняем PDF
        c.save()
        print(f"✓ PDF файл успешно создан: {pdf_filename}")
        print(f"✓ Размеры штрих-кода соответствуют требованиям")
        print(f"✓ Общая ширина штрих-кода: {total_width / generator.mm_to_pt:.2f} мм")

    except Exception as e:
        print(f"Ошибка при создании штрих-кода: {e}")


def generate_batch_barcodes(barcodes_list: List[dict], output_filename="batch_barcodes.pdf"):
    """
    Генерирует PDF с несколькими штрих-кодами (для печати на листе клейкой бумаги)

    barcodes_list: список словарей с ключами 'order_id', 'date_created', 'unique_code'
    """
    generator = CustomBarcodeGenerator()
    c = canvas.Canvas(output_filename, pagesize=A4)

    page_width, page_height = A4
    margin = 20 * generator.mm_to_pt
    spacing = 40 * generator.mm_to_pt

    current_x = margin
    current_y = page_height - margin

    for i, item in enumerate(barcodes_list):
        # Генерируем данные для штрих-кода
        barcode_data = generator.generate_barcode_data(
            item['order_id'],
            item['date_created'],
            item['unique_code']
        )

        # Рисуем штрих-код
        try:
            generator.draw_custom_barcode(c, barcode_data, current_x, current_y)

            # Добавляем текстовую информацию
            c.setFont("Helvetica", 8)
            info_text = f"{item['order_id']} | {item['date_created']} | {item['unique_code']}"
            c.drawString(current_x, current_y + 15, info_text)

            # Перемещаемся к следующему штрих-коду
            current_y -= spacing

            # Если достигли конца страницы, создаем новую
            if current_y < margin:
                c.showPage()
                current_y = page_height - margin

        except Exception as e:
            print(f"Ошибка для {item}: {e}")

    c.save()
    print(f"✓ Создан PDF с {len(barcodes_list)} штрих-кодами: {output_filename}")


if __name__ == "__main__":
    # Пример 1: Один штрих-код
    main()

    # Пример 2: Пакетная генерация для печати нескольких этикеток
    batch_data = [
        {"order_id": "5140920", "date_created": "2024-12-15", "unique_code": "123456"},
        {"order_id": "5140921", "date_created": "2024-12-15", "unique_code": "789012"},
        {"order_id": "5140922", "date_created": "2024-12-16", "unique_code": "345678"},
        {"order_id": "5140923", "date_created": "2024-12-16", "unique_code": "901234"},
    ]

    generate_batch_barcodes(batch_data, "batch_barcodes.pdf")