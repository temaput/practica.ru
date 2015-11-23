import logging
log = logging.getLogger(__name__)

from decimal import Decimal
D = lambda _float: Decimal(str(_float))


def estimateWeight(basket):
    log.debug("Estimating weight for basket %s...", basket)
    weight = D('0')
    for line in basket.lines.all():
        attr = line.product.attr
        if hasattr(attr, 'weight'):
            weight += D(line.quantity) * D(attr.weight)
        else:
            log.warning("Product %s has no weight", line.product)
    log.debug("... complete: weight=%s", weight)
    return weight
