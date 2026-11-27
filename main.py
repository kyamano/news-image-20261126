#!/usr/bin/env python3
"""The World in One Day - Thursday 26 November 2026.

Draws a newspaper-style front page summing up the world's news of
Thursday 26 November 2026 (10 detailed stories + 20 briefs + numbers box),
as a 1024x1024 PNG, using only the Python 3.13 standard library.

No network, no randomness, no timestamps: two runs produce byte-identical
output. Writes entry.png to MAKEFUN_OUTPUT_DIR if set, else to /output if
that directory exists, else next to this script.
"""

import os
import struct
import zlib

W = 1024
H = 1024

PAPER = (246, 241, 230)
NAVY = (20, 36, 62)
INK = (26, 26, 26)
RED = (155, 27, 27)
GOLD = (200, 162, 74)
GREY = (107, 107, 107)
WHITE = (255, 255, 255)

# ---------------------------------------------------------------- 5x7 font
# Each glyph: 7 rows of 5 bits, '1' = filled pixel. Uppercase ASCII only.
FONT = {
    "A": ("01110", "10001", "10001", "11111", "10001", "10001", "10001"),
    "B": ("11110", "10001", "10001", "11110", "10001", "10001", "11110"),
    "C": ("01110", "10001", "10000", "10000", "10000", "10001", "01110"),
    "D": ("11110", "10001", "10001", "10001", "10001", "10001", "11110"),
    "E": ("11111", "10000", "10000", "11110", "10000", "10000", "11111"),
    "F": ("11111", "10000", "10000", "11110", "10000", "10000", "10000"),
    "G": ("01110", "10001", "10000", "10111", "10001", "10001", "01111"),
    "H": ("10001", "10001", "10001", "11111", "10001", "10001", "10001"),
    "I": ("01110", "00100", "00100", "00100", "00100", "00100", "01110"),
    "J": ("00111", "00010", "00010", "00010", "00010", "10010", "01100"),
    "K": ("10001", "10010", "10100", "11000", "10100", "10010", "10001"),
    "L": ("10000", "10000", "10000", "10000", "10000", "10000", "11111"),
    "M": ("10001", "11011", "10101", "10101", "10001", "10001", "10001"),
    "N": ("10001", "11001", "10101", "10011", "10001", "10001", "10001"),
    "O": ("01110", "10001", "10001", "10001", "10001", "10001", "01110"),
    "P": ("11110", "10001", "10001", "11110", "10000", "10000", "10000"),
    "Q": ("01110", "10001", "10001", "10001", "10101", "10010", "01101"),
    "R": ("11110", "10001", "10001", "11110", "10100", "10010", "10001"),
    "S": ("01111", "10000", "10000", "01110", "00001", "00001", "11110"),
    "T": ("11111", "00100", "00100", "00100", "00100", "00100", "00100"),
    "U": ("10001", "10001", "10001", "10001", "10001", "10001", "01110"),
    "V": ("10001", "10001", "10001", "10001", "10001", "01010", "00100"),
    "W": ("10001", "10001", "10001", "10101", "10101", "11011", "10001"),
    "X": ("10001", "10001", "01010", "00100", "01010", "10001", "10001"),
    "Y": ("10001", "10001", "01010", "00100", "00100", "00100", "00100"),
    "Z": ("11111", "00001", "00010", "00100", "01000", "10000", "11111"),
    "0": ("01110", "10001", "10011", "10101", "11001", "10001", "01110"),
    "1": ("00100", "01100", "00100", "00100", "00100", "00100", "01110"),
    "2": ("01110", "10001", "00001", "00010", "00100", "01000", "11111"),
    "3": ("11110", "00001", "00001", "01110", "00001", "00001", "11110"),
    "4": ("00010", "00110", "01010", "10010", "11111", "00010", "00010"),
    "5": ("11111", "10000", "11110", "00001", "00001", "10001", "01110"),
    "6": ("01110", "10000", "10000", "11110", "10001", "10001", "01110"),
    "7": ("11111", "00001", "00010", "00100", "01000", "01000", "01000"),
    "8": ("01110", "10001", "10001", "01110", "10001", "10001", "01110"),
    "9": ("01110", "10001", "10001", "01111", "00001", "00001", "01110"),
    " ": ("00000", "00000", "00000", "00000", "00000", "00000", "00000"),
    ".": ("00000", "00000", "00000", "00000", "00000", "01100", "01100"),
    ",": ("00000", "00000", "00000", "00000", "01100", "00100", "01000"),
    ":": ("00000", "01100", "01100", "00000", "01100", "01100", "00000"),
    ";": ("00000", "01100", "01100", "00000", "01100", "00100", "01000"),
    "!": ("00100", "00100", "00100", "00100", "00100", "00000", "00100"),
    "?": ("01110", "10001", "00001", "00010", "00100", "00000", "00100"),
    "-": ("00000", "00000", "00000", "01110", "00000", "00000", "00000"),
    "'": ("00100", "00100", "01000", "00000", "00000", "00000", "00000"),
    '"': ("01010", "01010", "00000", "00000", "00000", "00000", "00000"),
    "(": ("00010", "00100", "01000", "01000", "01000", "00100", "00010"),
    ")": ("01000", "00100", "00010", "00010", "00010", "00100", "01000"),
    "/": ("00001", "00010", "00010", "00100", "01000", "01000", "10000"),
    "%": ("11001", "11010", "00010", "00100", "01000", "01011", "10011"),
    "$": ("00100", "01111", "10100", "01110", "00101", "11110", "00100"),
    "&": ("01100", "10010", "10100", "01000", "10101", "10010", "01101"),
    "+": ("00000", "00100", "00100", "01110", "00100", "00100", "00000"),
    "=": ("00000", "00000", "01110", "00000", "01110", "00000", "00000"),
    "*": ("00000", "10101", "01110", "10101", "00000", "00000", "00000"),
    "#": ("01010", "01010", "11111", "01010", "11111", "01010", "01010"),
    "@": ("01110", "10001", "10111", "10101", "10110", "10000", "01110"),
    "[": ("01110", "01000", "01000", "01000", "01000", "01000", "01110"),
    "]": ("01110", "00010", "00010", "00010", "00010", "00010", "01110"),
    "<": ("00010", "00100", "01000", "10000", "01000", "00100", "00010"),
    ">": ("01000", "00100", "00010", "00001", "00010", "00100", "01000"),
    "_": ("00000", "00000", "00000", "00000", "00000", "00000", "11111"),
    "\u2022": ("00000", "00000", "01100", "01100", "01100", "00000", "00000"),
}


