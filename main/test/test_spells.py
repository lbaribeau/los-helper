
#OK the best way to test as usual was just to edit in the code and run the code...
# Since this bit executes right off the bat

s="/=== Combat Spells ======================================================\\\
|                                   none                                 |\
/================== Healing and Protection ==============================\\\
|   Vigor                                                                |\
/======================================= Miscellaneous ==================\\\
|                                   none                                 |\
/===================================================== Running Spells ===\\\
|                                   none                                 |\
\========================================================================/"


test = (
    "\n\r"
    "/=== Combat Spells ======================================================\\\n\r"
    "|          none                                                          |\n\r"
    "/================== Healing and Protection ==============================\\\n\r"
    "|   Vigor                                                                |\n\r"
    "/======================================= Miscellaneous ==================\\\n\r"
    "|   Light                                                                |\n\r"
    "|   Show-Aura                                                            |\n\r"
    "/===================================================== Running Spells ===\\\n\r"
    "|                                   none                                 |\n\r"
    "\========================================================================/\n\r"

)


spells = (
    r"\n\r"
    r"/=== Combat Spells ======================================================\\\s+"
    r"\|\s(?:\s+none\s+\|)|(?:Level Earth        Wind         Fire         Water        Astral       \|\s+\|   1(?P<black1>.+?)\|\s+\|   2(?P<black2>.+?)\|\s+\|   3(?P<black3>.+?)\|\s+\|   4(?P<black4>.+?)\|\s+\|   5(?P<black5>.+?)\|)\s+"
    # r"|(?:\s+none\s+|)|"

    # r"(?P<black>(?:\|\s+.+?\s+\|\s*?\n\r)+)"
    # r"\|(?P<none>\s+none\s+\|)\s*?\n\r"
    # r"\|\s(?:\s+none\s+\|)|(?:Level Earth        Wind         Fire         Water        Astral       \|\s+\|   1(?P<black1>.+?)\|\s+\|   2(?P<black2>.+?)\|\s+\|   3(?P<black3>.+?)\|\s+\|   4(?P<black4>.+?)\|\s+\|   5(?P<black5>.+?)\|)\s+"
    # r"\|\s(Level Earth        Wind         Fire         Water        Astral       \|\s+\|   1(?P<black1>.+?)\|\s+\s+\|\s+\|   2(?P<black2>.+?)\|\s+\|   3(?P<black3>.+?)\|\s+\|   4(?P<black4>.+?)\|\s+\|   5(?P<black5>.+?)\|)\s+"
    # r"\|\s(  1(?P<black1>.+?)\|\s+\|\s+\|   2(?P<black2>.+?)\|\s+\|   3(?P<black3>.+?)\|\s+\|   4(?P<black4>.+?)\|\s+\|   5(?P<black5>.+?)\|)\s+"
    r"/================== Healing and Protection ==============================\\\s+"
    # r"\|   1(?P<black1>.+?)\|\s+"  # . can match spaces, and \s can match newlines
    # r"\|   2(?P<black2>.+?)\|\s+"
    # r"\|   3(?P<black3>.+?)\|\s+"
    # r"\|   4(?P<black4>.+?)\|\s+"
    # r"\|   5(?P<black5>.+?)\|\s+"
    # A regex without 1-5 specified and done with a quantifier could work if we don't put 
    # .+ and \s+ next to eachother, like this (maybe) (same with \s and \n/\r):
    # r"(?P<black>(?:\|.+?\|\s*?)+)"  erhm except I think, we can't use | as the anchor now, 
    # and same with newline, we'd have to use the Astral    | and the /===== as the anchors 
    # and match everything in between.  Spells.py would need to deal with the grouped '|'s.
    # r"(?P<white>(?:\|\s+.+?\s+\|\s*?\n\r)+)"
    r"\|(?P<white>.+?)\|\s+"
    r"(?:\|(?P<white2>.+?)\|\s+)?"
    r"(?:\|(?P<white3>.+?)\|\s+)?"
    r"/======================================= Miscellaneous ==================\\\s+"
    # r"(?P<misc>(?:\|\s+.+?\s+\|\s*?\n\r)+)"
    r"\|(?P<misc>.+?)\|\s+"
    r"(?:\|(?P<misc2>.+?)\|\s+)?"
    r"(?:\|(?P<misc3>.+?)\|\s+)?"
    r"/===================================================== Running Spells ===\\\s+"
    # r"(?P<buffs>(?:\|\s+.+?\s+\|\s*?\n\r)+)"
    r"\|(?P<buffs>.+?)\|\s+"
    r"(?:\|(?P<buffs2>.+?)\|\s+)?"
    r"(?:\|(?P<buffs3>.+?)\|\s+)?"
    # r"\\========================================================================/\s*\n\r"
    r"\\="
)


