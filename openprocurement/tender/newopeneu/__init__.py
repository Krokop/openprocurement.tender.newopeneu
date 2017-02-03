from logging import getLogger
from pkg_resources import get_distribution

PKG = get_distribution(__package__)
LOGGER = getLogger(PKG.project_name)


def includeme(config):
    """
    Entry point to module
    :param config: Pyramid server configuration
    :return:
    """
    from openprocurement.tender.newopeneu.models import (Tender)
    LOGGER.info('init newopeneu plugin')
    config.add_tender_procurementMethodType(Tender)
    config.scan("openprocurement.tender.newopeneu.views")
