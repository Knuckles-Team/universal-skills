import sys

import requests
from agent_connector_sdk.exceptions import (
    AuthError,
    ParameterError,
    UnauthorizedError,
    require_auth,
)
from pydantic import ValidationError

from stirlingpdf_agent.api.api_client_base import BaseApiClient
from stirlingpdf_agent.stirlingpdf_agent_models import AddWatermarkModel, Response


class WatermarkClient(BaseApiClient):
    @staticmethod
    def _ingest_watermark(filepath: str, output_bytes: bytes, params: dict) -> None:
        """Best-effort native KG ingestion of a completed add-watermark operation.

        Records a :PdfOperation
        with :usedTool / :produced / :derivedFrom / :appliedWatermark provenance. Fully
        guarded: no-ops when the epistemic-graph engine or agent-connector-sdk KG stack is
        absent, so the watermark call never fails because of ingestion.
        """
        try:
            from stirlingpdf_agent.kg_ingest import ingest_operation

            ingest_operation(
                "add_watermark",
                params=params,
                size_bytes=len(output_bytes) if output_bytes else None,
            )
        except Exception as e:  # noqa: BLE001 — ingestion is strictly best-effort
            print(f"KG ingest skipped: {type(e).__name__}", file=sys.stderr)

    def get_status(self) -> Response:
        """
        Read the Stirling PDF server's status and version (GET /api/v1/info/status).

        The route needs no API key on a server without security; a configured
        key is still sent, and a 401/403 maps to the auth errors.

        :return: Response whose data is the server's status document.
        :rtype: Response
        """
        try:
            response = self._session.get(
                url=f"{self.url}/info/status", headers=self.headers
            )
            response.raise_for_status()
            return Response(response=response, data=response.json())
        except requests.exceptions.HTTPError as e:
            if e.response.status_code in [401, 403]:
                exc = AuthError if e.response.status_code == 401 else UnauthorizedError
                raise exc from e
            raise e from e

    @require_auth
    def add_watermark(
        self,
        filepath: str,
        watermarkType: str | None = None,
        watermarkText: str | None = None,
        alphabet: str | None = None,
        fontSize: str | None = None,
        rotation: str | None = None,
        opacity: str | None = None,
        widthSpacer: str | None = None,
        heightSpacer: str | None = None,
    ) -> Response:
        """
        Add a watermark to a PDF file.

        :param filepath: Path to the input PDF file.
        :type filepath: str
        :param watermarkType: Type of watermark (e.g. 'text').
        :param watermarkText: The text of the watermark.
        :param alphabet: Alphabet type (default roman).
        :param fontSize: Font size (default 30).
        :param rotation: Rotation angle (default 0).
        :param opacity: Opacity from 0.0 to 1.0 (default 0.5).
        :param widthSpacer: Width spacing (default 50).
        :param heightSpacer: Height spacing (default 50).

        :return: Response containing the raw PDF bytes.
        :rtype: Response
        """
        try:
            optional = {
                "alphabet": alphabet,
                "fontSize": fontSize,
                "rotation": rotation,
                "opacity": opacity,
                "widthSpacer": widthSpacer,
                "heightSpacer": heightSpacer,
            }
            model = AddWatermarkModel(
                **{
                    k: v
                    for k, v in {
                        "watermarkType": watermarkType,
                        "watermarkText": watermarkText,
                        **optional,
                    }.items()
                    if v is not None
                },
            )

            with open(filepath, "rb") as f:
                files = {"fileInput": (filepath, f, "application/pdf")}
                response = self._session.post(
                    url=f"{self.url}/general/add-watermark",
                    data=model.api_parameters,
                    files=files,
                    headers=self.headers,
                )

            response.raise_for_status()

            self._ingest_watermark(filepath, response.content, model.api_parameters)

            return Response(response=response, data=response.content)

        except ValidationError as ve:
            print(
                f"Invalid parameters or response data: {ve.errors()}", file=sys.stderr
            )
            raise ParameterError(f"Invalid parameters: {ve.errors()}") from ve
        except requests.exceptions.HTTPError as e:
            if e.response.status_code in [401, 403]:
                exc = AuthError if e.response.status_code == 401 else UnauthorizedError
                raise exc from e
            raise e from e
        except Exception as e:
            print(f"API call failed: {type(e).__name__}", file=sys.stderr)
            raise e from e
