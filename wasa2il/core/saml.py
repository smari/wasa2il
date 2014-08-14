
import os
import binascii

from lxml import etree
from StringIO import StringIO
from suds.client import Client

from django.conf import settings
from django.contrib.auth import login
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect


class SamlException(Exception):
    pass


def get_saml(request, token):
    # Fetch SAML info
    AI = settings.SAML_1['AUTH']
    client = Client(AI['wsdl'], username=AI['login'], password=AI['password'])
    ipaddr = request.META.get('REMOTE_ADDR')
    result = client.service.generateSAMLFromToken(token, ipaddr)

    if result['status']['message'] != 'Success':
        raise SamlException('%s' % result['status']['message'])

    return result


def parse_saml(saml):
    # Parse the SAML and retrieve user info
    tree = etree.parse(StringIO(saml))
    namespaces = {'saml': 'urn:oasis:names:tc:SAML:1.0:assertion'}
    name = tree.xpath('/saml:Assertion/saml:AttributeStatement/saml:Subject/saml:NameIdentifier[@NameQualifier="Full Name"]/text()', namespaces=namespaces)[0]
    ssn = tree.xpath('/saml:Assertion/saml:AttributeStatement/saml:Attribute[@AttributeName="SSN"]/saml:AttributeValue/text()', namespaces=namespaces)[0]
    return name, ssn


def authenticate(request, redirect_url):
    user = request.user
    token = request.GET.get('token')

    if not token:
        return HttpResponseRedirect(redirect_url)

    result = get_saml(request, token)
    name, ssn = parse_saml(result['saml'])

    return { 'ssn': ssn, 'name': name }

