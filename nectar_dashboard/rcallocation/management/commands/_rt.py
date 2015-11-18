from __future__ import absolute_import
from ConfigParser import SafeConfigParser
import os
import re

import requests
import rt


config = SafeConfigParser()
config.read(os.path.expanduser('~/.rt.ini'))

username = config.get('DEFAULT', 'username')
password = config.get('DEFAULT', 'password')
ticket_owner = config.get('DEFAULT', 'aaf_email')
rt_url = config.get('DEFAULT', 'url')


def get_allocation_requests(client):
    tickets = find_tickets(client)
    for ticket in tickets:
        ticket_id = ticket['id'].rsplit('/', 1)[1]
        allocation_id = get_allocation_id(client, ticket_id)
        if allocation_id:
            yield (allocation_id, ticket_id)


def resolve_allocation_ticket(client, allocation_id, message):
    allocations = dict(list(get_allocation_requests(client)))
    ticket_id = allocations[str(allocation_id)]
    take_and_resolve_ticket(client, ticket_id, message)


def take_and_resolve_ticket(client, ticket_id, message=None):
    take_ticket(client, ticket_id)
    if message is not None:
        reply_ticket(client, ticket_id, message)
    resolve_ticket(client, ticket_id)


def get_rt_client():
    client = rt.Rt('%s/REST/1.0/' % rt_url, basic_auth=(username, password))
    return client


def find_tickets(client):
    return client.search(Queue='accounts', Status='new', Owner='Nobody')


def get_allocation_id(client, ticket_id):
    attachments = client.get_attachments(ticket_id)
    attachment = client.get_attachment(ticket_id, attachments[0][0])
    content = attachment['Content']
    match = re.search('/project/requests/view/(?P<allocation_id>\d+)/',
                      content)
    if match and 'has been approved' in content:
        return match.group(1)


def take_ticket(client, ticket_id):
    client.edit_ticket(ticket_id, Owner=ticket_owner)


def reply_ticket(client, ticket_id, message):
    client.reply(ticket_id, text=message)


def comment_ticket(client, ticket_id, message):
    client.comment(ticket_id, text=message)


def open_ticket(client, ticket_id):
    client.edit_ticket(ticket_id, Status='open')


def resolve_ticket(client, ticket_id):
    client.edit_ticket(ticket_id, Status='resolved')
