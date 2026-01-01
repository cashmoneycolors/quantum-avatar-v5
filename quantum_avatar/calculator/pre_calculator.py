def calculate_break_even(marge, lohnkosten, mietkosten, fixe_kosten=9900):
    # Break-Even: Fixkosten / Marge
    # fixe_kosten ist der Baseline-Block; Lohn/Miete kommen typischerweise oben drauf.
    total_fixkosten = float(fixe_kosten) + float(lohnkosten) + float(mietkosten)
    break_even = total_fixkosten / float(marge)
    return round(break_even, 2)


if __name__ == "__main__":
    print(f"Break-Even bei 35% Marge: CHF {calculate_break_even(0.35, 2000, 1000)}")
