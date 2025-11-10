"""Mini implementação de Flask suficiente para os testes automatizados."""

from __future__ import annotations

import json
from dataclasses import dataclass
from http import HTTPStatus
from typing import Any, Callable, Dict, Iterable, List, Optional, Tuple
from urllib.parse import parse_qs, urlencode


@dataclass
class Response:
    data: Any
    status_code: int = HTTPStatus.OK
    headers: Dict[str, str] | None = None

    def get_data(self, as_text: bool = False):
        if as_text:
            return self.data if isinstance(self.data, str) else json.dumps(self.data)
        if isinstance(self.data, (bytes, bytearray)):
            return bytes(self.data)
        if isinstance(self.data, str):
            return self.data.encode("utf-8")
        return json.dumps(self.data).encode("utf-8")

    def get_json(self):
        if isinstance(self.data, (dict, list)):
            return self.data
        if isinstance(self.data, str):
            return json.loads(self.data)
        return json.loads(self.get_data().decode("utf-8"))


class Request:
    def __init__(self):
        self.headers: Dict[str, str] = {}
        self.args: Dict[str, str] = {}
        self.form: Dict[str, str] = {}
        self._json_data: Any = None
        self.method: str = "GET"

    def get_json(self, silent: bool = False):
        if self._json_data is None and not silent:
            raise ValueError("No JSON payload available")
        return self._json_data


request = Request()

_current_app: "Flask" | None = None


def jsonify(data: Any = None, **kwargs: Any) -> Response:
    if data is None:
        data = kwargs
    return Response(data)


def redirect(location: str, status_code: int = HTTPStatus.FOUND) -> Response:
    return Response("", status_code=status_code, headers={"Location": location})


def render_template(template_name: str, **context: Any) -> Response:
    # Renderização simplificada apenas para mostrar o nome do template e dados principais.
    body = {
        "template": template_name,
        "context": context,
    }
    html = "<html><body><pre>" + json.dumps(body, default=str, indent=2) + "</pre></body></html>"
    return Response(html)


class _ContextProcessor:
    def __init__(self):
        self.processors: List[Callable[[], Dict[str, Any]]] = []

    def add(self, func: Callable[[], Dict[str, Any]]):
        self.processors.append(func)
        return func


@dataclass
class _Route:
    rule: str
    methods: Tuple[str, ...]
    func: Callable
    parts: List[Tuple[str, Optional[str]]]


