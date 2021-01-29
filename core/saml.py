from datetime import datetime
from signxml import XMLVerifier
from xml.etree import ElementTree

from django.conf import settings
from django.contrib.auth import login
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect


class SamlException(Exception):
    pass


def authenticate(input_xml, ca_pem_file):

    # @test: Check signature and retrieve the XML that's guaranteed to be signed.
    signed_xml = XMLVerifier().verify(input_xml, require_x509=True, ca_pem_file=ca_pem_file).signed_xml

    # @test: Verify they're not sending us multiple root level assertions.
    if len(signed_xml.findall('./{urn:oasis:names:tc:SAML:2.0:assertion}Assertion')) > 1:
        raise SamlException('Too many assertion matched')

    # @process: Obtain the assertion.
    assertion = signed_xml.find('./{urn:oasis:names:tc:SAML:2.0:assertion}Assertion')
    if not assertion:
        raise SamlException('Could not find valid assertion')

    # @process: Obtain the conditions.
    conds_xml = assertion.find('./{urn:oasis:names:tc:SAML:2.0:assertion}Conditions')
    if not conds_xml:
        raise SamlException('Could not find valid conditions statement. This is required.')

    # @test: Verify audience.
    audience = conds_xml.find("{urn:oasis:names:tc:SAML:2.0:assertion}AudienceRestriction/{urn:oasis:names:tc:SAML:2.0:assertion}Audience").text
    if audience not in settings.ALLOWED_HOSTS:
        raise SamlException('Incorrect audience specified')

    # @test: Verify date boundaries
    #   Apparently the datetimes have 7 digits of microseconds when normally
    #   they should be 6 when parsed. We'll leave them out by only using the
    #   first 19 characters.
    time_limit_lower = datetime.strptime(conds_xml.attrib['NotBefore'][:19],'%Y-%m-%dT%H:%M:%S')
    time_limit_upper = datetime.strptime(conds_xml.attrib['NotOnOrAfter'][:19],'%Y-%m-%dT%H:%M:%S')
    now = datetime.now()
    if time_limit_lower > now or time_limit_upper < now:
        raise SamlException('Remote authentication expired')

    # @process: obtain ID.
    #   Find the assertion ID for our records. This is not needed for
    #   functionality's sake and is only kept for the hypothetical scenario
    #   where a particular authentication needs to be matched with records on
    #   the identity provider's side.
    assertion_id = assertion.attrib['ID']

    # @process: Translate SAML attributes into a handy dictionary.
    attributes = {}
    for attribute in assertion.findall('.//{urn:oasis:names:tc:SAML:2.0:assertion}Attribute'):
        attributes[attribute.attrib['Name']] = attribute.find('.//{urn:oasis:names:tc:SAML:2.0:assertion}AttributeValue').text

    return assertion_id, attributes