# SCRAP ATTEMPTS
# Not completely sure why they didn't work
# Splitting it in two works...
# No need to be perfectionist...


# spells= [(
#     r"\n\r"
#     r"/=== Combat Spells ======================================================\\\s+"
#     r"\|          none                                                          \|\s+"
#     r"/================== Healing and Protection ==============================\\\s+"
#     r"\|   Vigor                                                                \|\s+"
#     r"/======================================= Miscellaneous ==================\\\s+"
#     r"\|   Light                                                                \|\s+"
#     r"\|   Show-Aura                                                            \|\s+"
#     r"/===================================================== Running Spells ===\\\s+"
#     r"\|                                   none                                 \|\s+"
#     r"\\========================================================================/"
# )]

# spells_good_progress = [(
#     r"\n\r"
#     r"/=== Combat Spells ======================================================\\\s+"
#     # r"(\|\s+none\s+\|)|(\s+" # Unterminated subpattern
#     r"/================== Healing and Protection ==============================\\\s+"
#     r"\|(?P<white>.+?)\|\s+"
#     r"(?:\|(?P<white2>.+?)\|\s+)?"
#     r"(?:\|(?P<white3>.+?)\|\s+)?"
#     r"/======================================= Miscellaneous ==================\\\s+"
#     r"\|(?P<misc>.+?)\|\s+"
#     r"(?:\|(?P<misc2>.+?)\|\s+)?"
#     r"(?:\|(?P<misc3>.+?)\|\s+)?"
#     r"/===================================================== Running Spells ===\\\s+"
#     r"\|(?P<buffs>.+?)\|\s+"
#     r"(?:\|(?P<buffs2>.+?)\|\s+)?"
#     r"(?:\|(?P<buffs3>.+?)\|\s+)?"
#     r"\\========================================================================/"
# )]

# spells=spells_basic_test

# Doesn't work...
# spells = [(
#     r"\n\r"
#     r"/=== Combat Spells ======================================================\\\s+"
#     # r"(\|\s+none\s+\|)|(\s+Level Earth        Wind         Fire         Water        Astral\s+\|\s+\|\s+1\s+(?P<black1>.+?)\|\s+\|\s+2\s+(?P<black2>.+?)\|\s+\|\s+3\s+(?P<black3>.+?)\|\s+\|\s+4\s+(?P<black4>.+?)\|\s+\|\s+5\s+(?P<black5>.+?)\|)"
#      # r"\|\s+none\s+\|"
#     r"(\|\s+none\s+\|)|(\| Level Earth        Wind         Fire         Water        Astral\s+\|\s+"
#     r"\|\s+1\s+(?P<black1>.+?)\|\s+"
#     r"\|\s+2\s+(?P<black2>.+?)\|\s+"
#     r"\|\s+3\s+(?P<black3>.+?)\|\s+"
#     r"\|\s+4\s+(?P<black4>.+?)\|\s+"
#     r"\|\s+5\s+(?P<black5>.+?)\|)"
#     r"\s+/================== Healing and Protection ==============================\\\s+"
#     r"\|(?P<white>.+?)\|\s+"
#     r"(?:\|(?P<white2>.+?)\|\s+)?"
#     r"(?:\|(?P<white3>.+?)\|\s+)?"
#     r"/======================================= Miscellaneous ==================\\\s+"
#     r"\|(?P<misc>.+?)\|\s+"
#     r"(?:\|(?P<misc2>.+?)\|\s+)?"
#     r"(?:\|(?P<misc3>.+?)\|\s+)?"
#     r"/===================================================== Running Spells ===\\\s+"
#     r"\|(?P<buffs>.+?)\|\s+"
#     r"(?:\|(?P<buffs2>.+?)\|\s+)?"
#     r"(?:\|(?P<buffs3>.+?)\|\s+)?"
#     r"\\========================================================================/"
# )]

