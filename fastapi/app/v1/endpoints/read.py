import os
import traceback
from collections.abc import Iterable

from app.models.database import SessionLocal
from app.settings import serverSettings, tables
from app.sta2rest import sta2rest
from fastapi.responses import JSONResponse, Response
from sqlalchemy.orm import Session

from fastapi import APIRouter, Depends, Request, status

v1 = APIRouter()

try:
    DEBUG = int(os.getenv("DEBUG"))
    if DEBUG:
        from app.utils.utils import response2jsonfile
except:
    DEBUG = 0


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def __handle_root(request: Request):
    """
    Handle the root path.

    Args:
        request (Request): The incoming request object.

    Returns:
        dict: The response containing the value and server settings.
    """
    value = []
    # append the domain to the path for each table
    for table in tables:
        value.append(
            {
                "name": table,
                "url": f"{os.getenv('HOSTNAME')}{os.getenv('SUBPATH')}{os.getenv('VERSION')}"
                + "/"
                + table,
            }
        )

    response = {
        "value": value,
        "serverSettings": serverSettings,
    }
    if DEBUG:
        response2jsonfile(request, response, "requests.json")
    return response


@v1.api_route("/{path_name:path}", methods=["GET"])
async def catch_all_get(
    request: Request, path_name: str, db: Session = Depends(get_db)
):
    """
    Handle GET requests for all paths.

    Args:
        request (Request): The incoming request object.
        path_name (str): The path name extracted from the URL.
        db (Session, optional): The database session. Defaults to Depends(get_db).

    Returns:
        dict: The response data.

    Raises:
        JSONResponse: If the requested resource is not found.
        JSONResponse: If there is a bad request.
    """
    if not path_name:
        # Handle the root path
        return __handle_root(request)

    try:
        # get full path from request
        full_path = request.url.path
        if request.url.query:
            full_path += "?" + request.url.query

        result = sta2rest.STA2REST.convert_query(full_path, db)
        items = result["query"]
        query_count = result["query_count"]
        item_dicts = []
        for item in items:
            item_dicts.append(item[0])

        data = {}
        if len(item_dicts) == 1 and result["single_result"]:
            data = item_dicts[0]
        else:
            nextLink = f"{os.getenv('HOSTNAME')}{full_path}"
            new_top_value = 100
            if "$top" in nextLink:
                start_index = nextLink.find("$top=") + 5
                end_index = len(nextLink)
                for char in ("&", ";", ")"):
                    char_index = nextLink.find(char, start_index)
                    if char_index != -1 and char_index < end_index:
                        end_index = char_index
                top_value = int(nextLink[start_index:end_index])
                new_top_value = top_value
                nextLink = (
                    nextLink[:start_index]
                    + str(new_top_value)
                    + nextLink[end_index:]
                )
            else:
                if "?" in nextLink:
                    nextLink = nextLink + f"&$top={new_top_value}"
                else:
                    nextLink = nextLink + f"?$top={new_top_value}"
            if "$skip" in nextLink:
                start_index = nextLink.find("$skip=") + 6
                end_index = len(nextLink)
                for char in ("&", ";", ")"):
                    char_index = nextLink.find(char, start_index)
                    if char_index != -1 and char_index < end_index:
                        end_index = char_index
                skip_value = int(nextLink[start_index:end_index])
                new_skip_value = skip_value + new_top_value
                nextLink = (
                    nextLink[:start_index]
                    + str(new_skip_value)
                    + nextLink[end_index:]
                )
            else:
                new_skip_value = new_top_value
                nextLink = nextLink + f"&$skip={new_skip_value}"
            if result["count_query"]:
                data["@iot.count"] = query_count

            if new_skip_value < query_count:
                data["@iot.nextLink"] = nextLink

            # Always included
            data["value"] = item_dicts

        if result["ref"]:
            if "value" in data:
                if not result["single_result"]:
                    data["value"] = [
                        {"@iot.selfLink": item.get("@iot.selfLink")}
                        for item in data["value"]
                        if "@iot.selfLink" in item
                    ]
                else:
                    if "@iot.selfLink" in data["value"][0]:
                        data["@iot.selfLink"] = data["value"][0][
                            "@iot.selfLink"
                        ]
                    del data["value"]
            else:
                data = (
                    {"@iot.selfLink": data.get("@iot.selfLink")}
                    if "@iot.selfLink" in data
                    else {}
                )

        if result["value"]:
            if "value" in data:
                data = data[list(data.keys())[0]][0]
            data = data[list(data.keys())[0]]
            if data is None:
                if DEBUG:
                    response2jsonfile(request, "", "requests.json")
                return Response(status_code=status.HTTP_200_OK)

        if not data or (
            isinstance(data, Iterable)
            and "value" in data
            and len(data["value"]) == 0
            and result["single_result"]
        ):
            return JSONResponse(
                status_code=status.HTTP_404_NOT_FOUND,
                content={"code": 404, "type": "error", "message": "Not Found"},
            )
        if DEBUG:
            print(f"GET data", data)
            response2jsonfile(request, data, "requests.json")
        return data
    except Exception as e:
        traceback.print_exc()
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"code": 400, "type": "error", "message": str(e)},
        )
