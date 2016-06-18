# -*- coding: utf-8 -*-
#
# This comment will populate certain fixed Icelandic tables with data
#
from django.core.management.base import BaseCommand
from django.db.utils import IntegrityError

from core.models import LocationCode


# Gögn frá: https://is.wikipedia.org/wiki/%C3%8Dslensk_sveitarf%C3%A9l%C3%B6g_eftir_sveitarf%C3%A9lagsn%C3%BAmerum
SVEITARFELOG = (
    ('0000', 'Reykjavíkurborg', (101,102,103,104,105,107,108,109,110,111,112,113,116,121,123,124,125,127,128,129,130,132,150,155)),
    ('1000', 'Kópavogsbær', (200, 201, 202, 203)),
    ('1100', 'Seltjarnarnesbær', (170,)),
    ('1300', 'Garðabær', (210,)),
    ('1400', 'Hafnarfjarðarkaupstaður', (220,221,222)),
    ('1603', 'Sveitarfélagið Álftanes', (225,)),
    ('1604', 'Mosfellsbær', (270,)),
    ('1606', 'Kjósarhreppur', (270,)),
    ('2000', 'Reykjanesbær', (230,232,233,235,260,)),
    ('2300', 'Grindavíkurbær', (240,)),
    ('2503', 'Sandgerðisbær', (245,)),
    ('2504', 'Sveitarfélagið Garður', (250,)),
    ('2506', 'Sveitarfélagið Vogar', (190,)),
    ('3000', 'Akraneskaupstaður', (300,)),
    ('3506', 'Skorradalshreppur', (311,)),
    ('3511', 'Hvalfjarðarsveit', (301,)),
    ('3609', 'Borgarbyggð', (310,311,320,)),
    ('3709', 'Grundarfjarðarbær', (350,)),
    ('3710', 'Helgafellssveit', (340,)),
    ('3711', 'Stykkishólmsbær', (340,)),
    ('3713', 'Eyja- og Miklaholtshreppur', (311,)),
    ('3714', 'Snæfellsbær', (360,)),
    ('3811', 'Dalabyggð', (370,371,)),
    ('4100', 'Bolungarvíkurkaupstaður', (415,)),
    ('4200', 'Ísafjarðarbær', (400,401,410,425,430,470,471,)),
    ('4502', 'Reykhólahreppur', (380,)),
    ('4604', 'Tálknafjarðarhreppur', (460,)),
    ('4607', 'Vesturbyggð', (450,451,465,)),
    ('4803', 'Súðavíkurhreppur', (420,)),
    ('4901', 'Árneshreppur', (524,)),
    ('4902', 'Kaldrananeshreppur', (510,520,)),
    ('4908', 'Bæjarhreppur', (500,)),
    ('4911', 'Strandabyggð', (510,)),
    ('5200', 'Sveitarfélagið Skagafjörður', (550,551,560,565,566,570,)),
    ('5508', 'Húnaþing vestra', (500,530,531,)),
    ('5604', 'Blönduósbær', (540,)),
    ('5609', 'Sveitarfélagið Skagaströnd', (545,)),
    ('5611', 'Skagabyggð', (545,)),
    ('5612', 'Húnavatnshreppur', (541,)),
    ('5706', 'Akrahreppur', (560,)),
    ('6000', 'Akureyrarkaupstaður', (600,603,611,630,)),
    ('6100', 'Norðurþing', (640,670,671,675,)),
    ('6250', 'Fjallabyggð', (580,625,)),
    ('6400', 'Dalvíkurbyggð', (620,621,)),
    ('6513', 'Eyjafjarðarsveit', (601,)),
    ('6515', 'Hörgársveit', (601,)),
    ('6601', 'Svalbarðsstrandarhreppur', (601,)),
    ('6602', 'Grýtubakkahreppur', (601,610,)),
    ('6607', 'Skútustaðahreppur', (660,)),
    ('6611', 'Tjörneshreppur', (641,)),
    ('6612', 'Þingeyjarsveit', (601,641,645,650,)),
    ('6706', 'Svalbarðshreppur', (681,)),
    ('6709', 'Langanesbyggð', (680,681,685,)),
    ('7000', 'Seyðisfjarðarkaupstaður', (710,)),
    ('7300', 'Fjarðabyggð', (715,730,735,740,750,755,)),
    ('7502', 'Vopnafjarðarhreppur', (690,)),
    ('7505', 'Fljótsdalshreppur', (701,)),
    ('7509', 'Borgarfjarðarhreppur', (701,)),
    ('7613', 'Breiðdalshreppur', (760,)),
    ('7617', 'Djúpavogshreppur', (765,)),
    ('7620', 'Fljótsdalshérað', (700,701,)),
    ('7708', 'Sveitarfélagið Hornafjörður', (780,781,785,)),
    ('8000', 'Vestmannaeyjabær', (900,902,)),
    ('8200', 'Sveitarfélagið Árborg', (800,801,802,820,825,)),
    ('8508', 'Mýrdalshreppur', (870,871,)),
    ('8509', 'Skaftárhreppur', (880,)),
    ('8610', 'Ásahreppur', (851,)),
    ('8613', 'Rangárþing eystra', (860,861,)),
    ('8614', 'Rangárþing ytra', (850,851,)),
    ('8710', 'Hrunamannahreppur', (845,)),
    ('8716', 'Hveragerðisbær', (810,)),
    ('8717', 'Sveitarfélagið Ölfus', (815,)),
    ('8719', 'Grímsnes- og Grafningshreppur', (801,)),
    ('8720', 'Skeiða- og Gnúpverjahreppur', (801,)),
    ('8721', 'Bláskógabyggð', (801,)),
    ('8722', 'Flóahreppur', (801,)))


class Command(BaseCommand):

    def _add_or_update_code(self, code, name):
        try:
            LocationCode(
                location_name=name,
                location_code=code
                ).save()
        except IntegrityError:
            lc = LocationCode.objects.get(location_code=code)
            if lc.location_name and lc.location_name != name:
                lc.location_name = name
                lc.save()

    def handle(self, *args, **options):
        postnumerin = {}
        for svfnr, nafn, postnumer in SVEITARFELOG:
            for pnr in postnumer:
                pnr = '%3.3d' % pnr
                if pnr in postnumerin:
                    postnumerin[pnr] = '%s, %s' % (postnumerin[pnr], nafn)
                else:
                    postnumerin[pnr] = nafn

        for svfnr, nafn, postnumer in SVEITARFELOG:
            self._add_or_update_code('svfnr:' + svfnr, nafn)

        for pnr in sorted(postnumerin.keys()):
            self._add_or_update_code('pnr:' + pnr, postnumerin[pnr])
