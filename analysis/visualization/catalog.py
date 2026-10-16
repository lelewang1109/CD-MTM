"""One method catalogue and explicit handling of unevaluable motion rates."""
from dataclasses import dataclass


@dataclass(frozen=True)
class Method:
    key: str
    label: str
    color: str


METHODS = (
    Method('TMTM', 'TMTM', '#777777'),
    Method('ST-MTM', 'ST-MTM', '#56b4e9'),
    Method('A', 'RG-MTM-P', '#0072b2'),
    Method('R 20%', 'RG-MTM-R', '#009e73'),
    Method('Hilbert', 'Hilbert', '#d55e00'),
    Method('Morton', 'Morton', '#cc79a7'),
)


def motion_row(record, method, k=2, eps=.02):
    """Return a saved observation; zero events remain undefined, never 0% error."""
    rows = [r for r in record['proxy']
            if r['method'] == method and r['k'] == k and r['eps'] == eps]
    if len(rows) > 1:
        raise ValueError(f'Duplicate motion setting: {method}, {k}, {eps}')
    return rows[0] if rows else {'clear': 0}


def motion_rate(record, method, k=2, eps=.02):
    row = motion_row(record, method, k, eps)
    return row['error'] if row.get('clear') else None


def evenly_spaced_frames(count):
    if count < 1:
        raise ValueError('A sequence must contain at least one frame')
    return tuple(dict.fromkeys((0, (count - 1) // 2, count - 1)))
