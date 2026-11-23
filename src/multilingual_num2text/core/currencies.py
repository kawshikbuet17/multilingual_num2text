"""Every circulating ISO 4217 currency: code, written symbols and digits after the decimal point.

Names live in each language (languages/<lang>/currencies.py) and are joined with this table by
build_currencies(). The ISO code itself is always recognised, so symbols list only extra forms.
Ambiguous signs shared by many currencies (kr, R, P, Fr) are left out on purpose.
"""

from dataclasses import dataclass

from .lexicon import Currency


@dataclass(frozen=True)
class CurrencyCode:
    code: str
    symbols: tuple[str, ...] = ()
    minor_digits: int = 2


CURRENCY_CODES = (
    CurrencyCode("AED", ("د.إ",)),
    CurrencyCode("AFN", ("؋",)),
    CurrencyCode("ALL"),
    CurrencyCode("AMD", ("֏",)),
    CurrencyCode("AOA", ("Kz",)),
    CurrencyCode("ARS"),
    CurrencyCode("AUD", ("A$", "AU$")),
    CurrencyCode("AWG", ("Afl.",)),
    CurrencyCode("AZN", ("₼",)),
    CurrencyCode("BAM", ("KM",)),
    CurrencyCode("BBD", ("Bds$",)),
    CurrencyCode("BDT", ("৳", "Tk.", "Tk", "TK")),
    CurrencyCode("BHD", ("BD",), 3),
    CurrencyCode("BIF", (), 0),
    CurrencyCode("BMD"),
    CurrencyCode("BND", ("B$",)),
    CurrencyCode("BOB", ("Bs.",)),
    CurrencyCode("BRL", ("R$",)),
    CurrencyCode("BSD"),
    CurrencyCode("BTN", ("Nu.",)),
    CurrencyCode("BWP"),
    CurrencyCode("BYN"),
    CurrencyCode("BZD", ("BZ$",)),
    CurrencyCode("CAD", ("C$", "CA$")),
    CurrencyCode("CDF", ("FC",)),
    CurrencyCode("CHF"),
    CurrencyCode("CLP", (), 0),
    CurrencyCode("CNY", ("CN¥", "元", "RMB")),
    CurrencyCode("COP", ("COL$",)),
    CurrencyCode("CRC", ("₡",)),
    CurrencyCode("CUP"),
    CurrencyCode("CVE"),
    CurrencyCode("CZK", ("Kč",)),
    CurrencyCode("DJF", ("Fdj",), 0),
    CurrencyCode("DKK"),
    CurrencyCode("DOP", ("RD$",)),
    CurrencyCode("DZD"),
    CurrencyCode("EGP", ("E£",)),
    CurrencyCode("ERN", ("Nfk",)),
    CurrencyCode("ETB"),
    CurrencyCode("EUR", ("€",)),
    CurrencyCode("FJD", ("FJ$",)),
    CurrencyCode("FKP"),
    CurrencyCode("GBP", ("£",)),
    CurrencyCode("GEL", ("₾",)),
    CurrencyCode("GHS", ("GH₵", "₵")),
    CurrencyCode("GIP"),
    CurrencyCode("GMD"),
    CurrencyCode("GNF", ("FG",), 0),
    CurrencyCode("GTQ"),
    CurrencyCode("GYD", ("G$",)),
    CurrencyCode("HKD", ("HK$",)),
    CurrencyCode("HNL"),
    CurrencyCode("HTG"),
    CurrencyCode("HUF", ("Ft",)),
    CurrencyCode("IDR", ("Rp",)),
    CurrencyCode("ILS", ("₪",)),
    CurrencyCode("INR", ("₹", "Rs.", "Rs")),
    CurrencyCode("IQD", (), 3),
    CurrencyCode("IRR", (), 0),
    CurrencyCode("ISK", (), 0),
    CurrencyCode("JMD", ("J$",)),
    CurrencyCode("JOD", ("JD",), 3),
    CurrencyCode("JPY", ("¥", "円"), 0),
    CurrencyCode("KES", ("KSh",)),
    CurrencyCode("KGS"),
    CurrencyCode("KHR", ("៛",)),
    CurrencyCode("KMF", (), 0),
    CurrencyCode("KPW"),
    CurrencyCode("KRW", ("₩",), 0),
    CurrencyCode("KWD", ("KD",), 3),
    CurrencyCode("KYD", ("CI$",)),
    CurrencyCode("KZT", ("₸",)),
    CurrencyCode("LAK", ("₭",)),
    CurrencyCode("LBP"),
    CurrencyCode("LKR"),
    CurrencyCode("LRD", ("L$",)),
    CurrencyCode("LSL"),
    CurrencyCode("LYD", ("LD",), 3),
    CurrencyCode("MAD"),
    CurrencyCode("MDL"),
    CurrencyCode("MGA", (), 0),
    CurrencyCode("MKD"),
    CurrencyCode("MMK"),
    CurrencyCode("MNT", ("₮",)),
    CurrencyCode("MOP", ("MOP$",)),
    CurrencyCode("MRU", (), 0),
    CurrencyCode("MUR"),
    CurrencyCode("MVR", ("Rf",)),
    CurrencyCode("MWK"),
    CurrencyCode("MXN", ("Mex$",)),
    CurrencyCode("MYR", ("RM",)),
    CurrencyCode("MZN", ("MT",)),
    CurrencyCode("NAD", ("N$",)),
    CurrencyCode("NGN", ("₦",)),
    CurrencyCode("NIO"),
    CurrencyCode("NOK"),
    CurrencyCode("NPR"),
    CurrencyCode("NZD", ("NZ$",)),
    CurrencyCode("OMR", (), 3),
    CurrencyCode("PAB"),
    CurrencyCode("PEN", ("S/",)),
    CurrencyCode("PGK"),
    CurrencyCode("PHP", ("₱",)),
    CurrencyCode("PKR"),
    CurrencyCode("PLN", ("zł",)),
    CurrencyCode("PYG", ("₲",), 0),
    CurrencyCode("QAR"),
    CurrencyCode("RON"),
    CurrencyCode("RSD"),
    CurrencyCode("RUB", ("₽",)),
    CurrencyCode("RWF", (), 0),
    CurrencyCode("SAR"),
    CurrencyCode("SBD", ("SI$",)),
    CurrencyCode("SCR"),
    CurrencyCode("SDG"),
    CurrencyCode("SEK"),
    CurrencyCode("SGD", ("S$",)),
    CurrencyCode("SHP"),
    CurrencyCode("SLE"),
    CurrencyCode("SOS"),
    CurrencyCode("SRD"),
    CurrencyCode("SSP"),
    CurrencyCode("STN", ("Db",)),
    CurrencyCode("SYP"),
    CurrencyCode("SZL"),
    CurrencyCode("THB", ("฿",)),
    CurrencyCode("TJS"),
    CurrencyCode("TMT"),
    CurrencyCode("TND", ("DT",), 3),
    CurrencyCode("TOP", ("T$",)),
    CurrencyCode("TRY", ("₺",)),
    CurrencyCode("TTD", ("TT$",)),
    CurrencyCode("TWD", ("NT$",)),
    CurrencyCode("TZS", ("TSh",)),
    CurrencyCode("UAH", ("₴",)),
    CurrencyCode("UGX", ("USh",), 0),
    CurrencyCode("USD", ("$", "US$")),
    CurrencyCode("UYU"),
    CurrencyCode("UZS"),
    CurrencyCode("VES"),
    CurrencyCode("VND", ("₫",), 0),
    CurrencyCode("VUV", (), 0),
    CurrencyCode("WST"),
    CurrencyCode("XAF", (), 0),
    CurrencyCode("XCD", ("EC$",)),
    CurrencyCode("XCG"),
    CurrencyCode("XOF", (), 0),
    CurrencyCode("XPF", (), 0),
    CurrencyCode("YER"),
    CurrencyCode("ZAR"),
    CurrencyCode("ZMW"),
    CurrencyCode("ZWG", ("ZiG",)),
)