# spells = [(
#     r"\n\r"
#     r"/=== Combat Spells ======================================================\\\s+"
#     # r"(\|\s+none\s+\|)|(\s+Level Earth        Wind         Fire         Water        Astral\s+\|\s+\|\s+1\s+(?P<black1>.+?)\|\s+\|\s+2\s+(?P<black2>.+?)\|\s+\|\s+3\s+(?P<black3>.+?)\|\s+\|\s+4\s+(?P<black4>.+?)\|\s+\|\s+5\s+(?P<black5>.+?)\|)"
#      # r"\|\s+none\s+\|"
#     r"(\|\s+none\s+\|)?"
#     r"(\| Level Earth        Wind         Fire         Water        Astral\s+\|\s+)?"
#     r"(\|\s+1\s+(?P<black1>.+?)\|\s+)?"
#     r"(\|\s+2\s+(?P<black2>.+?)\|\s+)?"
#     r"(\|\s+3\s+(?P<black3>.+?)\|\s+)?"
#     r"(\|\s+4\s+(?P<black4>.+?)\|\s+)?"
#     r"(\|\s+5\s+(?P<black5>.+?)\|)?"
#     r"\s+/================== Healing and Protection ==============================\\\s+"
#     r"\|(?P<white>.+?)\|\s+"
#     r"(?:\|(?P<white2>.+?)\|\s+)?"
#     r"(?:\|(?P<white3>.+?)\|\s+)?"
#     r"/======================================= Miscellaneous ==================\\\s+"
#     r"\|(?P<misc>.+?)\|\s+"
#     r"(?:\|(?P<misc2>.+?)\|\s+)?"
#     r"(?:\|(?P<misc3>.+?)\|\s+)?"
#     r"/===================================================== Running Spells ===\\\s+"
#     r"\|(?P<buffs>.+?)\|\s+"
#     r"(?:\|(?P<buffs2>.+?)\|\s+)?"
#     r"(?:\|(?P<buffs3>.+?)\|\s+)?"
#     r"\\========================================================================/"
# )]

# spells = [(
#     r"\n\r"
#     r"/=== Combat Spells ======================================================\\\s+"
#     # r"(\|\s+none\s+\|)|(\s+Level Earth        Wind         Fire         Water        Astral\s+\|\s+\|\s+1\s+(?P<black1>.+?)\|\s+\|\s+2\s+(?P<black2>.+?)\|\s+\|\s+3\s+(?P<black3>.+?)\|\s+\|\s+4\s+(?P<black4>.+?)\|\s+\|\s+5\s+(?P<black5>.+?)\|)"
#      # r"\|\s+none\s+\|"
#     r"(\|\s+none\s+\|)|(\| Level Earth        Wind         Fire         Water        Astral\s+\|)\s+"
#     r"(\|\s+1\s+(?P<black1>.+?)\|\s+)?"
#     r"(\|\s+2\s+(?P<black2>.+?)\|\s+)?"
#     r"(\|\s+3\s+(?P<black3>.+?)\|\s+)?"
#     r"(\|\s+4\s+(?P<black4>.+?)\|\s+)?"
#     r"(\|\s+5\s+(?P<black5>.+?)\|)?"
#     r"\s+/================== Healing and Protection ==============================\\\s+"
#     r"\|(?P<white>.+?)\|\s+"
#     r"(?:\|(?P<white2>.+?)\|\s+)?"
#     r"(?:\|(?P<white3>.+?)\|\s+)?"
#     r"/======================================= Miscellaneous ==================\\\s+"
#     r"\|(?P<misc>.+?)\|\s+"
#     r"(?:\|(?P<misc2>.+?)\|\s+)?"
#     r"(?:\|(?P<misc3>.+?)\|\s+)?"
#     r"/===================================================== Running Spells ===\\\s+"
#     r"\|(?P<buffs>.+?)\|\s+"
#     r"(?:\|(?P<buffs2>.+?)\|\s+)?"
#     r"(?:\|(?P<buffs3>.+?)\|\s+)?"
#     r"\\========================================================================/"
# )]




