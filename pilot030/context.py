"""Small source-language paraphrases to disambiguate football terms.
Only an explicitly selected football context enables these general phrase rules.
"""
import re
def normalize(text,domain):
    if domain!="football":return text
    text=re.sub(r"\bvisiting team\b","away team",text,flags=re.I)
    text=re.sub(r"\bjust before (?:half[ -]?time)\b","just before the first half ended",text,flags=re.I)
    return text
if __name__=="__main__":
    assert normalize("The visiting team scored.","football")=="The away team scored."
    assert normalize("The visiting team scored.","general")=="The visiting team scored."
    assert normalize("They scored just before half-time.","football")=="They scored just before the first half ended."
    assert normalize("There is a penalty for late payment.","general")=="There is a penalty for late payment."
    print("PASS context isolation and football paraphrases")