class Flask:
    def __init__(self, name: str):
        self.name = name
        self._routes: List[_Route] = []
        self._context_processor = _ContextProcessor()
        self.secret_key: str | None = None
        self._flashes: List[Tuple[str, str]] = []
        global _current_app
        _current_app = self

    # Decorators -----------------------------------------------------------------
    def route(self, rule: str, methods: Optional[Iterable[str]] = None):
        if methods is None:
            methods = ("GET",)
        methods = tuple(method.upper() for method in methods)

        def decorator(func: Callable):
            raw_rule = rule.strip("/")
            if raw_rule:
                fragments = raw_rule.split("/")
            else:
                fragments = []

            parts = []
            for fragment in fragments:
                if fragment.startswith("<") and fragment.endswith(">"):
                    fragment = fragment[1:-1]
                    if ":" in fragment:
                        type_name, name = fragment.split(":", 1)
                    else:
                        type_name, name = "string", fragment
                    parts.append((name, type_name))
                else:
                    parts.append((fragment, None))
            self._routes.append(_Route(rule, methods, func, parts))
            return func

        return decorator

    def context_processor(self, func: Callable[[], Dict[str, Any]]):
        return self._context_processor.add(func)

    # Routing --------------------------------------------------------------------
    def _match_route(self, path: str, method: str):
        segments = [segment for segment in path.strip("/").split("/") if segment]
        for route in self._routes:
            if method not in route.methods:
                continue
            route_segments = [part for part, _ in route.parts]
            if len(route_segments) != len(segments):
                continue
            values = {}
            matched = True
            for segment, (part, type_name) in zip(segments, route.parts):
                if type_name is None:
                    if segment != part:
                        matched = False
                        break
                else:
                    try:
                        if type_name == "int":
                            values[part] = int(segment)
                        else:
                            values[part] = segment
                    except ValueError:
                        matched = False
                        break
            if matched:
                return route, values
        return None, None

    def _build_url(self, endpoint: str, values: Dict[str, Any]) -> str:
        for route in self._routes:
            if route.func.__name__ != endpoint:
                continue
            url_parts = []
            for part, type_name in route.parts:
                if type_name is None:
                    url_parts.append(part)
                else:
                    if part not in values:
                        raise KeyError(f"Missing value for {part}")
                    url_parts.append(str(values[part]))
            return "/" + "/".join(url_parts)
        raise KeyError(f"Endpoint {endpoint} não encontrado")

    # Request handling -----------------------------------------------------------
    def dispatch_request(self, method: str, path: str, headers: Dict[str, str], data: Any = None):
        path_only, _, query_string = path.partition("?")
        route, values = self._match_route(path_only, method)
        if route is None:
            return Response({"error": "Not Found"}, status_code=HTTPStatus.NOT_FOUND)

        request.headers = headers
        request.method = method
        request.args = {}
        request.form = {}
        request._json_data = None

        if query_string:
            request.args = {k: v[0] for k, v in parse_qs(query_string).items()}

        content_type = headers.get("Content-Type", "")
        if method in {"POST", "PUT", "PATCH"}:
            if "application/json" in content_type and data:
                request._json_data = json.loads(data)
            elif data:
                request.form = {k: v[0] for k, v in parse_qs(data).items()}

        response = route.func(**(values or {}))
        if not isinstance(response, Response):
            response = Response(response)
        if response.headers is None:
            response.headers = {}
        return response

    # Test client ----------------------------------------------------------------
    class _TestClient:
        def __init__(self, app: "Flask"):
            self.app = app

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

        def open(self, path: str, method: str = "GET", headers: Optional[Dict[str, str]] = None, data: Any = None, json_data: Any = None):
            headers = headers or {}
            body = None
            if json_data is not None:
                headers.setdefault("Content-Type", "application/json")
                body = json.dumps(json_data)
            elif data is not None:
                if isinstance(data, dict):
                    body = urlencode(data)
                    headers.setdefault("Content-Type", "application/x-www-form-urlencoded")
                else:
                    body = data
            return self.app.dispatch_request(method.upper(), path, headers, body)

        def get(self, path: str, headers: Optional[Dict[str, str]] = None):
            return self.open(path, "GET", headers=headers)

        def post(self, path: str, headers: Optional[Dict[str, str]] = None, data: Any = None, json: Any = None):
            return self.open(path, "POST", headers=headers, data=data, json_data=json)

        def put(self, path: str, headers: Optional[Dict[str, str]] = None, data: Any = None, json: Any = None):
            return self.open(path, "PUT", headers=headers, data=data, json_data=json)

        def delete(self, path: str, headers: Optional[Dict[str, str]] = None):
            return self.open(path, "DELETE", headers=headers)

    def test_client(self):
        return Flask._TestClient(self)

    def run(self, debug: bool = False):  # pragma: no cover - não utilizado nos testes
        raise RuntimeError("run() não é suportado no ambiente de testes")

    class _AppContext:
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

    def app_context(self):
        return Flask._AppContext()


# Utilidades globais -------------------------------------------------------------

def url_for(endpoint: str, **values: Any) -> str:
    if _current_app is None:
        raise RuntimeError("Nenhuma aplicação ativa para url_for")
    return _current_app._build_url(endpoint, values)


def flash(message: str, category: str = "message") -> None:  # pragma: no cover - comportamento mínimo
    if _current_app is None:
        return
    _current_app._flashes.append((category, message))


def get_flashed_messages(with_categories: bool = False):  # pragma: no cover - usado apenas em templates
    if _current_app is None:
        return []
    messages = list(_current_app._flashes)
    _current_app._flashes.clear()
    if with_categories:
        return messages
    return [message for _, message in messages]
