
from fastapi.openapi.utils import get_openapi



def custom_openapi(app):
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="City Alert API",
        version="1.0.0",
        routes=app.routes,
        description="API для реєстру тривог. Додайте токен через Authorize, використовуючи Bearer або X-API-Token.",
    )
    components = openapi_schema.get("components", {})
    security_schemes = components.get("securitySchemes", {})

    # Define both supported auth methods used by the middleware
    security_schemes.update(
        {
            "ApiKeyAuth": {"type": "apiKey", "in": "header", "name": "X-API-Token"},
        }
    )
    components["securitySchemes"] = security_schemes
    openapi_schema["components"] = components

    # Apply global security requirement so all endpoints prompt for token in Swagger
    openapi_schema["security"] = [{"BearerAuth": []}, {"ApiKeyAuth": []}]

    app.openapi_schema = openapi_schema
    return app.openapi_schema