# spells = [(
#     r"\n\r"
#     r"/=== Combat Spells ======================================================\\\s+"
#     # r"(\|\s+none\s+\|)|(\s+Level Earth        Wind         Fire         Water        Astral\s+\|\s+\|\s+1\s+(?P<black1>.+?)\|\s+\|\s+2\s+(?P<black2>.+?)\|\s+\|\s+3\s+(?P<black3>.+?)\|\s+\|\s+4\s+(?P<black4>.+?)\|\s+\|\s+5\s+(?P<black5>.+?)\|)"
#      # r"\|\s+none\s+\|"
#     r"(\|\s+none\s+\|)|(\| Level Earth        Wind         Fire         Water        Astral\s+\|\s+\|\s+1\s+(?P<black1>[A-Za-z]+?)\|\s+\|\s+2\s+(?P<black2>.+?)\|\s+\|\s+3\s+(?P<black3>.+?)\|\s+\|\s+4\s+(?P<black4>.+?)\|\s+\|\s+5\s+(?P<black5>.+?)\|)"
#     r"\s+/================== Healing and Protection ==============================\\\s+"
#     r"\|(?P<white>.+?)\|\s+"
#     r"(?:\|(?P<white2>.+?)\|\s+)?"
#     r"(?:\|(?P<white3>.+?)\|\s+)?"
#     r"/======================================= Miscellaneous ==================\\\s+"
#     r"\|(?P<misc>.+?)\|\s+"
#     r"(?:\|(?P<misc2>.+?)\|\s+)?"
#     r"(?:\|(?P<misc3>.+?)\|\s+)?"
#     r"/===================================================== Running Spells ===\\\s+"
#     r"\|(?P<buffs>.+?)\|\s+"
#     r"(?:\|(?P<buffs2>.+?)\|\s+)?"
#     r"(?:\|(?P<buffs3>.+?)\|\s+)?"
#     r"\\========================================================================/"
# )]
# r"(?P<black1>.+?)\|\s+\|\s+\|   2(?P<black2>.+?)\|\s+\|   3(?P<black3>.+?)\|\s+\|   4(?P<black4>.+?)\|\s+\|   5(?P<black5>.+?)\|)\s+"

# Level Earth        Wind         Fire         Water        Astral       










# spells_before=[(
#     r"\|\s+none\s+\|"
#     # r".+"
# #|(?:Level Earth        Wind         Fire         Water        Astral       \|\s+\|   1(?P<black1>.+?)\|\s+\|   2(?P<black2>.+?)\|\s+\|   3(?P<black3>.+?)\|\s+\|   4(?P<black4>.+?)\|\s+\|   5(?P<black5>.+?)\|)\s+"
#     # r"|(?:\s+none\s+|)|"

