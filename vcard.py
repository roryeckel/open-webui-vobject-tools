"""
title: VCard Generation Toolkit
author: ex0dus
author_url: https://github.com/roryeckel
version: 0.0.1
requirements: vobject
"""
import vobject
from datetime import datetime
from typing import Optional, Callable, Awaitable

class Tools:
    def __init__(self):
        pass

    def _validate_date(self, date_string: str, format: str = "%Y-%m-%dT%H:%M:%S%z") -> Optional[datetime]:
        """
        Validate and parse a date string in ISO 8601 format.
        :param date_string: The date string to validate.
        :param format: The expected format of the date string (default: ISO 8601).
        :return: Parsed datetime object if valid, None otherwise.
        """
        try:
            return datetime.strptime(date_string, format)
        except ValueError:
            return None

    async def create_contact_vcard(
        self,
        __event_emitter__: Callable[[dict], Awaitable[None]],
        first_name: str,
        last_name: Optional[str] = None,
        organization: Optional[str] = None,
        email: Optional[str] = None,
        phone: Optional[str] = None,
        address: Optional[str] = None,
        title: Optional[str] = None,
        website: Optional[str] = None,
        birthday: Optional[str] = None,
        note: Optional[str] = None,
        photo_url: Optional[str] = None,
        **kwargs
    ) -> str:
        """
        Create a contact VCard based on the input parameters.
        Note: strictly adhere to JSON syntax.
        :param first_name: The first name of the contact.
        :param last_name: The last name of the contact.
        :param organization: The organization of the contact.
        :param email: The email of the contact.
        :param phone: The phone number of the contact.
        :param address: The address of the contact.
        :param title: The job title of the contact.
        :param website: The website of the contact.
        :param birthday: The birthday of the contact (ISO 8601 format: YYYY-MM-DDTHH:MM:SS±HHMM).
        :param note: Additional notes about the contact.
        :param photo_url: URL of the contact's photo.
        :return: The VCF formatted VCard contact file contents.
        """
        vcard = vobject.vCard()
        vcard.add("n").value = vobject.vcard.Name(family=last_name, given=first_name)
        vcard.add("fn").value = f"{first_name} {last_name}"

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
            vcard.tel.type_param = "CELL"

        if address:
            vcard.add("adr")
            vcard.adr.value = vobject.vcard.Address(street=address)
            vcard.adr.type_param = "HOME"

        if title:
            vcard.add("title")
            vcard.title.value = title

        if website:
            vcard.add("url")
            vcard.url.value = website

        if birthday:
            parsed_date = self._validate_date(birthday)
            if parsed_date:
                vcard.add("bday")
                vcard.bday.value = parsed_date.strftime("%Y-%m-%dT%H:%M:%S%z")
            else:
                await __event_emitter__(
                {
                    "data": {
                        "description": f"Invalid date format for birthday: {birthday}. Expected format: YYYY-MM-DDTHH:MM:SS±HHMM.",
                        "status": "complete",
                        "done": True,
                    },
                    "type": "status",
                })

        if note:
            vcard.add("note")
            vcard.note.value = note

        if photo_url:
            vcard.add("photo")
            vcard.photo.value = photo_url
            vcard.photo.type_param = "URL"

        for key, value in kwargs.items():
            vcard.add(key).value = value

        try:
            result = vcard.serialize()

            await __event_emitter__(
                {
                    "type": "message",
                    "data": {"content": f"```VCARD\n{result}\n```\n"},
                }
            )

            return result
        except Exception as e:
            await __event_emitter__(
                {
                    "data": {
                        "description": f"Error serializing VCard: {e}",
                        "status": "complete",
                        "done": True,
                    },
                    "type": "status",
                }
            )

    async def create_icalendar_todo(
        self,
        __event_emitter__: Callable[[dict], Awaitable[None]],
        summary: str,
        status: Optional[str] = None,
        uid: Optional[str] = None,
        dtstamp: Optional[str] = None,
        sequence: Optional[str] = None,
        created: Optional[str] = None,
        last_modified: Optional[str] = None,
        description: Optional[str] = None,
        percent_complete: Optional[str] = None,
        **kwargs
    ) -> str:
        """
        Create an iCalendar TODO item based on the input parameters.
        Note: strictly adhere to JSON syntax.
        :param summary: The required summary of the TODO item.
        :param status: The status of the TODO item.
        :param uid: The unique identifier for the TODO item. Should be left empty if new entry, otherwise provide the existing UID.
        :param dtstamp: The timestamp of the TODO item (ISO 8601 format: YYYY-MM-DDTHH:MM:SS±HHMM).
        :param sequence: The sequence number of the TODO item.
        :param created: The creation date of the TODO item (ISO 8601 format: YYYY-MM-DDTHH:MM:SS±HHMM). If empty, will be set to now.
        :param last_modified: The last modified date of the TODO item (ISO 8601 format: YYYY-MM-DDTHH:MM:SS±HHMM).
        :param description: The description of the TODO item. This description may also be formatted in Markdown, but be careful to escape any special characters.
        :param percent_complete: The percentage of completion of the TODO item.
        :return: The iCalendar formatted TODO item.
        """
        cal = vobject.iCalendar()

        todo = cal.add('vtodo')
        todo.add('dtstamp').value = self._validate_date(dtstamp) if dtstamp else datetime.now()
        if uid:
            todo.add('uid').value = uid
        todo.add('summary').value = summary
        todo.add('status').value = status or 'IN-PROCESS'
        if sequence:
            todo.add('sequence').value = sequence
        if created:
            parsed_created = self._validate_date(created)
            if parsed_created:
                todo.add('created').value = parsed_created
        if last_modified:
            parsed_last_modified = self._validate_date(last_modified)
            if parsed_last_modified:
                todo.add('last-modified').value = parsed_last_modified
        if description:
            todo.add('description').value = description
        if percent_complete:
            todo.add('percent-complete').value = percent_complete
        
        for key, value in kwargs.items():
            todo.add(key).value = value

        try:
            result = cal.serialize()

            await __event_emitter__(
                {
                    "type": "message",
                    "data": {"content": f"```VCALENDAR\n{result}\n```\n"},
                }
            )

            return result
        except Exception as e:
            await __event_emitter__(
                {
                    "data": {
                        "description": f"Error serializing iCalendar: {e}",
                        "status": "complete",
                        "done": True,
                    },
                    "type": "status",
                }
            )
