from pathlib import Path
from typing import Type

from asyncapi_container.asyncapi.generators.v3.generator import AsyncAPISpecV3Generator
from asyncapi_container.containers.v3.simple_spec import SimpleSpecV3
from asyncapi_container.utils import retrieve_merged_asyncapi_container, retrieve_asyncapi_spec_containers
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates


class FastestAsyncAPIApp(FastAPI):

    def configure(self, asyncapi_spec_classes: list[Type[SimpleSpecV3]]) -> None:
        self.asyncapi_spec_classes = asyncapi_spec_classes


fastest_asyncapi_app = FastestAsyncAPIApp()

path_to_current_file = Path(__file__)
fastapi_asyncapi_dir = path_to_current_file.parent.parent.parent.parent
asyncapi_v3_template_path = fastapi_asyncapi_dir.joinpath("templates").joinpath("v3")

asyncapi_v3_templates = Jinja2Templates(directory=asyncapi_v3_template_path)


@fastest_asyncapi_app.get("/asyncapi/v3/")
def asyncapi_v3_docs(
        request: Request,
) -> HTMLResponse:
    spec_containers = retrieve_asyncapi_spec_containers(fastest_asyncapi_app.asyncapi_spec_classes)

    asyncapi_generator = AsyncAPISpecV3Generator(
        asyncapi_spec_container=retrieve_merged_asyncapi_container(
            spec_containers,
        )
    )

    first_spec_container = spec_containers[0]

    config = {
        "title": first_spec_container.info.title,
        "version": first_spec_container.info.version,
        "schema": asyncapi_generator.as_json(),
        "config": {
            "show": {
                "sidebar": True,
                "info": True,
                "servers": True,
                "operations": True,
                "messages": True,
                "schemas": True,
                "errors": True,
            },
            "expand": {
                "messageExamples": False,
            },
            "sidebar": {
                "showServers": "byDefault",
                "showOperations": "byDefault",
            },
        },
    }
    context = {}
    context["asyncapi_json"] = config

    context["service_title"] = first_spec_container.info.title

    return asyncapi_v3_templates.TemplateResponse(
        request=request, name="asyncapi.html", context=context
    )
