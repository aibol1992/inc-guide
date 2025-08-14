import re

# Қазақ тіліндегі сандарды цифрлық түрге ауыстыратын сөздік
numbers_dict = {
    "нөл": 0, "бір": 1, "екі": 2, "үш": 3, "төрт": 4, "бес": 5, "алты": 6, "жеті": 7, "сегіз": 8, "тоғыз": 9,
    "он": 10, "жиырма": 20, "отыз": 30, "қырық": 40, "елу": 50, "алпыс": 60, "жетпіс": 70, "сексен": 80, "тоқсан": 90,
    "жүз": 100, "мың": 1000
}

# Мәтіндегі сөздерді санға айналдыратын функция
def text_to_number(text):
    words = text.split()
    total = 0
    current_number = 0
    
    for word in words:
        if word in numbers_dict:
            # Егер сөз "жүз", "мың" болса, көбейту қажет
            if word == "жүз":
                current_number = (current_number or 1) * 100
            elif word == "мың":
                current_number = (current_number or 1) * 1000
                total += current_number
                current_number = 0
            else:
                current_number += numbers_dict[word]
        else:
            total += current_number
            current_number = 0
    return total + current_number

# Мысал сөйлем (бұл жерде "бөлме" сөзін қолданбаймыз)
text = "жүз бесінші бөлме"

# Сөйлемнен барлық санға сәйкес сөздерді табамыз
san_sandar = re.findall(r'нөл|бір|екі|үш|төрт|бес|алты|жеті|сегіз|тоғыз|он|жиырма|отыз|қырық|елу|алпыс|жетпіс|сексен|тоқсан|жүз|мың', text)

if san_sandar:
    # Сөздерді санға айналдыру
    san_text = ' '.join(san_sandar)
    room_number = text_to_number(san_text)
    print(f"Табылған сан: {room_number}")
else:
    print("Сан табылған жоқ")