CurrencyName = tuple[str, str | None, str | None, str | None]


def build_currencies(
    names: dict[str, CurrencyName],
    aliases: dict[str, str] | None = None,
    extra_symbols: dict[str, tuple[str, ...]] | None = None,
    ambiguous_words: tuple[str, ...] = (),
) -> tuple[Currency, ...]:
    """Joins the code table with one language's names.

    names: code -> (unit, unit plural or None, subunit or None, subunit plural or None)
    aliases: other written words for a currency, e.g. {"রিয়াল": "SAR"}
    extra_symbols: language-specific written forms, e.g. {"BDT": ("/-",)}
    ambiguous_words: unit names that must not be read as money after a number, e.g. "pound" (weight)
    """
    aliases = aliases or {}
    extra_symbols = extra_symbols or {}
    currencies = []
    for entry in CURRENCY_CODES:
        if entry.code not in names:
            continue
        unit, unit_plural, subunit, subunit_plural = names[entry.code]
        written_names = (unit, unit_plural, *(word for word, code in aliases.items() if code == entry.code))
        currencies.append(
            Currency(
                unit=unit,
                subunit=subunit,
                unit_plural=unit_plural,
                subunit_plural=subunit_plural,
                code=entry.code,
                minor_digits=entry.minor_digits if subunit else 0,
                symbols=(entry.code, *entry.symbols),
                suffix_symbols=(
                    *extra_symbols.get(entry.code, ()),
                    *(word for word in written_names if word and word not in ambiguous_words),
                ),
            )
        )
    return tuple(currencies)
