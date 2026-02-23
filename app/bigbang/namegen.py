"""Syllable-based sector name generator, ported from twclone's namegen."""

import random

PREFIXES = [
    "A", "Ab", "Ac", "Add", "Ad", "Af", "Aggr", "Ax", "Az",
    "Bat", "Be", "Byt", "Cyth", "Agr", "Ast", "As", "Al", "Adw",
    "Adr", "Ar", "B", "Br", "C", "Cr", "Ch", "Cad", "D", "Dr",
    "Dw", "Ed", "Eth", "Et", "Er", "El", "Eow", "F", "Fr", "Ferr",
    "G", "Gr", "Gw", "Gal", "Gl", "H", "Ha", "Ib", "Jer", "K",
    "Ka", "Ked", "L", "Loth", "Lar", "Leg", "M", "Mir", "N", "Nyd",
    "Ol", "Oc", "On", "P", "Pr", "R", "Rh", "S", "Sev", "T",
    "Tr", "Th", "V", "Y", "Yb", "Z", "W", "Wic", "Wac", "Wer",
    "Fert", "D'al", "Fl'a", "L'Dre", "Ra", "Rea", "Og", "O'g",
    "Ndea", "Faw", "Cef", "Wyh", "Gyh", "G'As", "Red", "Aas",
    "Aaw", "Ewwa", "Syw", "Tal", "Zan", "Vex", "Kor", "Dra",
    "Xen", "Pyr", "Qar", "Jex", "Nym", "Bel", "Cel", "Fen",
]

MIDDLES = [
    "a", "ase", "ae", "au", "ao", "are", "ale", "ali", "ay", "ardo",
    "e", "ere", "ehe", "eje", "eo", "ei", "ea", "eye", "eri", "era",
    "ela", "eli", "enda", "erra",
    "i", "ia", "ioe", "itti", "otte", "ie", "ire", "ira", "ila", "ili",
    "illi", "igo",
    "o", "oje", "oli", "olye",
    "ua", "ue", "uyye", "oa", "oi", "oe", "ore",
    "ana", "ula", "ova", "yne", "axi", "eri", "onn", "ith", "esh", "aur",
    "ell", "arr", "unn",
]

SUFFIXES = [
    "and", "be", "bwyn", "baen", "bard", "ctred", "cred", "ch", "can",
    "dan", "don", "der", "dric", "dfrid", "dus",
    "gord", "gan",
    "li", "le", "lgrin", "lin", "lith", "lath", "loth", "ld", "ldric",
    "ldan",
    "mas", "mos", "mar",
    "ond", "ydd", "idd",
    "nnon", "wan", "yth", "nad", "nn", "nor", "nd",
    "ron", "rd", "sh", "seth",
    "ean", "th", "threm", "tha", "tan", "tem", "tam",
    "vix", "vud",
    "wix", "win", "wyn", "wyr", "wyth",
    "zer", "zan",
    "qela", "rli",
    "wa", "kera", "ji", "jia", "kie", "hireg",
    "jira", "fila", "vili", "cira", "digo",
    "no", "noje", "woli",
    "tua", "tue", "tye", "toa", "toi", "toe", "tore",
    "rix", "nus", "tis", "vos", "xar", "zul", "phe", "gor", "wen",
    "ton", "ley", "mir", "nar", "sol", "ven",
]


def generate_name(rng: random.Random | None = None) -> str:
    """Generate a random sector name from syllable components."""
    r = rng or random
    return r.choice(PREFIXES) + r.choice(MIDDLES) + r.choice(SUFFIXES)


def generate_unique_names(count: int, rng: random.Random | None = None) -> list[str]:
    """Generate `count` unique sector names."""
    r = rng or random
    names: set[str] = set()
    while len(names) < count:
        names.add(generate_name(r))
    return list(names)
