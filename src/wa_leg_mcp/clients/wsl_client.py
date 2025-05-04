"""
Washington State Legislature API Client

A thin wrapper around the wa-leg-api library for consistent error handling
and potential future enhancements.
"""

import logging
from typing import Any, Dict, List, Optional

from wa_leg_api.amendment import get_amendments
from wa_leg_api.committee import get_committees
from wa_leg_api.committeemeeting import get_committee_meetings
from wa_leg_api.legislation import get_legislation, get_legislation_by_year
from wa_leg_api.legislativedocument import get_documents
from wa_leg_api.sponsor import get_sponsors

logger = logging.getLogger(__name__)


class WSLClient:
    """
    Client for interacting with Washington State Legislature APIs.

    This is a thin wrapper around the wa-leg-api library that provides consistent error handling and logging.
    """

    def get_legislation(self, biennium: str, bill_number: str) -> Optional[List[Dict[str, Any]]]:
        """
        Get information about a specific bill.

        Example Response: [
            {
                'biennium': '2025-26',
                'bill_id': 'HB 1000',
                'bill_number': '1000',
                'substitute_version': '0',
                'engrossed_version': '0',
                'short_legislation_type': {
                    'short_legislation_type': 'B',
                    'long_legislation_type': 'Bill'
                },
                'original_agency': 'House',
                'active': True,
                'state_fiscal_note': False,
                'local_fiscal_note': False,
                'appropriations': False,
                'requested_by_governor': False,
                'requested_by_budget_committee': False,
                'requested_by_department': False,
                'requested_by_other': False,
                'short_description': 'Controlled subst. violations',
                'request': 'H-0097.1',
                'introduced_date': datetime.datetime(2025, 1, 13, 0, 0),
                'current_status': {
                    'bill_id': 'HB 1000',
                    'history_line': 'First reading, referred to Community Safety.',
                    'action_date': datetime.datetime(2025, 1, 13, 0, 0),
                    'amended_by_opposite_body': False,
                    'partial_veto': False,
                    'veto': False,
                    'amendments_exist': False,
                    'status': 'H Community Safe'
                },
                'sponsor': '(Walsh)',
                'prime_sponsor_i_d': 27181,
                'long_description': 'Expanding the circumstances that may constitute a major violation of the uniform controlled substances act.',
                'legal_title': 'AN ACT Relating to expanding the circumstances that may constitute a major violation of the uniform controlled substances act;',
                'companions': None
            }
        ]
        """
        try:
            result = get_legislation(biennium, bill_number)
            return result.get("array_of_legislation", []) if result else None
        except Exception as e:
            logger.error(f"Failed to get legislation {bill_number} for {biennium}: {e}")
            return None

    def get_legislation_by_year(self, year: str) -> Optional[List[Dict[str, Any]]]:
        """
        Get all legislation for a specific year.

        Example Response: [
            {
                'biennium': '2025-26',
                'bill_id': 'HB 1000',
                'bill_number': 1000,
                'substitute_version': 0,
                'engrossed_version': 0,
                'short_legislation_type': {
                    'short_legislation_type': 'B',
                    'long_legislation_type': 'Bill'
                },
                'original_agency': 'House',
                'active': True
            }
        ]
        """
        try:
            result = get_legislation_by_year(year)
            return result.get("array_of_legislation_info", []) if result else None
        except Exception as e:
            logger.error(f"Failed to get legislation for year {year}: {e}")
            return None

    def get_committees(self, biennium: str) -> Optional[List[Dict[str, Any]]]:
        """
        Get list of committees for a biennium.

        Example Response: [
            {
                'id': '31649',
                'name': 'Agriculture & Natural Resources',
                'long_name': 'House Committee on Agriculture & Natural Resources',
                'agency': 'House',
                'acronym': 'AGNR',
                'phone': '(360) 786-7339'
            }
        ]
        """
        try:
            result = get_committees(biennium)
            return result.get("array_of_committee", []) if result else None
        except Exception as e:
            logger.error(f"Failed to get committees for {biennium}: {e}")
            return None

    def get_committee_meetings(
        self, begin_date: str, end_date: str
    ) -> Optional[List[Dict[str, Any]]]:
        """
        Get committee meetings for a date range.

        Example Response: [
            {
                'agenda_id': 32300,
                'agency': 'Joint',
                'committees': [
                    {
                        'id': '27992',
                        'name': 'Joint Committee on Employment Relations',
                        'long_name': 'Joint Joint Committee on Employment Relations',
                        'agency': 'Joint',
                        'acronym': 'JCER',
                        'phone': None
                    }
                ],
                'room': 'Virtual',
                'building': None,
                'address': ',',
                'city': None,
                'state': '',
                'zip_code': 0,
                'date': datetime.datetime(2025, 1, 9, 14, 0),
                'cancelled': False,
                'revised_date': datetime.datetime(1, 1, 1, 0, 0),
                'contact_information': None,
                'committee_type': 'Full Committee',
                'notes': "To view committee meetings or access the committee meeting documents, visit the Legislature's committee schedules, agendas, and documents website: https://app.leg.wa.gov/committeeschedules"
            }
        ]
        """
        try:
            result = get_committee_meetings(begin_date, end_date)
            return result.get("array_of_committee_meeting", []) if result else None
        except Exception as e:
            logger.error(f"Failed to get committee meetings from {begin_date} to {end_date}: {e}")
            return None

    def get_sponsors(self, biennium: str) -> Optional[List[Dict[str, Any]]]:
        """
        Get list of sponsors/legislators for a biennium.

        Example Response: [
            {
                'id': '31526',
                'name': 'Peter Abbarno',
                'long_name': 'Representative Abbarno',
                'agency': 'House',
                'acronym': 'ABBA',
                'party': 'R',
                'district': '20',
                'phone': '(360) 786-7896',
                'email': 'Peter.Abbarno@leg.wa.gov',
                'first_name': 'Peter',
                'last_name': 'Abbarno'
            }
        ]
        """
        try:
            result = get_sponsors(biennium)
            return result.get("array_of_member", []) if result else None
        except Exception as e:
            logger.error(f"Failed to get sponsors for {biennium}: {e}")
            return None

    def get_amendments(self, year: str) -> Optional[List[Dict[str, Any]]]:
        """
        Get amendments for a specific bill.

        Example Response: [
            {
                'bill_number': 5195,
                'name': '5195-S AMH THAR H2391.1',
                'bill_id': 'SSB 5195',
                'legislative_session': '2025 Regular Session',
                'type': 'Floor',
                'floor_number': 1457,
                'sponsor_name': 'Tharinger',
                'description': 'Striker',
                'drafter': 'H2391.1',
                'floor_action': 'ADOPTED',
                'floor_action_date': datetime.datetime(2025, 4, 27, 0, 0),
                'document_exists': True,
                'htm_url': 'http://lawfilesext.leg.wa.gov/biennium/2025-26/Htm/Amendments/House/5195-S AMH THAR H2391.1.htm',
                'pdf_url': 'http://lawfilesext.leg.wa.gov/biennium/2025-26/Pdf/Amendments/House/5195-S AMH THAR H2391.1.pdf',
                'agency': 'House'
            }
        ]
        """
        try:
            result = get_amendments(year)
            return result.get("array_of_amendment", []) if result else None
        except Exception as e:
            logger.error(f"Failed to get amendments in {year}: {e}")
            return None

    def get_documents(self, biennium: str, bill_number: str) -> Optional[List[Dict[str, Any]]]:
        """
        Get documents for a specific bill.

        Example Response: [
            {
                'name': '1000',
                'short_friendly_name': 'Original Bill',
                'biennium': '2025-26',
                'long_friendly_name': 'House Bill 1000',
                'description': None,
                'type': 'House Bills',
                'class': 'Bills',
                'htm_url': 'http://lawfilesext.leg.wa.gov/biennium/2025-26/Htm/Bills/House Bills/1000.htm',
                'htm_create_date': datetime.datetime(2024, 12, 2, 14, 22, 43, 770000),
                'htm_last_modified_date': datetime.datetime(2024, 12, 2, 14, 22, 43, 770000),
                'pdf_url': 'http://lawfilesext.leg.wa.gov/biennium/2025-26/Pdf/Bills/House Bills/1000.pdf',
                'pdf_create_date': datetime.datetime(2024, 12, 2, 14, 22, 43, 970000),
                'pdf_last_modified_date': datetime.datetime(2024, 12, 2, 14, 22, 43, 970000),
                'bill_id': 'HB 1000'
            }
        ]
        """
        try:
            result = get_documents(biennium, bill_number)
            return result.get("array_of_legislative_document", []) if result else None
        except Exception as e:
            logger.error(f"Failed to get documents for {bill_number} in {biennium}: {e}")
            return None
