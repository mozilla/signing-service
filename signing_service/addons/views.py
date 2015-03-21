import os.path

from base64 import b64encode

from django import forms
from django.conf import settings

from commonware.log import getLogger
from rest_framework.response import Response

from websigning import new_addon_signer
from websigning.sign.xpi import ParsingError, Signature

from signing_service.base import APIView
from signing_service.exceptions import BadRequestError
from signing_service.apps.views import SignAppForm

log = getLogger(__name__)


# Initialize the signer
_SIGNER = new_addon_signer(settings.SIGNING_SERVICE_ADDONS_CA_KEY_FILE,
                           settings.SIGNING_SERVICE_ADDONS_CA_CERT_FILE,
                           settings.SIGNING_SERVICE_ADDONS_BASE_DN,
                           backend=settings.SIGNING_SERVICE_ENGINE,
                           key_size=settings.SIGNING_SERVICE_ADDONS_KEY_SIZE,
                           validity_lifetime=settings.SIGNING_SERVICE_ADDONS_LIFETIME,  # noqa
                           digest_alg=settings.SIGNING_SERVICE_ADDONS_DIGEST_ALGO,  # noqa
                           cert_extensions=settings.SIGNING_SERVICE_ADDONS_CERT_EXTENSIONS)  # noqa


class SignAddonForm(SignAppForm):
    # max_length refers to the filename length, not the size of the file
    # itself
    file = forms.FileField(max_length=128)
    addon_id = forms.CharField(min_length=4, max_length=128)


class AddonsView(APIView):

    def post(self, request):
        if 'addons' not in settings.SIGNING_SERVICE_WE_ARE_SIGNING:
            raise BadRequestError('Addons signing not supported by this '
                                  'instance.')

        form = SignAddonForm(request.POST, request.FILES)
        if not form.is_valid():
            return self.form_errors([form])

        addon_id = form.cleaned_data['addon_id']
        fname = os.path.splitext(request.FILES['file'].name)[0]
        # It's a file object, remember to read it
        jar_signature = form.cleaned_data['file'].read()
        pkcs7 = _SIGNER.sign(jar_signature, addon_id)

        return Response({fname + '.rsa': b64encode(pkcs7)})