#     # r"(?P<black>(?:\|\s+.+?\s+\|\s*?\n\r)+)"
#     # r"\|(?P<none>\s+none\s+\|)\s*?\n\r"
#     # r"\|\s(?:\s+none\s+\|)|(?:Level Earth        Wind         Fire         Water        Astral       \|\s+\|   1(?P<black1>.+?)\|\s+\|   2(?P<black2>.+?)\|\s+\|   3(?P<black3>.+?)\|\s+\|   4(?P<black4>.+?)\|\s+\|   5(?P<black5>.+?)\|)\s+"
#     # r"\|\s(Level Earth        Wind         Fire         Water        Astral       \|\s+\|   1(?P<black1>.+?)\|\s+\s+\|\s+\|   2(?P<black2>.+?)\|\s+\|   3(?P<black3>.+?)\|\s+\|   4(?P<black4>.+?)\|\s+\|   5(?P<black5>.+?)\|)\s+"
#     # r"\|\s(  1(?P<black1>.+?)\|\s+\|\s+\|   2(?P<black2>.+?)\|\s+\|   3(?P<black3>.+?)\|\s+\|   4(?P<black4>.+?)\|\s+\|   5(?P<black5>.+?)\|)\s+"
#     r"/================== Healing and Protection ==============================\\\s+"
#     # r"\|   1(?P<black1>.+?)\|\s+"  # . can match spaces, and \s can match newlines
#     # r"\|   2(?P<black2>.+?)\|\s+"
#     # r"\|   3(?P<black3>.+?)\|\s+"
#     # r"\|   4(?P<black4>.+?)\|\s+"
#     # r"\|   5(?P<black5>.+?)\|\s+"
#     # A regex without 1-5 specified and done with a quantifier could work if we don't put 
#     # .+ and \s+ next to eachother, like this (maybe) (same with \s and \n/\r):
#     # r"(?P<black>(?:\|.+?\|\s*?)+)"  erhm except I think, we can't use | as the anchor now, 
#     # and same with newline, we'd have to use the Astral    | and the /===== as the anchors 
#     # and match everything in between.  Spells.py would need to deal with the grouped '|'s.
#     # r"(?P<white>(?:\|\s+.+?\s+\|\s*?\n\r)+)"
#     r"\|(?P<white>.+?)\|\s+"
#     r"(?:\|(?P<white2>.+?)\|\s+)?"
#     r"(?:\|(?P<white3>.+?)\|\s+)?"
#     r"/======================================= Miscellaneous ==================\\\s+"
#     # r"(?P<misc>(?:\|\s+.+?\s+\|\s*?\n\r)+)"
#     r"\|(?P<misc>.+?)\|\s+"
#     r"(?:\|(?P<misc2>.+?)\|\s+)?"
#     r"(?:\|(?P<misc3>.+?)\|\s+)?"
#     r"/===================================================== Running Spells ===\\\s+"
#     # r"(?P<buffs>(?:\|\s+.+?\s+\|\s*?\n\r)+)"
#     r"\|(?P<buffs>.+?)\|\s+"
#     r"(?:\|(?P<buffs2>.+?)\|\s+)?"
#     r"(?:\|(?P<buffs3>.+?)\|\s+)?"
#     # r"\\========================================================================/\s*\n\r"
#     r"\\="
# )]


# spells = [(
#     r"\n\r"
#     r"/=== Combat Spells ======================================================\\\s+"

