import os.path

from base64 import b64encode

from django import forms
from django.conf import settings

from django_paranoia.forms import ParanoidForm
from commonware.log import getLogger
from rest_framework.response import Response

from websigning import new_app_signer
from websigning.sign.xpi import ParsingError, Signature

from signing_service.base import APIView
from signing_service.exceptions import BadRequestError


log = getLogger(__name__)


# Initialize the signer
_SIGNER = new_app_signer(settings.SIGNING_SERVICE_APPS_KEY_FILE,
                         settings.SIGNING_SERVICE_APPS_CERT_FILE,
                         settings.SIGNING_SERVICE_APPS_CA_CHAIN_FILE,
                         backend=settings.SIGNING_SERVICE_ENGINE)


class SignAppForm(ParanoidForm):
    # max_length refers to the filename length, not the size of the file
    # itself
    file = forms.FileField(max_length=128)

    def clean_file(self):
        jar_signature = self.cleaned_data['file']
        try:
            Signature.parse(jar_signature)
            # Don't forget to reset the file state
            jar_signature.seek(0)
        except ParsingError, e:
            raise forms.ValidationError(str(e))
        return jar_signature


class AppsView(APIView):

    def post(self, request):
        if 'apps' not in settings.SIGNING_SERVICE_WE_ARE_SIGNING:
            raise BadRequestError('Apps signing not supported by this '
                                  'instance.')

        form = SignAppForm(request.POST, request.FILES)
        if not form.is_valid():
            return self.form_errors([form])

        fname = os.path.splitext(request.FILES['file'].name)[0]
        jar_signature = form.cleaned_data['file']
        pkcs7 = _SIGNER.sign(jar_signature)

        return Response({fname + '.rsa': b64encode(pkcs7)})
