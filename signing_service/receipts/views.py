import json

from django.conf import settings

from commonware.log import getLogger
from rest_framework.response import Response

from websigning import new_receipt_signer
from websigning.validators import (
    valid_receipt,
    ValidationError,
    ReceiptConflict)

from signing_service.base import APIView
from signing_service.exceptions import BadRequestError, ConflictError


log = getLogger(__name__)


# Initialize the credentials and signer
_SIGNER = new_receipt_signer(settings.SIGNING_SERVICE_RECEIPTS_KEY_FILE,
                             settings.SIGNING_SERVICE_RECEIPTS_CERT_FILE)


class ReceiptsView(APIView):

    def post(self, request):
        if 'receipts' not in settings.SIGNING_SERVICE_WE_ARE_SIGNING:
            raise BadRequestError('Receipts signing not supported by this '
                                  'instance.')

        try:
            receipt = json.loads(request.body)
        except ValueError:
            raise BadRequestError('Invalid JSON receipt')

        # cert_data is the decoded JSON blob
        try:
            valid_receipt(receipt, _SIGNER.cert_data,
                          settings.SIGNING_SERVICE_RECEIPTS_ISSUERS)
        except ValidationError, e:
            log.warning(e.log_msg)
            raise BadRequestError(e.short_msg)
        except ReceiptConflict, e:
            log.warning(e.log_msg)
            raise ConflictError(e.short_msg)

        # The parsed body goes in as a dict and is eventually converted back
        # to JSON before signing.
        signed_jwt = _SIGNER.sign(receipt)

        return Response({'receipt': '~'.join((_SIGNER.certificate,
                                              signed_jwt))})
