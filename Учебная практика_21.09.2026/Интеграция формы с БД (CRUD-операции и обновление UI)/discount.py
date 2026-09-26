def calculate_partner_discount(total_quantity: int) -> int:
    if total_quantity >= 300000:
        return 15
    if total_quantity >= 50000:
        return 10
    if total_quantity >= 10000:
        return 5
    return 0


def run_tests():
    test_cases = [
        (9999,   0,  "Граница снизу: меньше 10 000"),
        (10000,  5,  "Граница: ровно 10 000"),
        (49999,  5,  "Граница сверху: 49 999"),
        (50000,  10, "Граница: ровно 50 000"),
        (299999, 10, "Граница сверху: 299 999"),
        (300000, 15, "Граница: ровно 300 000"),
        (500000, 15, "Выше максимума: 500 000"),
        (0,      0,  "Ноль"),
    ]

    passed = 0
    failed = 0

    for total_quantity, expected, description in test_cases:
        result = calculate_partner_discount(total_quantity)
        status = "OK" if result == expected else "FAIL"
        if status == "OK":
            passed += 1
        else:
            failed += 1
        print(f"[{status}] {description}: кол-во={total_quantity}, ожидалось={expected}%, получено={result}%")

    print(f"\nРезультат: {passed} passed, {failed} failed")


if __name__ == "__main__":
    run_tests()
