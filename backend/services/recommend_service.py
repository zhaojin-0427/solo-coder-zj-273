from itertools import product
from backend.models import Accessory
from backend.utils.constants import COLOR_COMBINATIONS, STYLE_MATCH
from backend.utils.helpers import get_color_score, get_style_score, get_occasion_score


def generate_reason(necklace, earring, bracelet, main_color, style, occasion):
    reasons = []
    pieces = [('项链', necklace), ('耳环', earring), ('手链', bracelet)]
    pieces = [(n, p) for n, p in pieces if p]

    color_match_count = sum(1 for _, p in pieces if p.color_family in COLOR_COMBINATIONS.get(main_color, []) or p.color_family == main_color)
    if color_match_count == len(pieces):
        reasons.append(f"所有饰品的色系都与主色调{main_color}完美协调")
    elif color_match_count > 0:
        reasons.append(f"部分饰品与主色调{main_color}形成和谐搭配")

    style_match_count = sum(1 for _, p in pieces if p.style == style or p.style in STYLE_MATCH.get(style, []))
    if style_match_count == len(pieces):
        reasons.append(f"整体风格统一为{style}风")
    elif style_match_count > 0:
        reasons.append(f"主要单品契合{style}风格定位")

    if occasion:
        occ_match = [n for n, p in pieces if occasion in (p.occasions.split(',') if p.occasions else [])]
        if occ_match:
            reasons.append(f"{'、'.join(occ_match)}适合{occasion}场合佩戴")

    materials = list(set(p.material for _, p in pieces))
    if len(materials) == 1:
        reasons.append(f"材质统一为{materials[0]}，整体质感一致")
    elif len(materials) == 2:
        reasons.append(f"{materials[0]}与{materials[1]}材质碰撞，产生层次感")

    if not reasons:
        reasons.append("整体搭配简洁大方，适合日常佩戴")

    return '；'.join(reasons) + '。'


def get_recommendations(main_color, style, occasion):
    all_acc = Accessory.query.all()
    available = [a for a in all_acc if a.get_status() == 'in_stock']
    necklaces = [a for a in available if a.category == '项链']
    earrings = [a for a in available if a.category == '耳环']
    bracelets = [a for a in available if a.category == '手链']

    def score_item(acc):
        if not acc:
            return 0
        s = 0
        if main_color:
            s += get_color_score(acc.color_family, main_color) * 2
        if style:
            s += get_style_score(acc.style, style) * 1.5
        if occasion:
            s += get_occasion_score(acc, occasion)
        s += min(acc.wear_count, 5) * 0.2
        return s

    def pick_best(items, top_n=3):
        scored = [(score_item(it), it) for it in items]
        scored.sort(key=lambda x: -x[0])
        return [it for _, it in scored[:top_n]]

    top_necklaces = pick_best(necklaces)
    top_earrings = pick_best(earrings)
    top_bracelets = pick_best(bracelets)

    combos = list(product(top_necklaces or [None], top_earrings or [None], top_bracelets or [None]))
    combos = [c for c in combos if any(c)]

    def combo_score(combo):
        n, e, b = combo
        s = 0
        for p in [n, e, b]:
            s += score_item(p)
        colors = set(p.color_family for p in [n, e, b] if p)
        if len(colors) <= 2:
            s += 5
        materials = set(p.material for p in [n, e, b] if p)
        if len(materials) == 1:
            s += 3
        return s

    max_per_item = 0
    if main_color:
        max_per_item += 10 * 2
    if style:
        max_per_item += 10 * 1.5
    if occasion:
        max_per_item += 10
    max_per_item += 1
    piece_count = 3 if (necklaces and earrings and bracelets) else (
        2 if ((necklaces and earrings) or (necklaces and bracelets) or (earrings and bracelets)) else 1
    )
    max_combo_score = max_per_item * piece_count + 8
    if max_combo_score == 0:
        max_combo_score = 1

    combos.sort(key=combo_score, reverse=True)
    top_combos = combos[:5]

    results = []
    for idx, combo in enumerate(top_combos):
        n, e, b = combo
        raw_score = combo_score(combo)
        results.append({
            'id': idx + 1,
            'score': round(raw_score, 1),
            'score_percent': min(100, round(raw_score / max_combo_score * 100)),
            'necklace': n.to_dict() if n else None,
            'earring': e.to_dict() if e else None,
            'bracelet': b.to_dict() if b else None,
            'reason': generate_reason(n, e, b, main_color, style, occasion)
        })

    return results
