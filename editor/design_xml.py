"""Versioned design-only XML interchange; JSON remains the active source."""
import html
import re
import xml.etree.ElementTree as ET
from .design import GROUPS, validate_design

MAX_XML_BYTES = 65536


def to_xml(design):
    errors = validate_design(design)
    if errors:
        raise ValueError('\n'.join(errors))
    lines = ['<?xml version="1.0" encoding="UTF-8"?>', '<website-design version="1">']
    for group in GROUPS:
        lines.append(f'  <{group["key"]}')
        for field in group['fields']:
            value = design[group['key']][field['key']]
            value = f'{value:g}' if field['type'] == 'range' else str(value)
            name = field['key'].replace('_', '-')
            lines.append(f'    {name}="{html.escape(value, quote=True)}"')
        lines.append('  />')
    return '\n'.join(lines + ['</website-design>', ''])


def from_xml(source):
    if not isinstance(source, str) or len(source.encode('utf-8')) > MAX_XML_BYTES:
        raise ValueError('Choose a design XML file smaller than 64 KiB.')
    if re.search(r'<!\s*(?:DOCTYPE|ENTITY)', source, re.I):
        raise ValueError('Document types and entity declarations are not supported.')
    try:
        root = ET.fromstring(source)
    except ET.ParseError as error:
        raise ValueError('The design XML is malformed.') from error
    if root.tag != 'website-design' or root.attrib != {'version': '1'}:
        raise ValueError('Use <website-design version="1"> as the root.')
    if (root.text or '').strip():
        raise ValueError('Design groups must use attributes, without text content.')
    known = {group['key']: group for group in GROUPS}
    design = {}
    for node in root:
        if node.tag not in known or node.tag in design:
            raise ValueError('Each known design group must appear exactly once.')
        if len(node) or (node.text or '').strip() or (node.tail or '').strip():
            raise ValueError('Design groups must be empty elements with attributes.')
        fields = known[node.tag]['fields']
        expected = {field['key'].replace('_', '-') for field in fields}
        if set(node.attrib) != expected:
            raise ValueError(f'{node.tag}: include every documented attribute, with no extras.')
        values = {}
        for field in fields:
            value = node.attrib[field['key'].replace('_', '-')]
            if field['type'] == 'range':
                if not re.fullmatch(r'-?(?:\d+(?:\.\d+)?|\.\d+)', value):
                    raise ValueError(f'{node.tag}: {field["key"]} must be a number without units.')
                value = float(value) if '.' in value else int(value)
            values[field['key']] = value
        design[node.tag] = values
    errors = validate_design(design)
    if errors:
        raise ValueError('\n'.join(errors))
    return design
