#!/usr/bin/python
# coding: utf-8
from typing import Optional

import requests
import urllib3
from pydantic import ValidationError

from {api_name}_models import (
    ExampleResourceModel,
    ExampleResourceResponse,
    Response
)
from agent_utilities.decorators import require_auth
from agent_utilities.exceptions import (
    AuthError,
    UnauthorizedError,
    ParameterError,
    MissingParameterError,
)

class Api(object):

    def __init__(
        self,
        url: str = None,
        username: Optional[str] = None,
        password: Optional[str] = None,
        token: Optional[str] = None,
        proxies: Optional[dict] = None,
        verify: Optional[bool] = True,
    ):
        if url is None:
            raise MissingParameterError

        self._session = requests.Session()
        self.base_url = url.rstrip("/")
        self.url = f"{self.base_url}/api/v1"
        self.headers = None
        self.token = None
        self.verify = verify
        self.proxies = proxies

        if self.verify is False:
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

        if token:
            self.token = token
            self.headers = {
                "Authorization": f"Bearer {self.token}",
                "Content-Type": "application/json",
            }
        elif username and password:
            self.headers = {
                "Authorization": f"Basic ..." # Encode if basic auth is used
            }
        else:
            raise MissingParameterError

        # Optional: Test authentication
        response = self._session.get(
            url=f"{self.url}/auth/test",
            headers=self.headers,
            verify=self.verify,
            proxies=self.proxies,
        )

        if response.status_code == 403:
            raise UnauthorizedError
        elif response.status_code == 401:
            raise AuthError
        elif response.status_code == 404:
            raise ParameterError

    @require_auth
    def get_example_resource(self, **kwargs) -> Response:
        """
        Get information about an example resource.

        :param resource_id: The unique identifier.
        :type resource_id: str

        :return: Response containing parsed Pydantic model.
        :rtype: Response

        :raises MissingParameterError: If the required parameter is not provided.
        """
        try:
            model = ExampleResourceModel(**kwargs)
            if model.resource_id is None:
                 raise MissingParameterError

            response = self._session.get(
                url=f"{self.url}/resources/{model.resource_id}",
                params=model.api_parameters,
                headers=self.headers,
                verify=self.verify,
                proxies=self.proxies,
            )
            response.raise_for_status()
            json_response = response.json()
            
            # Extract data if nested, e.g., result_data = json_response.get("result", json_response)
            parsed_data = ExampleResourceResponse.model_validate(json_response)
            return Response(response=response, data=parsed_data)
        except ValidationError as ve:
            print(f"Invalid parameters or response data: {ve.errors()}")
            raise ParameterError(f"Invalid parameters: {ve.errors()}")
        except requests.exceptions.HTTPError as e:
            if e.response.status_code in [401, 403]:
                raise AuthError if e.response.status_code == 401 else UnauthorizedError
            raise e
        except Exception as e:
            print(f"Error during API call: {e}")
            raise