#     # r"(?P<black>(?:\|\s+.+?\s+\|\s*?\n\r)+)"
#     # r"\|(?P<none>\s+none\s+\|)\s*?\n\r"
#     r"\|\s(?:\s+none\s+\|)|(?:Level Earth        Wind         Fire         Water        Astral       \|\s+\|   1(?P<black1>.+?)\|\s+\|   2(?P<black2>.+?)\|\s+\|   3(?P<black3>.+?)\|\s+\|   4(?P<black4>.+?)\|\s+\|   5(?P<black5>.+?)\|)\s+"
#     # r"\|\s(Level Earth        Wind         Fire         Water        Astral       \|\s+\|   1(?P<black1>.+?)\|\s+\s+\|\s+\|   2(?P<black2>.+?)\|\s+\|   3(?P<black3>.+?)\|\s+\|   4(?P<black4>.+?)\|\s+\|   5(?P<black5>.+?)\|)\s+"
#     # r"\|\s(  1(?P<black1>.+?)\|\s+\|\s+\|   2(?P<black2>.+?)\|\s+\|   3(?P<black3>.+?)\|\s+\|   4(?P<black4>.+?)\|\s+\|   5(?P<black5>.+?)\|)\s+"
#     r"/================== Healing and Protection ==============================\\\s+"
#     # r"\|   1(?P<black1>.+?)\|\s+"  # . can match spaces, and \s can match newlines
#     # r"\|   2(?P<black2>.+?)\|\s+"
#     # r"\|   3(?P<black3>.+?)\|\s+"
#     # r"\|   4(?P<black4>.+?)\|\s+"
#     # r"\|   5(?P<black5>.+?)\|\s+"
#     # A regex without 1-5 specified and done with a quantifier could work if we don't put 
#     # .+ and \s+ next to eachother, like this (maybe) (same with \s and \n/\r):
#     # r"(?P<black>(?:\|.+?\|\s*?)+)"  erhm except I think, we can't use | as the anchor now, 
#     # and same with newline, we'd have to use the Astral    | and the /===== as the anchors 
#     # and match everything in between.  Spells.py would need to deal with the grouped '|'s.
#     # r"(?P<white>(?:\|\s+.+?\s+\|\s*?\n\r)+)"
#     r"\|(?P<white>.+?)\|\s+"
#     r"(?:\|(?P<white2>.+?)\|\s+)?"
#     r"(?:\|(?P<white3>.+?)\|\s+)?"
#     r"/======================================= Miscellaneous ==================\\\s+"
#     # r"(?P<misc>(?:\|\s+.+?\s+\|\s*?\n\r)+)"
#     r"\|(?P<misc>.+?)\|\s+"
#     r"(?:\|(?P<misc2>.+?)\|\s+)?"
#     r"(?:\|(?P<misc3>.+?)\|\s+)?"
#     r"/===================================================== Running Spells ===\\\s+"
#     # r"(?P<buffs>(?:\|\s+.+?\s+\|\s*?\n\r)+)"
#     r"\|(?P<buffs>.+?)\|\s+"
#     r"(?:\|(?P<buffs2>.+?)\|\s+)?"
#     r"(?:\|(?P<buffs3>.+?)\|\s+)?"
#     # r"\\========================================================================/\s*\n\r"
#     r"\\="
# )]
# spells = [(
#     r"\n\r"
#     r"/=== Combat Spells ======================================================\\\s*\n\r"
#     r"(?P<black>(?:\|\s+.+?\s+\|\s*?\n\r)+)"
#     r"/================== Healing and Protection ==============================\\\s*\n\r"
#     r"(?P<white>(?:\|\s+.+?\s+\|\s*?\n\r)+)"
#     r"/======================================= Miscellaneous ==================\\\s*\n\r"
#     r"(?P<misc>(?:\|\s+.+?\s+\|\s*?\n\r)+)"
#     r"/===================================================== Running Spells ===\\\s*\n\r"
#     r"(?P<buffs>(?:\|\s+.+?\s+\|\s*?\n\r)+)"
#     r"\\========================================================================/\s*\n\r"
# )]
# spells = [(
#     r"\n\r"
#     r"/=== Combat Spells ======================================================\\\s+"
#     # r"(?P<black>(?:\|\s+.+?\s+\|\s*?\n\r)+)"
#     # r"\|(?P<none>\s+none\s+\|)\s*?\n\r"
#     r"\|\s+none\s+\|\s+"
#     r"/================== Healing"
# ),(
#     r"\n\r"
#     r"/=== Combat Spells ======================================================\\\s+"
#     r"\| Level Earth        Wind         Fire         Water        Astral       \|\s+"
#     # r"(?P<black>(?:\|\s+.+?\s+\|\s*?\n\r)+)"
#     r"\|   1(?P<black1>.+?)\|\s+"  # . can match spaces, and \s can match newlines
#     r"\|   2(?P<black2>.+?)\|\s+"
#     r"\|   3(?P<black3>.+?)\|\s+"
#     r"\|   4(?P<black4>.+?)\|\s+"
#     r"\|   5(?P<black5>.+?)\|\s+"
#     r"/================== Healing"
#     # A regex without 1-5 specified and done with a quantifier could work if we don't put 
#     # .+ and \s+ next to eachother, like this (maybe) (same with \s and \n/\r):
#     # r"(?P<black>(?:\|.+?\|\s*?)+)"  erhm except I think, we can't use | as the anchor now, 
#     # and same with newline, we'd have to use the Astral    | and the /===== as the anchors 
#     # and match everything in between.  Spells.py would need to deal with the grouped '|'s.
# ),(
#     # r"/================== Healing and Protection ==============================\\\s*\n\r"
#     r"/================== Healing and Protection ==============================\\\s+"
#     r"(?P<white>(?:\|\s+.+?\s+\|\s*?\n\r)+)"
#     # r"\|(?P<white>.+?)\|\s+"
#     # r"(\|(?P<white2>.+?)\|\s+)?"
#     # r"(\|(?P<white3>.+?)\|\s+)?"
#     r"/======================================= Misc"
# ),(
#     r"/======================================= Miscellaneous ==================\\\s*\n\r"
#     r"(?P<misc>(?:\|\s+.+?\s+\|\s*?\n\r)+)"
#     # r"\|(?P<misc>.+?)\|\s+"
#     # r"(\|(?P<misc2>.+?)\|\s+)?"
#     # r"(\|(?P<misc3>.+?)\|\s+)?"
#     r"/===================================================== Running"
# ),(
#     r"= Running Spells ===\\\s*\n\r"
#     r"(?P<buffs>(?:\|\s+.+?\s+\|\s*?\n\r)+)"
#     # r"\|(?P<buffs>.+?)\|\s+"
#     # r"(\|(?P<buffs2>.+?)\|\s+)?"
#     # r"(\|(?P<buffs3>.+?)\|\s+)?"
#     r"\\========================================================================/\s*\n\r"
# )]
# spells = [(
#     r"\n\r"
#     r"/=== Combat Spells ======================================================\\\s*\n\r"
#     r"(?P<black>(?:\|\s+.+?\s+\|\s*?\n\r)+)"
#     r"/================== Healing and Protection ==============================\\\s*\n\r"
# )]
# spells2 = [(
#     r"/================== Healing and Protection ==============================\\\s*\n\r"
#     r"(?P<white>(?:\|\s+.+?\s+\|\s*?\n\r)+)"
#     r"/======================================= Miscellaneous ==================\\\s*\n\r"
# )]
# spells3 = [(
#     r"/======================================= Miscellaneous ==================\\\s*\n\r"
#     r"(?P<misc>(?:\|\s+.+?\s+\|\s*?\n\r)+)"
#     r"/===================================================== Running Spells ===\\\s*\n\r"
# )]
# spells4 = [(
#     r"/===================================================== Running Spells ===\\\s*\n\r"
#     r"(?P<buffs>(?:\|\s+.+?\s+\|\s*?\n\r)+)"
#     r"\\========================================================================/\s*\n\r"
# )]
    # r"\|\s+(?P<black>.+?)+\s+\|\s*?\n\r"
    # r"\|\s+(?P<white>.+?)+\s+\|\s*?\n\r"
    # r"\|\s+(?P<misc>.+?)+\s+\|\s*?\n\r"
    # r"\|\s+(?P<buffs>.+?)+\s+\|\s*?\n\r"
    # r"/=== Combat Spells ======================================================\\\s*\n\r"
    # r"\|\s+(?P<black>.+?)\s+\|\s*?\n\r"
    # r"/================== Healing and Protection ==============================\\\s*\n\r"
    # r"\|\s+(?P<white>.+?)\s+\|\s*?\n\r"
    # r"/======================================= Miscellaneous ==================\\\s*\n\r"
    # r"\|\s+(?P<misc>.+?)\s+\|\s*?\n\r"
    # r"/===================================================== Running Spells ===\\\s*\n\r"
    # r"\|\s+(?P<buffs>.+?)\s+\|\s*?\n\r"
    # r"\\========================================================================/\s*\n\r"
