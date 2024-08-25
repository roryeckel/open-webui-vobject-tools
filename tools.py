"""
title: VCard Generation Toolkit
author: ex0dus
author_url: https://github.com/roryeckel
version: 0.0.1
requirements: vobject, pytz
"""
import vobject
from datetime import datetime
from pytz import UTC
from dateutil import parser
from typing import Callable, Awaitable, Optional

def validate_date(date_string: str) -> Optional[datetime]:
    """
    Validate and parse a date string.
    :param date_string: The date string to validate.
    :return: Parsed UTC datetime object if valid, None otherwise.
    """
    try:
        return parser.parse(date_string).astimezone(UTC)
    except ValueError:
        return None

class Tools:
    def __init__(self):
        pass

    async def create_contact_vcard(
        self,
        __event_emitter__: Callable[[dict], Awaitable[None]],
        first_name: str,
        last_name: str = None,
        organization: str = None,
        email: str = None,
        phone: str = None,
        address: str = None,
        title: str = None,
        website: str = None,
        birthday: str = None,
        note: str = None,
        photo_url: str = None
    ) -> str:
        """
        Create a new contact VCard based on the input parameters.
        Note: strictly adhere to JSON syntax.
        :param first_name: The first name of the contact.
        :param last_name: The last name of the contact.
        :param organization: The organization of the contact.
        :param email: The email of the contact.
        :param phone: The phone number of the contact.
        :param address: The address of the contact.
        :param title: The job title of the contact.
        :param website: The website of the contact.
        :param birthday: The birthday of the contact.
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
            parsed_date = validate_date(birthday)
            if parsed_date:
                vcard.add("bday").value = parsed_date.isoformat()
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

        # for key, value in kwargs.items():
        #     vcard.add(key).value = value

        try:
            result = vcard.serialize()

            await __event_emitter__(
                {
                    "type": "message",
                    "data": {"content": f"```vcard\n{result}\n```\n"},
                }
            )

            return result
        except Exception as e:
            print(e)
            vcard.prettyPrint()
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
        status: str = None,
        uid: str = None,
        dtstamp: str = None,
        sequence: str = None,
        created: str = None,
        last_modified: str = None,
        description: str = None,
        percent_complete: str = None
    ) -> str:
        """
        Create a new iCalendar TODO item based on the input parameters.
        Note: strictly adhere to JSON syntax.
        :param summary: The required summary of the TODO item.
        :param status: The status of the TODO item.
        :param uid: The unique identifier for the TODO item. Should be left empty if new entry, otherwise provide the existing UID.
        :param dtstamp: The timestamp of the TODO item.
        :param sequence: The sequence number of the TODO item.
        :param created: The creation date of the TODO item. If empty, will be set to now.
        :param last_modified: The last modified date of the TODO item.
        :param description: The description of the TODO item. This description may also be formatted in Markdown, but be careful to escape any special characters.
        :param percent_complete: The percentage of completion of the TODO item.
        :return: The iCalendar ICS formatted TODO item.
        """
        cal = vobject.iCalendar()

        todo = cal.add('vtodo')
        todo.add('dtstamp').value = validate_date(dtstamp) if dtstamp else datetime.now(UTC)
        if uid:
            todo.add('uid').value = uid
        todo.add('summary').value = summary
        todo.add('status').value = status or 'IN-PROCESS'
        if sequence:
            todo.add('sequence').value = sequence
        if created:
            parsed_created = validate_date(created)
            if parsed_created:
                todo.add('created').value = parsed_created
        if last_modified:
            parsed_last_modified = validate_date(last_modified)
            if parsed_last_modified:
                todo.add('last-modified').value = parsed_last_modified
        if description:
            todo.add('description').value = description
        if percent_complete:
            todo.add('percent-complete').value = percent_complete
        
        # for key, value in kwargs.items():
        #     todo.add(key).value = value

        try:
            result = cal.serialize()

            await __event_emitter__(
                {
                    "type": "message",
                    "data": {"content": f"```icalendar\n{result}\n```\n"},
                }
            )

            return result
        except Exception as e:
            print(e)
            cal.prettyPrint()
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

    async def create_icalendar_event(
        self,
        __event_emitter__: Callable[[dict], Awaitable[None]],
        dtstart: str,
        dtstamp: str = None,
        dtend: str = None,
        location: str = None,
        summary: str = None,
        description: str = None
    ) -> str:
        """
        Create a new iCalendar Event item based on the input parameters.
        :param dtstart: The start date-time of the Event.
        :param dtstamp: The timestamp of the Event.
        :param dtend: The end date-time of the Event.
        :param location: The location of the Event.
        :param summary: The required summary of the Event.
        :param description: The optional description of the Event.
        :return: The iCalendar ICS formatted Event item.
        """
        if not summary:
            description = summary
        if not description:
            description = summary

        cal = vobject.iCalendar()

        event = cal.add('vevent')
        event.add('dtstamp').value = validate_date(dtstamp) if dtstamp else datetime.now(UTC)
        event.add('summary').value = summary

        parsed_dtstart = validate_date(dtstart)
        if parsed_dtstart:
            event.add('dtstart').value = parsed_dtstart

        if not dtend:
            dtend = dtstart

        parsed_dtend = validate_date(dtend)
        if parsed_dtend:
            event.add('dtend').value = parsed_dtend

        if location:
            event.add('location').value = location

        if description:
            event.add('description').value = description

        # for key, value in kwargs.items():
        #     event.add(key).value = value

        try:
            result = cal.serialize()
            await __event_emitter__(
                {
                    "type": "message",
                    "data": {"content": f"```icalendar\n{result}\n```\n"},
                }
            )
            return result
        except Exception as e:
            print(e)
            cal.prettyPrint()
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