def glyph(ch):
    if ch in FONT:
        return FONT[ch]
    if ch == "\u2014" or ch == "\u2013":  # em/en dash -> hyphen
        return FONT["-"]
    if ch == "\u2019" or ch == "\u2018":  # curly quotes -> straight
        return FONT["'"]
    return FONT["?"]


# ------------------------------------------------------------------ canvas
class Canvas:
    def __init__(self, w, h, bg):
        self.w = w
        self.h = h
        self.px = bytearray(w * h * 3)
        self.fill_rect(0, 0, w, h, bg)

    def set(self, x, y, color):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.px[i], self.px[i + 1], self.px[i + 2] = color

    def fill_rect(self, x, y, w, h, color):
        x0 = max(0, x)
        y0 = max(0, y)
        x1 = min(self.w, x + w)
        y1 = min(self.h, y + h)
        for yy in range(y0, y1):
            base = (yy * self.w + x0) * 3
            for xx in range(x0, x1):
                i = base + (xx - x0) * 3
                self.px[i], self.px[i + 1], self.px[i + 2] = color

    def hline(self, x, y, w, color, thick=1):
        self.fill_rect(x, y, w, thick, color)

    def vline(self, x, y, h, color, thick=1):
        self.fill_rect(x, y, thick, h, color)

    def text_width(self, text, scale):
        return len(text) * 6 * scale - scale

    def draw_text(self, x, y, text, scale, color):
        cx = x
        for ch in text:
            g = glyph(ch)
            for row in range(7):
                bits = g[row]
                for col in range(5):
                    if bits[col] == "1":
                        self.fill_rect(cx + col * scale, y + row * scale,
                                       scale, scale, color)
            cx += 6 * scale
        return cx

    def draw_centered(self, y, text, scale, color, cx0=0, cx1=None):
        if cx1 is None:
            cx1 = self.w
        tw = self.text_width(text, scale)
        self.draw_text(cx0 + (cx1 - cx0 - tw) // 2, y, text, scale, color)

    def wrap(self, text, width_px, scale):
        """Greedy word wrap; returns list of lines fitting width_px."""
        max_chars = max(1, (width_px + scale) // (6 * scale))
        lines = []
        for para in text.split("\n"):
            words = para.split(" ")
            cur = ""
            for word in words:
                trial = word if not cur else cur + " " + word
                if len(trial) <= max_chars:
                    cur = trial
                else:
                    if cur:
                        lines.append(cur)
                    # hard-split overlong words
                    while len(word) > max_chars:
                        lines.append(word[:max_chars])
                        word = word[max_chars:]
                    cur = word
            if cur:
                lines.append(cur)
        return lines


# ------------------------------------------------------------------ content
STORIES = [
    ("GULF WAR",
     "IRAN DRONE STRIKE KILLS TWO ITALIANS IN KUWAIT",
     "DRONES HIT A KUWAITI AIR-DEFENCE SITE, KILLING TWO TECHNICIANS; "
     "TEHRAN DENIES IT. TWO MORE ITALIANS WERE INJURED."),
    ("ENERGY",
     "TWO TANKERS HIT MINES IN THE STRAIT OF HORMUZ",
     "IRAN SAYS TWO TANKERS STRUCK MINES AND CAUGHT FIRE; "
     "BRENT SETTLES AT $96.57. WTI UP TO $84.84."),
    ("ASIA",
     "KIM JONG UN TOURS NUCLEAR SITES",
     "KCNA REVEALS KIM INSPECTED NUCLEAR-MATERIAL PLANTS AND THE "
     "HWASAN-31 WARHEAD, AND ORDERED WIDER TACTICAL-NUKE DEPLOYMENT."),
    ("ASIA",
     "MYANMAR REJECTS PARTS OF ICJ GENOCIDE RULING",
     "JUNTA CHIEF MIN AUNG HLAING SAYS THE GOVERNMENT WILL NOT COMPLY "
     "WITH 'INAPPROPRIATE' PARTS OF THE RULING ON THE ROHINGYA CASE."),
    ("BRITAIN",
     "UK NET MIGRATION FALLS TO 77,000",
     "LOWEST SINCE 1997, DOWN FROM 204,000 A YEAR EARLIER AND A PEAK "
     "NEAR 944,000 IN 2023, ONS SAYS."),
    ("USA",
     "TRUMP'S THANKSGIVING MESSAGE ATTACKS CRITICS",
     "IN A 461-WORD POST HE HITS LIBERALS AND IMMIGRANTS, SINGLING OUT "
     "SOMALIS; CITES GDP AT 4.3%."),
    ("ASIA",
     "BANGKOK REFINERY BLAST INJURES SEVEN",
     "EXPLOSION AT BANGCHAK'S PHRA KHANONG REFINERY INJURES SEVEN, FOUR "
     "CRITICALLY; ALL UNITS SHUT. THE BLAST HIT AT ABOUT 14:45 LOCAL TIME."),
    ("AFRICA",
     "GUINEA-BISSAU DELAYS ELECTION TO NOVEMBER 2028",
     "JUNTA POSTPONES THE DECEMBER 6 VOTE BY DECREE, A YEAR AFTER THE "
     "2025 COUP."),
    ("EUROPE",
     "EU BACKS 45BN-EURO UKRAINE LOAN FOR 2027",
     "24 OF 27 STATES BACK THE LOAN IN BRUSSELS; A 2028-2034 BUDGET DEAL "
     "SLIPS TO DECEMBER. THE LOAN COVERS UKRAINE'S NEEDS IN 2027."),
    ("EUROPE",
     "DE COS TO LEAD THE ECB FROM FEBRUARY 2027",
     "EUROZONE LEADERS PICK PABLO HERNANDEZ DE COS TO SUCCEED CHRISTINE "
     "LAGARDE. HE TAKES OFFICE ON FEBRUARY 7, 2027."),
]

BRIEFS = [
    "NOR'EASTER SLAMS US EAST COAST ON THANKSGIVING; NYC PARADE MOVED TO SATURDAY.",
    "CAIRO TANKER FIRE: DRIVER DETAINED; DEATH TOLL CONFIRMED AT 31, WITH 26 INJURED.",
    "WORLD REACTS TO TRUMP TARIFFS; JAPAN PROTESTS NEW US TARIFF RATE.",
    "BANGLADESH GARMENT WORKERS REJECT 36% PAY RISE; HIGHWAYS BLOCKED, TEAR GAS FIRED.",
    "EBOLA IN DR CONGO: 12,021 CASES, 5,904 DEAD - FASTEST-GROWING OUTBREAK ON RECORD.",
    "INDONESIA GOLD-MINE FLOOD: 13 DEAD, 13 STILL TRAPPED AS SEARCH RESUMES.",
    "SINNER OUT OF 2027 AUSTRALIAN OPEN AFTER KNEE SURGERY.",
    "ISRAEL KILLS HAMAS ECONOMY CHIEF KHALED ABU NADA IN OVERNIGHT GAZA STRIKE.",
    "NVIDIA HALTS AI SERVER SHIPMENTS TO MALAYSIA, SINGAPORE, THAILAND, INDONESIA.",
    "HONG KONG MARKS ONE YEAR SINCE WANG FUK COURT FIRE THAT KILLED 168.",
    "PAKISTAN: JUI-F CHIEF CALLS NATIONWIDE HIGHWAY BLOCKADE AFTER LEADERS DETAINED.",
    "BANGLADESH: HASINA'S EX-PRESS AIDE ARRESTED; 108 PARAMILITARY PLATOONS DEPLOYED.",
    "MUSK PLEDGES A SPACEX SHARE FOR EVERY US CHILD, EVERY YEAR.",
    "US OFFICIALS DIVIDED OVER SPY CLAIMS ABOUT NVIDIA'S ALICE HUANG.",
    "NORSE ATLANTIC SUSPENDS ALL FLIGHTS, WARNS OF BANKRUPTCY FILING.",
    "DIESEL TANKER CAPSIZES OFF IBIZA; ONE CREW MEMBER DEAD, SPILL FEARED.",
    "SAUDI AIR DEFENCES DOWN HOUTHI MISSILES AIMED AT RIYADH.",
    "HOUTHI STRIKE ON JAZAN REFINERY KILLS ONE NEPALI WORKER; OUTPUT PARTLY HALTED.",
    "TRUMP SAYS US HAS 'VICTORY AT HAND' IN IRAN WAR, OFFERS TEHRAN A DEAL.",
    "PAKISTAN TO HOST MECCA PACT TALKS ON YEMEN, DEFENCE MINISTER SAYS.",
]

NUMBERS = [
    "$96.57 - BRENT CRUDE, HIGHEST SINCE NOV 6",
    "77,000 - UK NET MIGRATION, LOWEST SINCE 1997",
    "45BN EURO - EU LOAN FOR UKRAINE IN 2027",
    "31 - DEAD IN CAIRO TANKER FIRE",
    "12,021 - EBOLA CASES IN DR CONGO",
    "168 - KILLED IN HONG KONG FIRE, ONE YEAR ON",
]


# ------------------------------------------------------------------ drawing
def draw(c):
    # --- masthead ------------------------------------------------------
    c.fill_rect(0, 0, W, 116, NAVY)
    c.draw_centered(24, "THE WORLD IN ONE DAY", 4, WHITE)
    c.draw_centered(66, "THURSDAY 26 NOVEMBER 2026", 2, WHITE)
    c.hline(0, 112, W, GOLD, 3)

    # --- deck ----------------------------------------------------------
    c.draw_centered(130, "GULF WAR ESCALATES  \u2022  EUROPE BACKS UKRAINE  "
                         "\u2022  A STORMY THANKSGIVING", 1, RED)
    c.hline(28, 152, W - 56, NAVY, 2)

    # --- columns -------------------------------------------------------
    left_x, left_w = 28, 620
    right_x, right_w = 668, 324
    top_y = 168
    bottom_y = 940
    c.vline(656, top_y, bottom_y - top_y, NAVY, 1)

    # --- left: 10 detailed stories -------------------------------------
    # First measure every block, then spread the leftover space evenly.
    blocks = []
    for tag, head, summ in STORIES:
        hl = c.wrap(head, left_w - 38, 2)
        sl = c.wrap(summ, left_w - 38, 1)
        blocks.append((tag, hl, sl))
    base_h = []
    for _tag, hl, sl in blocks:
        base_h.append(14 + len(hl) * 16 + 3 + len(sl) * 9)
    total_base = sum(base_h)
    n = len(blocks)
    gap = (bottom_y - top_y - total_base) // (n - 1) if n > 1 else 12
    gap = max(gap, 10)
    y = top_y
    for i, (tag, hl, sl) in enumerate(blocks):
        num = str(i + 1)
        c.fill_rect(left_x, y, 28, 28, NAVY)
        c.draw_centered(y + 7, num, 2, WHITE, left_x, left_x + 28)
        c.draw_text(left_x + 38, y + 1, tag, 1, RED)
        hy = y + 14
        for line in hl:
            c.draw_text(left_x + 38, hy, line, 2, INK)
            hy += 16
        sy = hy + 3
        for line in sl:
            c.draw_text(left_x + 38, sy, line, 1, INK)
            sy += 9
        y = sy + gap

    # --- right: briefs --------------------------------------------------
    ry = top_y
    c.draw_text(right_x, ry, "ALSO ON THURSDAY", 2, NAVY)
    c.hline(right_x, ry + 20, right_w, RED, 2)
    ry += 30
    for brief in BRIEFS:
        lines = c.wrap(brief, right_w - 14, 1)
        c.fill_rect(right_x, ry + 2, 6, 6, RED)
        ly = ry
        for line in lines:
            c.draw_text(right_x + 14, ly, line, 1, INK)
            ly += 9
        ry = ly + 10

    # --- right: numbers box --------------------------------------------
    box_y = ry + 8
    box_h = 26 + len(NUMBERS) * 17 + 12
    c.fill_rect(right_x, box_y, right_w, box_h, (233, 226, 208))
    c.hline(right_x, box_y, right_w, NAVY, 2)
    c.draw_text(right_x + 10, box_y + 8, "THE DAY IN NUMBERS", 1, NAVY)
    ny = box_y + 28
    for row in NUMBERS:
        c.draw_text(right_x + 10, ny, row, 1, INK)
        ny += 17

    # --- footer ----------------------------------------------------------
    c.hline(28, 952, W - 56, NAVY, 2)
    c.draw_centered(962,
                    "SOURCES: REUTERS, AP, AFP, AL JAZEERA, YONHAP, ONS, "
                    "CNA, BANGKOK POST", 1, GREY)
    c.draw_centered(975,
                    "LE MONDE, HAARETZ, JERUSALEM POST, TIMES OF ISRAEL, "
                    "FINANCIAL TIMES, STRAITS TIMES", 1, GREY)
    c.draw_centered(990,
                    "ALL EVENTS HAPPENED OR WERE FIRST REPORTED ON "
                    "THURSDAY 26 NOVEMBER 2026", 1, NAVY)


# ------------------------------------------------------------------ PNG out
def _chunk(kind, data):
    out = struct.pack(">I", len(data)) + kind + data
    out += struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)
    return out


def write_png(path, c):
    raw = b"".join(
        b"\x00" + bytes(c.px[y * W * 3:(y + 1) * W * 3]) for y in range(H)
    )
    png = b"\x89PNG\r\n\x1a\n"
    png += _chunk(b"IHDR", struct.pack(">IIBBBBB", W, H, 8, 2, 0, 0, 0))
    png += _chunk(b"IDAT", zlib.compress(raw, 9))
    png += _chunk(b"IEND", b"")
    with open(path, "wb") as f:
        f.write(png)


def _output_dir():
    """Directory for entry.png.

    The grading sandbox mounts the repository read-only, so writing next
    to this script fails there; it writes to /output instead (via
    MAKEFUN_OUTPUT_DIR). Priority: the MAKEFUN_OUTPUT_DIR environment
    variable, then /output if it exists, then this script's directory.
    """
    env_dir = os.environ.get("MAKEFUN_OUTPUT_DIR")
    if env_dir:
        return env_dir
    if os.path.isdir("/output"):
        return "/output"
    return os.path.dirname(os.path.abspath(__file__))


def main():
    canvas = Canvas(W, H, PAPER)
    draw(canvas)
    write_png(os.path.join(_output_dir(), "entry.png"), canvas)


if __name__ == "__main__":
    main()
