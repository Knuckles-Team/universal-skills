#!/usr/bin/python
# coding: utf-8
from typing import Optional, List, Any, Dict
from pydantic import BaseModel, ConfigDict, Field
import requests

class Response(BaseModel):
    """
    Standard Response Wrapper.
    """
    model_config = ConfigDict(arbitrary_types_allowed=True)
    response: requests.Response
    data: Any = None

class BaseModelWrapper(BaseModel):
    """
    Base Model wrapping common functionalities such as extracting nested API parameters
    from the root attributes.
    """
    model_config = ConfigDict(populate_by_name=True)

    @property
    def api_parameters(self) -> dict:
        """
        Convert the Pydantic model to a dictionary suitable for passing as API arguments or params.
        Can be customized to exclude specific internal fields like IDs that are passed in the URL.
        """
        return self.model_dump(exclude_none=True, by_alias=True)

class ExampleResourceModel(BaseModelWrapper):
    """
    Input model for the example resource.
    """
    resource_id: Optional[str] = Field(None, description="The unique ID of the resource.")
    limit: Optional[int] = Field(None, description="Pagination limit")
    offset: Optional[int] = Field(None, description="Pagination offset")

    @property
    def api_parameters(self) -> dict:
        # Exclude resource_id from query params since it's typically part of the URL path
        return self.model_dump(exclude_none=True, exclude={'resource_id'}, by_alias=True)

class ExampleResourceResponse(BaseModel):
    """
    Output model parsed from the JSON response.
    """
    id: str
    name: str
    status: Optional[str] = None
