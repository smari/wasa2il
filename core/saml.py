
import os
import binascii

from lxml import etree
from StringIO import StringIO
from suds.client import Client

import xml.etree.ElementTree as ET
from base64 import b64decode
from signxml import xmldsig

from django.conf import settings
from django.contrib.auth import login
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect


class SamlException(Exception):
    pass


def get_saml(request, token):
    try:
        # Fetch SAML 1.2 info
        AI = settings.SAML_1['AUTH']
        client = Client(AI['wsdl'], username=AI['login'], password=AI['password'])
        ipaddr = request.META.get('REMOTE_ADDR')
        result = client.service.generateSAMLFromToken(token, ipaddr)

        if result['status']['message'] != 'Success':
            raise SamlException('%s' % result['status']['message'])

        return result
    except: #saml 2
        data = b64decode(token)
        root = ET.fromstring(data)
        cert = root.find('.//{http://www.w3.org/2000/09/xmldsig#}X509Certificate').text
        try:
            assertion_data = xmldsig(data).verify(x509_cert=cert)
        except:
            raise SamlException('x509 certificate exception')
        return {'saml': data}


def parse_saml(saml):
    try:
        # Parse the SAML 1.2 and retrieve user info
        tree = etree.parse(StringIO(saml))
        namespaces = {'saml': 'urn:oasis:names:tc:SAML:1.0:assertion'}
        name = tree.xpath('/saml:Assertion/saml:AttributeStatement/saml:Subject/saml:NameIdentifier[@NameQualifier="Full Name"]/text()', namespaces=namespaces)[0]
        ssn = tree.xpath('/saml:Assertion/saml:AttributeStatement/saml:Attribute[@AttributeName="SSN"]/saml:AttributeValue/text()', namespaces=namespaces)[0]
        return name, ssn
    except:
        # Parse saml 2 and retrieve user info
        root = ET.fromstring(saml)
        attributes = {}
            for attribute in root.findall('.//{urn:oasis:names:tc:SAML:2.0:assertion}Attribute'):
                attributes[attribute.attrib['Name']] = attribute.find('.//{urn:oasis:names:tc:SAML:2.0:assertion}AttributeValue').text
        return {'name': attributes.get('Name'), 'ssn': attributes.get('UserSSN') }


def authenticate(request, redirect_url):
    user = request.user
    token = request.GET.get('token')

    if not token:
        return HttpResponseRedirect(redirect_url)

    result = get_saml(request, token)
    name, ssn = parse_saml(result['saml'])

    return { 'ssn': ssn, 'name': name }

