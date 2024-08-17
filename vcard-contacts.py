"""
title: VCard Contacts
author: ex0dus
author_url: https://github.com/roryeckel
# funding_url: https://github.com/open-webui
version: 0.0.1
requirements: vobject
"""

import vobject
from typing import Optional, Callable, Awaitable


class Tools:
    def __init__(self):
        pass

    async def create_vcard(
        self,
        __event_emitter__: Callable[[dict], Awaitable[None]],
        first_name: str,
        last_name: Optional[str] = None,
        organization: Optional[str] = None,
        email: Optional[str] = None,
        phone: Optional[str] = None,
        address: Optional[str] = None,
    ) -> str:
        """
        Create a contact VCard based on the input parameters.
        :param first_name: The first name of the contact.
        :param last_name: The last name of the contact.
        :param organization: The organization of the contact.
        :param email: The organization of the contact.
        :param phone: The phone of the contact.
        :param address: The phone of the contact.
        :return: The VCF formatted VCard contact file contents
        """
        vcard = vobject.vCard()
        vcard.add("n")
        vcard.n.value = vobject.vcard.Name(family=last_name, given=first_name)
        vcard.add("fn")
        vcard.fn.value = f"{first_name} {last_name}"

        if organization:
            vcard.add("org")
            vcard.org.value = [organization]

        if email:
            vcard.add("email")
            vcard.email.value = email
            vcard.email.type_param = "INTERNET"

        if phone:
            vcard.add("tel")
            vcard.tel.value = phone
            vcard.tel.type_param = "HOME"

        if address:
            vcard.add("adr")
            vcard.adr.value = vobject.vcard.Address(street=address)

        result = vcard.serialize()

        await __event_emitter__(
            {
                "type": "message",
                "data": {"content": f"```VCARD\n{result}\n```\n"},
            }
        )
